#!/usr/bin/env python3
"""Aggregate per-device network compliance reports into a network summary."""

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
OUTPUT = REPORT_DIR / "network-summary.json"

EXPECTED_REPORTS = {
    "mikrotik-01.json",
    "cisco-01.json",
    "fortigate-01.json",
}

VALID_STATUSES = {"COMPLIANT", "DRIFT", "ERROR", "UNKNOWN"}


def normalize_status(value):
    status = str(value or "UNKNOWN").upper()
    return status if status in VALID_STATUSES else "UNKNOWN"


def aggregate_reports(report_dir=REPORT_DIR, output=OUTPUT):
    devices = []
    errors = []
    missing = []
    totals = {
        "total": 0,
        "compliant": 0,
        "drift": 0,
        "error": 0,
        "unknown": 0,
    }
    reports_found = 0

    for filename in sorted(EXPECTED_REPORTS):
        path = report_dir / filename

        if not path.is_file():
            missing.append(filename)
            devices.append({
                "device": path.stem,
                "status": "UNKNOWN",
                "report": filename,
                "controls": [],
                "error": "Report file is missing",
            })
            continue

        reports_found += 1

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Report root must be a JSON object")

            raw_controls = data.get("controls")
            if not isinstance(raw_controls, list):
                raise ValueError("'controls' must be a JSON array")
            if not raw_controls:
                raise ValueError("Report contains no controls")

            controls = []
            for item in raw_controls:
                if not isinstance(item, dict):
                    raise ValueError("Each control must be a JSON object")

                status = normalize_status(item.get("status"))
                controls.append({
                    "id": item.get("id"),
                    "name": item.get("name", "Unnamed control"),
                    "status": status,
                })
                totals["total"] += 1
                totals[status.lower()] += 1

            device_status = normalize_status(data.get("status"))
            control_statuses = [control["status"] for control in controls]

            if device_status == "ERROR" or "ERROR" in control_statuses:
                device_status = "ERROR"
            elif device_status == "UNKNOWN" or "UNKNOWN" in control_statuses:
                device_status = "UNKNOWN"
            elif device_status != "COMPLIANT" or any(
                status != "COMPLIANT" for status in control_statuses
            ):
                device_status = "DRIFT"

            devices.append({
                "device": data.get("device", path.stem),
                "vendor": data.get("vendor", "UNKNOWN"),
                "platform": data.get("platform", "UNKNOWN"),
                "management_ip": data.get("management_ip"),
                "status": device_status,
                "report": filename,
                "controls": controls,
            })

        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append({"report": filename, "message": str(exc)})
            devices.append({
                "device": path.stem,
                "status": "ERROR",
                "report": filename,
                "controls": [],
                "error": str(exc),
            })

    statuses = [device["status"] for device in devices]

    if errors or "ERROR" in statuses:
        overall_status = "ERROR"
    elif missing or "UNKNOWN" in statuses:
        overall_status = "UNKNOWN"
    elif any(status != "COMPLIANT" for status in statuses):
        overall_status = "DRIFT"
    else:
        overall_status = "COMPLIANT"

    summary = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": overall_status,
        "summary": {
            "expected_devices": len(EXPECTED_REPORTS),
            "reports_found": reports_found,
            "devices_compliant": sum(
                device["status"] == "COMPLIANT" for device in devices
            ),
            "devices_drift": sum(
                device["status"] == "DRIFT" for device in devices
            ),
            "devices_error": sum(
                device["status"] == "ERROR" for device in devices
            ),
            "devices_unknown": sum(
                device["status"] == "UNKNOWN" for device in devices
            ),
            "controls": totals,
        },
        "missing_reports": missing,
        "report_errors": errors,
        "devices": devices,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return summary


def main():
    summary = aggregate_reports()
    controls = summary["summary"]["controls"]

    print(f"Network report: {OUTPUT.relative_to(ROOT)}")
    print(f"Overall status: {summary['status']}")
    print(
        f"Devices: {len(summary['devices'])} | "
        f"Controls: {controls['total']}"
    )
    print(f"Compliant controls: {controls['compliant']}")
    print(
        f"Drift: {controls['drift']} | Errors: {controls['error']} | "
        f"Unknown: {controls['unknown']}"
    )

    return 0 if summary["status"] == "COMPLIANT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
