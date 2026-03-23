---
name: mikrotik-network
description: "Use when the user asks about MikroTik RouterOS devices: interfaces, routing, firewall rules, DHCP, wireless, CAPsMAN, system status, diagnostics, or configuration changes. Requires RouterOS v7+ REST API access."
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

## Available Tools (148 tools)

Tools marked `[WRITE]` modify device configuration and should be gated behind a Change Request in production environments.

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
9. **get_interface_traffic**(interface) — Real-time RX/TX rates on an interface

### IP Addresses
10. **get_ip_addresses** — All IP addresses assigned to interfaces
11. **add_ip_address**(address, interface) `[WRITE]` — Assign an IP address to an interface
12. **update_ip_address**(id, ...) `[WRITE]` — Modify an existing IP address entry
13. **remove_ip_address**(id) `[WRITE]` — Remove an IP address from an interface

### Routing
14. **get_routing_table** — Full IP routing table
15. **get_static_routes** — Statically configured routes with gateway and distance
16. **get_routing_rules** — Policy routing rules (table selection by src/dst/mark)
17. **get_routing_filters** — Routing filter rules for redistribution and filtering
18. **get_arp_table** — ARP table
19. **add_route**(dst_address, gateway) `[WRITE]` — Add a static route
20. **update_route**(id, ...) `[WRITE]` — Modify a static route
21. **remove_route**(id) `[WRITE]` — Delete a static route
22. **enable_route**(id) `[WRITE]` — Enable a disabled static route
23. **disable_route**(id) `[WRITE]` — Disable a static route without removing it

### Routing Protocols
24. **get_bgp_peers** — BGP peer connections and status
25. **get_bgp_sessions** — Active BGP sessions with state, remote AS, prefixes
26. **get_bgp_advertisements** — BGP advertised routes with prefix and path attributes
27. **get_ospf_neighbors** — OSPF neighbor adjacencies
28. **get_ospf_interfaces** — OSPF interface configuration
29. **get_ospf_instances** — OSPF instances with router-id, VRF, redistribution
30. **get_ospf_areas** — OSPF areas with type (backbone, stub, NSSA)
31. **get_ospf_lsa** — OSPF link-state database (LSDB) with LSA types

### Firewall — Filter
32. **get_firewall_filter** — All filter rules (input/forward/output)
33. **add_firewall_filter_rule**(chain, action, ...) `[WRITE]` — Add a filter rule
34. **update_firewall_filter_rule**(id, ...) `[WRITE]` — Modify a filter rule
35. **remove_firewall_filter_rule**(id) `[WRITE]` — Delete a filter rule
36. **enable_firewall_filter_rule**(id) `[WRITE]` — Enable a disabled filter rule
37. **disable_firewall_filter_rule**(id) `[WRITE]` — Disable a filter rule without removing it

### Firewall — NAT
38. **get_firewall_nat** — NAT rules (srcnat/dstnat)
39. **add_firewall_nat_rule**(chain, action, ...) `[WRITE]` — Add a NAT rule
40. **update_firewall_nat_rule**(id, ...) `[WRITE]` — Modify a NAT rule
41. **remove_firewall_nat_rule**(id) `[WRITE]` — Delete a NAT rule
42. **enable_firewall_nat_rule**(id) `[WRITE]` — Enable a disabled NAT rule
43. **disable_firewall_nat_rule**(id) `[WRITE]` — Disable a NAT rule without removing it

### Firewall — Other
44. **get_firewall_mangle** — Mangle rules
45. **get_firewall_raw** — Raw firewall rules (prerouting/output, before conntrack)
46. **get_firewall_layer7_protocols** — Layer 7 protocol matchers
47. **get_firewall_address_lists** — Address-list entries
48. **add_firewall_address_list_entry**(list, address) `[WRITE]` — Add an entry to an address list
49. **remove_firewall_address_list_entry**(id) `[WRITE]` — Remove an address list entry
50. **get_firewall_connections**(limit?) — Active connection tracking entries
51. **get_connection_tracking_config** — Conntrack settings: max entries, timeouts

### DNS
52. **get_dns_config** — DNS client configuration and cache stats
53. **get_dns_cache** — Cached DNS entries with TTL and resolved addresses
54. **get_dns_static** — Static DNS entries configured on the device
55. **set_dns_servers**(servers) `[WRITE]` — Set upstream DNS server addresses
56. **add_dns_static_entry**(name, address) `[WRITE]` — Add a static DNS record
57. **update_dns_static_entry**(id, ...) `[WRITE]` — Modify a static DNS record
58. **remove_dns_static_entry**(id) `[WRITE]` — Delete a static DNS record
59. **enable_dns_static_entry**(id) `[WRITE]` — Enable a disabled static DNS record
60. **disable_dns_static_entry**(id) `[WRITE]` — Disable a static DNS record without removing it
61. **flush_dns_cache**() `[WRITE]` — Flush the DNS resolver cache
62. **add_dns_forwarder**(servers, ...) `[WRITE]` — Add a DNS forwarder configuration

### DHCP
63. **get_dhcp_server_leases** — DHCP leases with MAC, IP, hostname, status
64. **get_dhcp_server_config** — DHCP server configuration
65. **get_dhcp_networks** — DHCP network pool definitions
66. **get_dhcp_client** — DHCP client instances with obtained address and lease status
67. **add_dhcp_lease**(address, mac_address) `[WRITE]` — Add a static DHCP lease
68. **remove_dhcp_lease**(id) `[WRITE]` — Remove a DHCP lease
69. **add_dhcp_network**(address, gateway) `[WRITE]` — Add a DHCP network definition
70. **remove_dhcp_network**(id) `[WRITE]` — Remove a DHCP network definition

### IP Pool
71. **get_ip_pools** — IP address pools with ranges (DHCP, VPN, HotSpot)
72. **get_ip_pool_used**(pool_name) — Addresses currently in use from a pool
73. **add_ip_pool**(name, ranges) `[WRITE]` — Create an IP address pool
74. **update_ip_pool**(id, ...) `[WRITE]` — Modify an IP address pool
75. **remove_ip_pool**(id) `[WRITE]` — Delete an IP address pool

### VLAN
76. **add_vlan**(name, vlan_id, interface) `[WRITE]` — Create a VLAN sub-interface
77. **update_vlan**(id, ...) `[WRITE]` — Modify a VLAN sub-interface
78. **remove_vlan**(id) `[WRITE]` — Remove a VLAN sub-interface

### Wireless
79. **get_wireless_interfaces** — Wireless interfaces and configuration
80. **get_wireless_registrations** — Connected wireless clients

### CAPsMAN / WiFi Controller
81. **get_capsman_interfaces** — CAPsMAN managed wireless interfaces
82. **get_capsman_registrations** — Clients registered via CAPsMAN

### IPsec VPN — Read
83. **get_ipsec_peers** — All IPsec peers with remote address, IKE version, profile
84. **get_ipsec_active_peers** — Currently established IPsec peer connections
85. **get_ipsec_policies** — IPsec policies (traffic selectors) with phase2 state
86. **get_ipsec_profiles** — Phase 1 profiles: encryption, hash, DH group, lifetime
87. **get_ipsec_proposals** — Phase 2 proposals: encryption, auth, PFS, lifetime
88. **get_ipsec_identities** — Auth method, peer binding, policy generation
89. **get_ipsec_installed_sa** — Installed Security Associations with SPI and state
90. **get_ipsec_statistics** — Global IPsec packet counts, errors, and failures

### IPsec VPN — Write
91. **add_ipsec_policy**(src_address, dst_address, peer, ...) `[WRITE]` — Add an IPsec traffic selector policy (peer parameter required)
92. **update_ipsec_policy**(id, ...) `[WRITE]` — Modify an IPsec policy
93. **remove_ipsec_policy**(id) `[WRITE]` — Delete an IPsec policy
94. **enable_ipsec_policy**(id) `[WRITE]` — Enable a disabled IPsec policy
95. **disable_ipsec_policy**(id) `[WRITE]` — Disable an IPsec policy without removing it
96. **update_ipsec_peer**(id, ...) `[WRITE]` — Modify an IPsec peer configuration
97. **update_ipsec_identity**(id, ...) `[WRITE]` — Modify an IPsec identity (auth method, pre-shared key, etc.)
98. **flush_ipsec_sa**() `[WRITE]` — Flush all installed IPsec Security Associations

### WireGuard
99. **get_wireguard_interfaces** — WireGuard interfaces with public key and listen port
100. **get_wireguard_peers** — WireGuard peers with allowed addresses and endpoint
101. **add_wireguard_interface**(name, listen_port) `[WRITE]` — Create a WireGuard interface
102. **remove_wireguard_interface**(id) `[WRITE]` — Delete a WireGuard interface
103. **add_wireguard_peer**(interface, public_key, allowed_address, ...) `[WRITE]` — Add a WireGuard peer
104. **update_wireguard_peer**(id, ...) `[WRITE]` — Modify a WireGuard peer
105. **remove_wireguard_peer**(id) `[WRITE]` — Delete a WireGuard peer
106. **enable_wireguard_peer**(id) `[WRITE]` — Enable a disabled WireGuard peer
107. **disable_wireguard_peer**(id) `[WRITE]` — Disable a WireGuard peer without removing it

### Spanning Tree / Bridge
108. **get_bridge_config** — Bridge interfaces with STP settings, priority, protocol mode
109. **get_bridge_hosts** — Bridge MAC address table (FDB) with learned MACs per port
110. **update_bridge_port**(id, ...) `[WRITE]` — Modify bridge port settings (horizon, pvid, edge, etc.)
111. **update_bridge_settings**(id, ...) `[WRITE]` — Modify bridge settings (STP, ageing-time, priority)

### Neighbor Discovery
112. **get_neighbors** — Discovered neighbors (LLDP/CDP/MNDP) with identity, IP, platform

### SNMP
113. **get_snmp_config** — SNMP service config: contact, location, engine-id, enabled state
114. **get_snmp_communities** — SNMP community strings with access rights and restrictions

### QoS / Queues
115. **get_simple_queues** — Simple queues with target, max-limit, burst, counters
116. **get_queue_tree** — Queue tree entries with parent, priority, rate limits
117. **get_queue_types** — Available queue disciplines (SFQ, PCQ, RED, etc.)

### Bonding / LACP
118. **get_bonding_interfaces** — Bonding interfaces with mode, slaves, link monitoring

### Certificates
119. **get_certificates** — Installed certificates with subject, issuer, expiry, key details

### PPP / VPN Sessions
120. **get_ppp_active_sessions** — Active PPP sessions (L2TP, SSTP, PPTP, OpenVPN)
121. **get_ppp_secrets** — PPP user accounts with service type and profile
122. **get_ppp_profiles** — PPP profiles with DNS, rate-limit, address pool
123. **get_l2tp_server_config** — L2TP server configuration and enabled state
124. **get_sstp_server_config** — SSTP server config: port, certificate, auth methods

### System & Monitoring
125. **get_system_logs**(topics?) — System log entries, optional topic filter
126. **get_ip_services** — Enabled IP services and ports
127. **update_ip_service**(id, ...) `[WRITE]` — Modify an IP service (port, disabled state)
128. **get_ntp_status** — NTP synchronization state
129. **get_system_health** — Hardware health: temperature, voltage, fan speed, PSU
130. **get_system_clock** — System clock: date, time, timezone
131. **get_system_packages** — Installed packages with version and enabled state
132. **get_system_scheduler** — Scheduled tasks/scripts with interval and next run
133. **get_system_scripts** — System scripts with source, policy, last run status

### Users
134. **get_users** — User accounts and groups
135. **add_user**(name, group, password) `[WRITE]` — Create a user account
136. **update_user**(id, ...) `[WRITE]` — Modify a user account
137. **remove_user**(id) `[WRITE]` — Delete a user account (admin deletion is blocked)
138. **enable_user**(id) `[WRITE]` — Enable a disabled user account
139. **disable_user**(id) `[WRITE]` — Disable a user account without removing it

### MPLS
140. **get_mpls_forwarding_table** — MPLS forwarding table with label and next-hop
141. **get_mpls_ldp_neighbors** — LDP neighbors with transport address and session state
142. **get_mpls_ldp_interfaces** — Interfaces participating in MPLS LDP

### Files
143. **get_files** — List files on the device (backups, exports, etc.)

### Diagnostics
144. **run_ping**(address, count?) — Ping a target address
145. **run_traceroute**(address) — Traceroute to a target address
146. **get_torch**(interface) — Real-time traffic flow on an interface

### Configuration & Backup
147. **export_config** — Export full router configuration as text
148. **create_backup**(name) `[WRITE]` — Create a binary backup file on the device

## Blocked Operations

The following operations are NOT supported via this MCP server for safety:

- `/system reset-configuration` — Factory reset
- `/system/shutdown` — Device shutdown
- `/system/reboot` — Device reboot (use RouterOS CLI directly)
- `/file remove` — File deletion
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
get_dhcp_server_config → get_dhcp_networks → get_dhcp_server_leases → get_dhcp_client → get_arp_table → get_ip_pools
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

### 13. Firewall Rule Deployment (WRITE)
```
get_firewall_filter → add_firewall_filter_rule → get_firewall_filter (verify)
```
Review existing rules, insert new rule at desired position, verify placement.

### 14. WireGuard VPN Provisioning (WRITE)
```
get_wireguard_interfaces → add_wireguard_interface → add_wireguard_peer → get_wireguard_peers (verify)
```
Create WireGuard interface, configure peer with public key and allowed addresses.

### 15. DNS Static Entry Management (WRITE)
```
get_dns_static → add_dns_static_entry → get_dns_static (verify)
```
Review existing static DNS records, add new entries, verify resolution.

### 16. DHCP Static Lease Provisioning (WRITE)
```
get_dhcp_server_leases → add_dhcp_lease → get_dhcp_server_leases (verify)
```
Check existing leases, bind a MAC address to a static IP, confirm reservation.

### 17. Configuration Backup (WRITE)
```
create_backup → get_files (verify)
```
Save binary backup to device, confirm file appears in file list.

### 18. User Management (WRITE)
```
get_users → add_user → get_users (verify)
```
Review existing accounts, create new user with appropriate group, confirm creation.

## Integration with Other NetClaw Skills

| Skill                        | Integration                                              |
|------------------------------|----------------------------------------------------------|
| servicenow-change-workflow   | Gate `[WRITE]` operations behind approved Change Request |
| gait-session-tracking        | Immutable audit trail for all operations                 |
| netbox-reconcile             | Reconcile MikroTik state against NetBox source-of-truth  |
| grafana-observability        | Correlate MikroTik metrics with Grafana dashboards       |
| packet-analysis              | Capture and analyze traffic from MikroTik interfaces     |
