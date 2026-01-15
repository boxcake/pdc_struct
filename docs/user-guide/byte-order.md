# Byte Order (Endianness)

Byte order, also called endianness, determines how multi-byte values are arranged in memory. PDC Struct supports all common byte order formats with automatic propagation to nested structures.

## What is Byte Order?

When storing a 16-bit value like `0x1234` in memory:

**Little-endian** (least significant byte first):
```
Memory:  [0x34] [0x12]
Address:  0x00   0x01
```

**Big-endian** (most significant byte first):
```
Memory:  [0x12] [0x34]
Address:  0x00   0x01
```

## Supported Byte Orders

PDC Struct provides three byte order options via the `ByteOrder` enum:

```python
from pdc_struct import ByteOrder

# Little-endian (x86, ARM in little mode)
ByteOrder.LITTLE_ENDIAN  # '<' in struct format

# Big-endian (network byte order, some ARM/MIPS)
ByteOrder.BIG_ENDIAN     # '>' in struct format

# Native (matches current platform)
ByteOrder.NATIVE         # '=' in struct format
```

## Setting Byte Order

Byte order is specified in `StructConfig`:

```python
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.c_types import UInt16, UInt32

class Packet(StructModel):
    sequence: UInt16
    timestamp: UInt32

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN  # Network byte order
    )

packet = Packet(sequence=0x1234, timestamp=0x56789ABC)
data = packet.to_bytes()

# Bytes are in big-endian order
print(data.hex())  # '123456789abc'
```

## Default Byte Order

If not specified, byte order defaults to the system's native endianness:

```python
class Example(StructModel):
    value: UInt16
    struct_config = StructConfig()  # Uses system byte order

# On x86/x64 (little-endian), defaults to LITTLE_ENDIAN
# On some ARM/MIPS (big-endian), defaults to BIG_ENDIAN
```

## Common Use Cases

### Network Protocols (Big-Endian)

Network protocols typically use big-endian (network byte order):

```python
from ipaddress import IPv4Address
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.c_types import UInt16

class UDPHeader(StructModel):
    """UDP header per RFC 768."""
    source_port: UInt16
    dest_port: UInt16
    length: UInt16
    checksum: UInt16

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN  # Network byte order
    )

header = UDPHeader(
    source_port=53,     # DNS
    dest_port=12345,
    length=100,
    checksum=0xABCD
)
```

### Little-Endian Systems

Most modern computers use little-endian:

```python
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.c_types import UInt16, UInt32

class FileHeader(StructModel):
    """Custom file format header."""
    magic: UInt16       # File type identifier
    version: UInt16
    file_size: UInt32

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN  # Most common for files
    )
```

### Platform-Native Byte Order

Use `NATIVE` when interfacing with platform-specific APIs:

```python
class SystemStruct(StructModel):
    """Matches system's native byte order."""
    flags: UInt32
    pointer: UInt32

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.NATIVE  # Matches platform
    )
```

## Byte Order Propagation

By default, byte order automatically propagates to nested structs. This ensures consistent endianness throughout the entire structure.

### Automatic Propagation (Default)

```python
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.c_types import UInt16

class Inner(StructModel):
    x: UInt16
    y: UInt16
    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN  # Inner's preference
    )

class Outer(StructModel):
    id: UInt16
    data: Inner  # Nested struct

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN,  # Override
        propagate_byte_order=True  # Default - propagates to Inner
    )

outer = Outer(id=1, data=Inner(x=2, y=3))

# Both outer and inner fields use BIG_ENDIAN
# Inner's byte_order setting is overridden
```

### Disabling Propagation

Set `propagate_byte_order=False` to let nested structs use their own byte order:

```python
class Outer(StructModel):
    id: UInt16
    data: Inner

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN,
        propagate_byte_order=False  # Each struct uses its own byte order
    )

# Outer fields: BIG_ENDIAN
# Inner fields: LITTLE_ENDIAN (from Inner's config)
```

This is useful for mixing protocols or wrapping foreign binary formats.

## Checking Byte Order

### Format String

The format string shows the byte order prefix:

```python
class Example(StructModel):
    value: UInt16
    struct_config = StructConfig(
        byte_order=ByteOrder.LITTLE_ENDIAN
    )

print(Example.struct_format_string())  # '<H' (little-endian uint16)

# Byte order prefixes:
# '<' = Little-endian
# '>' = Big-endian
# '=' = Native
```

### Runtime Detection

```python
import sys

# Check system byte order
if sys.byteorder == "little":
    print("System is little-endian")
else:
    print("System is big-endian")
```

## Examples

### Network Packet with Mixed Endianness

```python
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.c_types import UInt16, UInt32

class PayloadData(StructModel):
    """Payload uses little-endian (application data)."""
    sensor_id: UInt16
    reading: UInt32
    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN
    )

class NetworkPacket(StructModel):
    """Header uses big-endian (network order)."""
    protocol_id: UInt16
    sequence: UInt16
    payload: PayloadData

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN,
        propagate_byte_order=False  # Payload keeps its own byte order
    )

packet = NetworkPacket(
    protocol_id=0x1234,
    sequence=42,
    payload=PayloadData(sensor_id=5, reading=12345)
)

# Header fields in big-endian, payload in little-endian
```

### Cross-Platform File Format

```python
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pydantic import Field
from pdc_struct.c_types import UInt16, UInt32

class FileHeader(StructModel):
    """Always big-endian for cross-platform compatibility."""
    magic: UInt16 = 0x4D59  # 'MY' in hex
    version: UInt16
    record_count: UInt32
    name: str = Field(max_length=32)

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN  # Platform-independent
    )

# Works the same on all platforms
header = FileHeader(version=1, record_count=100, name="dataset-2025")

# Write to file
with open("data.bin", "wb") as f:
    f.write(header.to_bytes())

# Read on any platform (converts automatically)
with open("data.bin", "rb") as f:
    loaded = FileHeader.from_bytes(f.read(FileHeader.struct_size()))
```

### ARM/x86 Interoperability

```python
# C code on ARM (big-endian) writes:
# struct sensor_data {
#     uint16_t device_id;
#     uint32_t timestamp;
#     int16_t temperature;
# } __attribute__((packed));

# Python on x86 (little-endian) reads:
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.c_types import UInt16, UInt32, Int16

class SensorData(StructModel):
    device_id: UInt16
    timestamp: UInt32
    temperature: Int16

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN  # Match ARM's byte order
    )

# PDC Struct handles conversion automatically
with open("/dev/sensor", "rb") as f:
    data = f.read(SensorData.struct_size())
    sensor = SensorData.from_bytes(data)
    print(f"Temp: {sensor.temperature / 100:.1f}°C")
```

## DYNAMIC Mode and Byte Order

In DYNAMIC mode, the byte order is stored in the header:

```python
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.c_types import UInt16

class Message(StructModel):
    msg_id: UInt16
    value: UInt16

    struct_config = StructConfig(
        mode=StructMode.DYNAMIC,
        byte_order=ByteOrder.BIG_ENDIAN
    )

msg = Message(msg_id=1, value=0x1234)
data = msg.to_bytes()

# Header byte 1, bit 0 indicates endianness
# Unpacking reads the header and uses correct byte order
restored = Message.from_bytes(data)
assert restored.value == 0x1234  # Correct regardless of system
```

The header's endianness flag ensures correct unpacking even across different platforms.

## BitFields and Byte Order

BitFields respect byte order for multi-byte widths (16-bit and 32-bit):

```python
from pdc_struct import BitFieldModel, StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.models.bit_field import Bit

class Flags(BitFieldModel):
    flag0: bool = Bit(0)
    flag15: bool = Bit(15)
    struct_config = StructConfig(bit_width=16)  # 2 bytes

class Packet(StructModel):
    flags: Flags
    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN  # Affects how 16-bit flags are stored
    )
```

8-bit bitfields (1 byte) are unaffected by byte order.

## Best Practices

1. **Network protocols** → Use `ByteOrder.BIG_ENDIAN` (network byte order)
2. **Cross-platform files** → Use `ByteOrder.BIG_ENDIAN` or `ByteOrder.LITTLE_ENDIAN` explicitly
3. **Platform-specific** → Use `ByteOrder.NATIVE` when interfacing with OS APIs
4. **Mixed protocols** → Set `propagate_byte_order=False` and specify per-struct
5. **Document your choice** → Add comments explaining why you chose a specific byte order

## Common Pitfalls

### Forgetting to Set Byte Order

```python
# Bad - defaults to native, not portable
class NetworkHeader(StructModel):
    sequence: UInt16
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)
    # Byte order depends on platform!

# Good - explicit byte order
class NetworkHeader(StructModel):
    sequence: UInt16
    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN  # Explicit
    )
```

### Mixing Byte Orders Unintentionally

```python
# Problematic - nested struct has different byte order
class Inner(StructModel):
    value: UInt32
    struct_config = StructConfig(
        byte_order=ByteOrder.LITTLE_ENDIAN
    )

class Outer(StructModel):
    header: UInt32
    data: Inner
    struct_config = StructConfig(
        byte_order=ByteOrder.BIG_ENDIAN,
        propagate_byte_order=False  # Inner keeps little-endian - intended?
    )
```

## Summary

Byte order is critical for:

- **Network protocols** - Use big-endian (network byte order)
- **File formats** - Choose explicitly for cross-platform compatibility
- **Hardware interfaces** - Match device's byte order
- **Nested structs** - Use propagation for consistency

Key points:

- **Explicitly set byte order** for portability
- **Use `propagate_byte_order=True`** (default) for consistent endianness
- **Big-endian for networks**, little-endian for most files/systems
- **DYNAMIC mode stores byte order** in header for automatic handling

For more information:

- [Modes](modes.md) - How byte order works in C_COMPATIBLE vs DYNAMIC
- [Nested Structs](nested-structs.md) - Byte order propagation in nested structures
- [Types](types.md) - Which types are affected by byte order
