from __future__ import annotations

import argparse
from pathlib import Path

from .engine import run


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Network discovery and inventory"
    )

    parser.add_argument(
        "--config",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output"),
    )

    args = parser.parse_args()

    inventory = run(
        args.config,
        args.output,
    )

    print("Discovery completed")
    print(
        f"Devices discovered: "
        f"{len(inventory.devices)}"
    )

    print(
        "Interfaces discovered: "
        f"{sum(len(device.interfaces) for device in inventory.devices)}"
    )

    print(
        f"Inventory: "
        f"{args.output / 'inventory.json'}"
    )


if __name__ == "__main__":
    main()