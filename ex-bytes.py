from pydantic import Field
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder

print("creating class")
class InvalidModel(StructModel):
    invalid_string: str = Field(description="String without max_length")

    struct_config = StructConfig(mode=StructMode.DYNAMIC)


a = InvalidModel(invalid_string="asdasd")
print("created instance")

print(a.get_struct_format())
print(a.to_bytes())
exit(0)


class ARPPacket(StructModel):
    """ARP Packet Structure (RFC 826)"""

    addr: bytes = Field(struct_length=6, description="Source hardware address")

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.LITTLE_ENDIAN
    )

sample_data: bytes = b"\x01\x02\x03\x04\x05\x06"

print(f"Struct format string {ARPPacket.get_struct_format()}")


p = ARPPacket(addr=sample_data)
print(p)

s = p.to_bytes()
print(s)
