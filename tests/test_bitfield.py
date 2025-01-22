"""Test BitField implementation and integration with PDC Struct."""
from typing import Optional

import pytest
from pydantic import Field
from pdc_struct import (
    StructModel,
    StructConfig,
    StructMode,
    ByteOrder,
    BitFieldStruct,
    Bit
)


# Test Classes
class BasicFlags(BitFieldStruct):
    """Simple 8-bit flags."""
    read: bool = Bit(0)
    write: bool = Bit(1)
    exec: bool = Bit(2)

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN,
        bit_width=8
    )


class ComplexFlags(BitFieldStruct):
    """16-bit flags with multi-bit fields."""
    status: bool = Bit(0, 1, 2)  # 3-bit field
    debug: bool = Bit(3)
    reserved: bool = Bit(4, 5, 6, 7)  # 4-bit field
    active: bool = Bit(8)

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN,
        bit_width=16
    )


class Device(StructModel):
    """Model using bit fields."""
    flags: BasicFlags
    extended: ComplexFlags
    name: str = Field(max_length=10)

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN
    )


# BitFieldStruct Unit Tests

def test_basic_bit_operations():
    """Test basic bit field operations."""
    flags = BasicFlags()

    # Initially all bits should be False
    assert not flags.read
    assert not flags.write
    assert not flags.exec

    # Set individual bits
    flags.read = True
    assert flags.read
    assert not flags.write
    assert not flags.exec
    assert flags.raw_value == 0b00000001

    flags.write = True
    assert flags.read
    assert flags.write
    assert not flags.exec
    assert flags.raw_value == 0b00000011


def test_multi_bit_fields():
    """Test fields spanning multiple bits."""
    flags = ComplexFlags()

    # Test status field (3 bits)
    flags.status = True
    assert flags.raw_value == 0b00000111

    # Test reserved field (4 bits)
    flags.reserved = True
    assert flags.raw_value == 0b11110111

    # Test high bit
    flags.active = True
    assert flags.raw_value == 0b0000000111110111


def test_raw_value_access():
    """Test setting and getting raw values."""
    flags = BasicFlags()

    # Set via raw value
    flags.raw_value = 0b00000101  # read and exec
    assert flags.read
    assert not flags.write
    assert flags.exec

    # Check value limits
    with pytest.raises(ValueError):
        flags.raw_value = 256  # Too large for 8 bits


def test_bit_width_validation():
    """Test bit width validation."""
    # Invalid bit width
    with pytest.raises(ValueError):
        class InvalidWidth(BitFieldStruct):
            flag: bool = Bit(0)
            struct_config = StructConfig(
                mode=StructMode.C_COMPATIBLE,
                bit_width=12  # Not 8, 16, or 32
            )

    # Bit position exceeds width
    with pytest.raises(ValueError):
        class ExceedsBits(BitFieldStruct):
            flag: bool = Bit(8)  # Exceeds 8 bits
            struct_config = StructConfig(
                mode=StructMode.C_COMPATIBLE,
                bit_width=8
            )


def test_overlapping_bits():
    """Test detection of overlapping bit definitions."""
    with pytest.raises(ValueError):
        class OverlappingBits(BitFieldStruct):
            field1: bool = Bit(0, 1)  # Bits 0-1
            field2: bool = Bit(1, 2)  # Bits 1-2 overlap!
            struct_config = StructConfig(
                mode=StructMode.C_COMPATIBLE,
                bit_width=8
            )


def test_non_contiguous_bits():
    """Test validation of non-contiguous bit ranges."""
    with pytest.raises(ValueError):
        class NonContiguousBits(BitFieldStruct):
            field: bool = Bit(0, 2)  # Skips bit 1
            struct_config = StructConfig(
                mode=StructMode.C_COMPATIBLE,
                bit_width=8
            )


# Integration Tests with StructModel

def test_struct_integration():
    """Test integration with StructModel."""
    device = Device(
        flags=BasicFlags(read=True, write=True),
        extended=ComplexFlags(status=True, active=True),
        name="test"
    )

    # Pack to bytes
    data = device.to_bytes()

    # Unpack and verify
    recovered = Device.from_bytes(data)
    assert recovered.flags.read
    assert recovered.flags.write
    assert not recovered.flags.exec
    assert recovered.extended.status
    assert recovered.extended.active
    assert not recovered.extended.debug
    assert recovered.name == "test"


def test_struct_byte_order():
    """Test bit field handling with different byte orders."""

    class BigEndianDevice(StructModel):
        flags: BasicFlags
        name: str = Field(max_length=10)

        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE,
            byte_order=ByteOrder.BIG_ENDIAN
        )

    # Create and pack device
    device = BigEndianDevice(
        flags=BasicFlags(read=True, write=True),
        name="test"
    )
    data = device.to_bytes()

    # Unpack and verify
    recovered = BigEndianDevice.from_bytes(data)
    assert recovered.flags.read
    assert recovered.flags.write
    assert not recovered.flags.exec


def test_dynamic_mode():
    """Test bit fields in dynamic mode."""

    class DynamicDevice(StructModel):
        flags: Optional[BasicFlags] = None
        name: str = Field(max_length=10)

        struct_config = StructConfig(
            mode=StructMode.DYNAMIC,
            byte_order=ByteOrder.LITTLE_ENDIAN
        )

    # Test with flags
    device = DynamicDevice(
        flags=BasicFlags(read=True),
        name="test"
    )
    data = device.to_bytes()
    recovered = DynamicDevice.from_bytes(data)
    assert recovered.flags.read
    assert not recovered.flags.write

    # Test without flags
    device = DynamicDevice(name="test")
    data = device.to_bytes()
    recovered = DynamicDevice.from_bytes(data)
    assert recovered.flags is None
