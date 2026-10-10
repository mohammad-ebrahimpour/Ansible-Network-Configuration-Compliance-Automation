Ansible Multi-Vendor Network Configuration & Compliance Automation

Ansible-based framework for multi-vendor network automation, configuration compliance, drift detection, and controlled remediation.

Scope

- MikroTik RouterOS — SSH / Network CLI
- Cisco IOS — SSH / Network CLI
- Fortinet FortiOS — HTTPS / HTTPAPI

The design separates desired state and compliance policy from vendor-specific execution.

Architecture

Inventory
   ↓
Discovery
   ↓
Normalize
   ↓
Compliance
   ↓
Desired State
   ↓
Remediation
   ↓
Validation
   ↓
Reporting
   ↓
CI/CD

Key Capabilities

- Multi-vendor network automation
- Configuration and security compliance
- Configuration drift detection
- Declarative desired-state management
- Idempotent remediation
- Post-change validation
- Structured JSON reporting
- Centralized multi-vendor JSON reporting
- Ansible Vault credential management
- Automated testing and CI/CD
- Vendor-specific automation with a common control model

The report aggregator combines per-device JSON reports into `reports/network-summary.json`. Run it with `python scripts/aggregate_reports.py`.

Design Principles

READ → COMPARE → CHANGE → VALIDATE

Device state is collected before changes are made. Remediation is applied only where required, followed by independent validation.

Project Structure

ansible/
├── desired_state/
├── inventory/
└── playbooks/

filter_plugins/
tests/
reports/
.github/workflows/

Security

Credentials are managed through Ansible Vault and are excluded from source control.

No device credentials or Vault passwords are stored in the repository.

Quality

GitHub Actions performs:

- Unit testing
- Desired-state validation
- Ansible syntax checks
- Ansible Lint
- Pull Request validation

Roadmap

- Expanded compliance controls
- NetBox integration
- Integration testing
- Cloud network automation
- Infrastructure as Code
- API-driven automation
- AI-assisted Network Operations

Version

v1.2 — Multi-Vendor Network Configuration & Compliance Automation