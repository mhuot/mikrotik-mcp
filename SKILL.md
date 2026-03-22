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

## Available Tools (80 tools)

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

### Neighbor Discovery
41. **get_neighbors** — Discovered neighbors (LLDP/CDP/MNDP) with identity, IP, platform

### Spanning Tree / Bridge
42. **get_bridge_config** — Bridge interfaces with STP settings, priority, protocol mode
43. **get_bridge_hosts** — Bridge MAC address table (FDB) with learned MACs per port

### SNMP
44. **get_snmp_config** — SNMP service config: contact, location, engine-id, enabled state
45. **get_snmp_communities** — SNMP community strings with access rights and restrictions

### Connection Tracking
46. **get_firewall_connections**(limit?) — Active connection tracking entries
47. **get_connection_tracking_config** — Conntrack settings: max entries, timeouts

### QoS / Queues
48. **get_simple_queues** — Simple queues with target, max-limit, burst, counters
49. **get_queue_tree** — Queue tree entries with parent, priority, rate limits
50. **get_queue_types** — Available queue disciplines (SFQ, PCQ, RED, etc.)

### Bonding / LACP
51. **get_bonding_interfaces** — Bonding interfaces with mode, slaves, link monitoring

### System Health & Environment
52. **get_system_health** — Hardware health: temperature, voltage, fan speed, PSU
53. **get_system_clock** — System clock: date, time, timezone
54. **get_system_packages** — Installed packages with version and enabled state
55. **get_system_scheduler** — Scheduled tasks/scripts with interval and next run
56. **get_system_scripts** — System scripts with source, policy, last run status

### Certificates
57. **get_certificates** — Installed certificates with subject, issuer, expiry, key details

### IP Pool
58. **get_ip_pools** — IP address pools with ranges (DHCP, VPN, HotSpot)
59. **get_ip_pool_used**(pool_name) — Addresses currently in use from a pool

### PPP / VPN Sessions
60. **get_ppp_active_sessions** — Active PPP sessions (L2TP, SSTP, PPTP, OpenVPN)
61. **get_ppp_secrets** — PPP user accounts with service type and profile
62. **get_ppp_profiles** — PPP profiles with DNS, rate-limit, address pool
63. **get_l2tp_server_config** — L2TP server configuration and enabled state
64. **get_sstp_server_config** — SSTP server config: port, certificate, auth methods

### Routing Protocol Detail
65. **get_ospf_instances** — OSPF instances with router-id, VRF, redistribution
66. **get_ospf_areas** — OSPF areas with type (backbone, stub, NSSA)
67. **get_ospf_lsa** — OSPF link-state database (LSDB) with LSA types
68. **get_bgp_sessions** — Active BGP sessions with state, remote AS, prefixes
69. **get_bgp_advertisements** — BGP advertised routes with prefix and path attributes
70. **get_routing_rules** — Policy routing rules (table selection by src/dst/mark)
71. **get_routing_filters** — Routing filter rules for redistribution and filtering

### Extended Diagnostics
72. **run_traceroute**(address) — Traceroute to a target address
73. **get_dns_cache** — Cached DNS entries with TTL and resolved addresses
74. **get_dns_static** — Static DNS entries configured on the device

### MPLS
75. **get_mpls_forwarding_table** — MPLS forwarding table with label and next-hop
76. **get_mpls_ldp_neighbors** — LDP neighbors with transport address and session state
77. **get_mpls_ldp_interfaces** — Interfaces participating in MPLS LDP

### Additional
78. **get_static_routes** — Statically configured routes with gateway and distance
79. **get_dhcp_client** — DHCP client instances with obtained address and lease status
80. **get_firewall_raw** — Raw firewall rules (prerouting/output, before conntrack)

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
get_identity → get_system_resources → get_system_health → get_interfaces → get_ip_services
```
Review hostname, CPU/memory, hardware temps, interface status, and exposed services.

### 2. Routing Audit
```
get_routing_table → get_bgp_peers → get_bgp_sessions → get_ospf_neighbors → get_ospf_lsa
```
Verify routes, check BGP peer state, review LSDB, confirm OSPF adjacencies.

### 3. Firewall Review
```
get_firewall_filter → get_firewall_nat → get_firewall_raw → get_firewall_address_lists → get_firewall_connections
```
Audit filter rules, NAT, raw rules, address-lists, and active connections.

### 4. DHCP Troubleshooting
```
get_dhcp_server_config → get_dhcp_server_leases → get_dhcp_client → get_arp_table → get_ip_pools
```
Check DHCP pool config, current leases, client status, ARP entries, and pool usage.

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

### 8. Topology Discovery
```
get_neighbors → get_bridge_hosts → get_arp_table → get_interfaces
```
Discover adjacent devices via LLDP/CDP/MNDP, map MAC table, correlate with ARP and interfaces.

### 9. Security Audit
```
get_ip_services → get_snmp_config → get_snmp_communities → get_users → get_certificates → get_firewall_filter
```
Review exposed services, SNMP security, user accounts, certificate expiry, and firewall posture.

### 10. VPN Session Monitoring
```
get_ppp_active_sessions → get_l2tp_server_config → get_sstp_server_config → get_ip_pool_used
```
Monitor active VPN sessions, verify server config, and check IP pool utilization.

### 11. QoS Analysis
```
get_simple_queues → get_queue_tree → get_queue_types
```
Review bandwidth limits, queue hierarchy, and scheduling disciplines.

### 12. MPLS Verification
```
get_mpls_forwarding_table → get_mpls_ldp_neighbors → get_mpls_ldp_interfaces
```
Verify label switching, LDP adjacencies, and participating interfaces.

## Integration with Other NetClaw Skills

| Skill                        | Integration                                              |
|------------------------------|----------------------------------------------------------|
| servicenow-change-workflow   | Gate configuration changes behind approved Change Request |
| gait-session-tracking        | Immutable audit trail for all operations                 |
| netbox-reconcile             | Reconcile MikroTik state against NetBox source-of-truth  |
| grafana-observability        | Correlate MikroTik metrics with Grafana dashboards       |
| packet-analysis              | Capture and analyze traffic from MikroTik interfaces     |
