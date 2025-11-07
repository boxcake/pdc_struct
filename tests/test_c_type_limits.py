# tests/test_ctype_min_max.py

import pytest
from pdc_struct.c_types import Int8, UInt8, Int16, UInt16


def test_int8_bounds():
    """Test Int8 bounds and type checking."""
    # Test valid values
    assert Int8(127) == 127  # Max value
    assert Int8(-128) == -128  # Min value
    assert Int8(0) == 0  # Zero

    # Test invalid values
    with pytest.raises(ValueError, match="must be between -128 and 127"):
        Int8(128)  # Too high
    with pytest.raises(ValueError, match="must be between -128 and 127"):
        Int8(-129)  # Too low

    # Test invalid types
    with pytest.raises(TypeError, match="Int8 requires an integer value"):
        Int8(3.14)
    with pytest.raises(TypeError, match="Int8 requires an integer value"):
        Int8("123")
    with pytest.raises(TypeError, match="Int8 requires an integer value"):
        Int8(None)


def test_uint8_bounds():
    """Test UInt8 bounds and type checking."""
    # Test valid values
    assert UInt8(255) == 255  # Max value
    assert UInt8(0) == 0  # Min value
    assert UInt8(128) == 128  # Middle value

    # Test invalid values
    with pytest.raises(ValueError, match="must be between 0 and 255"):
        UInt8(256)  # Too high
    with pytest.raises(ValueError, match="must be between 0 and 255"):
        UInt8(-1)  # Too low

    # Test invalid types
    with pytest.raises(TypeError, match="UInt8 requires an integer value"):
        UInt8(3.14)
    with pytest.raises(TypeError, match="UInt8 requires an integer value"):
        UInt8("123")
    with pytest.raises(TypeError, match="UInt8 requires an integer value"):
        UInt8(None)


def test_int16_bounds():
    """Test Int16 bounds and type checking."""
    # Test valid values
    assert Int16(32767) == 32767  # Max value
    assert Int16(-32768) == -32768  # Min value
    assert Int16(0) == 0  # Zero

    # Test invalid values
    with pytest.raises(ValueError, match="must be between -32768 and 32767"):
        Int16(32768)  # Too high
    with pytest.raises(ValueError, match="must be between -32768 and 32767"):
        Int16(-32769)  # Too low

    # Test invalid types
    with pytest.raises(TypeError, match="Int16 requires an integer value"):
        Int16(3.14)
    with pytest.raises(TypeError, match="Int16 requires an integer value"):
        Int16("123")
    with pytest.raises(TypeError, match="Int16 requires an integer value"):
        Int16(None)


def test_uint16_bounds():
    """Test UInt16 bounds and type checking."""
    # Test valid values
    assert UInt16(65535) == 65535  # Max value
    assert UInt16(0) == 0  # Min value
    assert UInt16(32768) == 32768  # Middle value

    # Test invalid values
    with pytest.raises(ValueError, match="must be between 0 and 65535"):
        UInt16(65536)  # Too high
    with pytest.raises(ValueError, match="must be between 0 and 65535"):
        UInt16(-1)  # Too low

    # Test invalid types
    with pytest.raises(TypeError, match="UInt16 requires an integer value"):
        UInt16(3.14)
    with pytest.raises(TypeError, match="UInt16 requires an integer value"):
        UInt16("123")
    with pytest.raises(TypeError, match="UInt16 requires an integer value"):
        UInt16(None)


def test_type_promotion():
    """Test that types can accept their own type as input."""
    # Int8
    val8 = Int8(100)
    assert Int8(val8) == 100

    # UInt8
    val_u8 = UInt8(200)
    assert UInt8(val_u8) == 200

    # Int16
    val16 = Int16(1000)
    assert Int16(val16) == 1000

    # UInt16
    val_u16 = UInt16(2000)
    assert UInt16(val_u16) == 2000


def test_value_comparison():
    """Test comparison operations with plain integers."""
    # Int8
    assert Int8(100) == 100
    assert Int8(100) < 101
    assert Int8(100) > 99

    # UInt8
    assert UInt8(200) == 200
    assert UInt8(200) < 201
    assert UInt8(200) > 199

    # Int16
    assert Int16(1000) == 1000
    assert Int16(1000) < 1001
    assert Int16(1000) > 999

    # UInt16
    assert UInt16(2000) == 2000
    assert UInt16(2000) < 2001
    assert UInt16(2000) > 1999
