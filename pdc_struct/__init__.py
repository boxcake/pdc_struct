# pdc_struct/__init__.py

try:
    from importlib.metadata import version, PackageNotFoundError
    try:
        __version__ = version("pdc_struct")
    except PackageNotFoundError:
        # package is not installed
        __version__ = "0.1.0"
except ImportError:
    # importlib.metadata not available (Python < 3.8)
    __version__ = "0.1.0"
    
try:
    from pydantic import VERSION as PYDANTIC_VERSION
except ImportError:
    raise ImportError("Could not determine pydantic version. Is pydantic installed?")

from .exc import StructPackError, StructUnpackError
from .enums import StructVersion, ByteOrder, HeaderFlags, StructMode
from .models import (
    StructConfig,
    StructModel,
    BitFieldModel,
    Bit,
)

class PydanticVersionError(Exception):
    """Raised when an incompatible version of pydantic is installed"""
    pass


def check_pydantic_version():
    """
    Check if the installed version of pydantic is compatible.
    Requires Pydantic v2.0.0 or higher.

    Raises:
        PydanticVersionError: If pydantic version is < 2.0.0
    """
    major_version = int(PYDANTIC_VERSION.split('.')[0])
    if major_version < 2:
        raise PydanticVersionError(
            f"pdc_struct requires pydantic >= 2.0.0, but found version {PYDANTIC_VERSION}"
        )


# Check pydantic version on import
check_pydantic_version()

__all__ = [
    'StructMode',
    'StructModel',
    'StructConfig',
    'StructVersion',
    'ByteOrder',
    'HeaderFlags',
    'StructPackError',
    'StructUnpackError',
    'PydanticVersionError',
    'Bit',
    'BitFieldModel',
]
