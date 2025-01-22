"""BitField implementation for PDC Struct."""
from typing import Any, Dict, List, Optional, Set, Tuple, ClassVar
from dataclasses import dataclass
from pydantic import BaseModel

from .struct_config import StructConfig


@dataclass
class BitDefinition:
    """Definition of a single bit or bit-range."""
    start_bit: int
    num_bits: int = 1

    @property
    def end_bit(self) -> int:
        """Last bit position (exclusive)."""
        return self.start_bit + self.num_bits


class Bit:
    """Descriptor for bit field attributes."""

    def __init__(self, start_bit: int, *additional_bits: int):
        """Initialize a bit field.

        Args:
            start_bit: Starting bit position
            *additional_bits: Additional bit positions for multi-bit fields
        """
        self.start_bit = start_bit
        self.num_bits = 1 + len(additional_bits)

        # Verify bits are contiguous if multiple bits specified
        if additional_bits:
            bits = [start_bit] + list(additional_bits)
            if bits != list(range(min(bits), max(bits) + 1)):
                raise ValueError(f"Bit positions must be contiguous, got {bits}")

        # Will be set when the descriptor is bound to the class
        self.name: Optional[str] = None

    def __set_name__(self, owner, name):
        """Called when the descriptor is bound to the class."""
        self.name = name

        # Register this bit definition with the class
        if not hasattr(owner, '_bit_definitions'):
            owner._bit_definitions = {}
        owner._bit_definitions[name] = BitDefinition(self.start_bit, self.num_bits)

    def __get__(self, obj, objtype=None):
        """Get the bit field value."""
        if obj is None:
            return self
        return obj._get_bits(self.name)

    def __set__(self, obj, value):
        """Set the bit field value."""
        obj._set_bits(self.name, value)


class BitFieldStruct(BaseModel):
    """Base class for bit field structures."""

    # Class variables
    struct_config: ClassVar[StructConfig] = StructConfig()
    _bit_definitions: ClassVar[Dict[str, BitDefinition]] = {}

    def __init__(self, **data):
        """Initialize the bit field structure."""
        super().__init__(**data)

        # Validate bit_width in config
        if not hasattr(self, 'struct_config'):
            raise ValueError("BitFieldStruct requires struct_config with bit_width")

        if self.struct_config.bit_width not in (8, 16, 32):
            raise ValueError("bit_width must be 8, 16, or 32")

        # Initialize bit storage
        self._bit_value = 0

        # Validate bit definitions
        self._validate_bit_definitions()

        # Set initial values from data
        for name, value in data.items():
            if name in self._bit_definitions:
                self._set_bits(name, value)

    def _validate_bit_definitions(self):
        """Validate that bit definitions don't overlap and are within range."""
        if not hasattr(self, '_bit_definitions'):
            raise ValueError("No bit fields defined")

        # Check for overlapping bits
        used_bits: Set[int] = set()
        for name, bit_def in self._bit_definitions.items():
            bits = set(range(bit_def.start_bit, bit_def.end_bit))
            if bits & used_bits:
                raise ValueError(f"Overlapping bits in field {name}")
            if max(bits) >= self.struct_config.bit_width:
                raise ValueError(
                    f"Bit field {name} exceeds bit_width {self.struct_config.bit_width}"
                )
            used_bits.update(bits)

    def _get_bits(self, name: str) -> bool:
        """Get the value of a bit field."""
        bit_def = self._bit_definitions[name]
        mask = ((1 << bit_def.num_bits) - 1) << bit_def.start_bit
        return bool((self._bit_value & mask) >> bit_def.start_bit)

    def _set_bits(self, name: str, value: bool):
        """Set the value of a bit field."""
        bit_def = self._bit_definitions[name]
        mask = ((1 << bit_def.num_bits) - 1) << bit_def.start_bit
        self._bit_value &= ~mask  # Clear bits
        if value:
            self._bit_value |= (1 << bit_def.start_bit) & mask  # Set bits

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


