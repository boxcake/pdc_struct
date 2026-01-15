# enums.py
"""Enums for pdc_struct"""

from enum import Enum, IntFlag


class StructVersion(Enum):
    """Version enum for struct format versioning"""

    V1 = 1


class StructMode(Enum):
    """Defines the serialization mode for struct packing.

    Modes:
        C_COMPATIBLE: Fixed-size mode compatible with C structs.
            - Fixed struct size
            - No header metadata
            - Optional fields must have default values or factories
            - Null-terminated strings
            - Fixed-length buffers

        DYNAMIC: Variable-size mode optimized for Python-to-Python communication.
            - Variable struct size
            - Includes header metadata
            - Supports optional fields
            - Variable-length strings
    """

    C_COMPATIBLE = "c_compatible"  # Fixed size, no header, no optional fields
    DYNAMIC = "dynamic"  # Variable size, header present, optional fields supported


class ByteOrder(Enum):
    """Byte order (endianness) for multi-byte value serialization.

    Controls how integers, floats, and other multi-byte values are arranged in memory.
    Each value corresponds to a Python struct module format character.

    Attributes:
        LITTLE_ENDIAN: Least significant byte first. Used by x86, x64, and most ARM
            systems. Struct format: '<'.
        BIG_ENDIAN: Most significant byte first. Also called "network byte order".
            Used by many network protocols. Struct format: '>'.
        NATIVE: Use the system's native byte order. Not recommended for cross-platform
            data exchange. Struct format: '='.

    Example:
        >>> from pdc_struct import StructConfig, ByteOrder
        >>>
        >>> # For network protocols, use big-endian (network byte order)
        >>> config = StructConfig(byte_order=ByteOrder.BIG_ENDIAN)
        >>>
        >>> # For x86/x64 compatibility, use little-endian
        >>> config = StructConfig(byte_order=ByteOrder.LITTLE_ENDIAN)
    """

    LITTLE_ENDIAN = "<"
    BIG_ENDIAN = ">"
    NATIVE = "="


class HeaderFlags(IntFlag):
    """Bit flags stored in byte 1 of DYNAMIC mode headers.

    These flags describe properties of the serialized data, allowing the deserializer
    to correctly interpret the binary format. Multiple flags can be combined using
    bitwise OR.

    The DYNAMIC mode header structure is:
        Byte 0: Version (StructVersion value)
        Byte 1: Flags (this enum)
        Byte 2: Reserved
        Byte 3: Reserved

    Attributes:
        LITTLE_ENDIAN: Data uses little-endian byte ordering (0x00).
        BIG_ENDIAN: Data uses big-endian byte ordering (0x01).
        HAS_OPTIONAL_FIELDS: A field presence bitmap follows the header (0x02).

    Example:
        >>> from pdc_struct.enums import HeaderFlags
        >>>
        >>> # Check flags from raw header data
        >>> header = b'\\x01\\x03\\x00\\x00'  # Version 1, big-endian with optional fields
        >>> flags = header[1]
        >>> bool(flags & HeaderFlags.BIG_ENDIAN)
        True
        >>> bool(flags & HeaderFlags.HAS_OPTIONAL_FIELDS)
        True
    """

    LITTLE_ENDIAN = 0x00
    BIG_ENDIAN = 0x01
    HAS_OPTIONAL_FIELDS = 0x02
    # Bits 2-7 reserved for future use
