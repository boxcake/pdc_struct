"""
Example using pdc_struct to decode ARP packets.

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
from pydantic import Field
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder
from pdc_struct.c_types import UInt8, UInt16


class ProtocolType(IntEnum):
    IP = 0x0800
    ARP = 0x0806


class Operation(IntEnum):
    REQUEST = 1
    REPLY = 2


class ARPPacket(StructModel):
    """ARP Packet Structure (RFC 826)"""

    htype: UInt16 = Field(description="Hardware type (Ethernet=1")
    ptype: UInt16 = Field(description="Protocol type [IPv4 = 0x0800]")
    hlen: UInt8 = Field(description="Hardware address length [MAC=6 bytes]")
    plen: UInt8 = Field(description="Protocol address length [IPv4=4 bytes]")
    operation: UInt16 = Field(description="Operation code [1=request 2=reply")
    sha: bytes = Field(struct_length=6, description="Source hardware address")
    spa: IPv4Address = Field(description="Source protocol address")
    tha: bytes = Field(struct_length=6, description="Target hardware address")
    tpa: IPv4Address = Field(description="Target protocol address")

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN  # ARP uses network byte order
    )

def listen_for_arp():
    """Listen for and decode ARP packets."""

    # Create raw socket
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))

    print("Listening for ARP packets...\n")

    rx_packets = 2

    while rx_packets:
        packet = s.recvfrom(2048)[0]

        # Check if it's an ARP packet (Ethertype 0x0806)
        ethertype = struct.unpack("!H", packet[12:14])[0]
        if ethertype == ProtocolType.ARP:
            # Extract ARP portion (skip Ethernet header)
            arp_data = packet[14:42]  # ARP packet is 28 bytes

            # Decode using our StructModel
            arp = ARPPacket.from_bytes(arp_data)

            print(f"""ARP Packet Received:
            Operation : {'REQUEST' if arp.operation == 1 else 'REPLY'}
            Source IP : {arp.spa}
            SourceMac : {arp.sha.hex()}
            Query IP  : {arp.tpa}
            """)

            rx_packets -= 1

if __name__ == "__main__":
    print(f"Equivalent struct format string:  {ARPPacket.struct_format_string()}\n")

    listen_for_arp()
