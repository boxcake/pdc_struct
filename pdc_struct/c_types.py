# pdc_struct/c_types.py
"""Fixed-width integer types for C compatibility."""

from typing import Any, ClassVar
from pydantic_core import CoreSchema, core_schema


class Int8(int):
    """8-bit signed integer (-128 to 127).

    Equivalent to C's ``int8_t`` or ``signed char``. Serializes to exactly 1 byte.
    Use for small signed values where memory efficiency matters.

    Example:
        >>> from pdc_struct import StructModel, StructConfig, StructMode
        >>> from pdc_struct.c_types import Int8
        >>>
        >>> class Temperature(StructModel):
        ...     celsius: Int8  # -128 to 127 degrees
        ...     struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)
        >>>
        >>> reading = Temperature(celsius=-10)
        >>> len(reading.to_bytes())
        1
    """

    _min_value: ClassVar[int] = -128
    _max_value: ClassVar[int] = 127
    _struct_format: ClassVar[str] = "b"

    def __new__(cls, value: int):
        if not isinstance(value, (int, Int8)):
            raise TypeError(f"{cls.__name__} requires an integer value")
        if not cls._min_value <= value <= cls._max_value:
            raise ValueError(
                f"{cls.__name__} value must be between {cls._min_value} and {cls._max_value}"
            )
        return super().__new__(cls, value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Any,
    ) -> CoreSchema:
        """Pydantic validation schema."""
        return core_schema.int_schema(ge=cls._min_value, le=cls._max_value)


class UInt8(int):
    """8-bit unsigned integer (0 to 255).

    Equivalent to C's ``uint8_t`` or ``unsigned char``. Serializes to exactly 1 byte.
    Commonly used for byte values, flags, and small counters.

    Example:
        >>> from pdc_struct import StructModel, StructConfig, StructMode
        >>> from pdc_struct.c_types import UInt8
        >>>
        >>> class Pixel(StructModel):
        ...     r: UInt8
        ...     g: UInt8
        ...     b: UInt8
        ...     struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)
        >>>
        >>> pixel = Pixel(r=255, g=128, b=0)
        >>> pixel.to_bytes()
        b'\\xff\\x80\\x00'
    """

    _min_value: ClassVar[int] = 0
    _max_value: ClassVar[int] = 255
    _struct_format: ClassVar[str] = "B"

    def __new__(cls, value: int):
        if not isinstance(value, (int, UInt8)):
            raise TypeError(f"{cls.__name__} requires an integer value")
        if not cls._min_value <= value <= cls._max_value:
            raise ValueError(
                f"{cls.__name__} value must be between {cls._min_value} and {cls._max_value}"
            )
        return super().__new__(cls, value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Any,
    ) -> CoreSchema:
        """Pydantic validation schema."""
        return core_schema.int_schema(ge=cls._min_value, le=cls._max_value)


class Int16(int):
    """16-bit signed integer (-32,768 to 32,767).

    Equivalent to C's ``int16_t`` or ``short``. Serializes to exactly 2 bytes.
    Use for medium-range signed values like audio samples or relative coordinates.

    Example:
        >>> from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
        >>> from pdc_struct.c_types import Int16
        >>>
        >>> class AudioSample(StructModel):
        ...     left: Int16
        ...     right: Int16
        ...     struct_config = StructConfig(
        ...         mode=StructMode.C_COMPATIBLE,
        ...         byte_order=ByteOrder.LITTLE_ENDIAN
        ...     )
        >>>
        >>> sample = AudioSample(left=-16384, right=16383)
        >>> len(sample.to_bytes())
        4
    """

    _min_value: ClassVar[int] = -32768
    _max_value: ClassVar[int] = 32767
    _struct_format: ClassVar[str] = "h"

    def __new__(cls, value: int):
        if not isinstance(value, (int, Int16)):
            raise TypeError(f"{cls.__name__} requires an integer value")
        if not cls._min_value <= value <= cls._max_value:
            raise ValueError(
                f"{cls.__name__} value must be between {cls._min_value} and {cls._max_value}"
            )
        return super().__new__(cls, value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Any,
    ) -> CoreSchema:
        """Pydantic validation schema."""
        return core_schema.int_schema(ge=cls._min_value, le=cls._max_value)


class UInt16(int):
    """16-bit unsigned integer (0 to 65,535).

    Equivalent to C's ``uint16_t`` or ``unsigned short``. Serializes to exactly 2 bytes.
    Commonly used for port numbers, lengths, and medium-range counters.

    Example:
        >>> from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
        >>> from pdc_struct.c_types import UInt16
        >>>
        >>> class NetworkHeader(StructModel):
        ...     source_port: UInt16
        ...     dest_port: UInt16
        ...     length: UInt16
        ...     struct_config = StructConfig(
        ...         mode=StructMode.C_COMPATIBLE,
        ...         byte_order=ByteOrder.BIG_ENDIAN  # Network byte order
        ...     )
        >>>
        >>> header = NetworkHeader(source_port=8080, dest_port=443, length=100)
        >>> header.to_bytes()
        b'\\x1f\\x90\\x01\\xbb\\x00d'
    """

    _min_value: ClassVar[int] = 0
    _max_value: ClassVar[int] = 65535
    _struct_format: ClassVar[str] = "H"

    def __new__(cls, value: int):
        if not isinstance(value, (int, UInt16)):
            raise TypeError(f"{cls.__name__} requires an integer value")
        if not cls._min_value <= value <= cls._max_value:
            raise ValueError(
                f"{cls.__name__} value must be between {cls._min_value} and {cls._max_value}"
            )
        return super().__new__(cls, value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Any,
    ) -> CoreSchema:
        """Pydantic validation schema."""
        return core_schema.int_schema(ge=cls._min_value, le=cls._max_value)
