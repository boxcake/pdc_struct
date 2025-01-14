"""
Example using PDC Struct to decode ARP packets.

This example shows how to:
1. Define an ARP packet structure
2. Listen for ARP packets on a network interface
3. Decode received packets
4. Create and send ARP requests
"""

from enum import IntEnum
import socket
import struct
from ipaddress import IPv4Address
from typing import List
from pydantic import Field
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.c_types import UInt8, UInt16

class HardwareType(IntEnum):
    ETHERNET = 1
    IEEE802 = 6
    ARCNET = 7
    FRAME_RELAY = 15
    ATM = 16


class ProtocolType(IntEnum):
    IP = 0x0800
    ARP = 0x0806
    RARP = 0x8035


class Operation(IntEnum):
    REQUEST = 1
    REPLY = 2


class ARPPacket(StructModel):
    """ARP Packet Structure (RFC 826)"""

    # Hardware type (e.g., Ethernet = 1)
    htype: UInt16 = Field(
        description="Hardware type"
    )

    # Protocol type (e.g., IPv4 = 0x0800)
    ptype: UInt16 = Field(
        description="Protocol type"
    )

    # Hardware address length (e.g., MAC = 6)
    hlen: UInt8 = Field(
        description="Hardware address length"

    )

    # Protocol address length (e.g., IPv4 = 4)
    plen: UInt8 = Field(
        description="Protocol address length"

    )

    # Operation (1 = request, 2 = reply)
    operation: UInt16 = Field(
        description="Operation code"
    )

    # Source hardware address (MAC)
    sha: bytes = Field(struct_length=6, description="Source hardware address")

    # Source protocol address (IP)
    spa: IPv4Address = Field(description="Source protocol address")

    # Target hardware address (MAC)
    tha: bytes = Field(struct_length=6, description="Target hardware address")

    # Target protocol address (IP)
    tpa: IPv4Address = Field(description="Target protocol address")

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN  # ARP uses network byte order
    )

print(ARPPacket.struct_format_string())

def listen_for_arp():
    """Listen for and decode ARP packets."""
    # Create raw socket
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))

    print("Listening for ARP packets...")
    while True:
        packet = s.recvfrom(2048)[0]

        # Check if it's an ARP packet (Ethertype 0x0806)
        ethertype = struct.unpack("!H", packet[12:14])[0]
        if ethertype == ProtocolType.ARP:
            # Extract ARP portion (skip Ethernet header)
            arp_data = packet[14:42]  # ARP packet is 28 bytes

            # Decode using our StructModel
            arp = ARPPacket.from_bytes(arp_data)

            print("\nARP Packet Received:")
            print(f"Operation: {'REQUEST' if arp.operation == 1 else 'REPLY'}")
            print(arp)
            print()


if __name__ == "__main__":
    # Example usage:
    # 1. Listen for ARP packets
    listen_for_arp()
