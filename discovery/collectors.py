from __future__ import annotations

from abc import ABC, abstractmethod

from .models import Device, DeviceConfig, Interface
from .parsers import (
    parse_cisco_interfaces,
    parse_cisco_ip_interfaces,
    parse_cisco_version,
)


class Collector(ABC):
    def __init__(self, config: DeviceConfig) -> None:
        self.config = config

    @abstractmethod
    def discover(self) -> Device:
        raise NotImplementedError


class CiscoCollector(Collector):
    def discover(self) -> Device:
        from netmiko import ConnectHandler

        params = {
            "device_type": self.config.device_type or "cisco_ios",
            "host": self.config.host,
            "username": self.config.username,
            "password": self.config.password,
        }

        if self.config.port:
            params["port"] = self.config.port

        connection = ConnectHandler(**params)

        try:
            identity = parse_cisco_version(
                connection.send_command("show version")
            )

            interfaces = parse_cisco_interfaces(
                connection.send_command("show interfaces")
            )

            ip_map = parse_cisco_ip_interfaces(
                connection.send_command("show ip interface brief")
            )

            for interface in interfaces:
                interface.ip_addresses = list(
                    ip_map.get(interface.name, [])
                )

            management_ip = next(
                (
                    ips[0]
                    for name, ips in ip_map.items()
                    if name.lower().startswith(("vlan", "loopback"))
                    and ips
                ),
                None,
            )

            return Device(
                hostname=identity["hostname"] or self.config.name,
                vendor="Cisco",
                platform="IOS",
                version=identity.get("version"),
                serial=identity.get("serial"),
                model=identity.get("model"),
                management_ip=management_ip,
                interfaces=interfaces,
            )

        finally:
            connection.disconnect()


class MikroTikCollector(Collector):
    def discover(self) -> Device:
        from librouteros import connect

        api = connect(
            self.config.host,
            self.config.username,
            self.config.password,
            port=self.config.api_port,
        )

        try:
            identity_rows = list(
                api.path("/system/identity").select("name")
            )

            resource_rows = list(
                api.path("/system/resource").select(
                    "version",
                    "board-name",
                    "architecture-name",
                )
            )

            interface_rows = list(
                api.path("/interface").select(
                    "name",
                    "type",
                    "mac-address",
                    "mtu",
                    "running",
                    "disabled",
                )
            )

            address_rows = list(
                api.path("/ip/address").select(
                    "address",
                    "interface",
                    "disabled",
                )
            )

            resource = resource_rows[0] if resource_rows else {}

            hostname = (
                identity_rows[0].get("name", self.config.name)
                if identity_rows
                else self.config.name
            )

            address_map: dict[str, list[str]] = {}

            for row in address_rows:
                if str(row.get("disabled", "false")).lower() == "true":
                    continue

                interface = str(row.get("interface", ""))
                address = str(row.get("address", ""))

                if interface and address:
                    address_map.setdefault(interface, []).append(address)

            interfaces: list[Interface] = []

            for row in interface_rows:
                name = str(row.get("name", ""

))

                if not name:
                    continue

                disabled = (
                    str(row.get("disabled", "false")).lower()
                    == "true"
                )

                running = (
                    str(row.get("running", "false")).lower()
                    == "true"
                )

                status = (
                    "disabled"
                    if disabled
                    else ("up" if running else "down")
                )

                mtu = row.get("mtu")

                interfaces.append(
                    Interface(
                        name=name,
                        status=status,
                        mac_address=(
                            str(row.get("mac-address"))
                            if row.get("mac-address")
                            else None
                        ),
                        mtu=(
                            int(mtu)
                            if str(mtu).isdigit()
                            else None
                        ),
                        ip_addresses=address_map.get(name, []),
                    )
                )

            management_ip = next(
                (
                    addresses[0]
                    for addresses in address_map.values()
                    if addresses
                ),
                None,
            )

            return Device(
                hostname=hostname,
                vendor="MikroTik",
                platform="RouterOS",
                version=resource.get("version"),
                model=resource.get("board-name"),
                management_ip=management_ip,
                interfaces=interfaces,
            )

        finally:
            close = getattr(api, "close", None)

            if callable(close):
                close()