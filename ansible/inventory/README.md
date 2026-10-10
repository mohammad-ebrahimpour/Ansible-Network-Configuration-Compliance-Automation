No real credentials are stored in the inventory.

Credentials will be introduced through Ansible Vault in Stage 2.

Do not commit plaintext credentials.

Architecture

Ansible Control Node
                           |
          +----------------+----------------+
          |                |                |
          | SSH            | SSH            | HTTPS API
          v                v                v
      MikroTik           Cisco           FortiGate
      RouterOS           IOSv             FortiOS

The inventory is intentionally vendor-aware.

Vendor-specific connection settings belong to their respective groups and must not be placed in group_vars/all.yml.

---

WSL/Host
192.168.203.1
      │
      │ VMnet203
      │
      ▼
FortiGate port1
192.168.203.2

Management

FortiGate port2
192.168.174.2
       │
       │
       ▼
Cisco Gi0/1
192.168.174.200


---
┌─────────────────────┐
                     │   Ansible Control   │
                     │        WSL           │
                     └──────────┬──────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
            SSH               SSH              HTTPS
              │                 │                 │
              ▼                 ▼                 ▼
       ┌────────────┐    ┌────────────┐    ┌────────────┐
       │  MikroTik  │    │   Cisco    │    │ FortiGate  │
       │  RouterOS  │    │    IOSv    │    │   FortiOS  │
       │            │    │            │    │            │
     Mikrotik_public_ip  │192.168.174 │    │192.168.203 │
       └────────────┘    └─────┬──────┘    └─────┬──────┘
                               │                  │
                               └──────────────────┘

Ansible:

MikroTik
  ↓
ansible.netcommon.network_cli
  ↓
community.routeros.routeros


Cisco
  ↓
ansible.netcommon.network_cli
  ↓
cisco.ios.ios


FortiGate
  ↓
ansible.netcommon.httpapi
  ↓
fortinet.fortios.fortios
