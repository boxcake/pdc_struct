# pdc_struct/c_types.py
"""Fixed-width integer types for C compatibility."""

from typing import Any, ClassVar
from pydantic_core import CoreSchema, core_schema


class Int8(int):
    """8-bit signed integer (-128 to 127)."""
    _min_value: ClassVar[int] = -128
    _max_value: ClassVar[int] = 127
    _struct_format: ClassVar[str] = 'b'

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
        return core_schema.int_schema(
            ge=cls._min_value,
            le=cls._max_value
        )


class UInt8(int):
    """8-bit unsigned integer (0 to 255)."""
    _min_value: ClassVar[int] = 0
    _max_value: ClassVar[int] = 255
    _struct_format: ClassVar[str] = 'B'

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
        return core_schema.int_schema(
            ge=cls._min_value,
            le=cls._max_value
        )


class Int16(int):
    """16-bit signed integer (-32,768 to 32,767)."""
    _min_value: ClassVar[int] = -32768
    _max_value: ClassVar[int] = 32767
    _struct_format: ClassVar[str] = 'h'

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
        return core_schema.int_schema(
            ge=cls._min_value,
            le=cls._max_value
        )


class UInt16(int):
    """16-bit unsigned integer (0 to 65,535)."""
    _min_value: ClassVar[int] = 0
    _max_value: ClassVar[int] = 65535
    _struct_format: ClassVar[str] = 'H'

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
        return core_schema.int_schema(
            ge=cls._min_value,
            le=cls._max_value
        )
