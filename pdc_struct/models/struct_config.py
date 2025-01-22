"""Config class for pdc_struct"""

from dataclasses import dataclass
from typing import Dict, Any, Optional

from pdc_struct.enums import (
    BitOrder,
    StructVersion,
    ByteOrder,
    StructMode
)


@dataclass
class StructConfig:
    """Configuration for struct packing/unpacking.

    Args:
        mode: StructMode determining C compatibility or dynamic Python mode
        version: Protocol version (only used in DYNAMIC mode)
        byte_order: Byte order for struct packing
        bit_width: Number of bits for BitFieldStruct (8, 16, or 32)
        bit_order: Bit ordering for BitFieldStruct
        metadata: Optional dictionary for custom metadata

    Notes:
        In C_COMPATIBLE mode:
        - No headers are included in the packed data
        - Optional fields must have defaults
        - Strings are fixed-length and null-terminated

        In DYNAMIC mode:
        - Headers are always included
        - Optional fields are supported
        - Strings are length-prefixed and variable length

        For BitFieldStruct:
        - bit_width must be 8, 16, or 32
        - bit_order determines whether bits are counted from LSB or MSB
        - Only needed when using BitFieldStruct
    """
    mode: StructMode = StructMode.DYNAMIC
    version: StructVersion = StructVersion.V1
    byte_order: ByteOrder = ByteOrder.LITTLE_ENDIAN
    bit_width: Optional[int] = None
    bit_order: BitOrder = BitOrder.LSB_FIRST
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

        # Validate bit_width if provided
        if self.bit_width is not None and self.bit_width not in (8, 16, 32):
            raise ValueError("bit_width must be 8, 16, or 32")
