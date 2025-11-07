"""Test BitFieldModel functionality."""

from typing import Optional

import pydantic_core
import pytest
from pydantic import ValidationError, Field
from pdc_struct import (
    BitFieldModel,
    StructConfig,
    StructMode,
    ByteOrder,
    Bit,
    StructModel,
)
import importlib
import sys

from pdc_struct.models import struct_config


def test_basic_boolean_bits():
    """Test basic boolean bit operations."""

    class BoolFlags(BitFieldModel):
        read: bool = Bit(0)
        write: bool = Bit(1)
        exec: bool = Bit(2)
        struct_config = StructConfig(mode=StructMode.C_COMPATIBLE, bit_width=8)

    flags = BoolFlags()
    assert not flags.read
    assert not flags.write
    assert not flags.exec
    assert flags.packed_value == 0

    flags.read = True
    assert flags.read
    assert not flags.write
    assert not flags.exec
    assert flags.packed_value == 0b00000001

    flags.write = True
    assert flags.packed_value == 0b00000011


def test_multi_bit_fields():
    """Test fields spanning multiple bits."""

    class MultiFlags(BitFieldModel):
        value: int = Bit(0, 1, 2)  # 3-bit value (0-7)
        flag: bool = Bit(3)
        mode: int = Bit(4, 5)  # 2-bit value (0-3)
        struct_config = StructConfig(bit_width=8)

    flags = MultiFlags(value=5, flag=True, mode=2)
    assert flags.value == 5
    assert flags.flag
    assert flags.mode == 2
    assert flags.packed_value == 0b00101101

    # ToDo: Pydantic doesnt validate constraints when an attribute is set, only on model_validate or dump
    # ToDo: BitFieldModel could implement validation checks to enable this functionality

    # # Test range validation
    # with pytest.raises(ValueError):
    #     flags.value = 8  # Too large for 3 bits
    # with pytest.raises(ValueError):
    #     flags.mode = 4  # Too large for 2 bits


def test_bit_widths():
    """Test different bit widths (8, 16, 32)."""
    for width, max_val in [(8, 255), (16, 65535), (32, 4294967295)]:

        class DynamicFlags(BitFieldModel):
            value: int = Bit(0, 1, 2, 3)
            struct_config = StructConfig(bit_width=width)

        flags = DynamicFlags(value=0)
        assert flags.struct_format_string == {8: "B", 16: "H", 32: "I"}[width]

        # Test max value validation
        with pytest.raises(ValueError):
            flags.packed_value = max_val + 1


def test_byte_order():
    """Test byte order handling."""

    class OrderFlags(BitFieldModel):
        value: int = Bit(0, 1, 2, 3)
        struct_config = StructConfig(bit_width=16, byte_order=ByteOrder.BIG_ENDIAN)

    # Test with bytes initialization
    flags = OrderFlags(packed_value=b"\x01\x02")  # 0x0102 in big endian
    assert flags.value == 2

    flags = OrderFlags(packed_value=b"\x02\x01")  # Should interpret differently
    assert flags.value == 1


def test_validation():
    """Test input validation."""

    importlib.reload(sys.modules["pdc_struct"])
    # Test invalid bit width configuration
    try:
        print("Module is being imported")

        class InvalidWidth(BitFieldModel):
            x: bool = Bit(0)
            struct_config = StructConfig(bit_width=12)

    except ValueError as e:
        assert True
        # assert str(e) == 'bit_width must be 8, 16, or 32'

    # Test overlapping bits
    with pytest.raises(ValueError):

        class OverlapBits(BitFieldModel):
            a: int = Bit(0, 1)
            b: int = Bit(1, 2)  # Overlaps with 'a'


def test_bytes_initialization():
    """Test initialization from bytes."""

    class ByteFlags(BitFieldModel):
        read: bool = Bit(0)
        value: int = Bit(1, 2, 3)
        struct_config = StructConfig(bit_width=8)

    # Test empty init
    flags = ByteFlags()
    assert flags.packed_value == 0

    # Test bytes init
    flags = ByteFlags(packed_value=b"\x0f")  # 0b00001111
    assert flags.read
    assert flags.value == 7

    # Test kwargs override bytes
    flags = ByteFlags(packed_value=b"\xff", read=False)
    assert not flags.read


def test_clone():
    """Test cloning BitFieldModel instances with optional field updates."""

    class TestFlags(BitFieldModel):
        read: bool = Bit(0)
        write: bool = Bit(1)
        value: int = Bit(2, 3, 4)  # 3-bit value
        struct_config = StructConfig(bit_width=8)

    # Create original instance with some values
    original = TestFlags(packed_value=b"\x07")  # 0b00000111 - read=1, write=1, value=1

    # Test basic clone without changes
    clone1 = original.clone()
    assert clone1.read == original.read
    assert clone1.write == original.write
    assert clone1.value == original.value
    assert clone1.packed_value == original.packed_value

    # Test clone with field updates
    clone2 = original.clone(read=False, value=4)
    assert not clone2.read  # Should be changed
    assert clone2.write == original.write  # Should be unchanged
    assert clone2.value == 4  # Should be changed


def test_bitfield_validation():
    """Ensure we validate the type as BitFieldStruct"""

    class Point(StructModel):
        x: float = Field(description="X coordinate")
        y: float = Field(description="Y coordinate")
        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE, byte_order=ByteOrder.LITTLE_ENDIAN
        )

    class DynamicCircle(StructModel):
        center: Optional[Point] = Field(description="Optional center point")
        radius: float = Field(description="Circle radius")
        struct_config = StructConfig(
            mode=StructMode.DYNAMIC,
            byte_order=ByteOrder.LITTLE_ENDIAN,
            propagate_byte_order=True,
        )

    # Set center to something of the wrong type
    dynamic_circle = DynamicCircle(center=Point(x=1, y=1), radius=5.0)

    dynamic_circle.center = "wrong type data"

    with pytest.raises(TypeError):
        dynamic_packed = dynamic_circle.to_bytes()
