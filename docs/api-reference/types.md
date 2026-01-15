# Type System

PDC Struct provides fixed-width integer types that ensure precise control over binary serialization. These types guarantee specific byte sizes regardless of platform, making them essential for C interoperability and cross-platform protocols.

## Overview

While Python's built-in `int` type has arbitrary precision, binary protocols and C structs require fixed-width integers. PDC Struct provides these types with built-in validation:

| Type | Size | Range | Struct Format |
|------|------|-------|---------------|
| `Int8` | 1 byte | -128 to 127 | `b` |
| `UInt8` | 1 byte | 0 to 255 | `B` |
| `Int16` | 2 bytes | -32,768 to 32,767 | `h` |
| `UInt16` | 2 bytes | 0 to 65,535 | `H` |

## Usage

### In StructModel Fields

```python
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import Int8, UInt8, Int16, UInt16

class SensorReading(StructModel):
    sensor_id: UInt8          # 0-255
    temperature: Int16        # -32768 to 32767 (e.g., hundredths of degrees)
    humidity: UInt8           # 0-255 (percentage)
    status_code: Int8         # -128 to 127

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# Values are validated on creation
reading = SensorReading(
    sensor_id=42,
    temperature=-1050,  # -10.50 degrees
    humidity=65,
    status_code=-1
)
```

### Direct Instantiation

These types can be used directly and behave like regular integers:

```python
from pdc_struct.c_types import UInt8, Int16

# Create instances
value = UInt8(255)
temp = Int16(-1000)

# Standard integer operations work
result = value + 1  # Returns regular int (256)
doubled = Int16(temp * 2)  # Wrap back in Int16 for validation

# Validation on creation
try:
    bad_value = UInt8(256)  # Raises ValueError
except ValueError as e:
    print(e)  # "UInt8 value must be between 0 and 255"
```

### Comparison with Plain int

When you use plain `int` in a [`StructModel`](struct-model.md), it serializes as a platform-dependent long integer (typically 8 bytes on 64-bit systems). Fixed-width types give you explicit control:

```python
class WithPlainInt(StructModel):
    value: int  # 8 bytes (platform-dependent)

class WithFixedWidth(StructModel):
    value: UInt16  # Always exactly 2 bytes
```

## Validation Behavior

All fixed-width types validate their values at construction time:

```python
from pdc_struct.c_types import Int8, UInt8

# Range validation
UInt8(-1)    # ValueError: UInt8 value must be between 0 and 255
Int8(128)    # ValueError: Int8 value must be between -128 and 127

# Type validation
UInt8("10")  # TypeError: UInt8 requires an integer value
Int16(3.14)  # TypeError: Int16 requires an integer value
```

Pydantic will also validate these types when used as model fields, providing detailed error messages.

## C Equivalent Types

These types correspond to standard C integer types:

| PDC Struct | C Type | stdint.h |
|------------|--------|----------|
| `Int8` | `signed char` | `int8_t` |
| `UInt8` | `unsigned char` | `uint8_t` |
| `Int16` | `short` | `int16_t` |
| `UInt16` | `unsigned short` | `uint16_t` |

## Other Supported Types

Beyond fixed-width integers, [`StructModel`](struct-model.md) supports these Python types automatically:

| Python Type | Serialization | Notes |
|-------------|---------------|-------|
| `int` | 8-byte signed | Platform long |
| `float` | 8-byte double | IEEE 754 |
| `bool` | 1 byte | 0 or 1 |
| `str` | Null-terminated | Requires `max_length` |
| `bytes` | Fixed-length | Requires `max_length` |
| `Enum` / `IntEnum` | Varies | Based on value type |
| `IPv4Address` | 4 bytes | Network byte order |
| `UUID` | 16 bytes | Binary format |
| `StructModel` | Nested | Recursive packing |
| `BitFieldModel` | 1/2/4 bytes | Based on bit_width |

## Class Reference

::: pdc_struct.c_types.Int8
    options:
      show_source: true

::: pdc_struct.c_types.UInt8
    options:
      show_source: true

::: pdc_struct.c_types.Int16
    options:
      show_source: true

::: pdc_struct.c_types.UInt16
    options:
      show_source: true

## See Also

- [`StructModel`](struct-model.md) - Using types in struct definitions
- [Type System Guide](../user-guide/types.md) - Detailed type usage patterns
- [C Interoperability](../examples/c-interop.md) - Working with C code
