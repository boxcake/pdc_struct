# types.py
"""Type utilities for pdc_struct"""

from typing import TypeVar, Union
from .exc import StructPackError

# Define TypeVar for return type hints
T = TypeVar("T", bound="StructModel")


def is_optional_type(python_type) -> bool:
    """Check if a type annotation represents an Optional type.

    Determines whether a given type annotation is Optional[T] by checking if it's
    a Union with NoneType as one of its arguments.

    Args:
        python_type: The type annotation to check.

    Returns:
        bool: True if the type is Optional[T], False otherwise.
    """
    if hasattr(python_type, "__origin__") and python_type.__origin__ is Union:
        args = set(python_type.__args__)
        # Optional[T] is equivalent to Union[T, None] or Union[T, NoneType]
        return len(args) == 2 and type(None) in args
    return False


def unwrap_optional_type(python_type):
    """Get the inner type T from an Optional[T] type annotation.

    If the type is Optional[T], returns T. Otherwise, returns the type unchanged.

    Args:
        python_type: The type annotation to unwrap.

    Returns:
        The unwrapped type (T from Optional[T]) or the original type if not Optional.
    """
    if not is_optional_type(python_type):
        return python_type
    # Get the non-None type from the Union
    return next(arg for arg in python_type.__args__ if arg != type(None))


def validate_field_type(field_name: str, python_type) -> None:
    """Validate that a field's type is supported for struct packing.

    Checks if the type is supported for struct packing, specifically ensuring that
    Union types are only used for Optional fields.

    Args:
        field_name: Name of the field being validated.
        python_type: The type annotation to validate.

    Raises:
        StructPackError: If the type is an unsupported Union type.
    """
    if hasattr(python_type, "__origin__") and python_type.__origin__ is Union:
        if not is_optional_type(python_type):
            raise StructPackError(
                f"Union types are not supported for struct packing. "
                f"Field '{field_name}' has type {python_type}. "
                f"Only Optional[T] is supported."
            )
