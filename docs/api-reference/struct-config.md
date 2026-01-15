# StructConfig

`StructConfig` controls how [`StructModel`](struct-model.md) and [`BitFieldModel`](bitfield-model.md) classes pack and unpack binary data. Every model class can have its own independent configuration.

## Overview

Configuration is set by creating a `StructConfig` instance as a class variable:

```python
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder

class MyPacket(StructModel):
    # ... fields ...

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN
    )
```

## Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | [`StructMode`](enums.md#pdc_struct.enums.StructMode) | `DYNAMIC` | Serialization mode (C-compatible or dynamic) |
| `version` | [`StructVersion`](enums.md#pdc_struct.enums.StructVersion) | `V1` | Protocol version for dynamic mode headers |
| `byte_order` | [`ByteOrder`](enums.md#pdc_struct.enums.ByteOrder) | System default | Endianness for multi-byte values |
| `bit_width` | `int` | `None` | Bit width for BitFieldModel (8, 16, or 32) |
| `propagate_byte_order` | `bool` | `True` | Apply byte order to nested structs |
| `metadata` | `dict` | `{}` | Custom metadata for application use |

## Mode Selection Guide

### C_COMPATIBLE Mode

Use when interfacing with C code or requiring fixed-size binary layouts:

```python
struct_config = StructConfig(
    mode=StructMode.C_COMPATIBLE,
    byte_order=ByteOrder.LITTLE_ENDIAN
)
```

**Characteristics:**

- No header bytes in output
- Fixed struct size
- Optional fields must have defaults
- Strings are null-terminated, fixed-length

### DYNAMIC Mode

Use for Python-to-Python communication with flexibility:

```python
struct_config = StructConfig(
    mode=StructMode.DYNAMIC,
    byte_order=ByteOrder.BIG_ENDIAN
)
```

**Characteristics:**

- 4-byte header with version and flags
- Supports truly optional fields (can be `None`)
- Field presence tracked via bitmap
- More space-efficient for sparse data

## Byte Order

The `byte_order` parameter controls how multi-byte values (integers, floats) are serialized:

```python
from pdc_struct import ByteOrder

# Network protocols typically use big-endian
struct_config = StructConfig(byte_order=ByteOrder.BIG_ENDIAN)

# x86/x64 systems use little-endian
struct_config = StructConfig(byte_order=ByteOrder.LITTLE_ENDIAN)

# Match current system (not recommended for cross-platform)
struct_config = StructConfig(byte_order=ByteOrder.NATIVE)
```

!!! tip "Default Byte Order"
    If not specified, `byte_order` defaults to the system's native byte order. For cross-platform compatibility, always specify byte order explicitly.

## BitFieldModel Configuration

For [`BitFieldModel`](bitfield-model.md) classes, you must specify `bit_width`:

```python
from pdc_struct import BitFieldModel, StructConfig, StructMode

class StatusFlags(BitFieldModel):
    ready: bool = Bit(0)
    error: bool = Bit(1)

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        bit_width=8  # Pack into a single byte
    )
```

Valid values for `bit_width`: `8`, `16`, or `32`

## Class Reference

::: pdc_struct.StructConfig
    options:
      show_source: true

## See Also

- [`StructModel`](struct-model.md) - Main model class using this configuration
- [`BitFieldModel`](bitfield-model.md) - Bit-packed fields configuration
- [Operating Modes](../user-guide/modes.md) - Detailed mode comparison
- [Byte Order Guide](../user-guide/byte-order.md) - Endianness explained
