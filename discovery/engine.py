from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import yaml

from .collectors import CiscoCollector, MikroTikCollector
from .models import DeviceConfig, Inventory


def _resolve_env(value: Any) -> Any:
    if (
        isinstance(value, str)
        and value.startswith("${")
        and value.endswith("}")
    ):
        return os.environ.get(value[2:-1], "")

    return value


def _load_configs(path: Path) -> list[DeviceConfig]:
    data = yaml.safe_load(
        path.read_text(encoding="utf-8")
    ) or {}

    return [
        DeviceConfig(
            **{
                key: _resolve_env(value)
                for key, value in item.items()
            }
        )
        for item in data.get("devices", [])
    ]


def discover(config_path: Path) -> Inventory:
    devices = []

    for config in _load_configs(config_path):
        vendor = config.vendor.lower()

        if vendor == "cisco":
            collector = CiscoCollector(config)

        elif vendor in {"mikrotik", "routeros"}:
            collector = MikroTikCollector(config)

        else:
            raise ValueError(
                f"Unsupported vendor: {config.vendor}"
            )

        devices.append(collector.discover())

    return Inventory(devices=devices)


def write_inventory(
    inventory: Inventory,
    output_dir: Path,
) -> None:
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        output_dir / "inventory.json"
    ).write_text(
        json.dumps(
            inventory.to_dict(),
            indent=2,
        ),
        encoding="utf-8",
    )


def run(
    config_path: Path,
    output_dir: Path,
) -> Inventory:
    inventory = discover(config_path)

    write_inventory(
        inventory,
        output_dir,
    )

    return inventory