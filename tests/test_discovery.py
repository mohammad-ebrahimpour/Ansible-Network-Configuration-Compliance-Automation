from discovery.parsers import (
    parse_cisco_interfaces,
    parse_cisco_ip_interfaces,
    parse_cisco_version,
    parse_mikrotik_interfaces,
    parse_mikrotik_ip_addresses,
    parse_mikrotik_resource,
)


def test_cisco_version_preserves_full_ios_release() -> None:
    text = (
        "Cisco IOS Software, Version 15.2(2)E9, RELEASE SOFTWARE (fc1)\n"
        "CORE-SW01 uptime is 42 weeks\n"
        "cisco WS-C2960X-24TS-L (APM86...) processor\n"
        "Processor board ID FOC1234X1YZ\n"
    )

    result = parse_cisco_version(text)

    assert result["hostname"] == "CORE-SW01"
    assert result["version"] == "15.2(2)E9"
    assert result["serial"] == "FOC1234X1YZ"
    assert result["model"] == "WS-C2960X-24TS-L"


def test_cisco_interfaces_and_ips() -> None:
    interfaces = parse_cisco_interfaces(
        """GigabitEthernet1/0/1 is up, line protocol is up
  Hardware is Gigabit Ethernet, address is 0011.2233.4455
  Description: Uplink to Router

GigabitEthernet1/0/2 is down, line protocol is down
  Hardware is Gigabit Ethernet, address is 0011.2233.4466
  Description: User Access
"""
    )

    ips = parse_cisco_ip_interfaces(
        """Interface IP-Address OK? Method Status Protocol
GigabitEthernet1/0/1 10.10.10.2 YES DHCP up up
GigabitEthernet1/0/2 unassigned YES unset down down
Vlan10 10.10.10.1 YES manual up up
"""
    )

    assert len(interfaces) == 2
    assert interfaces[0].description == "Uplink to Router"
    assert interfaces[0].mac_address == "0011.2233.4455"
    assert ips["Vlan10"] == ["10.10.10.1"]


def test_mikrotik_resource_and_interfaces() -> None:
    resource = parse_mikrotik_resource(
        """uptime: 1d2h
version: 7.23.7
board-name: CHR
"""
    )

    interfaces = parse_mikrotik_interfaces(
        """0 R name=ether1 type=ether mtu=1500 mac-address=AA:BB:CC:DD:EE:01 running=yes
1 name=ether2 type=ether mtu=1500 mac-address=AA:BB:CC:DD:EE:02 running=no
"""
    )

    assert resource["version"] == "7.23.7"
    assert interfaces[0].status == "up"
    assert interfaces[0].mtu == 1500
    assert interfaces[1].status == "down"


def test_mikrotik_addresses() -> None:
    result = parse_mikrotik_ip_addresses(
        """0 address=10.0.0.2/24 network=10.0.0.0 interface=ether1
1 address=192.168.10.1/24 network=192.168.10.0 interface=bridge1
"""
    )

    assert result["ether1"] == ["10.0.0.2/24"]
    assert result["bridge1"] == ["192.168.10.1/24"]