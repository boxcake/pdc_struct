# Exceptions

PDC Struct defines specific exception types for serialization errors. These exceptions provide clear feedback when packing or unpacking operations fail.

## Overview

| Exception | Raised During | Common Causes |
|-----------|---------------|---------------|
| `StructPackError` | `to_bytes()` | Value out of range, type mismatch, buffer overflow |
| `StructUnpackError` | `from_bytes()` | Truncated data, invalid header, version mismatch |

Both exceptions inherit from Python's built-in `Exception` class.

## StructPackError

Raised when converting a model instance to bytes fails.

### Common Causes

**Value Out of Range**
```python
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8

class Packet(StructModel):
    value: UInt8
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# This will raise StructPackError (via Pydantic validation)
packet = Packet(value=256)  # UInt8 max is 255
```

**String Too Long**
```python
from pydantic import Field

class Message(StructModel):
    text: str = Field(json_schema_extra={"max_length": 10})
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

msg = Message(text="This string is way too long")
msg.to_bytes()  # StructPackError: string exceeds max_length
```

**Type Mismatch**
```python
class Data(StructModel):
    count: int
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# Pydantic handles type coercion, but incompatible types fail
data = Data(count="not a number")  # ValidationError from Pydantic
```

### Handling StructPackError

```python
from pdc_struct import StructPackError

try:
    binary_data = my_model.to_bytes()
except StructPackError as e:
    print(f"Failed to serialize: {e}")
    # Handle error - log, return error response, etc.
```

## StructUnpackError

Raised when creating a model instance from bytes fails.

### Common Causes

**Truncated Data**
```python
from pdc_struct import StructUnpackError

class Packet(StructModel):
    x: float  # 8 bytes
    y: float  # 8 bytes
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# Only 10 bytes provided, but struct needs 16
try:
    packet = Packet.from_bytes(b'\x00' * 10)
except StructUnpackError as e:
    print(f"Data too short: {e}")
```

**Invalid Header (DYNAMIC Mode)**
```python
class DynamicPacket(StructModel):
    value: int
    struct_config = StructConfig(mode=StructMode.DYNAMIC)

# Corrupted or invalid header bytes
try:
    packet = DynamicPacket.from_bytes(b'\xff\xff\xff\xff')
except StructUnpackError as e:
    print(f"Invalid header: {e}")
```

**Version Mismatch**
```python
# Data was serialized with a different version than expected
try:
    packet = DynamicPacket.from_bytes(data_from_future_version)
except StructUnpackError as e:
    print(f"Version mismatch: {e}")
```

### Handling StructUnpackError

```python
from pdc_struct import StructUnpackError

def parse_packet(data: bytes) -> Optional[Packet]:
    try:
        return Packet.from_bytes(data)
    except StructUnpackError as e:
        logger.error(f"Failed to parse packet: {e}")
        return None
```

## Best Practices

### Validate Before Packing

Use Pydantic's validation to catch issues early:

```python
from pydantic import ValidationError

try:
    packet = Packet(value=invalid_value)
except ValidationError as e:
    # Handle validation error before attempting to_bytes()
    print(e.errors())
```

### Defensive Unpacking

Always handle potential errors when deserializing untrusted data:

```python
from pdc_struct import StructUnpackError

def handle_network_data(data: bytes):
    if len(data) < Packet.struct_size():
        raise ValueError("Packet too small")

    try:
        packet = Packet.from_bytes(data)
    except StructUnpackError:
        raise ValueError("Malformed packet")

    return packet
```

### Logging and Debugging

Include context when catching exceptions:

```python
import logging

logger = logging.getLogger(__name__)

try:
    packet = Packet.from_bytes(data)
except StructUnpackError as e:
    logger.error(
        "Failed to unpack packet",
        extra={
            "error": str(e),
            "data_length": len(data),
            "data_hex": data[:32].hex(),  # First 32 bytes
        }
    )
    raise
```

## Exception Reference

::: pdc_struct.StructPackError
    options:
      show_source: true

::: pdc_struct.StructUnpackError
    options:
      show_source: true

## See Also

- [`StructModel.to_bytes()`](struct-model.md) - Method that raises `StructPackError`
- [`StructModel.from_bytes()`](struct-model.md) - Method that raises `StructUnpackError`
