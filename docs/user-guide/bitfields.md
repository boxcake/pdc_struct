# Bitfields

Bitfields allow you to pack multiple boolean flags or small integer values into a single byte, word, or dword. This is essential for space-efficient binary formats and C struct compatibility.

## Why Use Bitfields?

Traditional approach with separate booleans:
```python
class Flags(StructModel):
    read: bool       # 1 byte
    write: bool      # 1 byte
    execute: bool    # 1 byte
    # Total: 3 bytes for 3 flags
```

With bitfields:
```python
class Flags(BitFieldModel):
    read: bool = Bit(0)
    write: bool = Bit(1)
    execute: bool = Bit(2)
    struct_config = StructConfig(bit_width=8)
    # Total: 1 byte for 3 flags (5 bits unused)
```

**Benefits:**
- **Space efficient** - Multiple flags in single byte/word/dword
- **C compatible** - Matches C bitfield layouts
- **Type safe** - Pydantic validation for each field
- **Readable** - Named fields instead of bit manipulation

## Basic Usage

### Creating a BitFieldModel

```python
from pdc_struct import BitFieldModel, StructConfig
from pdc_struct.models.bit_field import Bit

class FilePermissions(BitFieldModel):
    read: bool = Bit(0)      # Bit 0
    write: bool = Bit(1)     # Bit 1
    execute: bool = Bit(2)   # Bit 2

    struct_config = StructConfig(bit_width=8)  # 8, 16, or 32

# Create instance
perms = FilePermissions(read=True, write=True, execute=False)

# Access fields
print(perms.read)    # True
print(perms.write)   # True
print(perms.execute) # False

# Get packed value
print(bin(perms.packed_value))  # 0b11 (bits 0 and 1 set)
```

### Bit Width

BitFieldModels must specify a bit width: **8**, **16**, or **32** bits.

```python
# 8-bit (1 byte) - most common
class Flags8(BitFieldModel):
    flag0: bool = Bit(0)
    flag1: bool = Bit(1)
    struct_config = StructConfig(bit_width=8)

# 16-bit (2 bytes) - for more flags
class Flags16(BitFieldModel):
    flag0: bool = Bit(0)
    # ... up to Bit(15)
    flag15: bool = Bit(15)
    struct_config = StructConfig(bit_width=16)

# 32-bit (4 bytes) - maximum flags
class Flags32(BitFieldModel):
    flag0: bool = Bit(0)
    # ... up to Bit(31)
    flag31: bool = Bit(31)
    struct_config = StructConfig(bit_width=32)
```

## Multi-Bit Fields

You can pack small integers into bit ranges using multiple bit positions:

```python
from pdc_struct import BitFieldModel, StructConfig
from pdc_struct.models.bit_field import Bit

class Status(BitFieldModel):
    # Boolean flags
    enabled: bool = Bit(0)
    error: bool = Bit(1)

    # 3-bit integer (0-7) using bits 2, 3, 4
    priority: int = Bit(2, 3, 4)

    # 2-bit integer (0-3) using bits 5, 6
    state: int = Bit(5, 6)

    struct_config = StructConfig(bit_width=8)

# Create with integer values
status = Status(
    enabled=True,
    error=False,
    priority=5,  # 0-7 (3 bits)
    state=2      # 0-3 (2 bits)
)

print(f"Priority: {status.priority}")  # 5
print(f"State: {status.state}")        # 2
print(bin(status.packed_value))        # 0b01010101
```

### Multi-Bit Field Rules

- **Contiguous bits** - Bit positions must be adjacent (e.g., 2, 3, 4)
- **Value range** - For N bits, values must be 0 to 2^N - 1
- **Validation** - Out-of-range values raise ValueError

```python
class Config(BitFieldModel):
    # 4-bit field: values 0-15
    level: int = Bit(0, 1, 2, 3)
    struct_config = StructConfig(bit_width=8)

# Valid
cfg = Config(level=15)  # OK

# Invalid - out of range
try:
    cfg = Config(level=16)  # Error: 16 > 15 (max for 4 bits)
except ValueError as e:
    print(f"Validation error: {e}")
```

## Using BitFields in StructModel

BitFields integrate seamlessly with StructModels:

```python
from pdc_struct import StructModel, BitFieldModel, StructConfig, StructMode
from pdc_struct.models.bit_field import Bit
from pdc_struct.c_types import UInt16

class TCPFlags(BitFieldModel):
    """TCP header flags (8 bits)."""
    fin: bool = Bit(0)
    syn: bool = Bit(1)
    rst: bool = Bit(2)
    psh: bool = Bit(3)
    ack: bool = Bit(4)
    urg: bool = Bit(5)

    struct_config = StructConfig(bit_width=8)

class TCPHeader(StructModel):
    """Simplified TCP header."""
    source_port: UInt16
    dest_port: UInt16
    sequence: UInt16
    flags: TCPFlags  # BitField packed as single byte

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# Create packet
packet = TCPHeader(
    source_port=8080,
    dest_port=443,
    sequence=12345,
    flags=TCPFlags(syn=True, ack=False, fin=False)
)

# Pack to bytes
data = packet.to_bytes()
print(len(data))  # 7 bytes: 2 + 2 + 2 + 1

# Unpack preserves bitfield structure
restored = TCPHeader.from_bytes(data)
print(restored.flags.syn)  # True
print(restored.flags.ack)  # False
```

## Working with Packed Values

### Reading Packed Value

```python
flags = FilePermissions(read=True, write=False, execute=True)
value = flags.packed_value
print(f"Packed: 0x{value:02x}")  # 0x05 (bits 0 and 2 set)
print(f"Binary: {bin(value)}")    # 0b101
```

### Setting Packed Value

```python
# Create from packed value
flags = FilePermissions(packed_value=0x07)  # All 3 bits set
print(flags.read)    # True
print(flags.write)   # True
print(flags.execute) # True

# Modify via packed_value property
flags.packed_value = 0x02  # Only bit 1 set
print(flags.read)    # False
print(flags.write)   # True
print(flags.execute) # False
```

### From Bytes

```python
# Create from bytes (useful when unpacking from binary data)
raw_bytes = b'\x05'  # Binary data
flags = FilePermissions(packed_value=raw_bytes)
print(flags.read)    # True (bit 0)
print(flags.execute) # True (bit 2)
```

## Bit Numbering

Bits are numbered from **0** (least significant) to **N-1** (most significant):

```
8-bit example: 0b11010110
               ││││││││
Bit positions: 76543210

Bit 0 (LSB): 0
Bit 1: 1
Bit 2: 1
Bit 3: 0
...
Bit 7 (MSB): 1
```

```python
class Example(BitFieldModel):
    bit0: bool = Bit(0)  # Least significant bit (rightmost)
    bit7: bool = Bit(7)  # Most significant bit (leftmost in 8-bit)
    struct_config = StructConfig(bit_width=8)

ex = Example(bit0=True, bit7=True)
print(bin(ex.packed_value))  # 0b10000001 (bits 0 and 7 set)
```

## Optional BitFields

BitFields work with Optional in both C_COMPATIBLE and DYNAMIC modes:

### C_COMPATIBLE Mode

```python
from typing import Optional
from pdc_struct import StructModel, BitFieldModel, StructConfig, StructMode
from pdc_struct.models.bit_field import Bit
from pdc_struct.c_types import UInt8

class Flags(BitFieldModel):
    read: bool = Bit(0)
    write: bool = Bit(1)
    struct_config = StructConfig(bit_width=8)

class Packet(StructModel):
    msg_type: UInt8
    flags: Optional[Flags] = Flags()  # Must have default in C_COMPATIBLE

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# With flags
p1 = Packet(msg_type=1, flags=Flags(read=True, write=False))

# Without flags (uses default)
p2 = Packet(msg_type=1)  # flags=Flags(read=False, write=False)

# Both pack to same size
print(len(p1.to_bytes()))  # 2 bytes
print(len(p2.to_bytes()))  # 2 bytes
```

### DYNAMIC Mode

```python
class Packet(StructModel):
    msg_type: UInt8
    flags: Optional[Flags] = None  # Truly optional

    struct_config = StructConfig(mode=StructMode.DYNAMIC)

# With flags
p1 = Packet(msg_type=1, flags=Flags(read=True))
data1 = p1.to_bytes()

# Without flags
p2 = Packet(msg_type=1, flags=None)
data2 = p2.to_bytes()

# Different sizes!
print(len(data1))  # Larger (includes flags)
print(len(data2))  # Smaller (flags omitted)

# Roundtrip preserves None
restored = Packet.from_bytes(data2)
assert restored.flags is None
```

## Common Patterns

### File Permissions (Unix-style)

```python
class UnixPermissions(BitFieldModel):
    """Unix file permissions (9 bits)."""
    # Owner
    owner_read: bool = Bit(0)
    owner_write: bool = Bit(1)
    owner_execute: bool = Bit(2)

    # Group
    group_read: bool = Bit(3)
    group_write: bool = Bit(4)
    group_execute: bool = Bit(5)

    # Others
    other_read: bool = Bit(6)
    other_write: bool = Bit(7)
    other_execute: bool = Bit(8)

    struct_config = StructConfig(bit_width=16)  # 9 bits needs 16-bit width

# chmod 755 = rwxr-xr-x
perms = UnixPermissions(
    owner_read=True, owner_write=True, owner_execute=True,
    group_read=True, group_write=False, group_execute=True,
    other_read=True, other_write=False, other_execute=True
)
print(f"0o{perms.packed_value:o}")  # 0o755
```

### Device Control Register

```python
class DeviceControl(BitFieldModel):
    """Hardware device control register (16 bits)."""
    enable: bool = Bit(0)
    reset: bool = Bit(1)
    interrupt_enable: bool = Bit(2)

    mode: int = Bit(3, 4, 5)  # 3 bits: 0-7 for mode

    baudrate: int = Bit(6, 7, 8, 9)  # 4 bits: 0-15 for rate

    parity: int = Bit(10, 11)  # 2 bits: 0=none, 1=odd, 2=even

    struct_config = StructConfig(bit_width=16)

control = DeviceControl(
    enable=True,
    reset=False,
    interrupt_enable=True,
    mode=3,
    baudrate=9,
    parity=2
)
```

### Status Register with Reserved Bits

```python
class Status(BitFieldModel):
    """Device status with reserved bits."""
    ready: bool = Bit(0)
    busy: bool = Bit(1)
    error: bool = Bit(2)
    # Bits 3-5 reserved (leave undefined)
    overflow: bool = Bit(6)
    underflow: bool = Bit(7)

    struct_config = StructConfig(bit_width=8)

# Reserved bits remain 0
status = Status(ready=True, busy=False, error=False,
                overflow=False, underflow=False)
```

## Cloning BitFields

The `clone()` method creates a copy with selective updates:

```python
flags = FilePermissions(read=True, write=False, execute=True)

# Clone with modifications
new_flags = flags.clone(write=True)

print(flags.write)      # False (original unchanged)
print(new_flags.write)  # True (clone modified)
print(new_flags.read)   # True (copied from original)
```

## Validation

BitFieldModels validate at creation:

```python
class Config(BitFieldModel):
    level: int = Bit(0, 1, 2)  # 3 bits: 0-7
    struct_config = StructConfig(bit_width=8)

# Valid
c1 = Config(level=5)  # OK: 5 is in range 0-7

# Invalid - out of range
try:
    c2 = Config(level=8)  # Error: 8 > 7 (max for 3 bits)
except ValueError:
    print("Out of range!")

# Invalid - wrong type
try:
    c3 = Config(level=True)  # Error: bool not allowed for int field
except ValueError:
    print("Wrong type!")
```

## Byte Order

BitFields respect the struct_config byte order when used in StructModels:

```python
from pdc_struct import ByteOrder

class Flags(BitFieldModel):
    flag0: bool = Bit(0)
    flag1: bool = Bit(1)
    struct_config = StructConfig(bit_width=16)

class Packet(StructModel):
    flags: Flags
    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN  # Affects byte order of 16-bit flags
    )
```

## Best Practices

1. **Use descriptive names** - `is_valid` not `flag3`
2. **Document bit positions** - Add comments for hardware registers
3. **Group related flags** - One BitFieldModel per logical register
4. **Match hardware specs** - Use same bit numbering as datasheets
5. **Use appropriate width** - 8 bits for most cases, 16/32 when needed
6. **Validate ranges** - Test boundary conditions for multi-bit fields

## Limitations

- **Bit width must be 8, 16, or 32** - No arbitrary widths
- **Bits must be contiguous** - Multi-bit fields can't have gaps
- **No bit reuse** - Each bit can only be assigned once
- **No dynamic bit positions** - Positions must be compile-time constants

## Summary

BitFieldModels provide space-efficient binary encoding:

- **Pack multiple flags** into single bytes
- **Define multi-bit integer fields** for small value ranges
- **Integrate seamlessly** with StructModel
- **Type-safe** with Pydantic validation
- **C-compatible** for hardware/protocol work

For more information:

- [Types](types.md) - Other supported types
- [Nested Structs](nested-structs.md) - Composing complex structures
- [Modes](modes.md) - C_COMPATIBLE vs DYNAMIC behavior
