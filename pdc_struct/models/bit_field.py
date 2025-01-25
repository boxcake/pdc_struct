"""BitField implementation for PDC Struct."""
from sys import byteorder as system_byte_order
from typing import Any, Dict, Set, ClassVar, Literal
from dataclasses import dataclass
from pydantic import BaseModel, PrivateAttr
from pydantic.fields import FieldInfo

from pdc_struct import ByteOrder
from .struct_config import StructConfig


@dataclass
class BitDefinition:
    """Definition of a single bit or bit-range."""
    start_bit: int
    num_bits: int = 1
    is_bool: bool = True  # True for single-bit fields, False for multi-bit int fields

    @property
    def end_bit(self) -> int:
        """Last bit position (exclusive)."""
        return self.start_bit + self.num_bits

    @property
    def max_value(self) -> int:
        """Maximum value for this bit field."""
        return (1 << self.num_bits) - 1


from pydantic import Field


def Bit(start_bit: int, *additional_bits: int, **kwargs) -> FieldInfo:
    """Create a Field with bit information stored in json_schema_extra."""
    # Calculate bit info
    num_bits = 1 + len(additional_bits)
    is_bool = num_bits == 1

    # Verify bits are contiguous
    if additional_bits:
        bits = [start_bit] + list(additional_bits)
        if bits != list(range(min(bits), max(bits) + 1)):
            raise ValueError(f"Bit positions must be contiguous, got {bits}")

    # Store bit info in json_schema_extra
    bit_info = {
        'start_bit': start_bit,
        'num_bits': num_bits,
        'is_bool': is_bool
    }

    # Get existing json_schema_extra or create new
    json_schema_extra = kwargs.pop('json_schema_extra', {})
    if isinstance(json_schema_extra, dict):
        json_schema_extra['bit_info'] = bit_info
    else:
        raise ValueError("json_schema_extra must be a dict")

    # Default to False for bools, 0 for multi-bit fields
    default = kwargs.pop('default', False if is_bool else 0)

    field_params = {
        'default': default,
        **kwargs,
        'json_schema_extra': json_schema_extra,
        'ge': 0 if not is_bool else None,
        'lt': 1 << num_bits if not is_bool else None,
    }

    return Field(**field_params)


class BitFieldModel(BaseModel):
    """Base model for bit field structures, enabling packing of multiple boolean or integer
    values into a single byte/word/dword for C-compatible serialization.

    BitFieldModel maps Python attributes to bits within an integer, facilitating compact
    storage and C struct compatibility. Fields are defined using `Bit()` to specify their
    position and width:

    Example:
        class Flags(BitFieldModel):
            read: bool = Bit(0)     # Maps to bit 0
            write: bool = Bit(1)    # Maps to bit 1
            value: int = Bit(2,3,4) # Maps to bits 2-4

            struct_config = StructConfig(
                mode=StructMode.C_COMPATIBLE,
                bit_width=8  # Must be 8, 16, or 32
            )

    Access individual fields as normal attributes. Use raw_value property to get/set
    the packed integer representation for serialization.
    """

    # Class variables
    struct_config: ClassVar[StructConfig] = StructConfig()
    _bit_definitions: ClassVar[Dict[str, BitDefinition]] = {}
    _struct_format: ClassVar[str] = "B"  # Default to byte, updated in __pydantic_init_subclass__

    def __init__(self, __bit_sequence: bytes = None, **data):
        # If bytes passed, parse them first
        if __bit_sequence is not None:

            byte_order: Literal['little', 'big'] = system_byte_order
            if self.struct_config.byte_order is ByteOrder.LITTLE_ENDIAN:
                byte_order = 'little'
            elif self.struct_config.byte_order is ByteOrder.BIG_ENDIAN:
                byte_order = 'big'

            value = int.from_bytes(__bit_sequence, byteorder=byte_order)

            # Convert raw value to field values
            for name, bit_def in self._bit_definitions.items():
                if bit_def.is_bool:
                    data[name] = bool(value & (1 << bit_def.start_bit))
                else:
                    mask = ((1 << bit_def.num_bits) - 1) << bit_def.start_bit
                    data[name] = (value & mask) >> bit_def.start_bit

        super().__init__(**data)

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        """Initialize and validate a BitFieldStruct subclass."""
        super().__pydantic_init_subclass__(**kwargs)

        # Validate struct_config
        if not hasattr(cls, 'struct_config'):
            raise ValueError("BitFieldStruct requires struct_config with bit_width")

        if cls.struct_config.bit_width not in (8, 16, 32):
            raise ValueError("bit_width must be 8, 16, or 32")

        # Set struct format based on bit width
        cls._struct_format = {
            8: 'B',
            16: 'H',
            32: 'I'
        }[cls.struct_config.bit_width]

        # Initialize bit_definitions
        cls._bit_definitions = {}

        # Collect bit definitions from fields
        used_bits: Set[int] = set()
        for name, field in cls.model_fields.items():
            if field.json_schema_extra and 'bit_info' in field.json_schema_extra:
                bit_info = field.json_schema_extra['bit_info']
                start_bit = bit_info['start_bit']
                num_bits = bit_info['num_bits']
                is_bool = bit_info['is_bool']

                bits = set(range(start_bit, start_bit + num_bits))
                if bits & used_bits:
                    raise ValueError(f"Overlapping bits in field {name}")
                if max(bits) >= cls.struct_config.bit_width:
                    raise ValueError(
                        f"Bit field {name} exceeds bit_width {cls.struct_config.bit_width}"
                    )
                used_bits.update(bits)

                cls._bit_definitions[name] = BitDefinition(
                    start_bit=start_bit,
                    num_bits=num_bits,
                    is_bool=is_bool
                )

    @property
    def raw_value(self) -> int:
        """Calculate bit value from current attributes."""
        value = 0
        for name, bit_def in self._bit_definitions.items():
            attr_value = getattr(self, name)
            if bit_def.is_bool:
                if not isinstance(attr_value, bool):
                    raise ValueError(f"Field {name} requires a boolean value")
                if attr_value:
                    value |= (1 << bit_def.start_bit)
            else:
                if not isinstance(attr_value, int):
                    raise ValueError(f"Field {name} requires an integer value")
                max_val = (1 << bit_def.num_bits) - 1
                if not 0 <= attr_value <= max_val:
                    raise ValueError(f"Field {name} value {attr_value} out of range (0-{max_val})")
                value |= (attr_value << bit_def.start_bit)
        return value

    @raw_value.setter
    def raw_value(self, value: int):
        max_value = (1 << self.struct_config.bit_width) - 1
        if not 0 <= value <= max_value:
            raise ValueError(f"Value {value} out of range for {self.struct_config.bit_width} bits")

        model_fields = self.model_fields
        for name, bit_def in self._bit_definitions.items():
            field = model_fields[name]
            if bit_def.is_bool:
                value_to_set = bool(value & (1 << bit_def.start_bit))
            else:
                mask = ((1 << bit_def.num_bits) - 1) << bit_def.start_bit
                value_to_set = (value & mask) >> bit_def.start_bit

            self.__pydantic_validator__.validate_assignment(self, name, value_to_set)

    @property
    def struct_format_string(self) -> str:
        """Get the struct format string for this bit field."""
        return self._struct_format
