"""Test IP address support in PDC Struct."""

from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Optional
from pydantic import Field
from pdc_struct import StructModel, StructConfig, StructMode, ByteOrder

# Define some test addresses
ZERO_IPV4 = IPv4Address("0.0.0.0")
ZERO_IPV6 = IPv6Address("::")


class IPModel(StructModel):
    """Model with both IPv4 and IPv6 addresses."""

    ipv4: IPv4Address
    ipv6: IPv6Address
    optional_ipv4: Optional[IPv4Address] = ZERO_IPV4
    optional_ipv6: Optional[IPv6Address] = ZERO_IPV6
    name: str = Field(max_length=10)

    struct_config = StructConfig(
        mode=StructMode.C_COMPATIBLE,
        byte_order=ByteOrder.BIG_ENDIAN,  # Network byte order
    )


def test_ipv4_basic():
    """Test basic IPv4 packing and unpacking."""
    addr = IPv4Address("192.168.1.1")

    model = IPModel(ipv4=addr, ipv6=ZERO_IPV6, name="test")
    data = model.to_bytes()

    recovered = IPModel.from_bytes(data)
    assert recovered.ipv4 == addr
    assert recovered.name == "test"
    assert recovered.optional_ipv4 == ZERO_IPV4
    assert isinstance(recovered.ipv4, IPv4Address)


def test_ipv6_basic():
    """Test basic IPv6 packing and unpacking."""
    addr = IPv6Address("2001:db8::1")

    model = IPModel(ipv4=ZERO_IPV4, ipv6=addr, name="test")
    data = model.to_bytes()

    recovered = IPModel.from_bytes(data)
    assert recovered.ipv6 == addr
    assert recovered.name == "test"
    assert recovered.optional_ipv6 == ZERO_IPV6
    assert isinstance(recovered.ipv6, IPv6Address)


def test_both_ip_versions():
    """Test handling both IP versions together."""
    ipv4_addr = IPv4Address("192.168.1.1")
    ipv6_addr = IPv6Address("2001:db8::1")

    model = IPModel(
        ipv4=ipv4_addr,
        ipv6=ipv6_addr,
        optional_ipv4=IPv4Address("10.0.0.1"),
        optional_ipv6=IPv6Address("2001:db8::2"),
        name="test",
    )
    data = model.to_bytes()

    recovered = IPModel.from_bytes(data)
    assert recovered.ipv4 == ipv4_addr
    assert recovered.ipv6 == ipv6_addr
    assert recovered.optional_ipv4 == IPv4Address("10.0.0.1")
    assert recovered.optional_ipv6 == IPv6Address("2001:db8::2")


def test_ip_dynamic_mode():
    """Test IP addresses in dynamic mode."""

    class DynamicIPModel(StructModel):
        ipv4: Optional[IPv4Address] = None
        ipv6: Optional[IPv6Address] = None

        struct_config = StructConfig(
            mode=StructMode.DYNAMIC, byte_order=ByteOrder.BIG_ENDIAN
        )

    # Test with values
    ipv4_addr = IPv4Address("192.168.1.1")
    ipv6_addr = IPv6Address("2001:db8::1")
    model = DynamicIPModel(ipv4=ipv4_addr, ipv6=ipv6_addr)
    data = model.to_bytes()
    recovered = DynamicIPModel.from_bytes(data)
    assert recovered.ipv4 == ipv4_addr
    assert recovered.ipv6 == ipv6_addr

    # Test without values
    model = DynamicIPModel()
    data = model.to_bytes()
    recovered = DynamicIPModel.from_bytes(data)
    assert recovered.ipv4 is None
    assert recovered.ipv6 is None


def test_special_addresses():
    """Test handling of special IP addresses."""
    test_cases = [
        # IPv4
        "0.0.0.0",  # Zero address
        "127.0.0.1",  # Localhost
        "255.255.255.255",  # Broadcast
        # IPv6
        "::",  # Zero address
        "::1",  # Localhost
        "fe80::1",  # Link local
        "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff",  # All ones
    ]

    for addr_str in test_cases:
        addr = ip_address(addr_str)
        if isinstance(addr, IPv4Address):
            model = IPModel(ipv4=addr, ipv6=ZERO_IPV6, name="test")
        else:
            model = IPModel(ipv4=ZERO_IPV4, ipv6=addr, name="test")

        data = model.to_bytes()
        recovered = IPModel.from_bytes(data)

        if isinstance(addr, IPv4Address):
            assert recovered.ipv4 == addr
        else:
            assert recovered.ipv6 == addr
