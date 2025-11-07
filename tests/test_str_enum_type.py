"""Test string enum support in PDC Struct."""

from enum import StrEnum
import pytest
from pydantic import Field
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from typing import Optional


class Color(StrEnum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class Status(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class ColorModel(StructModel):
    """Model using StrEnum."""

    color: Color
    status: Optional[Status] = Status.ACTIVE
    name: str = Field(max_length=10)

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE, byte_order=ByteOrder.LITTLE_ENDIAN
    )


def test_str_enum_basic():
    """Test basic StrEnum packing and unpacking."""
    model = ColorModel(color=Color.RED, name="test")

    data = model.to_bytes()
    recovered = ColorModel.from_bytes(data)

    assert recovered.color == Color.RED
    assert recovered.color.value == "red"
    assert recovered.status == Status.ACTIVE
    assert recovered.name == "test"
    assert isinstance(recovered.color, Color)


def test_str_enum_all_values():
    """Test all string enum values can be packed and unpacked."""
    for color in Color:
        model = ColorModel(color=color, name="test")
        data = model.to_bytes()
        recovered = ColorModel.from_bytes(data)
        assert recovered.color == color
        assert recovered.color.value == color.value


def test_str_enum_dynamic_mode():
    """Test string enums in dynamic mode."""

    class DynamicModel(StructModel):
        color: Optional[Color] = None
        status: Optional[Status] = None

        struct_config = StructConfig(
            mode=StructMode.DYNAMIC, byte_order=ByteOrder.LITTLE_ENDIAN
        )

    # Test with values
    model = DynamicModel(color=Color.BLUE, status=Status.MAINTENANCE)
    data = model.to_bytes()
    recovered = DynamicModel.from_bytes(data)
    assert recovered.color == Color.BLUE
    assert recovered.color.value == "blue"
    assert recovered.status == Status.MAINTENANCE
    assert recovered.status.value == "maintenance"

    # Test without values
    model = DynamicModel()
    data = model.to_bytes()
    recovered = DynamicModel.from_bytes(data)
    assert recovered.color is None
    assert recovered.status is None


def test_invalid_str_enum_value():
    """Test handling of invalid string enum indices."""
    model = ColorModel(color=Color.RED, name="test")
    data = model.to_bytes()

    # Modify the first integer to an invalid index
    import struct

    format_str = "<ii10s"  # assuming this is the format string
    invalid_index = 99
    _, status, name = struct.unpack(format_str, data)
    invalid_data = struct.pack(format_str, invalid_index, status, name)

    with pytest.raises(ValueError, match="Invalid enum index: 99"):
        ColorModel.from_bytes(invalid_data)
