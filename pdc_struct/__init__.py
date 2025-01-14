# pdc_struct/__init__.py

try:
    from pydantic import VERSION as PYDANTIC_VERSION
except ImportError:
    raise ImportError("Could not determine pydantic version. Is pydantic installed?")

from .exc import StructPackError, StructUnpackError
from .enums import StructVersion, ByteOrder, HeaderFlags, StructMode
from .config import StructConfig
from .models import StructModel


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
]
