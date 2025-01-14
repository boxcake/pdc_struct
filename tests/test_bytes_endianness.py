""" tests/test_bytes_endianness.py:  """

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
    """Test that bytes are properly handled for different endianness."""

    class BytesModel(StructModel):
        mac_address: bytes = Field(struct_length=6, description="MAC address")

        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE,
            byte_order=ByteOrder.LITTLE_ENDIAN
        )

    # Create a test MAC address (big endian format)
    mac_be = bytes.fromhex('001122334455')
    mac_le = bytes.fromhex('554433221100')  # Same value in little endian

    # Test little endian
    model_le = BytesModel(mac_address=mac_be)
    data_le = model_le.to_bytes()
    recovered_le = BytesModel.from_bytes(data_le)
    assert recovered_le.mac_address == mac_le

    # Test big endian
    class BytesModelBE(BytesModel):
        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE,
            byte_order=ByteOrder.BIG_ENDIAN
        )

    model_be = BytesModelBE(mac_address=mac_be)
    data_be = model_be.to_bytes()
    recovered_be = BytesModelBE.from_bytes(data_be)
    assert recovered_be.mac_address == mac_be