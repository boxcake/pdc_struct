# tests/test_types.py

import pytest
from pydantic import Field
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder, StructVersion
from pdc_struct.c_types import Int8, UInt8, Int16, UInt16


class AllTypesModel(StructModel):
    """Test model containing all supported types."""

    # Basic types
    int_val: int = Field(description="Regular integer")
    float_val: float = Field(description="Float value")
    bool_val: bool = Field(description="Boolean value")
    string_val: str = Field(max_length=10, description="String value")
    bytes_val: bytes = Field(struct_length=6, description="Bytes value")

    # Fixed width integers
    int8_val: Int8 = Field(description="8-bit signed integer")
    uint8_val: UInt8 = Field(description="8-bit unsigned integer")
    int16_val: Int16 = Field(description="16-bit signed integer")
    uint16_val: UInt16 = Field(description="16-bit unsigned integer")

    struct_config = StructConfig(
        mode=StructMode.DYNAMIC,
        version=StructVersion.V1,
        byte_order=ByteOrder.LITTLE_ENDIAN,
    )


# Test data covering full range of values
TEST_DATA = {
    # Basic types
    "int_val": 42,
    "float_val": 3.14159,
    "bool_val": True,
    "string_val": "test",
    "bytes_val": b"hello\x00",
    # Fixed width integers - test boundary values
    "int8_val": 127,  # Max Int8
    "uint8_val": 255,  # Max UInt8
    "int16_val": 32767,  # Max Int16
    "uint16_val": 65535,  # Max UInt16
}


@pytest.fixture
def all_types_instance():
    """Fixture providing an instance with all types."""
    return AllTypesModel(**TEST_DATA)


def test_type_roundtrip(all_types_instance):
    """Test roundtrip serialization of all types."""
    # Convert to bytes
    data = all_types_instance.to_bytes()
    print(f"Encoded bytes: {data.hex()}")

    # Convert back
    recovered = AllTypesModel.from_bytes(data)

    # Verify all fields
    assert recovered.int_val == TEST_DATA["int_val"]
    assert abs(recovered.float_val - TEST_DATA["float_val"]) < 1e-6
    assert recovered.bool_val == TEST_DATA["bool_val"]
    assert recovered.string_val == TEST_DATA["string_val"]
    assert recovered.bytes_val == TEST_DATA["bytes_val"]
    assert recovered.int8_val == TEST_DATA["int8_val"]
    assert recovered.uint8_val == TEST_DATA["uint8_val"]
    assert recovered.int16_val == TEST_DATA["int16_val"]
    assert recovered.uint16_val == TEST_DATA["uint16_val"]


def test_fixed_width_bounds():
    """Test bounds checking for fixed-width integers."""
    # Test Int8 bounds
    with pytest.raises(ValueError):
        AllTypesModel(**{**TEST_DATA, "int8_val": 128})  # Too high
    with pytest.raises(ValueError):
        AllTypesModel(**{**TEST_DATA, "int8_val": -129})  # Too low

    # Test UInt8 bounds
    with pytest.raises(ValueError):
        AllTypesModel(**{**TEST_DATA, "uint8_val": 256})  # Too high
    with pytest.raises(ValueError):
        AllTypesModel(**{**TEST_DATA, "uint8_val": -1})  # Too low

    # Test Int16 bounds
    with pytest.raises(ValueError):
        AllTypesModel(**{**TEST_DATA, "int16_val": 32768})  # Too high
    with pytest.raises(ValueError):
        AllTypesModel(**{**TEST_DATA, "int16_val": -32769})  # Too low

    # Test UInt16 bounds
    with pytest.raises(ValueError):
        AllTypesModel(**{**TEST_DATA, "uint16_val": 65536})  # Too high
    with pytest.raises(ValueError):
        AllTypesModel(**{**TEST_DATA, "uint16_val": -1})  # Too low


def test_minimum_values():
    """Test minimum values for fixed-width integers."""
    min_data = {
        **TEST_DATA,
        "int8_val": -128,  # Min Int8
        "uint8_val": 0,  # Min UInt8
        "int16_val": -32768,  # Min Int16
        "uint16_val": 0,  # Min UInt16
    }

    model = AllTypesModel(**min_data)
    data = model.to_bytes()
    recovered = AllTypesModel.from_bytes(data)

    assert recovered.int8_val == min_data["int8_val"]
    assert recovered.uint8_val == min_data["uint8_val"]
    assert recovered.int16_val == min_data["int16_val"]
    assert recovered.uint16_val == min_data["uint16_val"]


def test_struct_format():
    """Test struct format string generation with fixed-width types."""
    format_string = AllTypesModel.struct_format_string()
    print(f"Format string: {format_string}")

    # Check for presence of format specifiers
    assert "i" in format_string  # regular int
    assert "d" in format_string  # float
    assert "?" in format_string  # bool
    assert "10s" in format_string  # string
    assert "6s" in format_string  # bytes
    assert "b" in format_string  # int8
    assert "B" in format_string  # uint8
    assert "h" in format_string  # int16
    assert "H" in format_string  # uint16
