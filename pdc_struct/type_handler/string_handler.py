""" Handler for string packing/unpacking """
from typing import Optional, Union
from pydantic import Field

from pdc_struct import StructMode, StructConfig
from .meta import TypeHandler


class StringHandler(TypeHandler):
    """Handler for Python str type."""

    @classmethod
    def handled_types(cls) -> list[type]:
        return [str]

    @classmethod
    def needs_length(cls) -> bool:
        return True

    @classmethod
    def get_struct_format(cls, field) -> str:
        struct_length = cls._get_field_length_generic(field)
        return f'{struct_length}s'

    @classmethod
    def pack(cls,
             value: str,
             field: Optional[Field] = None,
             struct_config: Optional[StructConfig] = None
             ) -> bytes:
        """Pack string to bytes.

        Args:
            value: The string to pack
            field: Field information including length constraints
            struct_config: The model's struct configuration for mode detection

        DYNAMIC mode:
            - Variable length, no padding needed
            - No null termination needed

        C_COMPATIBLE mode:
            - Fixed length buffer
            - Null terminated
            - Padded to full length
        """
        if not isinstance(value, str):
            return value

        encoded = value.encode('utf-8')

        # In DYNAMIC mode, just return the encoded string
        if not struct_config or struct_config.mode != StructMode.C_COMPATIBLE:
            return encoded

        # In C_COMPATIBLE mode, handle fixed length and null termination
        length = cls._get_field_length_generic(field)
        if length is None:
            raise ValueError("C_COMPATIBLE mode requires max_length or struct_length")

        # Ensure null termination and padding
        return encoded[:length - 1] + b'\0' + b'\0' * (length - len(encoded) - 1)

    @classmethod
    def unpack(cls, value: bytes, field: Optional[Field] = None) -> str:
        """Unpack bytes to string.

        In C_COMPATIBLE mode:
        - Stop at first null byte

        In DYNAMIC mode:
        - Strip all trailing nulls
        """
        if value is None:
            return None

        # Get mode from field metadata
        is_c_compatible = (field and hasattr(field, 'struct_config') and
                           field.struct_config.mode == StructMode.C_COMPATIBLE)

        if is_c_compatible:
            # Split at first null
            value = value.split(b'\0', 1)[0]
        else:
            # Strip all trailing nulls
            value = value.rstrip(b'\0')

        return value.decode('utf-8')
