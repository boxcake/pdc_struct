"""BitField implementation for PDC Struct."""
from typing import Any, Dict, Set, ClassVar
from dataclasses import dataclass
from pydantic import BaseModel, PrivateAttr
from pydantic.fields import FieldInfo


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

    return Field(default=default, **kwargs, json_schema_extra=json_schema_extra)


class BitFieldStruct(BaseModel):
    """Base class for bit field structures."""

    # Class variables
    struct_config: ClassVar[StructConfig] = StructConfig()
    _bit_definitions: ClassVar[Dict[str, BitDefinition]] = {}

    # Declare private attributes
    _bit_value: int = PrivateAttr(default=0)

    def __init__(self, **data):
        # Just do the normal initialization, Pydantic will handle the private attrs
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
        # DEBUG
        print("Bit definitions:")
        for name, bit_def in cls._bit_definitions.items():
            print(f"{name}: start={bit_def.start_bit}, num_bits={bit_def.num_bits}, is_bool={bit_def.is_bool}")

    def __getattribute__(self, name: str) -> Any:
        _bit_definitions = object.__getattribute__(self, '_bit_definitions')
        print(f"get_attribute: {name} in {_bit_definitions}")
        if name in _bit_definitions:
            try:
                _bit_value = object.__getattribute__(self, '_bit_value')
                print(f"Reading {name}, _bit_value={_bit_value:08b}")  # Debug value
                bit_def = _bit_definitions[name]
                mask = ((1 << bit_def.num_bits) - 1) << bit_def.start_bit
                value = (_bit_value & mask) >> bit_def.start_bit
                print(f"Returning {value}")  # Debug result
                return bool(value) if bit_def.is_bool else value
            except Exception as e:
                print(f"Error getting {name}: {e}")  # Debug errors
                raise
        print('Calling object.__getattribute__\n')
        return object.__getattribute__(self, name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Handle setting bit field values."""
        print(f"__setattr__: {name}={value}")
        if name in self._bit_definitions:
            print(f"Setting {name} to {value}")
            bit_def = self._bit_definitions[name]
            if bit_def.is_bool and not isinstance(value, bool):
                raise ValueError(f"Field {name} is a single bit and requires a boolean value")
            if not bit_def.is_bool:
                if not isinstance(value, int):
                    raise ValueError(f"Field {name} spans multiple bits and requires an integer value")
                max_val = (1 << bit_def.num_bits) - 1
                if not 0 <= value <= max_val:
                    raise ValueError(
                        f"Value {value} out of range for {bit_def.num_bits}-bit field {name} (0-{max_val})"
                    )

            print(f"Current _bit_value: {self._bit_value:08b}")
            mask = ((1 << bit_def.num_bits) - 1) << bit_def.start_bit
            print(f"Mask: {mask:08b}")
            self._bit_value &= ~mask  # Clear bits
            print(f"After clear: {self._bit_value:08b}")
            if bit_def.is_bool:
                if value:
                    self._bit_value |= (1 << bit_def.start_bit)
            else:
                self._bit_value |= (value << bit_def.start_bit) & mask
            print(f"Final _bit_value: {self._bit_value:08b}")
        else:
            super().__setattr__(name, value)

    @property
    def raw_value(self) -> int:
        """Get the raw integer value of all bits."""
        return self._bit_value

    @raw_value.setter
    def raw_value(self, value: int):
        """Set the raw integer value of all bits."""
        max_value = (1 << self.struct_config.bit_width) - 1
        if not 0 <= value <= max_value:
            raise ValueError(
                f"Value {value} out of range for {self.struct_config.bit_width} bits"
            )
        self._bit_value = value


