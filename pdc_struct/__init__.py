"""
pdc_struct: A library for structured data packing and unpacking.

This module provides utilities for defining and working with structured data
using Pydantic models and various helpers like enums and custom exceptions.
"""

from importlib.metadata import version, PackageNotFoundError

# Define the library version
DEFAULT_VERSION = "0.1.0"
try:
    __version__ = version("pdc_struct")
except PackageNotFoundError:
    __version__ = DEFAULT_VERSION

# Check for Pydantic and its version
try:
    PYDANTIC_VERSION = version("pydantic")
    if int(PYDANTIC_VERSION.split(".")[0]) < 2:
        raise ImportError(
            f"pdc_struct requires Pydantic >= 2.0.0, but found {PYDANTIC_VERSION}"
        )
except PackageNotFoundError:
    raise ImportError(
        "pdc_struct requires Pydantic >= 2.0.0, but Pydantic is not installed."
    )

# Internal imports
from .exc import StructPackError, StructUnpackError  # noqa: E402
from .enums import StructVersion, ByteOrder, HeaderFlags, StructMode  # noqa: E402
from .models import (  # noqa: E402
    StructConfig,
    StructModel,
    BitFieldModel,
    Bit,
)

__all__ = [
    "StructMode",
    "StructModel",
    "StructConfig",
    "StructVersion",
    "ByteOrder",
    "HeaderFlags",
    "StructPackError",
    "StructUnpackError",
    "Bit",
    "BitFieldModel",
]
