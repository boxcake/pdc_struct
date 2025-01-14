"""Integer type handler for PDC Struct."""
from typing import Optional

from pydantic import Field

from pdc_struct import StructConfig
from .meta import TypeHandler


class IntHandler(TypeHandler):
    """Handler for Python int type."""

    @classmethod
    def handled_types(cls) -> list[type]:
        return [int]

    @classmethod
    def get_struct_format(cls, field) -> str:
        # Check for explicit struct format
        if field.json_schema_extra and 'struct_format' in field.json_schema_extra:
            return field.json_schema_extra['struct_format']
        return 'i'  # Default to 32-bit int

    @classmethod
    def pack(cls,
             value: int,
             field: Optional[Field]=None,
             struct_config: Optional[StructConfig] = None
             ) -> int:
        return value

    @classmethod
    def unpack(cls, value: int, field: Optional[Field] = None) -> int:
        return value
