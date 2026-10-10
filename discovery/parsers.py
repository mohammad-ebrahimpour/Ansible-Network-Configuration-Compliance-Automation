from __future__ import annotations

import re

from .models import Interface


def parse_cisco_version(text: str) -> dict[str, str | None]:
    hostname = re.search(r"^(\S+)\s+uptime is ", text, re.MULTILINE)
    version = re.search(r"Version\s+([\w().+-]+)", text)
    serial = re.search(r"Processor board ID\s+(\S+)", text)
    model = re.search(
        r"cisco\s+(\S+)\s+\(.*?\)\s+processor",
        text,
        re.IGNORECASE,
    )

    return {
        "hostname": hostname.group(1) if hostname else "unknown",
        "version": version.group(1) if version else None,
        "serial": serial.group(1) if serial else None,
        "model": model.group(1) if model else None,
    }


def parse_cisco_interfaces(text: str) -> list[Interface]:
    interfaces: list[Interface] = []

    blocks = re.split(
        r"\n(?=\S+\s+is\s+(?:up|down),)",
        text.strip(),
    )

    for block in blocks:
        first = block.splitlines()[0].strip() if block.strip() else ""

        match = re.match(
            r"^(\S+)\s+is\s+(up|down),",
            first,
        )

        if not match:
            continue

        name, status = match.groups()

        desc = re.search(
            r"\n\s+Description:\s*(.+)",
            block,
        )

        mac = re.search(
            r"address is\s+([0-9a-f.]+)",
            block,
            re.IGNORECASE,
        )

        interfaces.append(
            Interface(
                name=name,
                status=status,
                description=desc.group(1).strip() if desc else None,
                mac_address=mac.group(1).lower() if mac else None,
            )
        )

    return interfaces


def parse_cisco_ip_interfaces(text: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}

    for line in text.splitlines():
        parts = line.split()

        if (
            len(parts) < 2
            or parts[0].lower() == "interface"
            or parts[1].lower() == "unassigned"
        ):
            continue

        result.setdefault(parts[0], []).append(parts[1])

    return result


def parse_mikrotik_resource(text: str) -> dict[str, str]:
    result: dict[str, str] = {}

    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()

    return result


def parse_mikrotik_interfaces(text: str) -> list[Interface]:
    interfaces: list[Interface] = []

    for line in text.splitlines():
        line = line.strip()

        if not line or not re.match(r"^\d+", line):
            continue

        name = re.search(r"\bname=([^\s]+)", line)

        if not name:
            continue

        mac = re.search(
            r"\bmac-address=([0-9A-Fa-f:]+)",
            line,
        )

        mtu = re.search(
            r"\bmtu=(\d+)",
            line,
        )

        if "disabled=yes" in line:
            status = "disabled"
        elif "running=yes" in line:
            status = "up"
        elif "running=no" in line:
            status = "down"
        else:
            status = None

        interfaces.append(
            Interface(
                name=name.group(1),
                status=status,
                mac_address=mac.group(1).lower() if mac else None,
                mtu=int(mtu.group(1)) if mtu else None,
            )
        )

    return interfaces


def parse_mikrotik_ip_addresses(text: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}

    for line in text.splitlines():
        interface = re.search(
            r"\binterface=([^\s]+)",
            line,
        )

        address = re.search(
            r"\baddress=([0-9A-Fa-f:./]+)",
            line,
        )

        if interface and address:
            result.setdefault(
                interface.group(1),
                [],
            ).append(address.group(1))

    return result