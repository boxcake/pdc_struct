# pdc-struct/type_handler.py
"""
Core type system for PDC Struct.
Provides type handler registration and lookup functionality.
"""
from typing import Any, Dict, Type, Optional
from abc import ABC, ABCMeta, abstractmethod
from pydantic import Field


class TypeHandlerMeta(ABCMeta):
    """Metaclass for TypeHandler that builds the type registry.

    Inherits from ABCMeta to resolve metaclass conflict with ABC.
    """

    # Class variable to store the type-to-handler mapping
    _handler_registry: Dict[Type, Type['TypeHandler']] = {}

    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        # Create the handler class
        cls = super().__new__(mcs, name, bases, namespace)

        # Don't register the base class itself
        if name != 'TypeHandler':
            # Register all types this handler can handle
            if hasattr(cls, 'handled_types'):
                for python_type in cls.handled_types():
                    if python_type in mcs._handler_registry:
                        existing = mcs._handler_registry[python_type].__name__
                        raise TypeError(
                            f"Type {python_type} already has a registered handler: {existing}"
                        )
                    mcs._handler_registry[python_type] = cls

        return cls

    @classmethod
    def get_handler(mcs, python_type: Type) -> Type['TypeHandler']:
        """Get the handler for a specific type."""
        # Check for the exact type first
        handler = mcs._handler_registry.get(python_type)
        if handler is not None:
            return handler

        # Check for base classes (like for Enum types)
        for base_type, handler in mcs._handler_registry.items():
            if isinstance(python_type, type) and issubclass(python_type, base_type):
                return handler

        raise NotImplementedError(f"No handler registered for type: {python_type}")

    @classmethod
    def register_handler(mcs, handler_cls: Type['TypeHandler']) -> None:
        """Manually register a type handler."""
        if not hasattr(handler_cls, 'handled_types'):
            raise TypeError(f"Handler class {handler_cls.__name__} must implement handled_types()")

        for python_type in handler_cls.handled_types():
            if python_type in mcs._handler_registry:
                existing = mcs._handler_registry[python_type].__name__
                raise TypeError(
                    f"Type {python_type} already has a registered handler: {existing}"
                )
            mcs._handler_registry[python_type] = handler_cls


class TypeHandler(ABC, metaclass=TypeHandlerMeta):
    """Base class for all PDC struct type handlers.

    Type handlers are responsible for:
    1. Determining which Python types they can handle
    2. Providing struct format strings for their types
    3. Packing Python values for struct
    4. Unpacking struct values back to Python
    5. Validating and setting up fields at model creation
    """

    @classmethod
    @abstractmethod
    def handled_types(cls) -> list[Type]:
        """Return list of Python types this handler can handle."""
        raise NotImplementedError

    @classmethod
    def is_valid_value(cls, value: Any) -> bool:
        """Check if a value is valid for this type handler.

        Base implementation just checks if value is instance of any handled type.
        Override in handlers that accept additional compatible types.
        """
        print(f"Is valid Value?\n Is type {type(value)} in {cls.handled_types()}")
        return any(isinstance(value, t) for t in cls.handled_types())

    @classmethod
    @abstractmethod
    def get_struct_format(cls, field) -> str:
        """Return the struct format string for this type."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def pack(cls,
             value: Any,
             field: Optional[Field],
             struct_config: Optional['StructConfig'] = None # noqa - ignore StructConfig to avoid a circular import
             ) -> Any:
        """Pack a value for struct.pack."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def unpack(
            cls,
            value: Any, field: Optional[Field],
            struct_config: Optional['StructConfig'] = None
            ) -> Any:
        """Unpack a value from struct.unpack."""
        raise NotImplementedError

    @classmethod
    def needs_length(cls) -> bool:
        """Return True if this type requires a length specification.

        Override in handlers that need lengths (str, bytes)
        """
        return False

    @classmethod
    def validate_field(cls, field) -> None:
        """Validate and set up a field at model creation time.

        For fields that require a length (like str and bytes), validates
        that the length is specified and stores it in the field metadata.

        Args:
            field: The field to validate and setup

        Raises:
            ValueError: If required length is missing
        """
        if cls.needs_length():  # New class method
            struct_length = cls._get_field_length_generic(field)
            if struct_length is None:
                raise ValueError(f"Field requires length specification (max_length or struct_length)")

            # Store validated length
            if not field.json_schema_extra:
                field.json_schema_extra = {}
            field.json_schema_extra['struct_length'] = struct_length

    @staticmethod
    def _get_field_length_generic(field) -> Optional[int]:
        print(f"Getting field length. json_schema_extra: {field.json_schema_extra}")
        print(f"Field metadata: {field.metadata}")

        struct_length = None
        if field.json_schema_extra:
            struct_length = field.json_schema_extra.get('struct_length')
        print(f"Found struct_length: {struct_length}")

        if struct_length:
            return struct_length

        max_length = None
        if field.metadata:
            for constraint in field.metadata:
                if hasattr(constraint, 'max_length'):
                    max_length = constraint.max_length
                    break
        print(f"Found max_length: {max_length}")

        return max_length
