"""Test enum support in PDC Struct."""
from enum import Enum, IntEnum
import pytest
from pydantic import Field
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from typing import Optional


# Test enum classes
class Color(Enum):
    """ Example enum """
    RED = 1
    GREEN = 2
    BLUE = 3


class DeviceType(IntEnum):
    """ Example enum """
    SENSOR = 1
    ACTUATOR = 2
    CONTROLLER = 3


# Test models
class BasicEnumModel(StructModel):
    """Model using regular Enum."""
    color: Color
    name: str = Field(max_length=10)

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN
    )


class IntEnumModel(StructModel):
    """Model using IntEnum."""
    device_type: DeviceType
    status: Optional[DeviceType] = DeviceType.SENSOR
    identifier: str = Field(max_length=10)

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN
    )


def test_basic_enum():
    """Test basic Enum packing and unpacking."""
    # Create instance
    model = BasicEnumModel(
        color=Color.RED,
        name="test"
    )

    # Pack to bytes
    data = model.to_bytes()

    # Unpack and verify
    recovered = BasicEnumModel.from_bytes(data)
    assert recovered.color == Color.RED
    assert recovered.name == "test"
    assert isinstance(recovered.color, Color)


def test_int_enum():
    """Test IntEnum packing and unpacking."""
    # Create instance
    model = IntEnumModel(
        device_type=DeviceType.ACTUATOR,
        identifier="device1"
    )

    # Pack to bytes
    data = model.to_bytes()

    # Unpack and verify
    recovered = IntEnumModel.from_bytes(data)
    assert recovered.device_type == DeviceType.ACTUATOR
    assert recovered.identifier == "device1"
    assert isinstance(recovered.device_type, DeviceType)
    assert recovered.status == DeviceType.SENSOR  # Default value


def test_enum_all_values():
    """Test all enum values can be packed and unpacked."""
    for color in Color:
        model = BasicEnumModel(
            color=color,
            name="test"
        )
        data = model.to_bytes()
        recovered = BasicEnumModel.from_bytes(data)
        assert recovered.color == color

    for device_type in DeviceType:
        model = IntEnumModel(
            device_type=device_type,
            identifier="test"
        )
        data = model.to_bytes()
        recovered = IntEnumModel.from_bytes(data)
        assert recovered.device_type == device_type


def test_invalid_enum_value():
    """Test handling of invalid enum values."""
    # Create invalid byte data (value 99 doesn't exist in enum)
    model = BasicEnumModel(
        color=Color.RED,
        name="test"
    )
    data = model.to_bytes()

    # Modify the first integer in the data to an invalid value
    import struct
    format_str = '<i10s'  # assuming this is the format string
    invalid_value = 99
    name = struct.unpack(format_str, data)[1]  # get the name
    invalid_data = struct.pack(format_str, invalid_value, name)

    # Attempt to unpack should raise ValueError
    with pytest.raises(ValueError, match="No enum member found for value: 99"):
        BasicEnumModel.from_bytes(invalid_data)


def test_dynamic_mode_enums():
    """Test enums in dynamic mode."""

    class DynamicEnumModel(StructModel):
        color: Optional[Color] = None
        device_type: Optional[DeviceType] = None

        struct_config = StructConfig(
            mode=StructMode.DYNAMIC,
            byte_order=ByteOrder.LITTLE_ENDIAN
        )

    # Test with some values set
    model = DynamicEnumModel(
        color=Color.BLUE,
        device_type=DeviceType.CONTROLLER
    )
    data = model.to_bytes()
    recovered = DynamicEnumModel.from_bytes(data)
    assert recovered.color == Color.BLUE
    assert recovered.device_type == DeviceType.CONTROLLER

    # Test with no values set
    model = DynamicEnumModel()
    data = model.to_bytes()
    recovered = DynamicEnumModel.from_bytes(data)
    assert recovered.color is None
    assert recovered.device_type is None
