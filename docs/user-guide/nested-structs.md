# Nested Structs

Nested structs allow you to compose complex data structures by embedding `StructModel` instances within other `StructModel` instances. This enables hierarchical organization of binary data.

## Basic Nesting

Any `StructModel` can be used as a field type in another `StructModel`:

```python
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt16

class Point(StructModel):
    """2D coordinate."""
    x: UInt16
    y: UInt16

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

class Rectangle(StructModel):
    """Rectangle defined by two points."""
    top_left: Point      # Nested struct
    bottom_right: Point  # Nested struct

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# Create hierarchical data
rect = Rectangle(
    top_left=Point(x=10, y=20),
    bottom_right=Point(x=100, y=200)
)

# Pack to bytes - includes both Points
data = rect.to_bytes()
print(len(data))  # 8 bytes: 4 (Point) + 4 (Point)

# Unpack preserves structure
restored = Rectangle.from_bytes(data)
print(restored.top_left.x)  # 10
print(restored.bottom_right.y)  # 200
```

## How Nested Structs Work

When packing:
1. Parent struct calls `to_bytes()` on each nested struct
2. Nested struct bytes are inserted at the field's position
3. Result is a flat byte sequence

When unpacking:
1. Parent struct extracts bytes for nested struct field
2. Calls nested struct's `from_bytes()` with extracted bytes
3. Reconstructs the hierarchy

## Byte Order Propagation

By default, the parent struct's byte order propagates to nested structs, ensuring consistent endianness throughout the entire structure.

### Automatic Propagation (Default)

```python
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.c_types import UInt16, UInt32

class Header(StructModel):
    magic: UInt16
    version: UInt16
    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN  # Header's preference
    )

class Packet(StructModel):
    header: Header  # Nested struct
    payload_size: UInt32

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN,  # Override
        propagate_byte_order=True  # Default - propagates to Header
    )

# All fields use BIG_ENDIAN (parent overrides child)
packet = Packet(
    header=Header(magic=0x1234, version=1),
    payload_size=1000
)
```

### Disabling Propagation

Set `propagate_byte_order=False` to preserve each struct's own byte order:

```python
class Packet(StructModel):
    header: Header
    payload_size: UInt32

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN,
        propagate_byte_order=False  # Header keeps LITTLE_ENDIAN
    )

# header fields: LITTLE_ENDIAN (from Header's config)
# payload_size: BIG_ENDIAN (from Packet's config)
```

This is useful when wrapping foreign binary formats that have mixed endianness.

## Deeply Nested Structs

Nesting can be arbitrarily deep:

```python
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt16

class Color(StructModel):
    """RGB color."""
    r: UInt8
    g: UInt8
    b: UInt8
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

class Style(StructModel):
    """Drawing style."""
    line_width: UInt8
    fill_color: Color     # Nested level 2
    stroke_color: Color
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

class Shape(StructModel):
    """Drawable shape."""
    shape_type: UInt8
    x: UInt16
    y: UInt16
    style: Style          # Nested level 1 (contains level 2)
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# Three levels of nesting
shape = Shape(
    shape_type=1,
    x=100, y=200,
    style=Style(
        line_width=2,
        fill_color=Color(r=255, g=0, b=0),
        stroke_color=Color(r=0, g=0, b=255)
    )
)

# All nested structs are flattened in binary representation
```

## Optional Nested Structs

Nested structs can be optional, with behavior depending on the mode:

### C_COMPATIBLE Mode

Optional nested structs must have defaults and are always packed:

```python
from typing import Optional
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt16

class Timestamp(StructModel):
    seconds: UInt32
    microseconds: UInt32
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

class Event(StructModel):
    event_type: UInt8
    # Optional nested struct with default
    timestamp: Optional[Timestamp] = Timestamp(seconds=0, microseconds=0)

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# Always same size - default timestamp is packed when None
e1 = Event(event_type=1)  # Uses default timestamp
e2 = Event(event_type=1, timestamp=Timestamp(seconds=123, microseconds=456))

print(len(e1.to_bytes()))  # Same size
print(len(e2.to_bytes()))  # Same size
```

### DYNAMIC Mode

Optional nested structs are truly optional and omitted when None:

```python
from typing import Optional
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt16

class Location(StructModel):
    latitude: UInt16
    longitude: UInt16
    struct_config = StructConfig(mode=StructMode.DYNAMIC)

class SensorReading(StructModel):
    sensor_id: UInt8
    temperature: UInt16
    location: Optional[Location] = None  # Truly optional

    struct_config = StructConfig(mode=StructMode.DYNAMIC)

# Without location
r1 = SensorReading(sensor_id=1, temperature=2150)

# With location
r2 = SensorReading(
    sensor_id=1,
    temperature=2150,
    location=Location(latitude=4000, longitude=7400)
)

# Different sizes!
print(len(r1.to_bytes()))  # Smaller - location omitted
print(len(r2.to_bytes()))  # Larger - location included
```

## Arrays of Structs

While PDC Struct doesn't natively support arrays, you can work around this:

### Fixed-Size Arrays (C_COMPATIBLE)

Define explicit fields:

```python
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt16

class Point(StructModel):
    x: UInt16
    y: UInt16
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

class Polygon(StructModel):
    """Triangle (3 points)."""
    p0: Point
    p1: Point
    p2: Point
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

triangle = Polygon(
    p0=Point(x=0, y=0),
    p1=Point(x=100, y=0),
    p2=Point(x=50, y=100)
)
```

### Variable-Size Collections

Pack/unpack collections manually:

```python
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt16

class Point(StructModel):
    x: UInt16
    y: UInt16
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# Pack multiple points
points = [Point(x=10, y=20), Point(x=30, y=40), Point(x=50, y=60)]
data = b''.join(p.to_bytes() for p in points)

# Unpack multiple points
point_size = Point.struct_size()
num_points = len(data) // point_size
restored_points = [
    Point.from_bytes(data[i*point_size:(i+1)*point_size])
    for i in range(num_points)
]
```

## Struct Size Calculation

Nested struct sizes are automatically calculated:

```python
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt16

class Inner(StructModel):
    a: UInt8
    b: UInt8
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

class Outer(StructModel):
    x: UInt16
    inner: Inner
    y: UInt16
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# Sizes are calculated correctly
print(Inner.struct_size())  # 2 bytes
print(Outer.struct_size())  # 6 bytes: 2 + 2 (Inner) + 2
```

## Common Patterns

### Protocol Headers

```python
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.c_types import UInt8, UInt16, UInt32

class EthernetHeader(StructModel):
    """Ethernet frame header."""
    dest_mac: bytes = Field(max_length=6)
    src_mac: bytes = Field(max_length=6)
    ethertype: UInt16
    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN
    )

class IPv4Header(StructModel):
    """IPv4 packet header (simplified)."""
    version_ihl: UInt8
    tos: UInt8
    total_length: UInt16
    identification: UInt16
    flags_fragment: UInt16
    ttl: UInt8
    protocol: UInt8
    checksum: UInt16
    source_ip: UInt32
    dest_ip: UInt32
    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN
    )

class IPPacket(StructModel):
    """Complete packet with nested headers."""
    ethernet: EthernetHeader
    ip: IPv4Header
    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN
    )
```

### File Format Structures

```python
from pydantic import Field
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.c_types import UInt16, UInt32

class BitmapInfoHeader(StructModel):
    """BMP info header."""
    size: UInt32
    width: UInt32
    height: UInt32
    planes: UInt16
    bit_count: UInt16
    compression: UInt32
    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN
    )

class BitmapFileHeader(StructModel):
    """BMP file header."""
    signature: bytes = Field(max_length=2)  # 'BM'
    file_size: UInt32
    reserved1: UInt16 = 0
    reserved2: UInt16 = 0
    data_offset: UInt32
    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN
    )

class BitmapFile(StructModel):
    """Complete BMP file header."""
    file_header: BitmapFileHeader
    info_header: BitmapInfoHeader
    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN
    )
```

### Configuration Hierarchies

```python
from typing import Optional
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt16, UInt32

class DatabaseConfig(StructModel):
    """Database connection settings."""
    port: UInt16
    timeout: UInt32
    max_connections: UInt16
    struct_config = StructConfig(mode=StructMode.DYNAMIC)

class CacheConfig(StructModel):
    """Cache settings."""
    size_mb: UInt16
    ttl_seconds: UInt32
    struct_config = StructConfig(mode=StructMode.DYNAMIC)

class AppConfig(StructModel):
    """Application configuration."""
    version: UInt8
    database: Optional[DatabaseConfig] = None
    cache: Optional[CacheConfig] = None
    struct_config = StructConfig(mode=StructMode.DYNAMIC)

# Flexible configuration with optional sections
config = AppConfig(
    version=1,
    database=DatabaseConfig(port=5432, timeout=30000, max_connections=100),
    cache=CacheConfig(size_mb=512, ttl_seconds=3600)
)
```

## Validation

Nested structs are validated recursively:

```python
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8

class Inner(StructModel):
    value: UInt8  # 0-255
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

class Outer(StructModel):
    inner: Inner
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# Valid
outer1 = Outer(inner=Inner(value=100))  # OK

# Invalid - Pydantic validates nested struct
try:
    outer2 = Outer(inner=Inner(value=256))  # Error: 256 > 255
except ValueError as e:
    print(f"Validation error: {e}")
```

## Performance Considerations

### Nesting Overhead

Each level of nesting adds:
- One additional `to_bytes()` call when packing
- One additional `from_bytes()` call when unpacking
- Minimal overhead for typical hierarchies (< 5 levels)

### When to Use Nesting

**Use nested structs when:**
- Logical grouping improves readability
- Reusing common sub-structures
- Building protocol stacks (Ethernet → IP → TCP)
- Hierarchical file formats

**Avoid excessive nesting when:**
- Flat structure is equally clear
- Performance is critical (> 10 levels deep)
- Serialization happens in tight loops

## Best Practices

1. **Logical grouping** - Nest related fields together
2. **Reusability** - Extract common patterns into reusable structs
3. **Byte order** - Use propagation for consistent endianness
4. **Documentation** - Document the hierarchy and purpose of each level
5. **Testing** - Test round-trip packing/unpacking of nested structures

## Common Pitfalls

### Forgetting Defaults in C_COMPATIBLE

```python
from typing import Optional
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8

class Inner(StructModel):
    value: UInt8
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# ERROR: Optional nested struct without default
try:
    class Outer(StructModel):
        inner: Optional[Inner]  # No default!
        struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)
except ValueError:
    print("Must provide default for optional nested struct!")

# Correct: Provide default
class Outer(StructModel):
    inner: Optional[Inner] = Inner(value=0)  # OK
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)
```

### Mixing Modes

```python
# Be careful mixing modes - DYNAMIC parent with C_COMPATIBLE child works,
# but may not behave as expected in some cases

class CChild(StructModel):
    x: UInt8
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

class DParent(StructModel):
    child: CChild
    struct_config = StructConfig(mode=StructMode.DYNAMIC)

# Works, but DYNAMIC header is added at parent level only
```

### Byte Order Confusion

```python
# Parent propagation overrides child's setting by default
class Child(StructModel):
    x: UInt16
    struct_config = StructConfig(byte_order=ByteOrder.LITTLE_ENDIAN)

class Parent(StructModel):
    child: Child
    struct_config = StructConfig(
        byte_order=ByteOrder.BIG_ENDIAN,  # Overrides child!
        propagate_byte_order=True  # Default
    )

# Child uses BIG_ENDIAN, not LITTLE_ENDIAN
# Set propagate_byte_order=False if this is not desired
```

## Summary

Nested structs enable hierarchical binary data structures:

- **Compose complex structures** from simple building blocks
- **Byte order propagates** from parent to child (by default)
- **Optional nested structs** work in both modes
- **Deeply nested** structures are supported
- **Automatic size calculation** for nested hierarchies

Use nested structs to organize your binary data logically and reuse common patterns across your project.

For more information:

- [Types](types.md) - All supported field types
- [Optional Fields](optional-fields.md) - Making nested structs optional
- [Byte Order](byte-order.md) - Controlling endianness propagation
- [Modes](modes.md) - How nesting works in C_COMPATIBLE vs DYNAMIC
