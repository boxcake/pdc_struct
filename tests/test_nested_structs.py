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


def test_nested_little_endian():
    """Test nested struct serialization with various byte order configurations."""

    class Point(StructModel):
        x: float = Field(description="X coordinate")
        y: float = Field(description="Y coordinate")
        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE, byte_order=ByteOrder.LITTLE_ENDIAN
        )

    class Circle(StructModel):
        center: Point = Field(description="Center point")
        radius: float = Field(description="Circle radius")
        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE, byte_order=ByteOrder.LITTLE_ENDIAN
        )

    # Test 1: Basic nesting with system byte order (little endian)
    circle = Circle(center=Point(x=1.0, y=2.0), radius=5.0)
    packed = circle.to_bytes()
    recovered = Circle.from_bytes(packed)
    assert recovered.center.x == 1.0
    assert recovered.center.y == 2.0
    assert recovered.radius == 5.0


def test_nested_explicit_big_endian():

    # Test 2: Explicit big endian for both parent and child
    class BigEndianPoint(StructModel):
        x: float = Field(description="X coordinate")
        y: float = Field(description="Y coordinate")
        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE, byte_order=ByteOrder.BIG_ENDIAN
        )

    class BigEndianCircle(StructModel):
        center: BigEndianPoint = Field(description="Center point")
        radius: float = Field(description="Circle radius")
        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE, byte_order=ByteOrder.BIG_ENDIAN
        )

    be_circle = BigEndianCircle(center=BigEndianPoint(x=1.0, y=2.0), radius=5.0)
    be_packed = be_circle.to_bytes()
    be_recovered = BigEndianCircle.from_bytes(be_packed)
    assert be_recovered.center.x == 1.0
    assert be_recovered.center.y == 2.0
    assert be_recovered.radius == 5.0


def test_mixed_endian_structs_no_propagation():
    # Test 3: Mixed endianness with propagation disabled

    class BigEndianPoint(StructModel):
        x: float = Field(description="X coordinate")
        y: float = Field(description="Y coordinate")
        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE, byte_order=ByteOrder.BIG_ENDIAN
        )

    class MixedCircle(StructModel):
        # Little endian parent with big endian child
        center: BigEndianPoint = Field(description="Center point")
        radius: float = Field(description="Circle radius")
        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE,
            byte_order=ByteOrder.LITTLE_ENDIAN,
            propagate_byte_order=False,  # Don't override child's endianness
        )

    mixed_circle = MixedCircle(center=BigEndianPoint(x=1.0, y=2.0), radius=5.0)
    mixed_packed = mixed_circle.to_bytes()
    mixed_recovered = MixedCircle.from_bytes(mixed_packed)
    assert mixed_recovered.center.x == 1.0
    assert mixed_recovered.center.y == 2.0
    assert mixed_recovered.radius == 5.0


def test_nested_mixed_endian_structs_with_propagation():
    # Test 4: Mixed endianness with propagation enabled
    class BigEndianPoint(StructModel):
        x: float = Field(description="X coordinate")
        y: float = Field(description="Y coordinate")
        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE, byte_order=ByteOrder.BIG_ENDIAN
        )

    class PropagatingCircle(StructModel):
        center: BigEndianPoint = Field(description="Center point")
        radius: float = Field(description="Circle radius")
        struct_config = StructConfig(
            mode=StructMode.C_COMPATIBLE,
            byte_order=ByteOrder.LITTLE_ENDIAN,
            propagate_byte_order=True,  # Override child's endianness
        )

    prop_circle = PropagatingCircle(center=BigEndianPoint(x=1.0, y=2.0), radius=5.0)
    prop_packed = prop_circle.to_bytes()
    prop_recovered = PropagatingCircle.from_bytes(prop_packed)
    assert prop_recovered.center.x == 1.0
    assert prop_recovered.center.y == 2.0
    assert prop_recovered.radius == 5.0


def test_dynamic_mode_nested_structs():
    # Test 5: Dynamic mode with nested structs
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

    # Test with present optional field
    dynamic_circle = DynamicCircle(center=Point(x=1.0, y=2.0), radius=5.0)
    dynamic_packed = dynamic_circle.to_bytes()
    dynamic_recovered = DynamicCircle.from_bytes(dynamic_packed)
    assert dynamic_recovered.center.x == 1.0
    assert dynamic_recovered.center.y == 2.0
    assert dynamic_recovered.radius == 5.0

    # Test with None optional field
    dynamic_circle_none = DynamicCircle(center=None, radius=5.0)
    dynamic_packed_none = dynamic_circle_none.to_bytes()
    dynamic_recovered_none = DynamicCircle.from_bytes(dynamic_packed_none)
    assert dynamic_recovered_none.center is None
    assert dynamic_recovered_none.radius == 5.0

    # Test 6: Verify byte patterns
    import struct

    # Create a point with known values that will have different
    # byte patterns in different endianness
    test_point = Point(x=1.0, y=2.0)

    # Get the byte patterns in both endiannesses
    le_bytes = test_point.to_bytes()
    be_bytes = test_point.to_bytes(override_endian=ByteOrder.BIG_ENDIAN)

    # These should be different
    assert le_bytes != be_bytes, "Little and big endian representations should differ"

    # Verify the actual byte patterns match what we expect
    le_expected = str
