"""Float type handler for PDC Struct."""
from typing import Optional

from pydantic import Field

from .meta import TypeHandler


class FloatHandler(TypeHandler):
    """Handler for Python float type."""

    @classmethod
    def handled_types(cls) -> list[type]:
        return [float]

    @classmethod
    def get_struct_format(cls, field) -> str:
        # Check for explicit struct format
        if field.json_schema_extra and 'struct_format' in field.json_schema_extra:
            return field.json_schema_extra['struct_format']
        return 'd'  # Default to double precision

    @classmethod
    def pack(cls,
             value: float,
             field: Optional[Field]=None,
             struct_config: Optional['StructConfig'] = None
             ) -> float:
        return value

    @classmethod
    def unpack(cls, value: float, field: Optional[Field] = None) -> float:
        return value
