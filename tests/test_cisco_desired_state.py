from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
DESIRED_STATE = ROOT / "ansible" / "desired_state" / "cisco.yml"


def load_desired_state():
    with DESIRED_STATE.open(encoding="utf-8") as file:
        return yaml.safe_load(file)


def test_cisco_desired_state_exists():
    data = load_desired_state()

    assert "desired_state" in data
    assert data["desired_state"]["vendor"] == "cisco"
    assert data["desired_state"]["platform"] == "ios"


def test_cisco_ssh_enabled():
    data = load_desired_state()

    assert data["desired_state"]["ssh"]["enabled"] is True


def test_cisco_ssh_version():
    data = load_desired_state()

    assert data["desired_state"]["ssh"]["version"] == 2


def test_cisco_management_protocol():
    data = load_desired_state()

    assert data["desired_state"]["management"]["protocol"] == "ssh"


def test_cisco_controls_exist():
    data = load_desired_state()

    controls = data["desired_state"]["controls"]

    assert len(controls) >= 2