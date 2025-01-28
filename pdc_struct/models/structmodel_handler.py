"""StructModel type handler for nested PDC Struct serialization"""
# This must live outside the type_handler package to avoid a circular import

from typing import Optional, Union

from pydantic import Field

from pdc_struct import StructModel, StructMode
from .meta import TypeHandler


class StructModelHandler(TypeHandler):
    """Handler for Python bytes type."""

    @classmethod
    def handled_types(cls) -> list[type]:
        return [StructModel]

    @classmethod
    def needs_length(cls) -> bool:
        """Return True if this type requires a length specification.

        Override in handlers that need lengths (str, bytes)
        """
        return False

    @classmethod
    def get_struct_format(cls, field) -> str:
        # struct_length should never be None here because validate_field would have failed
        struct_length = cls._get_field_length_generic(field)
        return f'{struct_length}s'

    @classmethod
    def pack(
            cls,
            value: StructModel,
            field: Optional[Field] = None,
            struct_config: Optional['StructConfig'] = None
    ) -> bytes:
        """Pack another StructModel object as bytes"""
        if value is None:
            # Handle null case based on mode
            if struct_config and struct_config.mode == StructMode.C_COMPATIBLE:
                # In C mode, return zeroed bytes of correct length
                struct_length = cls._get_field_length_generic(field)
                return b'\0' * struct_length
            return None

        # If parent wants to propagate byte order, override the child's setting
        if struct_config and struct_config.propagate_byte_order:
            return value.to_bytes(override_endian=struct_config.byte_order)

        # Otherwise use the child's own byte order setting
        return value.to_bytes()

    @classmethod
    def unpack(
            cls,
            value: bytes,
            field: Optional[Field] = None,
            struct_config: Optional['StructConfig'] = None
    ) -> Union[StructModel, None]:
        """Unpack bytes into an instance of the right StructModel"""
        if value is None:
            return None

        # Get the model class from the field's annotation
        model_class = field.annotation
        if not issubclass(model_class, StructModel):
            raise ValueError(f"Field annotation must be a StructModel subclass, got {model_class}")

        # If parent wants to propagate byte order, override the child's setting
        if struct_config and struct_config.propagate_byte_order:
            return model_class.from_bytes(value, override_endian=struct_config.byte_order)

        # Otherwise use the child's own byte order setting
        return model_class.from_bytes(value)


