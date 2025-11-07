"""tests/test_optional.py: Test fuctionality involving optional fields"""

from typing import Optional

import pytest
from pydantic import Field
from pdc_struct import (
    StructModel,
    StructPackError,
    StructUnpackError,
    StructVersion,
    HeaderFlags,
    StructConfig,
    ByteOrder,
    StructMode,
)
from tests.conftest import OptionalFieldsModel


def test_optional_fields_present(optional_fields_model):
    """Test serialization with all optional fields present."""
    # Convert to bytes
    data = optional_fields_model.to_bytes()

    # Convert back
    recovered = type(optional_fields_model).from_bytes(data)

    # Check required fields
    assert recovered.required_int == optional_fields_model.required_int
    assert recovered.required_string == optional_fields_model.required_string

    # Check optional fields that were set
    assert recovered.optional_float == optional_fields_model.optional_float
    assert recovered.optional_string == optional_fields_model.optional_string
    # optional_bool was not set, should be None
    assert recovered.optional_bool is None


def test_only_required_fields():
    """Test serialization with only required fields set."""
    model = OptionalFieldsModel(required_int=42, required_string="required")

    # Convert to bytes
    data = model.to_bytes()

    # Convert back
    recovered = OptionalFieldsModel.from_bytes(data)

    # Check required fields
    assert recovered.required_int == 42
    assert recovered.required_string == "required"

    # Check optional fields are None
    assert recovered.optional_float is None
    assert recovered.optional_string is None
    assert recovered.optional_bool is None


def test_bitmap_header_flag():
    """Test that optional fields presence is correctly flagged in header."""
    model = OptionalFieldsModel(
        required_int=42,
        required_string="required",
        optional_float=3.14,  # Set just one optional field
    )

    data = model.to_bytes()

    # Check header flags (bit 1 should be set for optional fields)
    assert data[1] & 0x02 != 0


def test_partial_optional_fields():
    """Test different combinations of optional fields present/missing."""
    # Test various combinations
    combinations = [
        {"optional_float": 1.23},
        {"optional_string": "test"},
        {"optional_bool": True},
        {"optional_float": 1.23, "optional_string": "test"},
        {"optional_float": 1.23, "optional_bool": True},
        {"optional_string": "test", "optional_bool": True},
        {"optional_float": 1.23, "optional_string": "test", "optional_bool": True},
    ]

    for optional_fields in combinations:
        # Create model with this combination
        model = OptionalFieldsModel(
            required_int=42, required_string="required", **optional_fields
        )

        # Round trip
        data = model.to_bytes()
        recovered = OptionalFieldsModel.from_bytes(data)

        # Check required fields
        assert recovered.required_int == 42
        assert recovered.required_string == "required"

        # Check optional fields
        for field, value in optional_fields.items():
            assert getattr(recovered, field) == value

        # Check unset fields are None
        for field in ["optional_float", "optional_string", "optional_bool"]:
            if field not in optional_fields:
                assert getattr(recovered, field) is None


def test_bitmap_structure():
    """Test the structure of the bitmap for optional fields."""
    model = OptionalFieldsModel(
        required_int=42,
        required_string="required",
        optional_float=1.23,
        optional_bool=True,
        # optional_string left unset
    )

    data = model.to_bytes()

    # After header (4 bytes), first byte is bitmap length
    bitmap_length = data[4]
    # Then comes the bitmap
    bitmap = data[5 : 5 + bitmap_length]

    # Check bitmap content - first and third optional fields are set
    # Should have bits 0 and 2 set in first byte: 0b00000101
    assert bitmap[0] == 0b00000101


def test_all_optional_model():
    """Test model with only optional fields."""

    class AllOptionalModel(StructModel):
        field1: Optional[int] = Field(None)
        field2: Optional[float] = Field(None)
        field3: Optional[str] = Field(None, max_length=10)

        struct_config = StructConfig(
            mode=StructMode.DYNAMIC,
            version=StructVersion.V1,
            byte_order=ByteOrder.LITTLE_ENDIAN,
        )

    # Test with no fields set
    empty = AllOptionalModel()
    empty_data = empty.to_bytes()

    print(f"## full data: {empty_data.hex()}")  # Debug

    # Check header structure - should be 6 bytes minimum
    # 4 bytes header + 1 byte bitmap length + 1 byte bitmap
    assert len(empty_data) >= 6, f"Data too short: {len(empty_data)} bytes"
    assert empty_data[0] == StructVersion.V1.value, f"Wrong version: {empty_data[0]}"
    assert (
        empty_data[1] & HeaderFlags.HAS_OPTIONAL_FIELDS != 0
    ), f"Optional fields flag not set: {bin(empty_data[1])}"
    assert empty_data[2] == 0, f"Reserved byte 1 not zero: {empty_data[2]}"
    assert empty_data[3] == 0, f"Reserved byte 2 not zero: {empty_data[3]}"
    assert (
        empty_data[4] == 1
    ), f"Wrong bitmap length: {empty_data[4]}"  # 1 byte needed for bitmap
    assert (
        empty_data[5] == 0
    ), f"Bitmap not empty: {bin(empty_data[5])}"  # All bits should be 0

    empty_recovered = AllOptionalModel.from_bytes(empty_data)
    assert all(
        getattr(empty_recovered, f) is None for f in ["field1", "field2", "field3"]
    )

    empty_recovered = AllOptionalModel.from_bytes(empty_data)
    assert all(
        getattr(empty_recovered, f) is None for f in ["field1", "field2", "field3"]
    )

    # Test with all fields set
    full = AllOptionalModel(field1=1, field2=2.0, field3="three")
    full_data = full.to_bytes()

    # Header + non-empty bitmap + actual data
    assert len(full_data) > len(empty_data)

    full_recovered = AllOptionalModel.from_bytes(full_data)
    assert full_recovered.field1 == 1
    assert full_recovered.field2 == 2.0
    assert full_recovered.field3 == "three"
    assert all(
        getattr(empty_recovered, f) is None for f in ["field1", "field2", "field3"]
    )

    # Test with all fields set
    full = AllOptionalModel(field1=1, field2=2.0, field3="three")
    full_data = full.to_bytes()
    full_recovered = AllOptionalModel.from_bytes(full_data)
    assert full_recovered.field1 == 1
    assert full_recovered.field2 == 2.0
    assert full_recovered.field3 == "three"


def test_all_optional_none_set(optional_fields_model_all_unset):
    """A model with all optional fields set to None"""
    m = optional_fields_model_all_unset.to_bytes()
    n = type(optional_fields_model_all_unset).from_bytes(m)


def test_optional_fields_c_mode():
    with pytest.raises(
        ValueError,
        match="Optional fields in C_COMPATIBLE mode must have either a default value or default_factory",
    ):

        class OptionalFieldsModelNoDefault(StructModel):
            field1: Optional[int] = Field(
                None, description="Optional field - no default"
            )
            struct_config = StructConfig(
                mode=StructMode.C_COMPATIBLE,
            )

    class OptionalFieldsModelDefault(StructModel):
        field1: Optional[int] = Field(
            default=100, description="Optional field - with default"
        )
        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE,
        )

    o = OptionalFieldsModelDefault()
    assert o.field1 == 100

    class OptionalFieldsModelFactory(StructModel):
        field1: Optional[int] = Field(
            default_factory=lambda: int(99), description="Optional field - with factory"
        )
        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE,
        )

    o = OptionalFieldsModelFactory()
    assert o.field1 == 99
