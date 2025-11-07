"""tests/test_bytes_endianness.py:"""

import pytest
import struct
from pydantic import Field
from pdc_struct import (
    StructModel,
    StructMode,
    StructConfig,
    StructVersion,
    ByteOrder,
)


def test_bytes_endianness():
    """Test that bytes are preserved regardless of struct endianness."""

    class BytesModel(StructModel):
        mac_address: bytes = Field(struct_length=6, description="MAC address")

        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE, byte_order=ByteOrder.LITTLE_ENDIAN
        )

    # Create a test MAC address
    mac = bytes.fromhex("001122334455")

    # Test little endian struct
    model_le = BytesModel(mac_address=mac)
    data_le = model_le.to_bytes()
    recovered_le = BytesModel.from_bytes(data_le)
    assert recovered_le.mac_address == mac  # Should preserve bytes exactly

    # Test big endian struct
    class BytesModelBE(BytesModel):
        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE, byte_order=ByteOrder.BIG_ENDIAN
        )

    model_be = BytesModelBE(mac_address=mac)
    data_be = model_be.to_bytes()
    recovered_be = BytesModelBE.from_bytes(data_be)
    assert recovered_be.mac_address == mac  # Should preserve bytes exactly
