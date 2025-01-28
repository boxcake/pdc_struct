"""Bytes type handler for PDC Struct."""
from typing import Optional, Union

from pydantic import Field

from pdc_struct import ByteOrder
from .meta import TypeHandler


class BytesHandler(TypeHandler):
    """Handler for Python bytes type."""

    @classmethod
    def handled_types(cls) -> list[type]:
        return [bytes, bytearray]

    @classmethod
    def needs_length(cls) -> bool:
        return True

    @classmethod
    def get_struct_format(cls, field) -> str:
        # struct_length should never be None here because validate_field would have failed
        struct_length = cls._get_field_length_generic(field)
        return f'{struct_length}s'

    @classmethod
    def pack(
            cls,
            value: bytes,
            field: Optional[Field] = None,
            struct_config: Optional['StructConfig'] = None      # noqa
    ) -> bytes:
        """Pack bytes/bytearray with proper endianness.

        Args:
            value: The bytes/bytearray to pack
            field: Field information including length constraints
            struct_config: The model's struct configuration for byte order
        """
        if isinstance(value, bytearray):
            value = bytes(value)

        # If no config or native byte order, return as is
        if not struct_config or struct_config.byte_order == ByteOrder.NATIVE:
            return value

        # Get the length this field should be
        length = cls._get_field_length_generic(field)
        if length is None or len(value) <= 1:
            return value  # No need to swap single bytes

        # For little endian, reverse the bytes
        if struct_config.byte_order == ByteOrder.LITTLE_ENDIAN:
            return value[::-1]

        return value

    @classmethod
    def unpack(
            cls,
            value: bytes,
            field: Optional[Field] = None,
            struct_config: Optional['StructConfig'] = None  # noqa
    ) -> Union[bytes, None]:
        """Unpack bytes with proper endianness.

        Args:
            value: The bytes to unpack
            field: Field information including length constraints
            struct_config: The model's struct configuration for byte order
        """

        # If no config or native byte order, return as is
        if not struct_config or struct_config.byte_order == ByteOrder.NATIVE:
            return value

        # Single bytes don't need swapping
        if len(value) <= 1:
            return value

        # For little endian, reverse the bytes
        if struct_config.byte_order == ByteOrder.LITTLE_ENDIAN:
            return value[::-1]

        return value
