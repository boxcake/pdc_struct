"""StructModel type handler for nested PDC Struct serialization"""
# This must live outside the type_handler package to avoid a circular import

from typing import Optional, Union, get_args

from pydantic import Field

from .struct_model import StructModel, StructMode
from ..type_handler.meta import TypeHandler
from ..types import is_optional_type


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
        # Get the nested model class
        model_class = field.annotation
        if is_optional_type(field.annotation):
            model_class = get_args(field.annotation)[0]

        # Calculate the total size needed for the nested struct
        struct_length = model_class.struct_size()

        # Store it in the field's metadata for use during packing/unpacking
        if not field.json_schema_extra:
            field.json_schema_extra = {}
        field.json_schema_extra['struct_length'] = struct_length

        # Return format for a bytes field of the required size
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
            struct_config: Optional['StructConfig'] = None  # noqa
    ) -> Union[StructModel, None]:
        """Unpack bytes into an instance of the right StructModel"""
        if value is None:
            return None

        # Get the model class from the field's annotation, handling Optional types
        model_class = field.annotation
        if is_optional_type(model_class):
            model_class = get_args(model_class)[0]

        if not issubclass(model_class, StructModel):
            raise ValueError(f"Field annotation must be a StructModel subclass, got {model_class}")

        # Get parent's byte order if we should propagate it
        override_endian = None
        if struct_config and struct_config.propagate_byte_order:
            override_endian = struct_config.byte_order

        # Create instance from bytes
        return model_class.from_bytes(value, override_endian=override_endian)
