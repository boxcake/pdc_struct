# models.py
"""Core struct model implementation"""

from typing import Optional, ClassVar, Type, Dict, Any
from pydantic import BaseModel
import struct

from .type_handler import TypeHandler, TypeHandlerMeta
from .types import T, unwrap_optional_type, is_optional_type
from .config import StructConfig
from .exc import StructPackError, StructUnpackError
from .enums import ByteOrder, StructVersion, HeaderFlags, StructMode
from .utils import create_field_bitmap, parse_field_bitmap


class StructModel(BaseModel):
    """Base model for struct-compatible Pydantic models"""

    # Class variables
    struct_config: ClassVar[StructConfig] = StructConfig()
    _field_handlers: ClassVar[Dict[str, TypeHandler]] = {}

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        """Initialize a StructModel subclass."""
        super().__pydantic_init_subclass__(**kwargs)

        # Validate struct_config options
        if not isinstance(cls.struct_config.mode, StructMode):
            raise ValueError(f"Invalid mode: {cls.struct_config.mode}. Must be a StructMode enum value.")

        if not isinstance(cls.struct_config.version, StructVersion):
            raise ValueError(f"Invalid version: {cls.struct_config.version}. Must be a StructVersion enum value.")

        if not isinstance(cls.struct_config.byte_order, ByteOrder):
            raise ValueError(f"Invalid byte_order: {cls.struct_config.byte_order}. Must be a ByteOrder enum value.")

        # Cache handlers and validate fields
        cls._field_handlers = {}
        for field_name, field in cls.model_fields.items():  # noqa - model_fields property returns dict
            # For C_COMPATIBLE mode, validate Optional fields have defaults
            if (cls.struct_config.mode == StructMode.C_COMPATIBLE and
                    is_optional_type(field.annotation)):
                # Check for either default value or default_factory
                if field.default is None and field.default_factory is None:
                    python_type = unwrap_optional_type(field.annotation)
                    raise ValueError(
                        f"Field '{field_name}': Optional fields in C_COMPATIBLE mode must have "
                        f"either a default value or default_factory. Add either "
                        f"'= {python_type.__name__}()' or define a default value."
                    )

            # Get the actual type and its handler
            python_type = unwrap_optional_type(field.annotation)
            try:
                handler = TypeHandlerMeta.get_handler(python_type)
            except NotImplementedError as e:
                raise NotImplementedError(f"Field '{field_name}': {e}")

            # Cache the handler
            cls._field_handlers[field_name] = handler

            try:
                handler.validate_field(field)
            except ValueError as e:
                raise ValueError(f"Field '{field_name}': {e}")

    @classmethod
    def struct_format_string(cls) -> str:
        """Get the struct format string that would be used for packing/unpacking.

        Returns the struct format string that represents the complete model, including
        byte order and all fields.

        Returns:
            str: The struct format string (e.g. '<dds10s?' for little-endian double,
                double, 10-char string, bool).

        Example:
            >>> from pydantic import Field
            >>> from pdc_struct import StructModel, StructConfig, ByteOrder, StructVersion
            >>>
            >>> class Point(StructModel):
            ...     x: float = Field(description="X coordinate")
            ...     y: float = Field(description="Y coordinate")
            ...     label: str = Field(json_schema_extra={"max_length": 10}, description="Point label")
            ...     active: bool = Field(default=True, description="Whether point is active")
            ...
            ...     struct_config = StructConfig(
            ...         include_header=True,
            ...         version=StructVersion.V1,
            ...         byte_order=ByteOrder.LITTLE_ENDIAN
            ...     )
            >>>
            >>> Point.struct_format_string()
            '<dd10s?'
        """
        return cls.get_struct_format()

    @classmethod
    def struct_size(cls) -> int:
        """Return the size in bytes of the struct when packed.

        For C_COMPATIBLE mode this is the exact size.
        For DYNAMIC mode this is less relevant as optional data is not packed.
        """
        return struct.calcsize(cls.struct_format_string())

    @classmethod
    def get_struct_format(cls, present_fields: Optional[list] = None) -> str:
        """Generate struct format string from model fields."""
        format_parts = []
        fields_to_process = present_fields or cls.model_fields.keys()   # noqa - model_fields property returns dict

        for field_name in fields_to_process:
            field = cls.model_fields[field_name]    # noqa - model_fields property returns dict
            handler = cls._field_handlers[field_name]
            format_parts.append(handler.get_struct_format(field))

        return cls.struct_config.byte_order.value + ''.join(format_parts)

    def _pack_value(self, field_name: str, value: Any) -> Any:
        """Pack a single value using its handler."""
        if value is None:
            return None
        field = self.model_fields[field_name]
        return self._field_handlers[field_name].pack(
            value,
            field=field,
            struct_config=self.struct_config
        )

    @classmethod
    def _unpack_value(cls, field_name: str, value: Any) -> Any:
        """Unpack a single value using its handler."""
        if value is None:
            return None
        # Pass the field information to the handler
        field = cls.model_fields[field_name]
        return cls._field_handlers[field_name].unpack(value, field=field)

    def to_bytes(self) -> bytes:
        """Convert model instance to bytes using configured mode and version.

        Returns:
            bytes: The packed binary data according to the configured mode.

        Raises:
            ValueError: If mode or version is unsupported
            StructPackError: If packing fails
        """
        # Validate version - currently only V1 is supported
        if self.struct_config.version != StructVersion.V1:
            raise ValueError(f"Unsupported struct version: {self.struct_config.version}")

        # Route based on mode
        match self.struct_config.mode:
            case StructMode.C_COMPATIBLE:
                return self._to_bytes_v1_c_compatible()
            case StructMode.DYNAMIC:
                return self._to_bytes_v1_dynamic()
            case _:
                raise ValueError(f"Unsupported mode: {self.struct_config.mode}")

    def _to_bytes_v1_c_compatible(self) -> bytes:
        """Pack data in C-compatible mode (V1).

        In C_COMPATIBLE mode:
        - No header is included
        - Fixed struct format
        - No optional fields allowed

        Returns:
            bytes: The packed binary data.

        Raises:
            StructPackError: If packing fails
        """
        try:
            # Get format string (fixed in C_COMPATIBLE mode)
            format_string = self.get_struct_format()
            values = []

            # Pack each field using its handler
            for field_name, field in self.model_fields.items():
                value = getattr(self, field_name)
                values.append(self._pack_value(field_name, value))

            return struct.pack(format_string, *values)

        except struct.error as e:
            raise StructPackError(f"Failed to pack struct data: {e}")

    def _to_bytes_v1_dynamic(self) -> bytes:
        """Pack data in dynamic mode (V1).

        In DYNAMIC mode:
        - Header is always included (version, flags)
        - Optional fields use bitmap
        - Field presence is tracked in bitmap

        Returns:
            bytes: The packed binary data including header and optional bitmap.

        Raises:
            StructPackError: If packing fails
        """
        try:
            # Check for optional fields in the model
            has_optional = any(
                is_optional_type(field.annotation)
                for field in self.model_fields.values()
            )

            # Create bitmap and get present fields
            if has_optional:
                bitmap, present_fields = create_field_bitmap(self)
            else:
                bitmap = bytes([0])  # Empty bitmap
                present_fields = list(self.model_fields.keys())

            # Pack the data fields
            packed = b''
            if present_fields:
                # Get format string for present fields only
                format_string = self.get_struct_format(present_fields)
                values = []

                # Pack each present field using its handler
                for field_name in present_fields:
                    value = getattr(self, field_name)
                    values.append(self._pack_value(field_name, value))

                packed = struct.pack(format_string, *values)

            # Create header
            flags = HeaderFlags.LITTLE_ENDIAN
            if self.struct_config.byte_order == ByteOrder.BIG_ENDIAN:
                flags |= HeaderFlags.BIG_ENDIAN
            if has_optional:
                flags |= HeaderFlags.HAS_OPTIONAL_FIELDS

            header = bytes([
                self.struct_config.version.value,  # Version
                flags,  # Flags
                0,  # Reserved
                0  # Reserved
            ])

            return header + bitmap + packed

        except struct.error as e:
            raise StructPackError(f"Failed to pack struct data: {e}")

    @classmethod
    def from_bytes(cls: Type[T], data: bytes, ignore_header_endian: bool = False) -> T:
        """Create model instance from bytes using configured mode and version.

        Args:
            data: The packed binary data to unpack
            ignore_header_endian: Used only in DYNAMIC mode to override header endianness

        Returns:
            An instance of the model class

        Raises:
            ValueError: If mode or version is unsupported
            StructUnpackError: If unpacking fails
        """
        # Validate version - currently only V1 is supported

        if cls.struct_config.version == StructVersion.V1:
            # Route based on mode
            match cls.struct_config.mode:
                case StructMode.C_COMPATIBLE:
                    return cls._from_bytes_v1_c_compatible(data)
                case StructMode.DYNAMIC:
                    return cls._from_bytes_v1_dynamic(data, ignore_header_endian)
        # No defaults needed-We validate that the options are valid enum values in post init checks

    @classmethod
    def _from_bytes_v1_c_compatible(cls: Type[T], data: bytes) -> T:
        """Unpack data in C-compatible mode (V1).

        In C_COMPATIBLE mode:
        - No header to process
        - Fixed struct format
        - No optional fields

        Args:
            data: The packed binary data

        Returns:
            An instance of the model class

        Raises:
            StructUnpackError: If unpacking fails
        """
        try:
            # Get format string (fixed in C_COMPATIBLE mode)
            format_string = cls.get_struct_format()

            # Unpack raw values
            values = struct.unpack(format_string, data)

            # Build field dictionary using handlers
            field_dict = {}
            for (field_name, field), value in zip(cls.model_fields.items(), values):
                field_dict[field_name] = cls._unpack_value(field_name, value)

            return cls.model_validate(field_dict)

        except struct.error as e:
            raise StructUnpackError(f"Failed to unpack struct data: {e}")

    @classmethod
    def _from_bytes_v1_dynamic(cls: Type[T], data: bytes, ignore_header_endian: bool = False) -> T:
        """Unpack data in dynamic mode (V1).

        In DYNAMIC mode:
        - Header must be processed
        - Optional fields use bitmap
        - Field presence tracked in bitmap

        Args:
            data: The packed binary data
            ignore_header_endian: If True, uses model's configured byte order
                                instead of the one specified in the header

        Returns:
            An instance of the model class

        Raises:
            StructUnpackError: If unpacking fails
        """
        try:
            byte_order = cls.struct_config.byte_order

            # Handle header
            if len(data) < 4:
                raise StructUnpackError("Data too short to contain header")

            version_byte, flags = data[0], data[1]
            data = data[4:]  # Skip header

            # Verify version
            try:
                version = StructVersion(version_byte)
            except ValueError:
                raise StructUnpackError(f"Unsupported struct version: {version_byte}")

            if version != cls.struct_config.version:
                raise StructUnpackError(
                    f"Version mismatch: expected {cls.struct_config.version}, got {version}"
                )

            # Check endianness
            if not ignore_header_endian:
                byte_order = (ByteOrder.BIG_ENDIAN
                              if flags & HeaderFlags.BIG_ENDIAN
                              else ByteOrder.LITTLE_ENDIAN)

            # Handle optional fields
            if flags & HeaderFlags.HAS_OPTIONAL_FIELDS:
                data, present_fields = parse_field_bitmap(data, cls)
            else:
                # Skip empty bitmap byte
                data = data[1:]
                present_fields = list(cls.model_fields.keys())

            # If no fields present in completely optional model
            if not present_fields:
                field_dict = {name: None for name in cls.model_fields.keys()}
                return cls.model_validate(field_dict)

            # Create format string and unpack
            format_string = byte_order.value + cls.get_struct_format(present_fields)[1:]
            values = struct.unpack(format_string, data)

            # Build field dictionary using handlers
            field_dict = {}
            for name, value in zip(present_fields, values):
                field_dict[name] = cls._unpack_value(name, value)

            # Set None for missing optional fields
            for name, field in cls.model_fields.items():
                if name not in field_dict and is_optional_type(field.annotation):
                    field_dict[name] = None

            return cls.model_validate(field_dict)

        except struct.error as e:
            raise StructUnpackError(f"Failed to unpack struct data: {e}")
