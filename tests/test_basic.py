""" tests/test_basic.py: Basic functionality tests """

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

def test_dynamic_roundtrip(dynamic_model):
    """Test basic round-trip serialization in DYNAMIC mode."""
    data = dynamic_model.to_bytes()
    recovered = type(dynamic_model).from_bytes(data)

    assert recovered.int_field == dynamic_model.int_field
    assert recovered.float_field == dynamic_model.float_field
    assert recovered.string_field == dynamic_model.string_field
    assert recovered.bool_field == dynamic_model.bool_field


def test_c_compatible_roundtrip(c_compatible_model):
    """Test basic round-trip serialization in C_COMPATIBLE mode."""
    data = c_compatible_model.to_bytes()
    recovered = type(c_compatible_model).from_bytes(data)

    assert recovered.int_field == c_compatible_model.int_field
    assert recovered.float_field == c_compatible_model.float_field
    assert recovered.string_field == c_compatible_model.string_field
    assert recovered.bool_field == c_compatible_model.bool_field


def test_string_field_length():
    """Test string field length validation during model creation."""
    with pytest.raises(ValueError,match="Field requires length specification"):
        class InvalidModel(StructModel):
            invalid_string: str = Field(description="String without max_length")
            struct_config = StructConfig(mode=StructMode.DYNAMIC)


def test_field_values(dynamic_model, c_compatible_model):
    """Test that field values are correctly set in both modes."""
    for model in [dynamic_model, c_compatible_model]:
        assert model.int_field == 42
        assert abs(model.float_field - 3.14159) < 1e-6
        assert model.string_field == "test data"
        assert model.bool_field is True


def test_dynamic_header_presence(dynamic_model):
    """Test that header is present and correct in DYNAMIC mode."""
    data = dynamic_model.to_bytes()

    # First byte should be version 1
    assert data[0] == 1
    # Second byte should be flags (little endian, no optional fields)
    assert data[1] == 0
    # Next two bytes are reserved
    assert data[2] == 0
    assert data[3] == 0


def test_c_compatible_no_header(c_compatible_model):
    """Test that no header is present in C_COMPATIBLE mode."""
    data = c_compatible_model.to_bytes()

    # Get expected struct size
    format_string = c_compatible_model.struct_format_string()
    expected_size = struct.calcsize(format_string)

    # Data should be exactly the struct size (no header)
    assert len(data) == expected_size


def test_invalid_string_length_dynamic():
    """Test string truncation in DYNAMIC mode."""
    class DynamicModel(StructModel):
        """Test model in DYNAMIC mode"""
        int_field: int = Field(description="Integer field")
        float_field: float = Field(description="Float field")
        string_field: str = Field(
            max_length=30,
            struct_length=10,
            description="String field"
        )
        bool_field: bool = Field(description="Boolean field")

        struct_config = StructConfig(
            mode=StructMode.DYNAMIC,
            version=StructVersion.V1,
            byte_order=ByteOrder.LITTLE_ENDIAN
        )

    model = DynamicModel(
        int_field=42,
        float_field=3.14,
        string_field="this string is way too long",
        bool_field=True
    )

    assert model.struct_format_string() == '<id10s?'
    data = model.to_bytes()
    recovered = type(model).from_bytes(data)

    assert len(recovered.string_field) == 10
    assert recovered.string_field == "this strin"


def test_invalid_string_length_c_compatible():
    """Test string truncation in C_COMPATIBLE mode."""

    class CCompatibleModel(StructModel):
        """Test model in C_COMPATIBLE mode"""
        int_field: int = Field(description="Integer field")
        float_field: float = Field(description="Float field")
        string_field: str = Field(
            max_length=30,
            struct_length=10,
            description="String field"
        )
        bool_field: bool = Field(description="Boolean field")

        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE,
            version=StructVersion.V1,
            byte_order=ByteOrder.LITTLE_ENDIAN
        )
    model = CCompatibleModel(
        int_field=42,
        float_field=3.14,
        string_field="this string is way too long",
        bool_field=True
    )

    data = model.to_bytes()
    recovered = type(model).from_bytes(data)

    # Should be null-terminated in C_COMPATIBLE mode
    assert recovered.string_field == "this strin"
