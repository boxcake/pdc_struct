""" tests/test_exc.py
Test exception handling
"""
from datetime import datetime

import pytest
from pydantic import Field
from pdc_struct import (
    StructModel,
    StructPackError,
    StructUnpackError, StructConfig, StructMode, ByteOrder, StructVersion,
)

def test_struct_unpack_error_missing_bytes():
    """ Unpacking data which does not match expected format
    should raise an exception.

    Float requires 8 bytes, int only provides 4
    """
    class DynamicModelInt(StructModel):
        """Test model in DYNAMIC mode"""
        int_field: int = Field(description="Integer field")

    class DynamicModelFloat(StructModel):
        """Test model in DYNAMIC mode"""
        float_field: float = Field(description="Float field")

    model_a = DynamicModelInt(
        int_field=5050,
    )

    packed_a = model_a.to_bytes()
    with pytest.raises(StructUnpackError):
        _ = DynamicModelFloat.from_bytes(packed_a)

def test_struct_unpack_error_extra_bytes():
    """ Unpacking data which does not match expected format
    should raise an exception.

    Float encodes 8 bytes, int only requires 4
    """
    class DynamicModelInt(StructModel):
        """Test model in DYNAMIC mode"""
        int_field: int = Field(description="Integer field")

    class DynamicModelFloat(StructModel):
        """Test model in DYNAMIC mode"""
        float_field: float = Field(description="Float field")

    model_f = DynamicModelFloat(
        float_field=1.234,
    )

    packed_f = model_f.to_bytes()
    with pytest.raises(StructUnpackError):
        _ = DynamicModelInt.from_bytes(packed_f)

def test_pack_unsupported_type():
    """ Packing an unsupported data type should raise an exception.

    datetime is currently not implemented
    """

    with pytest.raises(
            NotImplementedError,
            match="No handler registered for type"):

        class DynamicModelDateTime(StructModel):
            """Test model in DYNAMIC mode"""
            dt_field: datetime = Field(description="Integer field")

        dt_model = DynamicModelDateTime(
            dt_field=datetime(year=2020, month=12, day=31),
        )

        _ = dt_model.to_bytes()


def test_invalid_config_parameters():
    """Test validation of all StructConfig parameters."""

    # Test invalid mode
    with pytest.raises(ValueError, match="Invalid mode"):
        class InvalidModeModel(StructModel):
            field1: int = Field(description="Test field")
            struct_config = StructConfig(
                mode="invalid",
                version=StructVersion.V1,
                byte_order=ByteOrder.LITTLE_ENDIAN
            )

    # Test invalid version
    with pytest.raises(ValueError, match="Invalid version"):
        class InvalidVersionModel(StructModel):
            field1: int = Field(description="Test field")
            struct_config = StructConfig(
                mode=StructMode.DYNAMIC,
                version=2,  # Should be StructVersion enum
                byte_order=ByteOrder.LITTLE_ENDIAN
            )

    # Test invalid byte order
    with pytest.raises(ValueError, match="Invalid byte_order"):
        class InvalidByteOrderModel(StructModel):
            field1: int = Field(description="Test field")
            struct_config = StructConfig(
                mode=StructMode.DYNAMIC,
                version=StructVersion.V1,
                byte_order="little"  # Should be ByteOrder enum
            )
