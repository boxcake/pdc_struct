# PDC Struct

**A Pydantic extension for binary serialization and C-compatible struct packing**

[![Tests](https://github.com/boxcake/pdc_struct/actions/workflows/test.yml/badge.svg)](https://github.com/boxcake/pdc_struct/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/boxcake/pdc_struct/branch/main/graph/badge.svg)](https://codecov.io/gh/boxcake/pdc_struct)
[![PyPI version](https://badge.fury.io/py/pdc-struct.svg)](https://badge.fury.io/py/pdc-struct)
[![Python Version](https://img.shields.io/pypi/pyversions/pdc-struct.svg)](https://pypi.org/project/pdc-struct/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## What is PDC Struct?

PDC Struct combines **Pydantic's validation** with **Python's struct module** to create a powerful toolkit for binary data serialization. Whether you're building network protocols, interfacing with C libraries, or working with IoT devices, PDC Struct provides a clean, type-safe API for working with binary data.

## Key Features

### Dual Operating Modes

- **C_COMPATIBLE Mode**: Fixed-size binary layouts matching C struct specifications, ideal for network protocols, hardware interfaces, and legacy file formats
- **DYNAMIC Mode**: Flexible, self-describing format with true optional field support and variable-size packing for Python-to-Python communication

### Type Safety and Validation

- **Pydantic Integration**: Full validation at creation time with clear error messages
- **Fixed-Width Integer Types**: Explicit sizing with `Int8`, `UInt8`, `Int16`, `UInt16` prevents overflow errors
- **Automatic Range Checking**: Values validated against type constraints before packing

### Advanced Binary Features

- **Configurable Byte Order**: Little-endian, big-endian, or native with automatic propagation to nested structures
- **BitField Support**: Pack multiple boolean flags or small integers into single bytes for space efficiency
- **Nested Structs**: Compose complex hierarchical structures with automatic size calculation
- **Optional Fields**: Mode-dependent behavior - fixed defaults in C_COMPATIBLE, truly optional in DYNAMIC

### Rich Type Ecosystem

- **Network Types**: Native support for `IPv4Address` and `UUID`
- **Enums**: Automatic integer conversion for `IntEnum` and standard `Enum` types
- **Binary Data**: Fixed-length `bytes` and null-terminated `str` fields
- **Custom Extensions**: Pluggable type handler system for adding new types

## Quick Example

```python
from pdc_struct import StructModel, StructConfig, StructMode
from pdc_struct.c_types import UInt8, UInt16

class NetworkPacket(StructModel):
    msg_type: UInt8
    sequence: UInt16
    payload_length: UInt16

    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# Create and pack
packet = NetworkPacket(msg_type=1, sequence=100, payload_length=256)
data = packet.to_bytes()  # b'\x01\x00\x64\x01\x00'

# Unpack
received = NetworkPacket.from_bytes(data)
print(f"Received packet type {received.msg_type}")  # Received packet type 1
```

## Use Cases

### Network Protocols
Parse and generate binary network packets with ease:

```python
class ARPPacket(StructModel):
    hardware_type: UInt16
    protocol_type: UInt16
    hw_addr_len: UInt8
    proto_addr_len: UInt8
    operation: UInt16
    # ... more fields
```

### C Interoperability
Seamlessly exchange data with C programs:

```python
# Python side
class SensorData(StructModel):
    timestamp: UInt32
    temperature: float
    humidity: float
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)

# Matches C struct:
# typedef struct {
#     uint32_t timestamp;
#     float temperature;
#     float humidity;
# } SensorData;
```

### IoT Device Communication
Efficiently pack sensor data for transmission:

```python
class SensorReading(StructModel):
    device_id: UInt16
    temperature: Int16  # in 0.1°C
    battery: UInt8      # percentage
    struct_config = StructConfig(mode=StructMode.C_COMPATIBLE)
```

## Why PDC Struct?

| Feature | PDC Struct | Plain struct | Pydantic |
|---------|-----------|--------------|----------|
| Type Safety | Yes | No | Yes |
| Binary Packing | Yes | Yes | No |
| Validation | Yes | No | Yes |
| C Compatible | Yes | Yes | No |
| Modern API | Yes | No | Yes |

## Next Steps

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Quick Start**

    ---

    Get up and running in minutes

    [:octicons-arrow-right-24: Start tutorial](getting-started.md)

-   :material-book-open-variant:{ .lg .middle } **User Guide**

    ---

    Learn about modes, types, and advanced features

    [:octicons-arrow-right-24: Read the guide](user-guide/modes.md)

-   :material-code-braces:{ .lg .middle } **API Reference**

    ---

    Detailed API documentation

    [:octicons-arrow-right-24: Explore API](api-reference/struct-model.md)

-   :material-github:{ .lg .middle } **Examples**

    ---

    Real-world code examples

    [:octicons-arrow-right-24: View examples](examples/arp-packet.md)

</div>

## Installation

```bash
pip install pdc-struct
```

**Requirements**: Python 3.11+, Pydantic 2.0+

---

## Community & Support

- **GitHub**: [Report issues](https://github.com/boxcake/pdc_struct/issues) or contribute
- **Documentation**: You're reading it!
- **PyPI**: [Package details](https://pypi.org/project/pdc-struct/)

## License

PDC Struct is licensed under the [MIT License](https://opensource.org/licenses/MIT).
