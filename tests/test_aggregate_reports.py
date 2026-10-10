import json

from scripts.aggregate_reports import aggregate_reports


REPORT_NAMES = (
    "mikrotik-01.json",
    "cisco-01.json",
    "fortigate-01.json",
)


def write_report(report_dir, filename, status="COMPLIANT", controls=None):
    if controls is None:
        controls = [{
            "id": "test-control",
            "name": "Test control",
            "status": status,
        }]

    data = {
        "device": filename.removesuffix(".json"),
        "vendor": "test",
        "status": status,
        "controls": controls,
    }
    (report_dir / filename).write_text(
        json.dumps(data), encoding="utf-8"
    )


def write_all_reports(report_dir):
    for filename in REPORT_NAMES:
        write_report(report_dir, filename)


def test_all_compliant_reports_produce_compliant_summary(tmp_path):
    write_all_reports(tmp_path)
    result = aggregate_reports(tmp_path, tmp_path / "summary.json")

    assert result["status"] == "COMPLIANT"
    assert result["summary"]["reports_found"] == 3
    assert result["summary"]["controls"]["total"] == 3


def test_missing_report_is_unknown(tmp_path):
    write_report(tmp_path, "cisco-01.json")
    result = aggregate_reports(tmp_path, tmp_path / "summary.json")

    assert result["status"] == "UNKNOWN"
    assert "fortigate-01.json" in result["missing_reports"]
    assert result["summary"]["reports_found"] == 1


def test_invalid_json_is_error(tmp_path):
    write_all_reports(tmp_path)
    (tmp_path / "cisco-01.json").write_text(
        "{invalid", encoding="utf-8"
    )
    result = aggregate_reports(tmp_path, tmp_path / "summary.json")

    assert result["status"] == "ERROR"
    assert any(
        item["report"] == "cisco-01.json"
        for item in result["report_errors"]
    )
    assert result["summary"]["reports_found"] == 3


def test_empty_controls_are_error(tmp_path):
    write_all_reports(tmp_path)
    write_report(tmp_path, "cisco-01.json", controls=[])
    result = aggregate_reports(tmp_path, tmp_path / "summary.json")

    assert result["status"] == "ERROR"
    assert any(
        item["report"] == "cisco-01.json"
        for item in result["report_errors"]
    )


def test_noncompliant_control_prevents_compliant_device_status(tmp_path):
    write_all_reports(tmp_path)
    write_report(
        tmp_path,
        "cisco-01.json",
        controls=[{
            "id": "ssh",
            "name": "SSH",
            "status": "DRIFT",
        }],
    )
    result = aggregate_reports(tmp_path, tmp_path / "summary.json")

    assert result["status"] == "DRIFT"
    cisco = next(
        device for device in result["devices"]
        if device["report"] == "cisco-01.json"
    )
    assert cisco["status"] == "DRIFT"
