# Enums

PDC Struct uses enumeration types to configure serialization behavior. These enums provide type-safe configuration options for [`StructConfig`](struct-config.md).

## StructMode

Defines the serialization mode, which fundamentally affects how data is packed and what features are available.

| Value | Description |
|-------|-------------|
| `C_COMPATIBLE` | Fixed-size binary format compatible with C structs |
| `DYNAMIC` | Variable-size format with header metadata for Python-to-Python use |

### C_COMPATIBLE Mode

```python
from pdc_struct import StructConfig, StructMode

struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)
```

**Characteristics:**

- No header bytes in serialized output
- Fixed struct size (determined at class definition)
- Optional fields must have default values
- Strings are null-terminated with fixed allocation
- Direct binary compatibility with C `struct` definitions

**Best for:** Embedded systems, C/C++ interop, hardware protocols, file formats with fixed layouts.

### DYNAMIC Mode

```python
struct_config = StructConfig(mode=StructMode.DYNAMIC)
```

**Characteristics:**

- 4-byte header containing version and flags
- Truly optional fields (can be `None`, not serialized when absent)
- Field presence tracked via bitmap
- More space-efficient for sparse data structures

**Best for:** Python-to-Python IPC, network protocols between Python services, flexible data serialization.

## ByteOrder

Controls the byte ordering (endianness) for multi-byte values like integers and floats.

| Value | Struct Symbol | Description |
|-------|---------------|-------------|
| `LITTLE_ENDIAN` | `<` | Least significant byte first (x86, ARM default) |
| `BIG_ENDIAN` | `>` | Most significant byte first (network byte order) |
| `NATIVE` | `=` | Use system's native byte order |

### Usage Examples

```python
from pdc_struct import StructConfig, ByteOrder

# Network protocols typically use big-endian (network byte order)
struct_config = StructConfig(byte_order=ByteOrder.BIG_ENDIAN)

# x86/x64 and most ARM systems use little-endian
struct_config = StructConfig(byte_order=ByteOrder.LITTLE_ENDIAN)

# Match current system (avoid for cross-platform code)
struct_config = StructConfig(byte_order=ByteOrder.NATIVE)
```

### Byte Order Visualization

For the integer `0x12345678`:

```
BIG_ENDIAN:    [0x12] [0x34] [0x56] [0x78]  (MSB first)
LITTLE_ENDIAN: [0x78] [0x56] [0x34] [0x12]  (LSB first)
```

!!! tip "Cross-Platform Compatibility"
    Always specify byte order explicitly when data will be exchanged between different systems. Using `NATIVE` can cause issues when data is shared across platforms.

## StructVersion

Version identifier for the serialization format, used in DYNAMIC mode headers.

| Value | Integer | Description |
|-------|---------|-------------|
| `V1` | 1 | Current version |

```python
from pdc_struct import StructConfig, StructVersion

struct_config = StructConfig(version=StructVersion.V1)
```

The version byte appears in the header of DYNAMIC mode serializations, allowing future format evolution while maintaining backward compatibility.

## HeaderFlags

Bit flags used in DYNAMIC mode headers to describe the serialized data. This is an `IntFlag` enum, allowing multiple flags to be combined.

| Flag | Value | Description |
|------|-------|-------------|
| `LITTLE_ENDIAN` | `0x00` | Data uses little-endian byte order |
| `BIG_ENDIAN` | `0x01` | Data uses big-endian byte order |
| `HAS_OPTIONAL_FIELDS` | `0x02` | Field presence bitmap follows header |

### Header Structure (DYNAMIC Mode)

```
Byte 0: Version (StructVersion value)
Byte 1: Flags (HeaderFlags combination)
Byte 2: Reserved
Byte 3: Reserved
[Optional: Field presence bitmap if HAS_OPTIONAL_FIELDS]
[Data fields]
```

### Programmatic Usage

```python
from pdc_struct.enums import HeaderFlags

# Check flags in received data
flags = data[1]
is_big_endian = bool(flags & HeaderFlags.BIG_ENDIAN)
has_optional = bool(flags & HeaderFlags.HAS_OPTIONAL_FIELDS)

# Combine flags
combined = HeaderFlags.BIG_ENDIAN | HeaderFlags.HAS_OPTIONAL_FIELDS
```

## Enum Reference

::: pdc_struct.enums.StructMode
    options:
      show_source: true

::: pdc_struct.enums.ByteOrder
    options:
      show_source: true

::: pdc_struct.enums.StructVersion
    options:
      show_source: true

::: pdc_struct.enums.HeaderFlags
    options:
      show_source: true

## See Also

- [`StructConfig`](struct-config.md) - Using enums in configuration
- [Operating Modes](../user-guide/modes.md) - Detailed mode comparison
- [Byte Order Guide](../user-guide/byte-order.md) - Understanding endianness
