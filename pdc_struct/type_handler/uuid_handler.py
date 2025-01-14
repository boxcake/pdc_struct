"""UUID type handler for PDC Struct."""
from uuid import UUID
from typing import Optional, Union
from pydantic import Field

from pdc_struct import StructConfig
from .meta import TypeHandler
from pdc_struct.enums import ByteOrder


class UUIDHandler(TypeHandler):
    """Handler for Python's UUID type."""

    @classmethod
    def handled_types(cls) -> list[type]:
        return [UUID]

    @classmethod
    def get_struct_format(cls, field) -> str:
        return '16s'

    @classmethod
    def pack(
            cls,
            value: UUID,
            field: Optional[Field] = None,
            struct_config: Optional[StructConfig] = None
    ) -> Union[bytes, None]:
        """Pack UUID to bytes with proper endianness."""
        if value is None:
            return None

        if not field or not hasattr(field, 'struct_config'):
            return value.bytes  # Default to big endian

        # Use bytes_le for little endian, bytes for big endian
        return value.bytes_le if field.struct_config.byte_order == ByteOrder.LITTLE_ENDIAN else value.bytes

    @classmethod
    def unpack(cls, value: bytes, field: Optional[Field] = None) -> Union[UUID, None]:
        """Unpack bytes into UUID with proper endianness."""
        if value is None:
            return None

        if not field or not hasattr(field, 'struct_config'):
            return UUID(bytes=value)  # Default to big endian

        # Use bytes_le for little endian, bytes for big endian
        return UUID(bytes_le=value if field.struct_config.byte_order == ByteOrder.LITTLE_ENDIAN else UUID(bytes=value))
