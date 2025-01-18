# PDC Struct

PDC Struct is a Pydantic extension that enables binary serialization of Pydantic models for efficient data exchange and C-compatible binary protocols. It combines Pydantic's powerful validation capabilities with Python's struct module to create a seamless bridge between high-level Python data models and low-level binary formats.

## Features

- 🔄 **Two Operating Modes**:
  - C-Compatible mode for direct interop with C structs
  - Dynamic mode for flexible Python-to-Python communication
- 🛡️ **Type Safety**: Full Pydantic validation combined with struct packing rules
- 🌍 **Cross-Platform**: Configurable endianness and alignment
- 📦 **Rich Type Support**: Integers, floats, strings, enums, UUIDs, IP addresses and more
- ↔️ **Optional Fields**: Efficient handling of optional data using bitmap tracking
- 🔍 **Validation**: Strong type checking and boundary validation
- 🧪 **Well-Tested**: Comprehensive test suite covering edge cases

## Installation

```bash
pip install git+hhttps://github.com/boxcake/pdc_struct.git
```

**Requirements**:
- Python 3.10+
- Pydantic 2.0+

## Quick Start

Here's a real-world example using PDC Struct to implement ARP (Address Resolution Protocol) packet handling:

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
    
    # Hardware type (e.g., Ethernet = 1)
    hardware_type: HardwareType = Field(
        description="Hardware type"
    )
    
    # Protocol type (e.g., IPv4 = 0x0800)
    protocol_type: UInt16 = Field(
        default=0x0800,  # IPv4
        description="Protocol type (0x0800 for IPv4)"
    )
    
    # Hardware/Protocol address lengths
    hw_addr_len: UInt8 = Field(
        default=6,  # MAC address length
        description="Hardware address length"
    )
    proto_addr_len: UInt8 = Field(
        default=4,  # IPv4 address length
        description="Protocol address length"
    )
    
    # Operation (request/reply)
    operation: Operation = Field(
        description="Operation code"
    )
    
    # Addresses
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

# Example Usage:
def create_arp_request(sender_mac: bytes, sender_ip: str, target_ip: str) -> bytes:
    """Create an ARP request packet"""
    return ARPPacket(
        hardware_type=HardwareType.ETHERNET,
        operation=Operation.REQUEST,
        sender_hw_addr=sender_mac,
        sender_proto_addr=IPv4Address(sender_ip),
        target_hw_addr=b'\x00\x00\x00\x00\x00\x00',  # Empty target MAC
        target_proto_addr=IPv4Address(target_ip)
    ).to_bytes()

# Create an ARP request
my_mac = bytes.fromhex('00112233445566')
packet_bytes = create_arp_request(
    sender_mac=my_mac,
    sender_ip='192.168.1.100',
    target_ip='192.168.1.1'
)

# Parse received ARP packet
received = ARPPacket.from_bytes(packet_bytes)
print(f"ARP {received.operation.name} from {received.sender_proto_addr}")
```

```shell
> python3 decode_arp.py 

Equivalent struct format string:  >HHBBH6s4s6s4s

Listening for ARP packets...

ARP Packet Received:
            Operation : REQUEST
            Source IP : 192.168.1.202
            SourceMac : d623cbd568a9
            Query IP  : 192.168.1.99
            
ARP Packet Received:
            Operation : REQUEST
            Source IP : 192.168.1.202
            SourceMac : d623cbd568a9
            Query IP  : 192.168.1.99
            
```
This example demonstrates the ability to handle real network protocols with:
- Fixed-width integers with specific sizes (uint8, uint16)
- Network byte order (big-endian)
- MAC addresses as fixed-length bytes
- IPv4 address handling
- Enum types for hardware types and operations

Here's a simpler example showing basic PDC Struct usage:

```python
from pydantic import Field
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder

class SensorData(StructModel):
    device_id: int = Field(description="Unique device identifier")
    temperature: float = Field(description="Temperature in Celsius")
    location: str = Field(max_length=16, description="Sensor location")

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN
    )

# Create and serialize
sensor = SensorData(
    device_id=42,
    temperature=23.5,
    location="Laboratory 1"
)
binary_data = sensor.to_bytes()

# Deserialize
recovered = SensorData.from_bytes(binary_data)
print(f"Temperature: {recovered.temperature}°C")
```

The repo also contains an example interprocess communication using unix sockets, with a python app encoding data, and the data being decoded by a simple binary written in C
[Code here](examples/py-c-interprocess/README.md)

## Operating Modes

PDC Struct provides two distinct operating modes to handle different use cases:

### C_COMPATIBLE Mode

Designed for interoperability with C structures and established binary protocols:

```python
from typing import Optional
from pdc_struct import StructModel, StructConfig, StructMode
from pydantic import Field

class NetworkPacket(StructModel):
    packet_type: int = Field(description="Packet type identifier")
    sequence_num: int = Field(description="Sequence number")
    payload: str = Field(
        max_length=1024,
        description="Packet payload"
    )
    checksum: Optional[int] = Field(
        default=0,
        description="Optional checksum"
    )

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN  # Network byte order
    )
```

Key characteristics:
- Fixed struct size
- Optional fields require defaults
- Null-terminated strings
- No headers or metadata
- Direct C struct compatibility

### DYNAMIC Mode

Optimized for Python-to-Python communication with maximum flexibility:

```python
class UserProfile(StructModel):
    user_id: int = Field(description="User identifier")
    username: str = Field(max_length=32, description="Username")
    email: Optional[str] = Field(
        None,
        max_length=64,
        description="Optional email"
    )
    active: Optional[bool] = None

    struct_config = StructConfig(
        mode=StructMode.DYNAMIC,
        byte_order=ByteOrder.LITTLE_ENDIAN
    )
```

Key characteristics:
- Variable-length structures
- Truly optional fields (no defaults required)
- Efficient bitmap field tracking
- Version headers for future compatibility
- UTF-8 string handling

## Type System

PDC Struct supports a comprehensive type system with C-compatible binary representations:

PDC Struct supports a variety of Python types with C-compatible struct packing:

### Supported Types

| Python Type | Struct Format | Size    | Notes                         |
|------------|---------------|---------|-------------------------------|
| int        | 'i'          | 4 bytes | Default integer               |
| float      | 'd'          | 8 bytes | Double precision              |
| bool       | '?'          | 1 byte  | Boolean                       |
| str        | 's'          | Varies  | Fixed-length UTF-8 string     |
| bytes      | 's'          | Varies  | Fixed-length bytes            |
| Int8       | 'b'          | 1 byte  | -128 to 127                  |
| UInt8      | 'B'          | 1 byte  | 0 to 255                     |
| Int16      | 'h'          | 2 bytes | -32,768 to 32,767            |
| UInt16     | 'H'          | 2 bytes | 0 to 65,535                  |
| Enum       | 'i'          | 4 bytes | Integer-based                 |
| IntEnum    | 'i'          | 4 bytes | Native integer representation |
| StrEnum    | 'i'          | 4 bytes | Index-based storage           |
| IPv4Address| '4s'         | 4 bytes | Network byte order            |
| IPv6Address| '16s'        | 16 bytes| Network byte order            |
| UUID       | '16s'        | 16 bytes| UUID bytes                    |

### Fixed-Width Types

```python
from pdc_struct import StructModel
from pdc_struct.c_types import Int8, UInt8, Int16, UInt16
from pydantic import Field

class SensorReading(StructModel):
    sensor_id: UInt8 = Field(description="Sensor ID (0-255)")
    value: Int16 = Field(description="Reading value (-32768 to 32767)")
```

Available types:
- `Int8`: -128 to 127
- `UInt8`: 0 to 255
- `Int16`: -32,768 to 32,767
- `UInt16`: 0 to 65,535

### Network Types

```python
from ipaddress import IPv4Address, IPv6Address
from uuid import UUID

class NetworkDevice(StructModel):
    id: UUID = Field(description="Device UUID")
    ipv4: IPv4Address = Field(description="Device IPv4 address")
    ipv6: Optional[IPv6Address] = Field(description="Optional IPv6 address")
```

### Enum Support

```python
from enum import IntEnum, StrEnum

class DeviceType(IntEnum):
    SENSOR = 1
    ACTUATOR = 2
    CONTROLLER = 3

class Status(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"

class Device(StructModel):
    type: DeviceType = Field(description="Device type")
    status: Status = Field(description="Device status")
```

## String Handling

PDC Struct provides robust string handling with UTF-8 support:

```python
class StringExample(StructModel):
    # Fixed buffer size (recommended)
    name: str = Field(max_length=32)
    
    # Separate validation and storage limits
    description: str = Field(
        max_length=100,     # Maximum logical length
        struct_length=256   # Binary storage size
    )
```

### String Buffer Sizing

- In C_COMPATIBLE mode:
  - Strings are null-terminated
  - Buffer size = max_length * 4 (for UTF-8)
  - Can be overridden with struct_length

- In DYNAMIC mode:
  - Variable length storage
  - Length prefix encoded
  - No null termination

## Error Handling

PDC Struct provides specific exceptions for different error cases:

```python
try:
    data = model.to_bytes()
except StructPackError as e:
    print(f"Serialization failed: {e}")
except StructUnpackError as e:
    print(f"Deserialization failed: {e}")
```

Common error cases:
- Invalid field values
- Buffer overflow
- String encoding errors
- Version mismatches
- Corrupted data

## Use Cases

PDC Struct is ideal for:

1. **Network Protocols**
   - Binary protocol implementations
   - Packet parsing and construction
   - Network byte order handling

2. **File Formats**
   - Binary file headers
   - Data structure serialization
   - Fixed-format records

3. **IPC/RPC**
   - Inter-process communication
   - Shared memory structures
   - System call interfaces

4. **Data Exchange**
   - Efficient data serialization
   - Cross-platform compatibility
   - Legacy system integration


## Contributing

Contributions are welcome!

- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

Built with [Pydantic](https://docs.pydantic.dev/latest/)
