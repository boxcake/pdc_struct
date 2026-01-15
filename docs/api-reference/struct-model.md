# StructModel

`StructModel` is the primary base class for creating binary-serializable data structures. It extends Pydantic's `BaseModel` to provide seamless conversion between Python objects and packed binary data.

## Overview

Use `StructModel` when you need to:

- Serialize Python objects to binary format for network protocols, file formats, or IPC
- Deserialize binary data back into validated Python objects
- Interface with C programs or libraries expecting specific struct layouts
- Define data structures that can work in both dynamic (Python-to-Python) and C-compatible modes

## Quick Example

```python
from pydantic import Field
from pdc_struct import StructModel, StructConfig, ByteOrder, StructMode

class Point(StructModel):
    x: float = Field(description="X coordinate")
    y: float = Field(description="Y coordinate")

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN
    )

# Create and serialize
point = Point(x=1.5, y=2.5)
data = point.to_bytes()  # Pack to binary

# Deserialize
restored = Point.from_bytes(data)
assert restored.x == 1.5
```

## Operating Modes

`StructModel` supports two operating modes configured via [`StructConfig`](struct-config.md):

| Mode | Description | Use Case |
|------|-------------|----------|
| `C_COMPATIBLE` | Fixed-size structs without headers | C interop, embedded systems |
| `DYNAMIC` | Variable-size with header metadata | Python-to-Python communication |

See the [Operating Modes](../user-guide/modes.md) guide for detailed information.

## Supported Field Types

`StructModel` automatically handles these Python types:

- **Numeric**: `int`, `float`, `bool`, [`Int8`](types.md#pdc_struct.c_types.Int8), [`UInt8`](types.md#pdc_struct.c_types.UInt8), [`Int16`](types.md#pdc_struct.c_types.Int16), [`UInt16`](types.md#pdc_struct.c_types.UInt16)
- **Text/Binary**: `str` (with `max_length`), `bytes` (with `max_length`)
- **Network**: `ipaddress.IPv4Address`
- **Identifiers**: `uuid.UUID`
- **Enums**: `Enum`, `IntEnum`
- **Nested**: Other `StructModel` or [`BitFieldModel`](bitfield-model.md) instances

## Class Reference

::: pdc_struct.StructModel
    options:
      show_source: true
      members:
        - struct_config
        - clone
        - struct_format_string
        - struct_size
        - to_bytes
        - from_bytes
        - get_struct_format

## See Also

- [`StructConfig`](struct-config.md) - Configuration options for struct behavior
- [`BitFieldModel`](bitfield-model.md) - For bit-packed fields within structs
- [Type System](../user-guide/types.md) - Detailed guide on supported types
