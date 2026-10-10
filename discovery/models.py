from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class DeviceConfig:
    name: str
    vendor: str
    host: str
    username: str
    password: str
    port: int | None = None
    device_type: str | None = None
    api_port: int = 8728


@dataclass
class Interface:
    name: str
    description: str | None = None
    status: str | None = None
    mac_address: str | None = None
    speed: str | None = None
    mtu: int | None = None
    ip_addresses: list[str] = field(default_factory=list)
    vlan: str | None = None


@dataclass
class Device:
    hostname: str
    vendor: str
    platform: str
    version: str | None = None
    serial: str | None = None
    model: str | None = None
    management_ip: str | None = None
    interfaces: list[Interface] = field(default_factory=list)


@dataclass
class Inventory:
    devices: list[Device] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)