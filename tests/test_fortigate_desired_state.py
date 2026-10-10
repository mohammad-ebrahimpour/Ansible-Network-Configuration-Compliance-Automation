from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
DESIRED_STATE = ROOT / "ansible" / "desired_state" / "fortigate.yml"


def load_desired_state():
    with DESIRED_STATE.open(encoding="utf-8") as file:
        return yaml.safe_load(file)


def test_fortigate_desired_state_exists():
    data = load_desired_state()

    assert "desired_state" in data
    assert data["desired_state"]["vendor"] == "fortinet"
    assert data["desired_state"]["platform"] == "fortios"


def test_fortigate_vdom():
    data = load_desired_state()

    assert data["desired_state"]["vdom"] == "root"


def test_fortigate_internet_access_disabled():
    data = load_desired_state()

    assert data["desired_state"]["internet_access"]["enabled"] is False


def test_fortigate_controls_exist():
    data = load_desired_state()

    controls = data["desired_state"]["controls"]

    assert len(controls) >= 3