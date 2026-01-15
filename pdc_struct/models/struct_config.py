"""Config class for pdc_struct"""

from sys import byteorder as system_byte_order
from typing import Dict, Any, Optional

from pdc_struct.enums import StructVersion, ByteOrder, StructMode


class StructConfig:
    """Configuration for struct packing/unpacking.

    Each model class gets its own independent configuration. Config values are set by
    creating a new StructConfig instance as a class variable.

    Example:
        >>> from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
        >>>
        >>> class NetworkPacket(StructModel):
        ...     sequence: int
        ...     payload: bytes
        ...
        ...     struct_config = StructConfig(
        ...         mode=StructMode.C_COMPATIBLE,
        ...         byte_order=ByteOrder.BIG_ENDIAN  # Network byte order
        ...     )

    Attributes:
        mode: The serialization mode (C_COMPATIBLE or DYNAMIC).
        version: Protocol version for DYNAMIC mode headers.
        byte_order: Byte ordering for multi-byte values.
        bit_width: Bit width for BitFieldModel (8, 16, or 32).
        propagate_byte_order: Whether to apply byte order to nested structs.
        metadata: Custom metadata dictionary for application use.
    """

    def __init__(
        self,
        mode: StructMode = StructMode.DYNAMIC,
        version: StructVersion = StructVersion.V1,
        byte_order: ByteOrder = (
            ByteOrder.LITTLE_ENDIAN
            if system_byte_order == "little"
            else ByteOrder.BIG_ENDIAN
        ),
        bit_width: Optional[int] = None,
        propagate_byte_order: bool = True,
        metadata: Dict[str, Any] = None,
    ):
        """Initialize a StructConfig with the specified options.

        Args:
            mode: Serialization mode. Use C_COMPATIBLE for fixed-size binary layouts
                compatible with C structs. Use DYNAMIC for variable-size formats with
                header metadata and optional field support. Defaults to DYNAMIC.
            version: Protocol version for DYNAMIC mode headers. Currently only V1 is
                supported. Defaults to V1.
            byte_order: Byte ordering (endianness) for multi-byte values like integers
                and floats. Defaults to the system's native byte order. For cross-platform
                compatibility, explicitly specify LITTLE_ENDIAN or BIG_ENDIAN.
            bit_width: Required for BitFieldModel classes. Specifies the packed integer
                size in bits. Must be 8, 16, or 32. Not used for StructModel classes.
            propagate_byte_order: If True, nested StructModel instances inherit the parent's
                byte order during serialization. Defaults to True.
            metadata: Optional dictionary for storing custom application-specific data.
                Not used by pdc_struct internally. Defaults to empty dict.

        Raises:
            ValueError: If bit_width is provided but not 8, 16, or 32.
        """
        self.mode = mode
        self.version = version
        self.byte_order = byte_order
        self.bit_width = bit_width
        self.metadata = metadata or {}
        self.propagate_byte_order = propagate_byte_order

        # Validate bit_width if provided
        if self.bit_width is not None and self.bit_width not in (8, 16, 32):
            raise ValueError("bit_width must be 8, 16, or 32")
