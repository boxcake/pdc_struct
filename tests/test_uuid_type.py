"""Test UUID support in PDC Struct."""
import uuid
from typing import Optional
from pydantic import Field
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder

# Create a zero UUID for use as a default
ZERO_UUID = uuid.UUID('00000000-0000-0000-0000-000000000000')


class UUIDModel(StructModel):
    """Model with UUID fields."""
    id: uuid.UUID
    optional_id: Optional[uuid.UUID] = ZERO_UUID  # Use zero UUID as default
    name: str = Field(max_length=10)

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN
    )


def test_uuid_basic():
    """Test basic UUID packing and unpacking."""
    # Create a UUID
    test_uuid = uuid.uuid4()

    # Create and pack model
    model = UUIDModel(
        id=test_uuid,
        name="test"
    )
    data = model.to_bytes()

    # Unpack and verify
    recovered = UUIDModel.from_bytes(data)
    assert recovered.id == test_uuid
    assert recovered.name == "test"
    assert recovered.optional_id == ZERO_UUID  # Should have default value
    assert isinstance(recovered.id, uuid.UUID)


def test_multiple_uuids():
    """Test handling multiple UUIDs."""
    # Create UUIDs
    id1 = uuid.uuid4()
    id2 = uuid.uuid4()

    # Create and pack model
    model = UUIDModel(
        id=id1,
        optional_id=id2,
        name="test"
    )
    data = model.to_bytes()

    # Unpack and verify
    recovered = UUIDModel.from_bytes(data)
    assert recovered.id == id1
    assert recovered.optional_id == id2
    assert recovered.name == "test"


def test_uuid_dynamic_mode():
    """Test UUIDs in dynamic mode."""

    class DynamicUUIDModel(StructModel):
        id: Optional[uuid.UUID] = None
        backup_id: Optional[uuid.UUID] = None

        struct_config = StructConfig(
            mode=StructMode.DYNAMIC,
            byte_order=ByteOrder.LITTLE_ENDIAN
        )

    # Test with values
    id1 = uuid.uuid4()
    id2 = uuid.uuid4()
    model = DynamicUUIDModel(
        id=id1,
        backup_id=id2
    )
    data = model.to_bytes()
    recovered = DynamicUUIDModel.from_bytes(data)
    assert recovered.id == id1
    assert recovered.backup_id == id2

    # Test without values
    model = DynamicUUIDModel()
    data = model.to_bytes()
    recovered = DynamicUUIDModel.from_bytes(data)
    assert recovered.id is None
    assert recovered.backup_id is None


def test_uuid_endianness():
    """Test UUID handling with different byte orders."""
    # Create a test UUID
    test_uuid = uuid.uuid4()

    # Test big endian
    class BigEndianModel(StructModel):
        id: uuid.UUID

        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE,
            byte_order=ByteOrder.BIG_ENDIAN
        )

    model = BigEndianModel(id=test_uuid)
    data = model.to_bytes()
    recovered = BigEndianModel.from_bytes(data)
    assert recovered.id == test_uuid

    # Test little endian
    class LittleEndianModel(StructModel):
        id: uuid.UUID

        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE,
            byte_order=ByteOrder.LITTLE_ENDIAN
        )

    model = LittleEndianModel(id=test_uuid)
    data = model.to_bytes()
    recovered = LittleEndianModel.from_bytes(data)
    assert recovered.id == test_uuid


def test_zero_uuid():
    """Test handling of zero UUID."""
    model = UUIDModel(
        id=ZERO_UUID,
        optional_id=ZERO_UUID,
        name="test"
    )
    data = model.to_bytes()
    recovered = UUIDModel.from_bytes(data)
    assert recovered.id == ZERO_UUID
    assert recovered.optional_id == ZERO_UUID
