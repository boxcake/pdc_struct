"""Type handler for BitFieldStruct types."""
from typing import Optional, Union
from pydantic import Field

from .meta import TypeHandler
from ..models.bit_field import BitFieldModel


class BitFieldHandler(TypeHandler):
    """Handler for BitFieldStruct types."""

    @classmethod
    def handled_types(cls) -> list[type]:
        return [BitFieldModel]

    @classmethod
    def get_struct_format(cls, field) -> str:
        """Get struct format based on bit_width."""
        # Get the actual type
        field_type = field.annotation
        if hasattr(field.annotation, "__origin__"):
            field_type = field.annotation.__args__[0]

        # Get an instance of the type to access its config
        dummy_instance = field_type()

        # Map the bit width to struct format
        return {
            8: 'B',  # unsigned char
            16: 'H',  # unsigned short
            32: 'I'  # unsigned int
        }[dummy_instance.struct_config.bit_width]

    @classmethod
    def validate_field(cls, field) -> None:
        """Validate bit field configuration."""
        super().validate_field(field)

        # Get the actual type
        field_type = field.annotation
        if hasattr(field.annotation, "__origin__"):
            field_type = field.annotation.__args__[0]

        # Verify it's a BitFieldStruct
        if not issubclass(field_type, BitFieldModel):
            raise ValueError(f"Type must be a BitFieldStruct, got {field_type}")

        # Create instance to validate bit definitions
        try:
            _ = field_type()
        except Exception as e:
            raise ValueError(f"Failed to validate bit field structure: {e}")

    @classmethod
    def pack(cls,
             value: BitFieldModel,
             field: Optional[Field] = None,
             struct_config: Optional['StructConfig'] = None,  # noqa - Ignore StructConfig due to circular import
             ) -> Union[int, None]:
        """Pack BitFieldStruct to integer value."""
        if value is None:
            return None
        return value.packed_value

    @classmethod
    def unpack(cls,
               value: int,
               field: Optional[Field] = None,
               struct_config: Optional['StructConfig'] = None
               ) -> Union[BitFieldModel, None]:
        """Unpack integer value to BitFieldStruct."""
        if value is None:
            return None

        # Get the BitFieldStruct class
        field_type = field.annotation
        if hasattr(field.annotation, "__origin__"):
            field_type = field.annotation.__args__[0]

        # Create instance and set raw value
        instance = field_type()
        instance.packed_value = value
        return instance
