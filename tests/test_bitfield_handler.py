"""Test BitFieldHandler type handler integration with StructModel.

This module tests the BitFieldHandler's behavior when BitFieldModel is used
as a field type within StructModel, including Optional handling, validation,
and struct format generation.
"""

from typing import Optional

import pytest
from pydantic import Field

from pdc_struct import (
    BitFieldModel,
    StructModel,
    StructConfig,
    StructMode,
    ByteOrder,
    Bit,
)
from pdc_struct.c_types import UInt8, UInt16


# ============================================================================
# HIGH PRIORITY TESTS - Optional BitField Support
# ============================================================================


def test_optional_bitfield_in_struct_present():
    """Test packing/unpacking a StructModel with an Optional BitFieldModel when value is present.

    Coverage: BitFieldHandler.get_struct_format() with Optional (lines 24-26),
              BitFieldHandler.unpack() with Optional (lines 82-84)
    """

    class Flags(BitFieldModel):
        read: bool = Bit(0)
        write: bool = Bit(1)
        execute: bool = Bit(2)
        struct_config = StructConfig(bit_width=8)

    class PacketWithOptionalFlags(StructModel):
        packet_type: UInt8
        flags: Optional[Flags] = Field(default=None, description="Optional flags")
        struct_config = StructConfig(mode=StructMode.DYNAMIC)

    # Test with flags present
    flags_value = Flags(read=True, write=False, execute=True)
    packet = PacketWithOptionalFlags(packet_type=1, flags=flags_value)

    # Pack to bytes
    data = packet.to_bytes()
    assert len(data) > 0

    # Unpack from bytes
    unpacked = PacketWithOptionalFlags.from_bytes(data)
    assert unpacked.packet_type == 1
    assert unpacked.flags is not None
    assert unpacked.flags.read is True
    assert unpacked.flags.write is False
    assert unpacked.flags.execute is True
    assert unpacked.flags.packed_value == flags_value.packed_value


def test_optional_bitfield_in_struct_absent():
    """Test packing/unpacking when Optional BitFieldModel is None.

    Coverage: BitFieldHandler.pack() returns None (lines 68-70)
    """

    class Flags(BitFieldModel):
        read: bool = Bit(0)
        write: bool = Bit(1)
        struct_config = StructConfig(bit_width=8)

    class PacketWithOptionalFlags(StructModel):
        packet_type: UInt8
        flags: Optional[Flags] = Field(default=None, description="Optional flags")
        struct_config = StructConfig(mode=StructMode.DYNAMIC)

    # Test with flags absent (None)
    packet = PacketWithOptionalFlags(packet_type=2, flags=None)

    # Pack to bytes
    data = packet.to_bytes()
    assert len(data) > 0

    # Unpack from bytes
    unpacked = PacketWithOptionalFlags.from_bytes(data)
    assert unpacked.packet_type == 2
    assert unpacked.flags is None


def test_optional_bitfield_c_compatible_mode():
    """Test Optional BitFieldModel in C_COMPATIBLE mode.

    In C_COMPATIBLE mode, optional fields must have a default_factory.

    Coverage: BitFieldHandler with Optional in C_COMPATIBLE mode
    """

    class Flags(BitFieldModel):
        enabled: bool = Bit(0)
        debug: bool = Bit(1)
        struct_config = StructConfig(bit_width=8)

    class CPacket(StructModel):
        value: UInt16
        flags: Optional[Flags] = Field(
            default_factory=lambda: Flags(), description="Optional flags"
        )
        struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

    # Test with flags present
    packet_with_flags = CPacket(value=100, flags=Flags(enabled=True, debug=False))
    data_with = packet_with_flags.to_bytes()

    # Test with flags absent - using default factory
    packet_without_flags = CPacket(value=100)
    data_without = packet_without_flags.to_bytes()

    # Both should produce valid data
    assert len(data_with) > 0
    assert len(data_without) > 0

    # Unpack and verify
    unpacked_with = CPacket.from_bytes(data_with)
    assert unpacked_with.flags.enabled is True
    assert unpacked_with.flags.debug is False


# ============================================================================
# HIGH PRIORITY TESTS - Bit Width Struct Formats
# ============================================================================


def test_bitfield_struct_formats_all_widths():
    """Verify correct struct format for 8, 16, and 32-bit BitFields in StructModels.

    Coverage: BitFieldHandler.get_struct_format() dummy instance creation and mapping (lines 29-36)
    """

    # Test 8-bit width
    class Flags8(BitFieldModel):
        value: int = Bit(0, 1)
        struct_config = StructConfig(bit_width=8)

    class Struct8(StructModel):
        flags: Flags8
        struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

    s8 = Struct8(flags=Flags8(value=3))
    assert "B" in s8.struct_format_string()
    data8 = s8.to_bytes()
    assert len(data8) == 1

    # Test 16-bit width
    class Flags16(BitFieldModel):
        value: int = Bit(0, 1, 2)
        struct_config = StructConfig(bit_width=16)

    class Struct16(StructModel):
        flags: Flags16
        struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

    s16 = Struct16(flags=Flags16(value=7))
    assert "H" in s16.struct_format_string()
    data16 = s16.to_bytes()
    assert len(data16) == 2

    # Test 32-bit width
    class Flags32(BitFieldModel):
        value: int = Bit(0, 1, 2, 3)
        struct_config = StructConfig(bit_width=32)

    class Struct32(StructModel):
        flags: Flags32
        struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

    s32 = Struct32(flags=Flags32(value=15))
    assert "I" in s32.struct_format_string()
    data32 = s32.to_bytes()
    assert len(data32) == 4


def test_bitfield_with_optional_annotation_get_format():
    """Test that get_struct_format correctly handles Optional[BitFieldModel] annotation.

    Coverage: Lines 24-26 where we unwrap Optional types
    """

    class StatusFlags(BitFieldModel):
        active: bool = Bit(0)
        ready: bool = Bit(1)
        error: bool = Bit(2)
        struct_config = StructConfig(bit_width=16)

    class Message(StructModel):
        msg_id: UInt8
        status: Optional[StatusFlags] = None
        struct_config = StructConfig(mode=StructMode.DYNAMIC)

    # Create with status present
    msg = Message(msg_id=42, status=StatusFlags(active=True, ready=True, error=False))
    data = msg.to_bytes()

    # Should successfully pack and unpack
    unpacked = Message.from_bytes(data)
    assert unpacked.msg_id == 42
    assert unpacked.status.active is True
    assert unpacked.status.ready is True
    assert unpacked.status.error is False


# ============================================================================
# MEDIUM PRIORITY TESTS - Validation Errors
# ============================================================================


def test_validate_bitfield_construction_error():
    """Test that BitFieldModels that fail to construct are caught during validation.

    Coverage: BitFieldHandler.validate_field() exception handling (lines 52-56)
    """

    # Create a BitFieldModel with overlapping bits (should fail during construction)
    with pytest.raises(ValueError):

        class BrokenFlags(BitFieldModel):
            # These bits overlap, which should cause an error during validation
            field_a: int = Bit(0, 1, 2)
            field_b: int = Bit(2, 3, 4)  # Overlaps with field_a at bit 2
            struct_config = StructConfig(bit_width=8)


def test_validate_invalid_bit_width():
    """Test that invalid bit widths are caught during BitFieldModel construction.

    This tests that the validation error is properly propagated through the handler.

    Coverage: BitFieldHandler.validate_field() exception path (lines 52-56)
    """

    # Try to create a BitFieldModel with an invalid bit width
    with pytest.raises(ValueError):

        class InvalidWidthFlags(BitFieldModel):
            flag: bool = Bit(0)
            struct_config = StructConfig(bit_width=24)  # Invalid: must be 8, 16, or 32


def test_bitfield_exceeds_bit_width():
    """Test that bit positions exceeding the configured bit width are caught.

    Coverage: BitFieldHandler validation error paths
    """

    with pytest.raises(ValueError):

        class ExceedingFlags(BitFieldModel):
            # Bit 8 is out of range for an 8-bit field
            flag: bool = Bit(8)
            struct_config = StructConfig(bit_width=8)


# ============================================================================
# ADDITIONAL COVERAGE - Pack/Unpack Integration
# ============================================================================


def test_bitfield_roundtrip_in_struct():
    """Test complete roundtrip of BitFieldModel within StructModel.

    This ensures pack() and unpack() work correctly together.
    """

    class ProtocolFlags(BitFieldModel):
        version: int = Bit(0, 1, 2)  # 3 bits for version (0-7)
        encrypted: bool = Bit(3)
        compressed: bool = Bit(4)
        ack_required: bool = Bit(5)
        struct_config = StructConfig(bit_width=8)

    class ProtocolHeader(StructModel):
        flags: ProtocolFlags
        sequence: UInt16
        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE, byte_order=ByteOrder.LITTLE_ENDIAN
        )

    # Create a header with specific flag values
    original = ProtocolHeader(
        flags=ProtocolFlags(
            version=5, encrypted=True, compressed=False, ack_required=True
        ),
        sequence=12345,
    )

    # Pack to bytes
    data = original.to_bytes()

    # Unpack from bytes
    restored = ProtocolHeader.from_bytes(data)

    # Verify all fields match
    assert restored.flags.version == 5
    assert restored.flags.encrypted is True
    assert restored.flags.compressed is False
    assert restored.flags.ack_required is True
    assert restored.sequence == 12345


def test_multiple_bitfields_in_struct():
    """Test StructModel with multiple BitFieldModel fields.

    Coverage: Ensure the handler works correctly with multiple bitfield fields
    """

    class Flags1(BitFieldModel):
        a: bool = Bit(0)
        b: bool = Bit(1)
        struct_config = StructConfig(bit_width=8)

    class Flags2(BitFieldModel):
        x: bool = Bit(0)
        y: bool = Bit(1)
        z: bool = Bit(2)
        struct_config = StructConfig(bit_width=16)

    class MultiFlags(StructModel):
        flags1: Flags1
        value: UInt8
        flags2: Flags2
        struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

    # Create and test
    obj = MultiFlags(
        flags1=Flags1(a=True, b=False), value=42, flags2=Flags2(x=False, y=True, z=True)
    )

    data = obj.to_bytes()
    restored = MultiFlags.from_bytes(data)

    assert restored.flags1.a is True
    assert restored.flags1.b is False
    assert restored.value == 42
    assert restored.flags2.x is False
    assert restored.flags2.y is True
    assert restored.flags2.z is True
