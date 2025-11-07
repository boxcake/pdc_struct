"""Integer type handler for PDC Struct. Handles native Int, and pdc_struct C fixed int types."""

from typing import TYPE_CHECKING, Optional, Any

from pydantic import Field

from .meta import TypeHandler
from ..c_types import Int8, UInt8, Int16, UInt16

if TYPE_CHECKING:
    from ..models.struct_config import StructConfig


class IntHandler(TypeHandler):
    """Handler for all integer types including fixed-width integers."""

    @classmethod
    def handled_types(cls) -> list[type]:
        return [int, Int8, UInt8, Int16, UInt16]

    @classmethod
    def get_struct_format(cls, field) -> str:
        python_type = field.annotation

        # For fixed-width types, use their specific format
        if hasattr(python_type, "_struct_format"):
            return python_type._struct_format

        # For standard int, check for explicit format or use default
        if field.json_schema_extra and "struct_format" in field.json_schema_extra:
            return field.json_schema_extra["struct_format"]
        return "i"  # Default to 32-bit int

    @classmethod
    def is_valid_value(cls, value: Any) -> bool:
        """Check if a value is valid for this type handler."""
        return isinstance(value, int)

    @classmethod
    def pack(
        cls,
        value: int,
        field: Optional[Field] = None,
        struct_config: Optional["StructConfig"] = None,  # noqa
    ) -> int:
        """Pack integer value.

        For fixed-width types, validation is handled by the type's __new__ method.
        For standard int, the struct module will handle size validation.
        """
        return int(value)

    @classmethod
    def unpack(
        cls,
        value: int,
        field: Optional[Field] = None,
        struct_config: Optional["StructConfig"] = None,
    ) -> int:
        """Unpack integer value.

        struct.unpack already gives us an integer of the right size.
        For fixed-width types, we just need to wrap it in the correct type.
        """
        python_type = field.annotation
        if hasattr(python_type, "_struct_format"):
            return python_type(value)
        return value
