"""Enum type handler for PDC Struct."""

from enum import Enum, IntEnum, StrEnum
from typing import Optional, Union
from pydantic import Field

from .meta import TypeHandler


class EnumHandler(TypeHandler):
    """Handler for all Python enum types (Enum, IntEnum, StrEnum)."""

    @classmethod
    def handled_types(cls) -> list[type]:
        return [Enum, IntEnum, StrEnum]

    @classmethod
    def get_struct_format(cls, field) -> str:
        # By default, pack as 32-bit integer
        if field.json_schema_extra and "struct_format" in field.json_schema_extra:
            return field.json_schema_extra["struct_format"]
        return "i"

    @classmethod
    def validate_field(cls, field) -> None:
        """Validate enum field configuration."""
        super().validate_field(field)

        # Get the enum class
        enum_class = field.annotation
        if hasattr(field.annotation, "__origin__"):  # Handle Optional[EnumType]
            enum_class = field.annotation.__args__[0]

        # Cache the members list for StrEnum
        if issubclass(enum_class, StrEnum):
            if not field.json_schema_extra:
                field.json_schema_extra = {}
            field.json_schema_extra["enum_members"] = list(
                enum_class.__members__.values()
            )
        else:
            # For non-StrEnum types, verify values are integers or convertible to integers
            for member in enum_class:
                try:
                    int(member.value)
                except (TypeError, ValueError):
                    raise ValueError(
                        f"All enum values must be integers or convertible to integers. "
                        f"Value '{member.name}' has non-integer value '{member.value}'"
                    )

    @classmethod
    def pack(
        cls,
        value: Enum,
        field: Optional[Field] = None,
        struct_config: Optional["StructConfig"] = None,  # noqa
    ) -> Union[int, None]:
        """Pack enum value.

        For StrEnum: converts to index
        For other enums: uses integer value
        """
        if value is None:
            return None

        if isinstance(value, StrEnum):
            enum_class = value.__class__
            return list(enum_class.__members__.values()).index(value)
        return int(value.value)

    @classmethod
    def unpack(
        cls,
        value: int,
        field: Optional[Field] = None,
        struct_config: Optional["StructConfig"] = None,
    ) -> Union[Enum, None]:
        """Unpack integer into enum member.

        Args:
            value: The integer value to convert to enum
            field: The field information containing the enum class

        Returns:
            The enum member corresponding to the value

        Raises:
            ValueError: If the value doesn't match any enum member
        """

        if field is None:
            raise ValueError("Cannot unpack enum without field type information")

        # Get the enum class
        enum_class = field.annotation
        if hasattr(enum_class, "__origin__"):
            enum_class = enum_class.__args__[0]

        if issubclass(enum_class, StrEnum):
            # For StrEnum, use cached members list or build it
            members = (
                field.json_schema_extra and field.json_schema_extra.get("enum_members")
            ) or list(enum_class.__members__.values())
            try:
                return members[value]
            except IndexError:
                raise ValueError(f"Invalid enum index: {value}")
        else:
            # For other enums, find member by value
            for member in enum_class:
                if int(member.value) == value:
                    return member
            raise ValueError(f"No enum member found for value: {value}")
