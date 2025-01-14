# enums.py
"""Enums for pdc_struct"""

from enum import Enum, IntFlag


class StructVersion(Enum):
    """Version enum for struct format versioning"""
    V1 = 1


class StructMode(Enum):
    C_COMPATIBLE = "c_compatible"  # Fixed size, no header, no optional fields
    DYNAMIC = "dynamic"           # Variable size, header present, optional fields supported

class ByteOrder(Enum):
    """Byte order for struct packing"""
    LITTLE_ENDIAN = '<'
    BIG_ENDIAN = '>'
    NATIVE = '='


class HeaderFlags(IntFlag):
    """Flags for header byte 1"""
    LITTLE_ENDIAN = 0x00
    BIG_ENDIAN = 0x01
    HAS_OPTIONAL_FIELDS = 0x02
    # Bits 2-7 reserved for future use