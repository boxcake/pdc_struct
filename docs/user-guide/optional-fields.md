# Optional Fields

Optional fields allow you to make struct fields conditional, with behavior that depends on the operating mode. This guide covers how optional fields work in both C_COMPATIBLE and DYNAMIC modes.

## Overview

Optional fields are declared using Python's `Optional` type hint:

```python
from typing import Optional
from pdc_struct import StructModel, StructConfig
from pdc_struct.c_types import UInt8, UInt16

class Message(StructModel):
    msg_type: UInt8              # Required
    sequence: Optional[UInt16]    # Optional

    struct_config = StructConfig()
```

**Critical difference:**
- **C_COMPATIBLE mode**: Optional fields must have defaults and are always packed
- **DYNAMIC mode**: Optional fields are truly optional and omitted when None

## C_COMPATIBLE Mode

In C_COMPATIBLE mode, optional fields are **not truly optional**. They must have defaults and are always included in the packed data.

### Requirements

1. **Must have a default value** or `default_factory`
2. **Always packed** - even when None
3. **Fixed struct size** - same regardless of field values

```python
from typing import Optional
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt16

class Packet(StructModel):
    msg_type: UInt8
    sequence: Optional[UInt16] = 0  # Must have default!

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# Both pack to the same size
p1 = Packet(msg_type=1, sequence=100)
p2 = Packet(msg_type=1, sequence=None)  # Uses default: 0

print(len(p1.to_bytes()))  # 3 bytes
print(len(p2.to_bytes()))  # 3 bytes (same!)
```

### Why This Behavior?

C structs have fixed layouts. Optional fields in C_COMPATIBLE mode allow you to:

- Mark fields as "may be zero/unset" in your schema
- Provide sensible defaults
- Maintain fixed struct size for C compatibility

!!! warning "Not Truly Optional"
    In C_COMPATIBLE mode, `Optional[T]` means "this field might be None in Python," but it's **always packed** using the default value. Use DYNAMIC mode for truly optional fields.

### Without Default (Error)

```python
from typing import Optional
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt16

# This raises ValueError!
try:
    class BadPacket(StructModel):
        msg_type: UInt8
        sequence: Optional[UInt16]  # No default - ERROR!

        struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)
except ValueError as e:
    print(f"Error: {e}")
    # "Field 'sequence': Optional fields in C_COMPATIBLE mode must have default"
```

### Examples

#### Optional with Simple Default

```python
from typing import Optional
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt16

class Config(StructModel):
    version: UInt8
    timeout: Optional[UInt16] = 3000  # Default timeout

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# Uses default
cfg1 = Config(version=1)  # timeout=3000
print(cfg1.timeout)  # 3000

# Override default
cfg2 = Config(version=1, timeout=5000)
print(cfg2.timeout)  # 5000

# Set to None - uses default when packing
cfg3 = Config(version=1, timeout=None)
data = cfg3.to_bytes()
restored = Config.from_bytes(data)
print(restored.timeout)  # 3000 (default was packed)
```

#### Optional Nested Struct

```python
from typing import Optional
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt16

class Point(StructModel):
    x: UInt16
    y: UInt16
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

class Shape(StructModel):
    shape_id: UInt16
    center: Optional[Point] = Point(x=0, y=0)  # Default center

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# Always 6 bytes: 2 (shape_id) + 4 (Point)
shape1 = Shape(shape_id=1)
shape2 = Shape(shape_id=1, center=Point(x=10, y=20))

print(len(shape1.to_bytes()))  # 6 bytes
print(len(shape2.to_bytes()))  # 6 bytes
```

## DYNAMIC Mode

In DYNAMIC mode, optional fields are **truly optional**. They are omitted from packed data when None, saving space.

### Characteristics

1. **No default required** - can be `None` without default
2. **Variable size** - depends on which fields are present
3. **Bitmap tracking** - header tracks which fields are included
4. **Space efficient** - absent fields don't consume bytes

```python
from typing import Optional
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt16

class Message(StructModel):
    msg_type: UInt8
    sequence: Optional[UInt16] = None  # Truly optional

    struct_config = StructConfig(mode=StructMode.DYNAMIC)

# Without sequence
m1 = Message(msg_type=1)
data1 = m1.to_bytes()

# With sequence
m2 = Message(msg_type=1, sequence=100)
data2 = m2.to_bytes()

# Different sizes!
print(len(data1))  # Smaller (no sequence)
print(len(data2))  # Larger (includes sequence)

# Roundtrip preserves None
restored1 = Message.from_bytes(data1)
assert restored1.sequence is None  # ✓
```

### How It Works

DYNAMIC mode uses a 4-byte header plus a bitmap to track field presence:

```
[Header: 4 bytes][Bitmap: variable][Data: variable]
```

The bitmap indicates which optional fields are present. Only present fields are packed.

### Examples

#### Minimal vs Full Message

```python
from typing import Optional
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt16, UInt32

class Event(StructModel):
    event_type: UInt8                # Required
    user_id: Optional[UInt32] = None  # Optional
    session_id: Optional[UInt16] = None  # Optional

    struct_config = StructConfig(mode=StructMode.DYNAMIC)

# Minimal event - only required fields
e1 = Event(event_type=1)
print(f"Minimal: {len(e1.to_bytes())} bytes")

# Partial event - some optional fields
e2 = Event(event_type=1, user_id=12345)
print(f"Partial: {len(e2.to_bytes())} bytes")

# Full event - all fields
e3 = Event(event_type=1, user_id=12345, session_id=999)
print(f"Full: {len(e3.to_bytes())} bytes")

# Each is a different size!
```

#### Optional Nested Struct

```python
from typing import Optional
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt16

class Location(StructModel):
    lat: UInt16
    lon: UInt16
    struct_config = StructConfig(mode=StructMode.DYNAMIC)

class SensorReading(StructModel):
    sensor_id: UInt8
    temperature: UInt16
    location: Optional[Location] = None  # GPS optional

    struct_config = StructConfig(mode=StructMode.DYNAMIC)

# Without location (GPS unavailable)
r1 = SensorReading(sensor_id=1, temperature=2150)

# With location (GPS available)
r2 = SensorReading(
    sensor_id=1,
    temperature=2150,
    location=Location(lat=4000, lon=7400)
)

# r1 is smaller - location not packed
print(f"Without GPS: {len(r1.to_bytes())} bytes")
print(f"With GPS: {len(r2.to_bytes())} bytes")
```

#### Multiple Optional Fields

```python
from typing import Optional
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt16, UInt32

class LogEntry(StructModel):
    level: UInt8  # Required
    thread_id: Optional[UInt16] = None
    user_id: Optional[UInt32] = None
    request_id: Optional[UInt32] = None

    struct_config = StructConfig(mode=StructMode.DYNAMIC)

# Different combinations
log1 = LogEntry(level=1)  # Only level
log2 = LogEntry(level=1, thread_id=5)  # +thread
log3 = LogEntry(level=1, user_id=1000, request_id=9999)  # +user+request

# Bitmap tracks which fields are present
# Each has different size based on present fields
```

## Comparison: C_COMPATIBLE vs DYNAMIC

| Feature | C_COMPATIBLE | DYNAMIC |
|---------|--------------|---------|
| **Default required?** | Yes | No |
| **Packed when None?** | Yes (uses default) | No (omitted) |
| **Struct size** | Fixed | Variable |
| **Space efficiency** | Lower | Higher |
| **C compatibility** | Yes | No |
| **Use case** | Fixed protocols, C interop | Python-to-Python, flexible formats |

## Choosing the Right Mode

### Use C_COMPATIBLE when:

✅ You need fixed struct sizes
✅ Interfacing with C/C++ code
✅ Network protocols with fixed headers
✅ Hardware communication
✅ Legacy file formats

### Use DYNAMIC when:

✅ You want truly optional fields
✅ Python-to-Python communication
✅ Space efficiency matters
✅ Fields are frequently absent
✅ No C compatibility required

## Advanced Patterns

### Optional BitFields

```python
from typing import Optional
from pdc_struct import StructModel, BitFieldModel, StructConfig, StructMode
from pdc_struct.models.bit_field import Bit
from pdc_struct.c_types import UInt8

class Flags(BitFieldModel):
    read: bool = Bit(0)
    write: bool = Bit(1)
    struct_config = StructConfig(bit_width=8)

# C_COMPATIBLE: Must have default
class PacketC(StructModel):
    msg_type: UInt8
    flags: Optional[Flags] = Flags()  # Default required
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# DYNAMIC: No default needed
class PacketD(StructModel):
    msg_type: UInt8
    flags: Optional[Flags] = None  # Truly optional
    struct_config = StructConfig(mode=StructMode.DYNAMIC)

# DYNAMIC version saves 1 byte when flags is None
```

### Conditional Fields

Use optional fields for protocol versioning:

```python
from typing import Optional
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt16, UInt32

class Message(StructModel):
    version: UInt8
    msg_id: UInt16

    # v2 fields (optional for backward compatibility)
    timestamp: Optional[UInt32] = None
    priority: Optional[UInt8] = None

    struct_config = StructConfig(mode=StructMode.DYNAMIC)

# v1 message (no optional fields)
v1_msg = Message(version=1, msg_id=100)

# v2 message (includes new fields)
v2_msg = Message(version=2, msg_id=100, timestamp=123456, priority=5)

# Old code can read both versions
# New fields gracefully absent in v1 messages
```

### Default Factories

Use `default_factory` for mutable defaults:

```python
from typing import Optional
from pydantic import Field
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt16

class Point(StructModel):
    x: UInt16
    y: UInt16
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

def default_point():
    return Point(x=0, y=0)

class Shape(StructModel):
    shape_id: UInt8
    center: Optional[Point] = Field(default_factory=default_point)

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# Each instance gets its own Point instance
s1 = Shape(shape_id=1)
s2 = Shape(shape_id=2)
assert s1.center is not s2.center  # Different objects
```

## Validation

### C_COMPATIBLE Validation

At class creation, C_COMPATIBLE mode validates all optional fields have defaults:

```python
# Valid
class Good(StructModel):
    x: Optional[UInt8] = 0
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# Invalid - raises ValueError
class Bad(StructModel):
    x: Optional[UInt8]  # No default!
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)
```

### DYNAMIC Validation

DYNAMIC mode doesn't require defaults:

```python
# Both valid in DYNAMIC mode
class Message1(StructModel):
    x: Optional[UInt8]  # No default - OK
    struct_config = StructConfig(mode=StructMode.DYNAMIC)

class Message2(StructModel):
    x: Optional[UInt8] = 0  # With default - also OK
    struct_config = StructConfig(mode=StructMode.DYNAMIC)
```

## Best Practices

1. **C_COMPATIBLE**: Provide sensible defaults for optional fields
2. **DYNAMIC**: Use optional fields to reduce message size
3. **Documentation**: Explain when optional fields should be present
4. **Versioning**: Use optional fields for backward compatibility
5. **Validation**: Add custom validators for field dependencies

## Common Pitfalls

### Expecting True Optionality in C_COMPATIBLE

```python
# WRONG: Expecting None to be preserved
class Packet(StructModel):
    flags: Optional[UInt8] = 0
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

p = Packet(flags=None)
data = p.to_bytes()
restored = Packet.from_bytes(data)
# restored.flags is 0, not None! Default was packed.
```

### Forgetting Defaults in C_COMPATIBLE

```python
# ERROR: No default provided
class Packet(StructModel):
    timeout: Optional[UInt16]  # ValueError!
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)
```

### Assuming Fixed Size in DYNAMIC

```python
# WRONG: Size is not fixed in DYNAMIC mode
class Message(StructModel):
    data: Optional[UInt32] = None
    struct_config = StructConfig(mode=StructMode.DYNAMIC)

m1 = Message(data=None)
m2 = Message(data=100)

# These are DIFFERENT sizes!
assert len(m1.to_bytes()) != len(m2.to_bytes())
```

## Summary

Optional fields provide flexibility with mode-specific behavior:

**C_COMPATIBLE Mode:**
- Optional fields must have defaults
- Always packed (not truly optional)
- Fixed struct size
- Use for C interoperability

**DYNAMIC Mode:**
- Optional fields can be None without defaults
- Truly optional (omitted when None)
- Variable struct size
- Use for space-efficient Python serialization

Choose the mode that matches your requirements for compatibility, size, and optionality semantics.

For more information:

- [Modes](modes.md) - Detailed comparison of C_COMPATIBLE vs DYNAMIC
- [Types](types.md) - All supported field types
- [Nested Structs](nested-structs.md) - Optional nested structures
