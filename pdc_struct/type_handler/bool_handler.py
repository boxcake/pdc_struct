"""Boolean type handler for PDC Struct."""

from typing import TYPE_CHECKING, Optional

from pydantic import Field

from .meta import TypeHandler

if TYPE_CHECKING:
    from ..models.struct_config import StructConfig


class BoolHandler(TypeHandler):
    """Handler for Python bool type."""

    @classmethod
    def handled_types(cls) -> list[type]:
        return [bool]

    @classmethod
    def get_struct_format(cls, field) -> str:
        return "?"

    @classmethod
    def pack(
        cls,
        value: bool,
        field: Optional[Field] = None,
        struct_config: Optional["StructConfig"] = None,
    ) -> bool:
        return value

    @classmethod
    def unpack(
        cls,
        value: bool,
        field: Optional[Field] = None,
        struct_config: Optional["StructConfig"] = None,
    ) -> bool:
        return bool(value)  # Ensure bool type
