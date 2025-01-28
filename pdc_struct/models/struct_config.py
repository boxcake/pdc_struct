"""Config class for pdc_struct"""

from sys import byteorder as system_byte_order
from dataclasses import dataclass
from typing import Dict, Any, Optional

from pdc_struct.enums import (
    BitOrder,
    StructVersion,
    ByteOrder,
    StructMode
)


class StructConfig:
    """Configuration for struct packing/unpacking.

    Each model class gets its own independent configuration. Config values are set by
    creating a new StructConfig in a class:

    class MyModel(BitFieldModel):
        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE,
            bit_width=8
        )
    """
    def __init__(
        self,
        mode: StructMode = StructMode.DYNAMIC,
        version: StructVersion = StructVersion.V1,
        byte_order: ByteOrder = ByteOrder.LITTLE_ENDIAN if system_byte_order == "little" else ByteOrder.BIG_ENDIAN,
        bit_width: Optional[int] = None,
        propagate_byte_order: bool = True,
        metadata: Dict[str, Any] = None
    ):
        self.mode = mode
        self.version = version
        self.byte_order = byte_order
        self.bit_width = bit_width
        self.metadata = metadata or {}
        self.propagate_byte_order = propagate_byte_order

        # Validate bit_width if provided
        if self.bit_width is not None and self.bit_width not in (8, 16, 32):
            raise ValueError("bit_width must be 8, 16, or 32")
