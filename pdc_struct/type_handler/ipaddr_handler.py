"""IP address type handler for PDC Struct."""
from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Any, Optional
from pydantic import Field

from .meta import TypeHandler


class IPAddressHandler(TypeHandler):
    """Handler for IPv4 and IPv6 addresses."""

    @classmethod
    def handled_types(cls) -> list[type]:
        return [IPv4Address, IPv6Address]

    @classmethod
    def get_struct_format(cls, field) -> str:
        # Get the actual type (unwrapped from Optional if needed)
        ip_type = field.annotation
        if hasattr(field.annotation, "__origin__"):
            ip_type = field.annotation.__args__[0]

        # IPv4 = 4 bytes, IPv6 = 16 bytes
        return '4s' if ip_type == IPv4Address else '16s'

    @classmethod
    def validate_field(cls, field) -> None:
        """Validate IP address field configuration."""
        super().validate_field(field)

        # Get the actual type
        ip_type = field.annotation
        if hasattr(field.annotation, "__origin__"):
            ip_type = field.annotation.__args__[0]

        # Verify it's one of our supported types
        if ip_type not in (IPv4Address, IPv6Address):
            raise ValueError(
                f"IP address type must be IPv4Address or IPv6Address, got {ip_type}"
            )

    @classmethod
    def pack(cls,
             value: Any,
             field: Optional[Field] = None,
             struct_config: Optional['StructConfig'] = None
             ) -> bytes:
        """Pack IP address to bytes.

        Always uses network byte order (big endian) as per IP standard.
        """
        if value is None:
            return None
        return value.packed

    @classmethod
    def unpack(cls, value: bytes, field: Optional[Field] = None) -> Any:
        """Unpack bytes into IP address.

        Input bytes should be in network byte order (big endian).
        """
        if value is None:
            return None

        # Get the target type
        ip_type = field.annotation
        if hasattr(field.annotation, "__origin__"):
            ip_type = field.annotation.__args__[0]

        # Create appropriate address type
        return ip_type(value)
