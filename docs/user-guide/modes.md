# Operating Modes

PDC Struct supports two distinct operating modes, each optimized for different use cases: **C_COMPATIBLE** and **DYNAMIC**.

## Quick Comparison

| Feature | C_COMPATIBLE | DYNAMIC |
|---------|-------------|---------|
| **Header** | None | 4-byte header |
| **Size** | Fixed | Variable |
| **Optional Fields** | Must have defaults, always packed | Truly optional, omitted when None |
| **Interoperability** | C/C++, network protocols, file formats | Python-to-Python |
| **Format String** | Fixed at class definition | Varies based on present fields |
| **Use Case** | Binary protocols, hardware, legacy formats | IPC, config storage, flexible serialization |

## C_COMPATIBLE Mode

### Overview

C_COMPATIBLE mode produces fixed-size binary data that exactly matches C struct layouts. This mode is ideal when you need to interface with systems that expect specific binary formats.

### Characteristics

- **No header overhead** - pure binary data
- **Fixed size** - every instance packs to the same number of bytes
- **Predictable layout** - byte-for-byte compatible with C structs
- **Optional fields** - allowed but must have defaults and are always packed

### When to Use

Choose C_COMPATIBLE mode when working with:

- **Network protocols** (TCP/IP, ARP, DNS packets)
- **Hardware interfaces** (sensor data, device communication)
- **Legacy file formats** (WAV, BMP, custom binary formats)
- **C/C++ interoperability** (shared memory, system calls)
- **Embedded systems** (fixed-size data structures)

### C Struct Padding Requirement

!!! warning "Important: C Interoperability Requires Packed Structs"
    PDC Struct produces **tightly packed** binary data with no padding bytes between fields. By default, C compilers insert padding to align struct members to word boundaries for CPU performance.

    **You must use `#pragma pack(1)` in your C code** to disable padding when exchanging data with PDC Struct:

    ```c
    // C code - REQUIRED for PDC Struct compatibility
    #pragma pack(push, 1)
    struct SensorData {
        uint8_t  device_id;
        uint32_t timestamp;   // No padding before this!
        uint16_t temperature;
    };
    #pragma pack(pop)
    ```

    Without `#pragma pack(1)`, C would insert 3 padding bytes before `timestamp`, making the struct 12 bytes instead of 7.

#### Why C Adds Padding

C compilers align struct members to their "natural" boundaries for faster memory access:

| Type | Size | Default Alignment |
|------|------|-------------------|
| `char`, `uint8_t` | 1 byte | 1-byte boundary |
| `short`, `uint16_t` | 2 bytes | 2-byte boundary |
| `int`, `uint32_t` | 4 bytes | 4-byte boundary |
| `double`, `uint64_t` | 8 bytes | 8-byte boundary (or 4 on 32-bit) |

This means a simple struct can have hidden padding:

```c
// Default C alignment - NOT compatible with PDC Struct
struct Example {
    uint8_t  a;      // offset 0, size 1
    // 3 bytes padding (to align next field to 4-byte boundary)
    uint32_t b;      // offset 4, size 4
    uint8_t  c;      // offset 8, size 1
    // 3 bytes padding (struct size rounds to largest alignment)
};  // Total: 12 bytes

// With #pragma pack(1) - compatible with PDC Struct
#pragma pack(push, 1)
struct Example {
    uint8_t  a;      // offset 0, size 1
    uint32_t b;      // offset 1, size 4
    uint8_t  c;      // offset 5, size 1
};  // Total: 6 bytes
#pragma pack(pop)
```

#### Matching Python and C Definitions

```python
# Python
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.c_types import UInt8, UInt32, UInt16

class SensorData(StructModel):
    device_id: UInt8
    timestamp: UInt32
    temperature: UInt16

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN
    )

print(SensorData.struct_size())  # 7 bytes
```

```c
// C - must match Python's packed layout
#pragma pack(push, 1)
struct SensorData {
    uint8_t  device_id;
    uint32_t timestamp;
    uint16_t temperature;
};
#pragma pack(pop)

printf("Size: %zu\n", sizeof(struct SensorData));  // 7 bytes
```

!!! note "Future Enhancement"
    Automatic struct alignment support is planned for a future release. See the [Roadmap](../roadmap.md) for details on the proposed `StructConfig(alignment=N)` feature.

### Example: Network Packet

```python
from pydantic import Field
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.c_types import UInt8, UInt16, UInt32

class TCPHeader(StructModel):
    """TCP packet header - must match RFC 793 specification exactly."""
    source_port: UInt16
    dest_port: UInt16
    sequence: UInt32
    ack_number: UInt32
    flags: UInt16
    window_size: UInt16
    checksum: UInt16
    urgent_pointer: UInt16

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN  # Network byte order
    )

# Every TCPHeader instance is exactly 20 bytes
print(f"Size: {TCPHeader.struct_size()} bytes")  # Output: Size: 20 bytes
print(f"Format: {TCPHeader.struct_format_string()}")  # Output: Format: >HHLLHHHH

# Create and pack
header = TCPHeader(
    source_port=8080,
    dest_port=443,
    sequence=12345,
    ack_number=0,
    flags=0x002,  # SYN flag
    window_size=65535,
    checksum=0,
    urgent_pointer=0
)

packet_bytes = header.to_bytes()  # Always 20 bytes
```

### Example: Sensor Data

```python
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.c_types import UInt16, Int16, UInt32

class SensorReading(StructModel):
    """IoT sensor data in fixed format for embedded system."""
    device_id: UInt16
    temperature: Int16  # Celsius * 100 (e.g., 2150 = 21.50°C)
    humidity: UInt16     # Percentage * 100
    timestamp: UInt32

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN
    )

# Reading continuous sensor data from binary file
with open('sensors.bin', 'rb') as f:
    record_size = SensorReading.struct_size()  # 12 bytes
    while data := f.read(record_size):
        reading = SensorReading.from_bytes(data)
        print(f"Device {reading.device_id}: {reading.temperature/100:.1f}°C")
```

### Optional Fields in C_COMPATIBLE Mode

Optional fields are supported but must have default values. They are **always packed** whether None or not:

```python
from typing import Optional
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt16

class Packet(StructModel):
    msg_type: UInt8
    # Optional field MUST have a default
    sequence: Optional[UInt16] = 0  # Will pack as 0 when None

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

p1 = Packet(msg_type=1, sequence=100)
p2 = Packet(msg_type=1, sequence=None)  # sequence becomes 0

print(len(p1.to_bytes()))  # 3 bytes
print(len(p2.to_bytes()))  # 3 bytes - same size!
```

!!! warning "C_COMPATIBLE Optional Behavior"
    In C_COMPATIBLE mode, Optional fields are **not truly optional** - they're always packed. Set `sequence=None` packs the default value. This ensures fixed struct size but may be counterintuitive.

## DYNAMIC Mode

### Overview

DYNAMIC mode provides flexible, self-describing binary serialization optimized for Python-to-Python communication. It supports truly optional fields that are omitted from the packed data when absent.

### Characteristics

- **4-byte header** - includes version, flags, and reserved bytes
- **Variable size** - depends on which optional fields are present
- **Field presence bitmap** - tracks which optional fields are included
- **Space efficient** - absent fields consume no space in packed data
- **Self-describing** - header contains metadata about the data

### Header Structure

```
Byte 0: Version (currently 0x01 for V1)
Byte 1: Flags
    Bit 0: Endianness (0=little, 1=big)
    Bit 1: Has optional fields (0=no, 1=yes)
    Bits 2-7: Reserved
Byte 2: Reserved
Byte 3: Reserved
```

### When to Use

Choose DYNAMIC mode when working with:

- **Inter-process communication** (Python microservices)
- **Configuration storage** (save/load app state)
- **Message queues** (flexible message formats)
- **Data persistence** (when fields may be added over time)
- **Space optimization** (when many fields are often None)

### Example: Configuration Data

```python
from typing import Optional
from pydantic import Field
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt16, UInt32

class AppConfig(StructModel):
    """Application configuration with optional features."""
    version: UInt8
    max_connections: UInt16
    timeout: UInt32
    # Optional features - only packed when present
    cache_size: Optional[UInt32] = None
    log_level: Optional[UInt8] = None

    struct_config = StructConfig(mode=StructMode.DYNAMIC)

# Minimal config - optional fields omitted
config1 = AppConfig(
    version=1,
    max_connections=100,
    timeout=3000
)
print(len(config1.to_bytes()))  # ~11 bytes (header + bitmap + 3 fields)

# Full config - all fields present
config2 = AppConfig(
    version=1,
    max_connections=100,
    timeout=3000,
    cache_size=1024,
    log_level=2
)
print(len(config2.to_bytes()))  # ~16 bytes (header + bitmap + 5 fields)
```

### Example: Message Queue

```python
from typing import Optional
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt16

class QueueMessage(StructModel):
    """Flexible message format for message queue."""
    msg_type: UInt8
    priority: UInt8
    # Optional metadata
    correlation_id: Optional[UInt16] = None
    retry_count: Optional[UInt8] = None

    struct_config = StructConfig(mode=StructMode.DYNAMIC)

# Quick message - no metadata
msg1 = QueueMessage(msg_type=1, priority=5)

# Retry message - includes retry metadata
msg2 = QueueMessage(
    msg_type=1,
    priority=5,
    correlation_id=12345,
    retry_count=2
)

# msg2 is only 4 bytes larger despite having 2 more fields
print(f"msg1: {len(msg1.to_bytes())} bytes")
print(f"msg2: {len(msg2.to_bytes())} bytes")
```

### Truly Optional Fields

Unlike C_COMPATIBLE mode, optional fields in DYNAMIC mode are **not packed when None**:

```python
from typing import Optional
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt32

class Event(StructModel):
    event_type: UInt8
    user_id: Optional[UInt32] = None  # Truly optional

    struct_config = StructConfig(mode=StructMode.DYNAMIC)

# Without user_id
e1 = Event(event_type=1)
data1 = e1.to_bytes()

# With user_id
e2 = Event(event_type=1, user_id=12345)
data2 = e2.to_bytes()

print(len(data1))  # Smaller - user_id not packed
print(len(data2))  # Larger - user_id included

# Roundtrip preserves None
decoded1 = Event.from_bytes(data1)
assert decoded1.user_id is None  # ✓ None preserved
```

## Choosing the Right Mode

### Use C_COMPATIBLE when you need:

✅ **Exact binary format** - matching a specification
✅ **Fixed size** - predictable memory/bandwidth usage
✅ **C interoperability** - talking to C/C++ code
✅ **No overhead** - every byte counts
✅ **Legacy compatibility** - existing file formats

### Use DYNAMIC when you need:

✅ **Flexibility** - fields that may be present or absent
✅ **Space efficiency** - save bandwidth when fields are None
✅ **Python-to-Python** - no external format constraints
✅ **Versioning** - header tracks format version
✅ **Self-describing data** - metadata in the header

## Advanced: Nested Structs and Byte Order

Both modes support nested `StructModel` instances and automatic byte order propagation:

```python
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.c_types import UInt16, UInt32

class Point(StructModel):
    x: UInt16
    y: UInt16
    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN
    )

class Shape(StructModel):
    shape_id: UInt32
    origin: Point  # Nested struct inherits parent's byte order

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN,
        propagate_byte_order=True  # Default - Point uses BIG_ENDIAN
    )
```

When `propagate_byte_order=True` (default), nested structs automatically use the parent's byte order, ensuring consistent endianness throughout the packed data.

## Performance Considerations

### C_COMPATIBLE Mode
- **Packing**: Very fast - single `struct.pack()` call
- **Unpacking**: Very fast - single `struct.unpack()` call
- **Memory**: Minimal - no header overhead
- **Best for**: High-throughput scenarios, tight loops

### DYNAMIC Mode
- **Packing**: Slightly slower - header creation + bitmap calculation
- **Unpacking**: Slightly slower - header parsing + bitmap processing
- **Memory**: 4+ bytes overhead per instance
- **Best for**: Flexibility over raw speed

The performance difference is negligible for most use cases. Choose based on your requirements, not performance.

## Summary

- **C_COMPATIBLE**: Fixed-size, C-compatible, no header, for binary protocols and interoperability
- **DYNAMIC**: Variable-size, self-describing, with header, for flexible Python serialization

Both modes are first-class citizens in PDC Struct. Pick the mode that matches your use case, and the library handles the rest.
