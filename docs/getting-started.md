# Quick Start

Get started with PDC Struct in minutes.

## Basic Example

```python
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt16

class SimplePacket(StructModel):
    msg_id: UInt8
    value: UInt16
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# Create instance
packet = SimplePacket(msg_id=1, value=1000)

# Pack to bytes
data = packet.to_bytes()
print(data.hex())  # 01e803

# Unpack from bytes
restored = SimplePacket.from_bytes(data)
print(f"Message ID: {restored.msg_id}, Value: {restored.value}")
```

## Next: Learn About Operating Modes

See [Operating Modes](user-guide/modes.md) to understand C_COMPATIBLE vs DYNAMIC modes.
