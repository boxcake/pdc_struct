# BitFieldModel

`BitFieldModel` enables packing multiple boolean or small integer values into a single byte, word, or double-word. This is essential for C-compatible bit flags and space-efficient binary protocols.

## Overview

Use `BitFieldModel` when you need to:

- Map individual bits to meaningful boolean flags
- Pack small integers into bit ranges within a byte/word
- Interface with C bit fields or hardware registers
- Create compact flag structures for network protocols

## Quick Example

```python
from pdc_struct import BitFieldModel, Bit, StructConfig, StructMode

class FilePermissions(BitFieldModel):
    read: bool = Bit(0)      # Bit 0
    write: bool = Bit(1)     # Bit 1
    execute: bool = Bit(2)   # Bit 2

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        bit_width=8
    )

# Create with individual flags
perms = FilePermissions(read=True, write=True, execute=False)
print(perms.packed_value)  # 3 (binary: 00000011)

# Create from packed value
perms = FilePermissions(packed_value=7)  # binary: 00000111
print(perms.read, perms.write, perms.execute)  # True True True
```

## The Bit() Function

`Bit()` defines where a field maps within the packed integer:

### Single-Bit Fields (Boolean)

```python
class Flags(BitFieldModel):
    active: bool = Bit(0)    # Single bit at position 0
    ready: bool = Bit(1)     # Single bit at position 1
    error: bool = Bit(7)     # Single bit at position 7
```

### Multi-Bit Fields (Integer)

For values that span multiple bits, list all bit positions:

```python
class StatusRegister(BitFieldModel):
    # 3-bit priority field using bits 0, 1, 2 (values 0-7)
    priority: int = Bit(0, 1, 2)

    # 4-bit error code using bits 4, 5, 6, 7 (values 0-15)
    error_code: int = Bit(4, 5, 6, 7)

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        bit_width=8
    )
```

!!! warning "Contiguous Bits Required"
    Bit positions must be contiguous. `Bit(0, 1, 3)` will raise a `ValueError` because bit 2 is missing.

## Bit Width

The `bit_width` in [`StructConfig`](struct-config.md) determines the packed size:

| bit_width | Packed Size | Max Bits | Struct Format |
|-----------|-------------|----------|---------------|
| 8 | 1 byte | 0-7 | `B` (unsigned char) |
| 16 | 2 bytes | 0-15 | `H` (unsigned short) |
| 32 | 4 bytes | 0-31 | `I` (unsigned int) |

```python
class WideFlags(BitFieldModel):
    # Can use bits 0-31 with bit_width=32
    low_byte: int = Bit(0, 1, 2, 3, 4, 5, 6, 7)
    high_bits: int = Bit(24, 25, 26, 27, 28, 29, 30, 31)

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        bit_width=32
    )
```

## Working with Packed Values

### The packed_value Property

Get or set the entire packed integer representation:

```python
flags = FilePermissions(read=True, write=False, execute=True)

# Read packed value
value = flags.packed_value  # 5 (binary: 101)

# Set packed value (updates all fields)
flags.packed_value = 3  # Sets read=True, write=True, execute=False
```

### Initializing from Bytes

Pass raw bytes to unpack into fields:

```python
# From a single byte
flags = FilePermissions(packed_value=b'\x07')

# From network data (16-bit example)
class NetworkFlags(BitFieldModel):
    syn: bool = Bit(0)
    ack: bool = Bit(1)
    fin: bool = Bit(2)

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        bit_width=16,
        byte_order=ByteOrder.BIG_ENDIAN
    )

flags = NetworkFlags(packed_value=b'\x00\x03')  # SYN and ACK set
```

## Embedding in StructModel

`BitFieldModel` instances can be nested within [`StructModel`](struct-model.md):

```python
class Packet(StructModel):
    flags: FilePermissions  # Embedded bit field
    data: bytes = Field(json_schema_extra={"max_length": 64})

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN
    )

# The flags field packs as a single byte within the struct
packet = Packet(
    flags=FilePermissions(read=True, write=True),
    data=b"hello"
)
binary = packet.to_bytes()
```

## Class Reference

### Bit Function

::: pdc_struct.Bit
    options:
      show_source: true

### BitFieldModel Class

::: pdc_struct.BitFieldModel
    options:
      show_source: true
      members:
        - struct_config
        - packed_value
        - struct_format_string
        - clone

## See Also

- [`StructConfig`](struct-config.md) - Configuration including `bit_width`
- [`StructModel`](struct-model.md) - Embedding bit fields in structs
- [BitFields Guide](../user-guide/bitfields.md) - Detailed usage patterns
