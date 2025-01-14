"""Config class for pdc_struct"""

from dataclasses import dataclass
from typing import Dict, Any
from .enums import StructVersion, ByteOrder, StructMode


@dataclass
class StructConfig:
    """Configuration for struct packing/unpacking.

    Args:
        mode: StructMode determining C compatibility or dynamic Python mode
        version: Protocol version (only used in DYNAMIC mode)
        byte_order: Byte order for struct packing
        metadata: Optional dictionary for custom metadata

    Notes:
        In C_COMPATIBLE mode:
        - No headers are included in the packed data
        - Optional fields are not allowed
        - Strings are fixed-length and null-terminated

        In DYNAMIC mode:
        - Headers are always included
        - Optional fields are supported
        - Strings are length-prefixed and variable length
    """
    mode: StructMode = StructMode.DYNAMIC
    version: StructVersion = StructVersion.V1
    byte_order: ByteOrder = ByteOrder.LITTLE_ENDIAN
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
