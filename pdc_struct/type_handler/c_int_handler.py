# pdc_struct/type_handler/fixed_int_handler.py
"""Type handler for fixed-width integer types."""
from typing import Optional

from pydantic import Field

from .meta import TypeHandler
from ..c_types import Int8, UInt8, Int16, UInt16


class FixedIntHandler(TypeHandler):
    """Handler for fixed-width integer types."""

    @classmethod
    def handled_types(cls) -> list[type]:
        return [Int8, UInt8, Int16, UInt16]

    @classmethod
    def get_struct_format(cls, field) -> str:
        """Get struct format character for the specific integer type."""
        python_type = field.annotation
        return python_type._struct_format

    @classmethod
    def pack(cls,
             value,
             field: Optional[Field]=None,
             struct_config: Optional['StructConfig'] = None     # noqa
             ) -> int:
        """Pack fixed-width integer.

        The value is already validated by the type's __new__ method.
        """
        return int(value)

    @classmethod
    def unpack(cls, value, field: Optional[Field] = None) -> int:
        """Unpack fixed-width integer."""
        # struct already gives us an integer of the right size,
        # we just need to wrap it in the correct type
        return value
