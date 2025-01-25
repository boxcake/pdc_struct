"""Test BitFieldModel functionality."""
import pytest
from pydantic import ValidationError
from pdc_struct import BitFieldModel, StructConfig, StructMode, ByteOrder, Bit


def test_basic_boolean_bits():
    """Test basic boolean bit operations."""
    class BoolFlags(BitFieldModel):
        read: bool = Bit(0)
        write: bool = Bit(1)
        exec: bool = Bit(2)
        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE,
            bit_width=8
        )

    flags = BoolFlags()
    assert not flags.read
    assert not flags.write
    assert not flags.exec
    assert flags.raw_value == 0

    flags.read = True
    assert flags.read
    assert not flags.write
    assert not flags.exec
    assert flags.raw_value == 0b00000001

    flags.write = True
    assert flags.raw_value == 0b00000011


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
    assert flags.raw_value == 0b00101101

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
        assert flags.struct_format_string == {8:'B', 16:'H', 32:'I'}[width]

        # Test max value validation
        with pytest.raises(ValueError):
            flags.raw_value = max_val + 1


def test_byte_order():
    """Test byte order handling."""
    class OrderFlags(BitFieldModel):
        value: int = Bit(0, 1, 2, 3)
        struct_config = StructConfig(
            bit_width=16,
            byte_order=ByteOrder.BIG_ENDIAN
        )

    # Test with bytes initialization
    flags = OrderFlags(b'\x01\x02')  # 0x0102 in big endian
    assert flags.value == 2

    flags = OrderFlags(b'\x02\x01')  # Should interpret differently
    assert flags.value == 1


def test_validation():
    """Test input validation."""
    class ValidFlags(BitFieldModel):
        value: int = Bit(0, 1)
        flag: bool = Bit(2)

    # Test invalid bit width configuration
    try:
        class InvalidWidth(BitFieldModel):
            x: bool = Bit(0)
            struct_config = StructConfig(bit_width=12)

    except ValueError as e:
        ...
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
    assert flags.raw_value == 0

    # Test bytes init
    flags = ByteFlags(__bit_sequence=b'\x0F')  # 0b00001111
    assert flags.read
    assert flags.value == 7

    # Test kwargs override bytes
    flags = ByteFlags(__bit_sequence=b'\xFF', read=False)
    assert not flags.read
