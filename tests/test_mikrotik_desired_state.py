from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
DESIRED_STATE = ROOT / "ansible" / "desired_state" / "mikrotik.yml"


def load_desired_state():
    with DESIRED_STATE.open(encoding="utf-8") as file:
        return yaml.safe_load(file)


def test_mikrotik_desired_state_exists():
    data = load_desired_state()

    assert "desired_state" in data
    assert data["desired_state"]["vendor"] == "mikrotik"
    assert data["desired_state"]["platform"] == "routeros"


def test_mikrotik_identity():
    data = load_desired_state()

    assert data["desired_state"]["identity"]["name"] == "AnsibleMikrotik"


def test_mikrotik_firewall_baseline_exists():
    data = load_desired_state()

    baseline = data["desired_state"]["firewall"]["baseline"]

    assert len(baseline) >= 1


def test_mikrotik_firewall_baseline_has_required_fields():
    data = load_desired_state()

    baseline = data["desired_state"]["firewall"]["baseline"]

    required_fields = {
        "name",
        "chain",
        "action",
    }

    for rule in baseline:
        assert required_fields.issubset(rule.keys())