# Supported Types

PDC Struct supports a wide range of Python types for binary serialization. This guide covers all supported types, their characteristics, and usage patterns.

## Overview

Types in PDC Struct fall into several categories:

- **Fixed-width integers** - C-compatible integer types (Int8, UInt16, etc.)
- **Floating-point** - float (packed as 32 or 64-bit)
- **Boolean** - bool (packed as single byte)
- **Text** - str (with length specification)
- **Binary** - bytes (with length specification)
- **Network** - IPv4Address, UUID
- **Enums** - IntEnum and standard Enum types
- **Composite** - BitFieldModel and nested StructModel

## Fixed-Width Integer Types

PDC Struct provides C-compatible integer types with explicit sizes and ranges. These types ensure consistent binary representation across platforms.

### Available Integer Types

```python
from pdc_struct.c_types import (
    Int8, UInt8,      # 8-bit (1 byte)
    Int16, UInt16,    # 16-bit (2 bytes)
    # Int32, UInt32,  # Coming soon
    # Int64, UInt64,  # Coming soon
)
```

### Integer Type Reference

| Type | Size | Signed | Range | Struct Format |
|------|------|--------|-------|---------------|
| `Int8` | 1 byte | Yes | -128 to 127 | `b` |
| `UInt8` | 1 byte | No | 0 to 255 | `B` |
| `Int16` | 2 bytes | Yes | -32,768 to 32,767 | `h` |
| `UInt16` | 2 bytes | No | 0 to 65,535 | `H` |

!!! note "Coming Soon"
    Int32, UInt32, Int64, and UInt64 types are planned for future releases.

### Usage

```python
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, Int16, UInt16

class SensorData(StructModel):
    device_id: UInt8        # 0-255
    temperature: Int16      # -32768 to 32767 (use scaled values)
    humidity: UInt16        # 0-65535

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# Validation happens automatically
sensor = SensorData(device_id=42, temperature=2150, humidity=6500)

# Out of range raises ValueError
try:
    bad = SensorData(device_id=256, temperature=0, humidity=0)  # 256 > 255
except ValueError as e:
    print(f"Validation error: {e}")
```

### Why Use Fixed-Width Types?

Python's native `int` type is arbitrary-precision. When serializing to binary, you must specify the exact size. Using PDC Struct's fixed-width types:

✅ Makes size explicit in the code
✅ Validates values at creation time
✅ Prevents overflow/underflow bugs
✅ Ensures compatibility with C structs

## Native Python int

You can also use Python's native `int` type, but you must specify the struct format manually:

```python
from pydantic import Field

class Example(StructModel):
    # Native int - requires struct format in json_schema_extra
    counter: int = Field(json_schema_extra={"struct_format": "I"})  # unsigned int
```

!!! warning "Prefer Fixed-Width Types"
    Using native `int` requires manual struct format specification and bypasses automatic validation. Prefer `Int8`, `UInt8`, etc. for better type safety.

## Floating-Point Types

Python's `float` type is supported and maps to C's double (64-bit) or float (32-bit) depending on your struct format specification.

```python
from pdc_struct import StructModel, StructConfig, StructMode

class Point3D(StructModel):
    x: float  # 64-bit double by default
    y: float
    z: float

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

point = Point3D(x=1.5, y=2.7, z=-3.2)
print(point.struct_format_string())  # '<ddd' (little-endian doubles)
```

### Float Format

| Struct Format | C Type | Size | Precision |
|---------------|--------|------|-----------|
| `f` | float | 4 bytes | ~7 decimal digits |
| `d` | double | 8 bytes | ~15 decimal digits |

By default, PDC Struct uses `d` (double) for Python `float` fields.

## Boolean Type

Python's `bool` type is packed as a single byte (0 for False, non-zero for True).

```python
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8

class Packet(StructModel):
    flags: UInt8
    is_valid: bool      # Packed as 1 byte (0x00 or 0x01)
    has_data: bool

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

p = Packet(flags=0xFF, is_valid=True, has_data=False)
data = p.to_bytes()
print(len(data))  # 3 bytes: 1 (flags) + 1 (is_valid) + 1 (has_data)
```

!!! tip "Use BitFields for Compact Flags"
    If you need multiple boolean flags, consider using `BitFieldModel` to pack them into a single byte. See [Bitfields](bitfields.md) for details.

## String Type

Strings are packed as fixed-length byte sequences. You must specify the maximum length.

```python
from pydantic import Field
from pdc_struct import StructModel, StructConfig, StructMode

class Device(StructModel):
    # Specify length with max_length
    name: str = Field(max_length=16)

    # Or with struct_length in json_schema_extra
    location: str = Field(json_schema_extra={"struct_length": 32})

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

device = Device(name="sensor-01", location="Building A, Floor 2")
print(device.struct_format_string())  # '<16s32s'
```

### String Behavior

**C_COMPATIBLE Mode:**
- Strings are null-terminated (C-style)
- Padded to fixed length with null bytes
- UTF-8 encoding

**DYNAMIC Mode:**
- Strings use specified length as maximum
- No null termination (length is tracked)
- UTF-8 encoding

```python
# C_COMPATIBLE mode example
class CString(StructModel):
    label: str = Field(max_length=10)
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

s = CString(label="hello")
data = s.to_bytes()
print(data)  # b'hello\x00\x00\x00\x00\x00' (null-terminated, padded)
```

## Bytes Type

Binary data is packed as fixed-length byte sequences.

```python
from pydantic import Field
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8

class Crypto(StructModel):
    algorithm: UInt8
    # Fixed-length binary data
    key: bytes = Field(max_length=32)       # 32-byte key
    iv: bytes = Field(max_length=16)        # 16-byte IV

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

crypto = Crypto(
    algorithm=1,
    key=b'\x00' * 32,
    iv=b'\xff' * 16
)
```

!!! warning "Fixed Length Required"
    Both `str` and `bytes` fields require a length specification via `max_length` or `struct_length` in `json_schema_extra`.

## Network Types

PDC Struct supports common network types with automatic serialization.

### IPv4Address

```python
from ipaddress import IPv4Address
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt16

class NetworkConfig(StructModel):
    port: UInt16
    ip_address: IPv4Address  # Packed as 4 bytes (network order)
    gateway: IPv4Address

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

config = NetworkConfig(
    port=8080,
    ip_address=IPv4Address("192.168.1.100"),
    gateway=IPv4Address("192.168.1.1")
)

print(config.struct_format_string())  # '<HII' (port + 2 IPs)
```

### UUID

```python
from uuid import UUID, uuid4
from pdc_struct import StructModel, StructConfig, StructMode

class Record(StructModel):
    record_id: UUID  # Packed as 16 bytes

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

record = Record(record_id=uuid4())
print(len(record.to_bytes()))  # 16 bytes
```

## Enum Types

Python enums are supported with automatic integer conversion.

```python
from enum import IntEnum, Enum
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8

class Status(IntEnum):
    """Use IntEnum for explicit integer values."""
    IDLE = 0
    RUNNING = 1
    ERROR = 2

class Priority(Enum):
    """Regular Enum works too."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Task(StructModel):
    status: Status      # Packed as UInt8 (based on enum values)
    priority: Priority

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

task = Task(status=Status.RUNNING, priority=Priority.HIGH)

# Unpacking restores enum values
data = task.to_bytes()
restored = Task.from_bytes(data)
assert restored.status == Status.RUNNING
assert isinstance(restored.status, Status)
```

## Composite Types

### BitFieldModel

Pack multiple boolean or small integer fields into a single byte/word/dword. See [Bitfields](bitfields.md) for details.

```python
from pdc_struct import BitFieldModel, StructModel, StructConfig, StructMode
from pdc_struct.models.bit_field import Bit
from pdc_struct.c_types import UInt8

class Permissions(BitFieldModel):
    read: bool = Bit(0)
    write: bool = Bit(1)
    execute: bool = Bit(2)

    struct_config = StructConfig(bit_width=8)

class File(StructModel):
    file_id: UInt8
    perms: Permissions  # Single byte containing 3 flags

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)
```

### Nested StructModel

StructModels can be nested for complex hierarchical data. See [Nested Structs](nested-structs.md) for details.

```python
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt16

class Point(StructModel):
    x: UInt16
    y: UInt16
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

class Rectangle(StructModel):
    top_left: Point      # Nested struct
    bottom_right: Point

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

rect = Rectangle(
    top_left=Point(x=10, y=20),
    bottom_right=Point(x=100, y=200)
)
```

## Type Handler System

PDC Struct uses a pluggable type handler system. Each supported type has a handler that knows how to:

- Generate struct format strings
- Pack Python values to binary
- Unpack binary to Python values
- Validate field configurations

### Currently Supported Types

The following type handlers are available:

| Python Type | Handler | Notes |
|-------------|---------|-------|
| `Int8`, `UInt8`, `Int16`, `UInt16` | IntHandler | Fixed-width integers |
| `float` | FloatHandler | Maps to `d` (double) |
| `bool` | BoolHandler | Maps to `?` (1 byte) |
| `str` | StringHandler | Requires length |
| `bytes` | BytesHandler | Requires length |
| `Enum`, `IntEnum` | EnumHandler | Integer-backed enums |
| `IPv4Address` | IPAddressHandler | 4-byte network address |
| `UUID` | UUIDHandler | 16-byte UUID |
| `BitFieldModel` | BitFieldHandler | Composite bit fields |
| `StructModel` | StructModelHandler | Nested structs |

## Summary

PDC Struct supports a rich set of types for binary serialization:

- **Use fixed-width integer types** (`Int8`, `UInt8`, etc.) for explicit sizing and validation
- **Strings and bytes require length specification** via `max_length` or `struct_length`
- **Enums work seamlessly** with automatic integer conversion
- **Network types** (IPv4Address, UUID) have built-in support
- **Composite types** (BitFieldModel, nested StructModel) enable complex structures

For more information:

- [Bitfields](bitfields.md) - Pack multiple flags into single bytes
- [Nested Structs](nested-structs.md) - Hierarchical struct composition
- [Optional Fields](optional-fields.md) - Making fields optional
