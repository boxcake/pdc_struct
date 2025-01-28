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


def test_string_handling_c_compatible():
    """Test string handling in C_COMPATIBLE mode, including:
    - ASCII strings (1 byte per char)
    - Unicode strings (multi-byte chars)
    - String length vs struct length handling
    - Mixed initialization methods
    """
    class StringModel(StructModel):
        ascii_field: str = Field(
            default=None,          # Allow None initially
            max_length=10,         # Max 10 characters
            struct_length=11,      # 10 bytes + null terminator (sufficient for ASCII)
            description="Field for ASCII strings"
        )
        unicode_field: str = Field(
            default=None,          # Allow None initially
            max_length=5,          # Max 5 characters
            struct_length=21,      # Space for 5 4-byte chars + null terminator
            description="Field for Unicode strings"
        )
        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE,
            version=StructVersion.V1,
            byte_order=ByteOrder.LITTLE_ENDIAN
        )

    # Test ASCII strings
    model = StringModel(
        ascii_field="Hello Test",  # 9 ASCII chars
        unicode_field="Hello"      # 5 ASCII chars
    )
    packed = model.to_bytes()
    recovered = StringModel.from_bytes(packed)
    assert recovered.ascii_field == "Hello Test"
    assert recovered.unicode_field == "Hello"

    # Test Unicode strings with multi-byte characters
    model = StringModel(
        ascii_field="ASCII",
        unicode_field="日本語"    # 3 Japanese characters, each 3 bytes in UTF-8
    )
    packed = model.to_bytes()
    recovered = StringModel.from_bytes(packed)
    assert recovered.ascii_field == "ASCII"
    assert recovered.unicode_field == "日本語"

    # Test mixed ASCII and Unicode
    model = StringModel(
        ascii_field="Hi!",
        unicode_field="Hi 🌍"     # ASCII + emoji (emoji is 4 bytes)
    )
    packed = model.to_bytes()
    recovered = StringModel.from_bytes(packed)
    assert recovered.ascii_field == "Hi!"
    assert recovered.unicode_field == "Hi 🌍"

    # Test initialization from packed value
    packed = model.to_bytes()
    from_packed = StringModel(packed_value=packed)
    assert from_packed.ascii_field == "Hi!"
    assert from_packed.unicode_field == "Hi 🌍"

    # Test cloning
    cloned = model.clone(ascii_field="New")
    assert cloned.ascii_field == "New"
    assert cloned.unicode_field == "Hi 🌍"
