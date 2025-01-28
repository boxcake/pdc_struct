""" Handler for string packing/unpacking """
from typing import Optional
from pydantic import Field

from pdc_struct.enums import StructMode
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
    def pack(cls, value: str, field: Optional[Field] = None, struct_config: Optional['StructConfig'] = None) -> bytes:
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

        # Encode string and remove any embedded null bytes
        encoded = value.encode('utf-8')
        cleaned = encoded.split(b'\0', 1)[0]
        print(f"Packing string: '{value}' -> cleaned bytes: {[hex(b) for b in cleaned]}")

        # In DYNAMIC mode, just return the encoded string
        if not struct_config or struct_config.mode != StructMode.C_COMPATIBLE:
            return cleaned

        # In C_COMPATIBLE mode, handle fixed length and null termination
        length = cls._get_field_length_generic(field)
        print(f"C_COMPATIBLE mode, length={length}")

        if length is None:
            raise ValueError("C_COMPATIBLE mode requires max_length or struct_length")

        # Take maximum string length that will fit with null terminator
        max_str_length = length - 1  # Reserve one byte for null terminator
        print(f"Max string length: {max_str_length}")
        truncated = cleaned[:max_str_length]
        print(f"Taking bytes: {[hex(b) for b in truncated]} (length: {len(truncated)})")

        # Add null terminator
        result = truncated + b'\0'
        print(f"After null terminator: {[hex(b) for b in result]} (length: {len(result)})")

        # Add any remaining padding if needed
        if len(result) < length:
            result = result + b'\0' * (length - len(result))
        print(f"Final result: {[hex(b) for b in result]} (length: {len(result)})")

        return result

    @classmethod
    def unpack(cls, value: bytes, field: Optional[Field] = None, struct_config: Optional['StructConfig'] = None) -> str:

        # Check mode from struct_config
        is_c_compatible = struct_config and struct_config.mode == StructMode.C_COMPATIBLE

        if is_c_compatible:
            # Split at first null
            value = value.split(b'\0', 1)[0]
        else:
            # Strip all trailing nulls
            value = value.rstrip(b'\0')

        result = value.decode('utf-8')
        return result
