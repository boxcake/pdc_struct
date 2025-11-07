# PDC Struct

PDC Struct is a Pydantic extension that enables binary serialization of Pydantic models for efficient data exchange and C-compatible binary protocols. It combines Pydantic's powerful validation capabilities with Python's struct module to create a seamless bridge between high-level Python data models and low-level binary formats.

## Features

- 🔄 **Two Operating Modes**:
  - C-Compatible mode for direct interop with C structs
  - Dynamic mode for flexible Python-to-Python communication
- 🛡️ **Type Safety**: Full Pydantic validation combined with struct packing rules
- 🌍 **Cross-Platform**: Configurable endianness and alignment
- 📦 **Rich Type Support**: Integers, floats, strings, enums, UUIDs, IP addresses and more
- 🔍 **Validation**: Strong type checking and boundary validation
- 🧪 **Well-Tested**: Comprehensive test suite covering edge cases

## Installation

```bash
pip install pdc_struct
```

Or install from source:

```bash
pip install git+https://github.com/boxcake/pdc_struct.git
```

**Requirements**:
- Python 3.10+
- Pydantic 2.0+

## Quick Start

Here's an example using PDC Struct to implement ARP (Address Resolution Protocol) packet handling:

```python
from enum import IntEnum
from ipaddress import IPv4Address  
from pydantic import Field
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.c_types import UInt8, UInt16

class HardwareType(IntEnum):
    """ARP Hardware Types"""
    ETHERNET = 1
    IEEE802 = 6
    ARCNET = 7 
    FRAME_RELAY = 15
    ATM = 16

class Operation(IntEnum):
    """ARP Operation Codes"""  
    REQUEST = 1
    REPLY = 2

class ARPPacket(StructModel):
    """ARP Packet Structure (RFC 826)"""
    
    hardware_type: HardwareType = Field(
        description="Hardware type"
    )
    
    protocol_type: UInt16 = Field(
        default=0x0800,  # IPv4
        description="Protocol type (0x0800 for IPv4)" 
    )
    
    hw_addr_len: UInt8 = Field(
        default=6,  # MAC address length
        description="Hardware address length"
    )
    proto_addr_len: UInt8 = Field(  
        default=4,  # IPv4 address length
        description="Protocol address length"
    )
    
    operation: Operation = Field(
        description="Operation code"
    )
    
    sender_hw_addr: bytes = Field(
        struct_length=6, 
        description="Sender hardware address (MAC)"
    )
    sender_proto_addr: IPv4Address = Field(
        description="Sender protocol address (IPv4)"
    )
    target_hw_addr: bytes = Field(
        struct_length=6,
        description="Target hardware address (MAC)"  
    )
    target_proto_addr: IPv4Address = Field(
        description="Target protocol address (IPv4)"
    )
    
    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,  # Fixed size for network protocol  
        byte_order=ByteOrder.BIG_ENDIAN  # Network byte order
    )

# Example usage
packet = ARPPacket(
    hardware_type=HardwareType.ETHERNET,
    operation=Operation.REQUEST,  
    sender_hw_addr=b'\x00\x11"3DUf',
    sender_proto_addr=IPv4Address('192.168.1.100'),
    target_hw_addr=b'\x00\x00\x00\x00\x00\x00', 
    target_proto_addr=IPv4Address('192.168.1.1')
)
binary_data = packet.to_bytes()

# Decode received data
received = ARPPacket.from_bytes(binary_data)
print(received.dict())
```

## Core Classes

### StructModel

Base class for binary-serializable models. Define fields and configuration:

```python
class MyModel(StructModel):
    field1: int
    field2: str = Field(max_length=10)

    struct_config = StructConfig(...)
```

**Class Methods:**
- `struct_format_string() -> str`: Returns the struct format string
- `struct_size() -> int`: Returns the size in bytes of the packed structure 
- `from_bytes(data: bytes) -> StructModel`: Creates a model instance from bytes

**Instance Methods:**
- `to_bytes() -> bytes`: Converts the model instance to bytes

### StructConfig 

Configuration for struct packing/unpacking behavior.

```python
StructConfig(
    mode: StructMode = StructMode.DYNAMIC,  
    version: StructVersion = StructVersion.V1,
    byte_order: ByteOrder = ByteOrder.LITTLE_ENDIAN,
)
```

**Parameters:**
- `mode`: Determines packing mode (C_COMPATIBLE or DYNAMIC)
- `version`: Protocol version for future compatibility
- `byte_order`: Byte ordering for numeric values

## Operating Modes

### C_COMPATIBLE Mode

Designed for interoperability with C structs:

- Fixed struct size
- Optional fields require defaults
- Null-terminated strings
- No headers or metadata 

### DYNAMIC Mode  

Optimized for Python-to-Python communication:

- Variable-length structures
  - Truly optional fields (no defaults required) 
  - Efficient bitmap field tracking
  - Version headers for compatibility

## Type System

PDC Struct supports key Python types:

| Python Type | Struct Format | Size    |
|-------------|---------------|---------|
| int         | 'i'           | 4 bytes |
| float       | 'd'           | 8 bytes |
| bool        | '?'           | 1 byte  |
| str         | 's'           | Varies  | 
| bytes       | 's'           | Varies  |
| Enum        | 'i'           | 4 bytes |
| IPv4Address | '4s'          | 4 bytes |
| IPv6Address | '16s'         | 16 bytes|
| UUID        | '16s'         | 16 bytes|

Fixed-width integer types are also available:
- Int8, UInt8, Int16, UInt16

## Error Handling

PDC Struct provides specific exceptions:

- `StructPackError`: Serialization errors
  - `StructUnpackError`: Deserialization errors

## Contributing

Contributions are welcome! Please submit issues and pull requests on GitHub.

## License

PDC Struct is open source, licensed under the MIT License.
