---
name: mikrotik-network
description: "Use when the user asks about MikroTik RouterOS devices: interfaces, routing, firewall rules, DHCP, wireless, CAPsMAN, system status, or diagnostics. Requires RouterOS v7+ REST API access."
user-invocable: true
metadata:
  { "openclaw": { "requires": { "bins": ["python3"], "env": ["MIKROTIK_HOST", "MIKROTIK_USER", "MIKROTIK_PASSWORD"] } } }
---

# MikroTik RouterOS Network Operations

## MCP Server

| Field          | Value                                |
|----------------|--------------------------------------|
| **Script**     | `mikrotik_mcp.py`                    |
| **Transport**  | stdio                                |
| **Python**     | 3.10+                                |
| **Protocol**   | RouterOS REST API (HTTPS)            |
| **RouterOS**   | v7.0+ required                       |

## Available Tools (40 tools)

### Device Information
1. **get_identity** — Get device hostname
2. **get_system_resources** — CPU, memory, uptime, version, board, architecture
3. **get_routerboard_info** — Hardware model, serial number, firmware versions

### Interfaces
4. **get_interfaces** — All interfaces with status, type, MAC, traffic counters
5. **get_interface_detail**(name) — Detailed info for a specific interface
6. **get_ethernet_interfaces** — Ethernet interfaces with speed, duplex, PoE
7. **get_bridge_ports** — Bridge port membership
8. **get_vlans** — VLAN interfaces

### IP & Routing
9. **get_ip_addresses** — All IP addresses assigned to interfaces
10. **get_routing_table** — Full IP routing table
11. **get_arp_table** — ARP table
12. **get_dns_config** — DNS client configuration and cache stats

### Routing Protocols
13. **get_bgp_peers** — BGP peer connections and status
14. **get_ospf_neighbors** — OSPF neighbor adjacencies
15. **get_ospf_interfaces** — OSPF interface configuration

### Firewall
16. **get_firewall_filter** — All filter rules (input/forward/output)
17. **get_firewall_nat** — NAT rules (srcnat/dstnat)
18. **get_firewall_mangle** — Mangle rules
19. **get_firewall_address_lists** — Address-list entries

### DHCP
20. **get_dhcp_server_leases** — DHCP leases with MAC, IP, hostname, status
21. **get_dhcp_server_config** — DHCP server configuration

### Wireless
22. **get_wireless_interfaces** — Wireless interfaces and configuration
23. **get_wireless_registrations** — Connected wireless clients

### System & Monitoring
24. **get_system_logs**(topics?) — System log entries, optional topic filter
25. **get_ip_services** — Enabled IP services and ports
26. **get_users** — User accounts and groups
27. **get_ntp_status** — NTP synchronization state

### Diagnostics
28. **run_ping**(address, count?) — Ping a target address
29. **get_torch**(interface) — Real-time traffic flow on an interface

### Configuration
30. **export_config** — Export full router configuration

### CAPsMAN / WiFi Controller
31. **get_capsman_interfaces** — CAPsMAN managed wireless interfaces
32. **get_capsman_registrations** — Clients registered via CAPsMAN

### IPsec VPN
33. **get_ipsec_peers** — All IPsec peers with remote address, IKE version, profile
34. **get_ipsec_active_peers** — Currently established IPsec peer connections
35. **get_ipsec_policies** — IPsec policies (traffic selectors) with phase2 state
36. **get_ipsec_profiles** — Phase 1 profiles: encryption, hash, DH group, lifetime
37. **get_ipsec_proposals** — Phase 2 proposals: encryption, auth, PFS, lifetime
38. **get_ipsec_identities** — Auth method, peer binding, policy generation
39. **get_ipsec_installed_sa** — Installed Security Associations with SPI and state
40. **get_ipsec_statistics** — Global IPsec packet counts, errors, and failures

## Blocked Commands

The following operations are NOT supported via this MCP server for safety:

- `/system reset-configuration` — Factory reset
- `/system/shutdown` — Device shutdown
- `/system/reboot` — Device reboot (use with caution via CLI)
- `/file remove` — File deletion
- `/user remove` — User deletion
- Firmware upgrade/downgrade operations

## Workflows

### 1. Device Health Check
```
get_identity → get_system_resources → get_interfaces → get_ip_services
```
Review hostname, CPU/memory usage, interface status, and exposed services.

### 2. Routing Audit
```
get_routing_table → get_bgp_peers → get_ospf_neighbors → get_ospf_interfaces
```
Verify routes, check BGP peer state, confirm OSPF adjacencies.

### 3. Firewall Review
```
get_firewall_filter → get_firewall_nat → get_firewall_address_lists
```
Audit filter rules, NAT translations, and address-list membership.

### 4. DHCP Troubleshooting
```
get_dhcp_server_config → get_dhcp_server_leases → get_arp_table
```
Check DHCP pool config, current leases, and ARP entries.

### 5. Wireless Client Analysis
```
get_wireless_interfaces → get_wireless_registrations → get_capsman_registrations
```
Review wireless config and connected clients (standalone or CAPsMAN).

### 6. IPsec VPN Troubleshooting
```
get_ipsec_peers → get_ipsec_active_peers → get_ipsec_installed_sa → get_ipsec_statistics
```
Check peer config, verify tunnels are established, review SA state, and inspect error counters.

### 7. IPsec VPN Audit
```
get_ipsec_profiles → get_ipsec_proposals → get_ipsec_identities → get_ipsec_policies
```
Review Phase 1/Phase 2 crypto settings, authentication config, and traffic selectors.

## Integration with Other NetClaw Skills

| Skill                        | Integration                                              |
|------------------------------|----------------------------------------------------------|
| servicenow-change-workflow   | Gate configuration changes behind approved Change Request |
| gait-session-tracking        | Immutable audit trail for all operations                 |
| netbox-reconcile             | Reconcile MikroTik state against NetBox source-of-truth  |
| grafana-observability        | Correlate MikroTik metrics with Grafana dashboards       |
| packet-analysis              | Capture and analyze traffic from MikroTik interfaces     |
