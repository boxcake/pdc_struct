# ARP Packet Decoder

This example demonstrates using PDC Struct to decode ARP (Address Resolution Protocol) packets captured from the network. It shows how binary network data maps cleanly to a Pydantic model.

## The ARP Packet Structure

ARP packets have a well-defined binary format (RFC 826). Here's how we define it with PDC Struct:

```python
from enum import IntEnum
from ipaddress import IPv4Address
from pydantic import Field
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.c_types import UInt8, UInt16


class HardwareType(IntEnum):
    ETHERNET = 1


class Operation(IntEnum):
    REQUEST = 1
    REPLY = 2


class ARPPacket(StructModel):
    """ARP Packet Structure (RFC 826)

    Total size: 28 bytes for IPv4 over Ethernet
    """

    htype: UInt16 = Field(description="Hardware type (1 = Ethernet)")
    ptype: UInt16 = Field(description="Protocol type (0x0800 = IPv4)")
    hlen: UInt8 = Field(description="Hardware address length (6 for MAC)")
    plen: UInt8 = Field(description="Protocol address length (4 for IPv4)")
    operation: UInt16 = Field(description="Operation (1=request, 2=reply)")
    sha: bytes = Field(
        json_schema_extra={"struct_length": 6},
        description="Sender hardware address (MAC)"
    )
    spa: IPv4Address = Field(description="Sender protocol address (IP)")
    tha: bytes = Field(
        json_schema_extra={"struct_length": 6},
        description="Target hardware address (MAC)"
    )
    tpa: IPv4Address = Field(description="Target protocol address (IP)")

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN  # Network byte order
    )


def format_mac(mac_bytes: bytes) -> str:
    """Format MAC address bytes as human-readable string."""
    return ":".join(f"{b:02x}" for b in mac_bytes)
```

## Field Breakdown

| Field | Type | Size | Description |
|-------|------|------|-------------|
| `htype` | UInt16 | 2 bytes | Hardware type (Ethernet = 1) |
| `ptype` | UInt16 | 2 bytes | Protocol type (IPv4 = 0x0800) |
| `hlen` | UInt8 | 1 byte | Hardware address length (6) |
| `plen` | UInt8 | 1 byte | Protocol address length (4) |
| `operation` | UInt16 | 2 bytes | Request (1) or Reply (2) |
| `sha` | bytes[6] | 6 bytes | Sender MAC address |
| `spa` | IPv4Address | 4 bytes | Sender IP address |
| `tha` | bytes[6] | 6 bytes | Target MAC address |
| `tpa` | IPv4Address | 4 bytes | Target IP address |

**Total: 28 bytes**

## Capturing ARP Packets

### Linux

On Linux, you can capture raw packets using `AF_PACKET` sockets (requires root):

```python
import socket
import struct

def listen_for_arp_linux():
    """Listen for ARP packets on Linux (requires root)."""

    # ETH_P_ALL = 0x0003 captures all protocols
    sock = socket.socket(
        socket.AF_PACKET,
        socket.SOCK_RAW,
        socket.ntohs(0x0003)
    )

    print("Listening for ARP packets (Linux)...")
    print(f"ARP struct size: {ARPPacket.struct_size()} bytes")
    print(f"Format string: {ARPPacket.struct_format_string()}\n")

    try:
        while True:
            packet, addr = sock.recvfrom(65535)

            # Ethernet header: 14 bytes
            # Bytes 12-13: EtherType
            ethertype = struct.unpack("!H", packet[12:14])[0]

            # EtherType 0x0806 = ARP
            if ethertype == 0x0806:
                # Extract ARP payload (after 14-byte Ethernet header)
                arp_data = packet[14:42]

                # Decode using PDC Struct
                arp = ARPPacket.from_bytes(arp_data)

                op_name = "REQUEST" if arp.operation == 1 else "REPLY"
                print(f"ARP {op_name}:")
                print(f"  {format_mac(arp.sha)} ({arp.spa})")
                print(f"  → {format_mac(arp.tha)} ({arp.tpa})")
                print()

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        sock.close()


if __name__ == "__main__":
    listen_for_arp_linux()
```

Run with:
```bash
sudo python3 arp_listener.py
```

### Windows (using Scapy)

On Windows, raw sockets are restricted. Use [Scapy](https://scapy.net/) with [Npcap](https://npcap.com/):

```python
from scapy.all import sniff, ARP as ScapyARP

def process_packet(packet):
    """Process captured packet with PDC Struct."""
    if ScapyARP in packet:
        # Get raw ARP bytes from Scapy
        arp_bytes = bytes(packet[ScapyARP])[:28]

        # Decode using PDC Struct
        arp = ARPPacket.from_bytes(arp_bytes)

        op_name = "REQUEST" if arp.operation == 1 else "REPLY"
        print(f"ARP {op_name}:")
        print(f"  {format_mac(arp.sha)} ({arp.spa})")
        print(f"  → {format_mac(arp.tha)} ({arp.tpa}}")
        print()


def listen_for_arp_windows():
    """Listen for ARP packets on Windows using Scapy."""
    print("Listening for ARP packets (Windows/Scapy)...")
    print(f"ARP struct size: {ARPPacket.struct_size()} bytes\n")

    # Filter for ARP packets only
    sniff(filter="arp", prn=process_packet, store=False)


if __name__ == "__main__":
    listen_for_arp_windows()
```

Install requirements:
```bash
pip install scapy
# Also install Npcap from https://npcap.com/
```

## Decoding from a Hex Dump

You can also decode ARP packets from captured hex data:

```python
# Example ARP request packet (hex)
hex_data = "0001080006040001aabbccddeeff0a0001010000000000000a000102"
arp_bytes = bytes.fromhex(hex_data)

arp = ARPPacket.from_bytes(arp_bytes)

print(f"Hardware Type: {arp.htype} ({'Ethernet' if arp.htype == 1 else 'Unknown'})")
print(f"Protocol Type: 0x{arp.ptype:04x}")
print(f"Operation: {arp.operation} ({'Request' if arp.operation == 1 else 'Reply'})")
print(f"Sender: {format_mac(arp.sha)} @ {arp.spa}")
print(f"Target: {format_mac(arp.tha)} @ {arp.tpa}")
```

Output:
```
Hardware Type: 1 (Ethernet)
Protocol Type: 0x0800
Operation: 1 (Request)
Sender: aa:bb:cc:dd:ee:ff @ 10.0.1.1
Target: 00:00:00:00:00:00 @ 10.0.1.2
```

## Creating ARP Packets

You can also create ARP packets to send:

```python
def create_arp_request(
    sender_mac: bytes,
    sender_ip: str,
    target_ip: str
) -> bytes:
    """Create an ARP request packet."""

    request = ARPPacket(
        htype=1,              # Ethernet
        ptype=0x0800,         # IPv4
        hlen=6,               # MAC length
        plen=4,               # IPv4 length
        operation=1,          # Request
        sha=sender_mac,
        spa=IPv4Address(sender_ip),
        tha=b"\x00" * 6,      # Unknown (we're asking)
        tpa=IPv4Address(target_ip)
    )

    return request.to_bytes()


# Example: Create ARP request
my_mac = bytes.fromhex("aabbccddeeff")
arp_request = create_arp_request(my_mac, "192.168.1.100", "192.168.1.1")
print(f"ARP Request: {arp_request.hex()}")
print(f"Size: {len(arp_request)} bytes")
```

## Why PDC Struct?

Without PDC Struct, you'd manually unpack the bytes:

```python
# Manual approach (error-prone)
import struct
import socket

def decode_arp_manual(data: bytes):
    htype, ptype, hlen, plen, op = struct.unpack("!HHBBH", data[:8])
    sha = data[8:14]
    spa = socket.inet_ntoa(data[14:18])
    tha = data[18:24]
    tpa = socket.inet_ntoa(data[24:28])
    return htype, ptype, hlen, plen, op, sha, spa, tha, tpa
```

With PDC Struct:

- **Type safety** - Fields have proper types (`IPv4Address`, `UInt16`)
- **Validation** - Pydantic validates all values
- **Self-documenting** - The model describes the packet format
- **Bidirectional** - Same model for encoding and decoding
- **IDE support** - Autocomplete and type checking

## Full Example

See the complete working example in the repository:
[`examples/ARP Packet decoder/decode_arp.py`](https://github.com/boxcake/pdc_struct/tree/main/examples/ARP%20Packet%20decoder)
