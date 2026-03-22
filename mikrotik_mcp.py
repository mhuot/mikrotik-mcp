#!/usr/bin/env python3
"""
MikroTik RouterOS MCP Server

Provides MCP tools for managing MikroTik devices via the RouterOS REST API (v7+)
and the RouterOS API protocol (v6/v7) via librouteros.

Copyright 2026 Michael Huot

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
import os
from typing import Optional

import requests
import urllib3
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Suppress InsecureRequestWarning when SSL verification is disabled
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

mcp = FastMCP("mikrotik-mcp")


def _get_connection_params():
    """Build connection parameters from environment variables."""
    host = os.environ.get("MIKROTIK_HOST", "192.168.88.1")
    port = os.environ.get("MIKROTIK_PORT", "443")
    use_ssl = os.environ.get("MIKROTIK_USE_SSL", "true").lower() == "true"
    verify_ssl = os.environ.get("MIKROTIK_VERIFY_SSL", "false").lower() == "true"
    user = os.environ.get("MIKROTIK_USER", "admin")
    password = os.environ.get("MIKROTIK_PASSWORD", "")

    scheme = "https" if use_ssl else "http"
    base_url = f"{scheme}://{host}:{port}/rest"

    return base_url, user, password, verify_ssl


def _rest_get(path: str, params: Optional[dict] = None) -> dict:
    """Make a GET request to the RouterOS REST API."""
    base_url, user, password, verify_ssl = _get_connection_params()
    url = f"{base_url}{path}"
    resp = requests.get(
        url, auth=(user, password), verify=verify_ssl, params=params, timeout=30
    )
    resp.raise_for_status()
    return resp.json()


def _rest_post(path: str, data: Optional[dict] = None) -> dict:
    """Make a POST request to the RouterOS REST API."""
    base_url, user, password, verify_ssl = _get_connection_params()
    url = f"{base_url}{path}"
    resp = requests.post(
        url, auth=(user, password), verify=verify_ssl, json=data, timeout=30
    )
    resp.raise_for_status()
    return resp.json()


def _rest_patch(path: str, item_id: str, data: dict) -> dict:
    """Make a PATCH request to the RouterOS REST API."""
    base_url, user, password, verify_ssl = _get_connection_params()
    url = f"{base_url}{path}/{item_id}"
    resp = requests.patch(
        url, auth=(user, password), verify=verify_ssl, json=data, timeout=30
    )
    resp.raise_for_status()
    return resp.json()


def _rest_delete(path: str, item_id: str) -> dict:
    """Make a DELETE request to the RouterOS REST API."""
    base_url, user, password, verify_ssl = _get_connection_params()
    url = f"{base_url}{path}/{item_id}"
    resp = requests.delete(url, auth=(user, password), verify=verify_ssl, timeout=30)
    resp.raise_for_status()
    if resp.content:
        return resp.json()
    return {"status": "deleted"}


# ---------------------------------------------------------------------------
# Device Info
# ---------------------------------------------------------------------------


@mcp.tool()
def get_identity() -> str:
    """Get the device identity (hostname)."""
    result = _rest_get("/system/identity")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_system_resources() -> str:
    """Get system resource usage: CPU, memory, uptime, version, board, architecture."""
    result = _rest_get("/system/resource")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_routerboard_info() -> str:
    """Get RouterBOARD hardware information: model, serial, firmware versions."""
    result = _rest_get("/system/routerboard")
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Interfaces
# ---------------------------------------------------------------------------


@mcp.tool()
def get_interfaces() -> str:
    """List all interfaces with their status, type, MAC address, and traffic counters."""
    result = _rest_get("/interface")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_interface_detail(name: str) -> str:
    """Get detailed information for a specific interface by name."""
    interfaces = _rest_get("/interface")
    matched = [i for i in interfaces if i.get("name") == name]
    if not matched:
        return json.dumps({"error": f"Interface '{name}' not found"})
    return json.dumps(matched[0], indent=2)


@mcp.tool()
def get_ethernet_interfaces() -> str:
    """List all ethernet interfaces with speed, duplex, and PoE status."""
    result = _rest_get("/interface/ethernet")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_bridge_ports() -> str:
    """List all bridge ports and their bridge membership."""
    result = _rest_get("/interface/bridge/port")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_vlans() -> str:
    """List all VLAN interfaces."""
    result = _rest_get("/interface/vlan")
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# IP Addresses & Routing
# ---------------------------------------------------------------------------


@mcp.tool()
def get_ip_addresses() -> str:
    """List all IP addresses assigned to interfaces."""
    result = _rest_get("/ip/address")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_routing_table() -> str:
    """Get the full IP routing table."""
    result = _rest_get("/ip/route")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_arp_table() -> str:
    """Get the ARP table."""
    result = _rest_get("/ip/arp")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_dns_config() -> str:
    """Get DNS client configuration and cache statistics."""
    result = _rest_get("/ip/dns")
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Routing Protocols
# ---------------------------------------------------------------------------


@mcp.tool()
def get_bgp_peers() -> str:
    """List BGP peer connections and their status (RouterOS v7 routing)."""
    result = _rest_get("/routing/bgp/connection")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_ospf_neighbors() -> str:
    """List OSPF neighbors and adjacency state."""
    result = _rest_get("/routing/ospf/neighbor")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_ospf_interfaces() -> str:
    """List OSPF interfaces and their configuration."""
    result = _rest_get("/routing/ospf/interface")
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Firewall
# ---------------------------------------------------------------------------


@mcp.tool()
def get_firewall_filter() -> str:
    """List all firewall filter rules (input, forward, output chains)."""
    result = _rest_get("/ip/firewall/filter")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_firewall_nat() -> str:
    """List all NAT rules (srcnat, dstnat)."""
    result = _rest_get("/ip/firewall/nat")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_firewall_mangle() -> str:
    """List all mangle rules."""
    result = _rest_get("/ip/firewall/mangle")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_firewall_address_lists() -> str:
    """List all firewall address-list entries."""
    result = _rest_get("/ip/firewall/address-list")
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# DHCP
# ---------------------------------------------------------------------------


@mcp.tool()
def get_dhcp_server_leases() -> str:
    """List all DHCP server leases with MAC, IP, hostname, and status."""
    result = _rest_get("/ip/dhcp-server/lease")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_dhcp_server_config() -> str:
    """Get DHCP server configuration."""
    result = _rest_get("/ip/dhcp-server")
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Wireless
# ---------------------------------------------------------------------------


@mcp.tool()
def get_wireless_interfaces() -> str:
    """List wireless interfaces and their configuration."""
    try:
        result = _rest_get("/interface/wireless")
        return json.dumps(result, indent=2)
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code == 404:
            return json.dumps(
                {"error": "Wireless package not installed or no wireless interfaces"}
            )
        raise


@mcp.tool()
def get_wireless_registrations() -> str:
    """List currently connected wireless clients."""
    try:
        result = _rest_get("/interface/wireless/registration-table")
        return json.dumps(result, indent=2)
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code == 404:
            return json.dumps({"error": "Wireless package not installed"})
        raise


# ---------------------------------------------------------------------------
# System Services & Monitoring
# ---------------------------------------------------------------------------


@mcp.tool()
def get_system_logs(topics: Optional[str] = None) -> str:
    """Get system log entries. Optionally filter by topic (e.g. 'firewall', 'dhcp', 'wireless')."""
    result = _rest_get("/log")
    if topics:
        topic_filter = topics.lower()
        result = [
            entry for entry in result if topic_filter in entry.get("topics", "").lower()
        ]
    # Return last 100 entries to avoid overwhelming output
    return json.dumps(result[-100:], indent=2)


@mcp.tool()
def get_ip_services() -> str:
    """List enabled IP services (API, SSH, Winbox, WWW, etc.) and their ports."""
    result = _rest_get("/ip/service")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_users() -> str:
    """List all user accounts and their groups."""
    result = _rest_get("/user")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_ntp_status() -> str:
    """Get NTP client status and synchronization state."""
    result = _rest_get("/system/ntp/client")
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Network Diagnostics
# ---------------------------------------------------------------------------


@mcp.tool()
def run_ping(address: str, count: int = 4) -> str:
    """Run ping to a target address. Returns results for the specified count."""
    # RouterOS REST API doesn't have a direct ping endpoint that returns results
    # synchronously. Use the /tool/ping approach with a POST.
    try:
        result = _rest_post("/tool/ping", {"address": address, "count": str(count)})
        return json.dumps(result, indent=2)
    except requests.exceptions.HTTPError:
        return json.dumps(
            {
                "info": "Ping via REST may not be supported on all versions. "
                "Use SSH/CLI for interactive ping."
            }
        )


@mcp.tool()
def get_torch(interface: str) -> str:
    """Get real-time traffic flow data (torch) for an interface."""
    try:
        result = _rest_post("/tool/torch", {"interface": interface, "duration": "5"})
        return json.dumps(result, indent=2)
    except requests.exceptions.HTTPError:
        return json.dumps(
            {
                "info": "Torch via REST may require RouterOS 7.x. "
                "Use SSH/CLI for interactive torch."
            }
        )


# ---------------------------------------------------------------------------
# Configuration Export
# ---------------------------------------------------------------------------


@mcp.tool()
def export_config() -> str:
    """Export the full router configuration as text."""
    try:
        result = _rest_post("/export", {})
        return json.dumps(result, indent=2)
    except requests.exceptions.HTTPError:
        return json.dumps(
            {"info": "Config export via REST may not be available. Use SSH: /export"}
        )


# ---------------------------------------------------------------------------
# CAPsMAN / WiFi (v7)
# ---------------------------------------------------------------------------


@mcp.tool()
def get_capsman_interfaces() -> str:
    """List CAPsMAN managed wireless interfaces (controller mode)."""
    try:
        result = _rest_get("/caps-man/interface")
        return json.dumps(result, indent=2)
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code == 404:
            return json.dumps({"error": "CAPsMAN not configured or not available"})
        raise


@mcp.tool()
def get_capsman_registrations() -> str:
    """List clients registered via CAPsMAN."""
    try:
        result = _rest_get("/caps-man/registration-table")
        return json.dumps(result, indent=2)
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code == 404:
            return json.dumps({"error": "CAPsMAN not configured or not available"})
        raise


# ---------------------------------------------------------------------------
# IPsec VPN
# ---------------------------------------------------------------------------


@mcp.tool()
def get_ipsec_peers() -> str:
    """List all IPsec peers with remote address, IKE version, profile, and enabled state."""
    result = _rest_get("/ip/ipsec/peer")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_ipsec_active_peers() -> str:
    """List currently established IPsec peer connections with uptime and SA counts."""
    result = _rest_get("/ip/ipsec/active-peers")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_ipsec_policies() -> str:
    """List all IPsec policies (traffic selectors) with src/dst, peer, action, and phase2 state."""
    result = _rest_get("/ip/ipsec/policy")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_ipsec_profiles() -> str:
    """List IPsec Phase 1 profiles (IKE proposals): encryption, hash, DH group, lifetime."""
    result = _rest_get("/ip/ipsec/profile")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_ipsec_proposals() -> str:
    """List IPsec Phase 2 proposals: encryption, auth algorithms, PFS group, lifetime."""
    result = _rest_get("/ip/ipsec/proposal")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_ipsec_identities() -> str:
    """List IPsec identities: auth method, peer binding, policy generation."""
    result = _rest_get("/ip/ipsec/identity")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_ipsec_installed_sa() -> str:
    """List installed IPsec Security Associations with SPI, state, encryption, and traffic stats."""
    result = _rest_get("/ip/ipsec/installed-sa")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_ipsec_statistics() -> str:
    """Get global IPsec statistics: packet counts, errors, and failures."""
    result = _rest_get("/ip/ipsec/statistics")
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Neighbor Discovery (LLDP/CDP equivalent)
# ---------------------------------------------------------------------------


@mcp.tool()
def get_neighbors() -> str:
    """List discovered neighbors (LLDP/CDP/MNDP) with identity, IP, interface, platform."""
    result = _rest_get("/ip/neighbor")
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Spanning Tree (Bridge STP)
# ---------------------------------------------------------------------------


@mcp.tool()
def get_bridge_config() -> str:
    """List bridge interfaces with STP settings, priority, and protocol mode."""
    result = _rest_get("/interface/bridge")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_bridge_hosts() -> str:
    """Get bridge MAC address table (FDB) with learned MACs per port."""
    result = _rest_get("/interface/bridge/host")
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# SNMP
# ---------------------------------------------------------------------------


@mcp.tool()
def get_snmp_config() -> str:
    """Get SNMP service configuration: contact, location, engine-id, enabled state."""
    result = _rest_get("/snmp")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_snmp_communities() -> str:
    """List SNMP community strings with access rights and address restrictions."""
    result = _rest_get("/snmp/community")
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Connection Tracking (Active Sessions)
# ---------------------------------------------------------------------------


@mcp.tool()
def get_firewall_connections(limit: int = 100) -> str:
    """List active connection tracking entries (like 'show conn' on ASA). Returns last N entries."""
    result = _rest_get("/ip/firewall/connection")
    return json.dumps(result[-limit:], indent=2)


@mcp.tool()
def get_connection_tracking_config() -> str:
    """Get connection tracking settings: enabled, max entries, timeouts."""
    result = _rest_get("/ip/firewall/connection/tracking")
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# QoS / Queues
# ---------------------------------------------------------------------------


@mcp.tool()
def get_simple_queues() -> str:
    """List simple queues with target, max-limit, burst, and traffic counters."""
    result = _rest_get("/queue/simple")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_queue_tree() -> str:
    """List queue tree entries with parent, priority, and rate limits."""
    result = _rest_get("/queue/tree")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_queue_types() -> str:
    """List available queue disciplines (SFQ, PCQ, RED, etc.)."""
    result = _rest_get("/queue/type")
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Bonding / LACP (Link Aggregation)
# ---------------------------------------------------------------------------


@mcp.tool()
def get_bonding_interfaces() -> str:
    """List bonding (LACP/balance) interfaces with mode, slaves, and link monitoring."""
    try:
        result = _rest_get("/interface/bonding")
        return json.dumps(result, indent=2)
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code == 404:
            return json.dumps({"error": "No bonding interfaces configured"})
        raise


# ---------------------------------------------------------------------------
# System Health & Environment
# ---------------------------------------------------------------------------


@mcp.tool()
def get_system_health() -> str:
    """Get hardware health: temperature, voltage, fan speed, PSU status."""
    try:
        result = _rest_get("/system/health")
        return json.dumps(result, indent=2)
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code == 404:
            return json.dumps(
                {"error": "Health monitoring not available on this model"}
            )
        raise


@mcp.tool()
def get_system_clock() -> str:
    """Get system clock settings: date, time, timezone."""
    result = _rest_get("/system/clock")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_system_packages() -> str:
    """List installed packages with version and enabled state."""
    result = _rest_get("/system/package")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_system_scheduler() -> str:
    """List scheduled tasks/scripts with interval, next run, and policy."""
    result = _rest_get("/system/scheduler")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_system_scripts() -> str:
    """List all system scripts with source, policy, and last run status."""
    result = _rest_get("/system/script")
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Certificates
# ---------------------------------------------------------------------------


@mcp.tool()
def get_certificates() -> str:
    """List installed certificates with subject, issuer, expiry, and key details."""
    result = _rest_get("/certificate")
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# IP Pool
# ---------------------------------------------------------------------------


@mcp.tool()
def get_ip_pools() -> str:
    """List IP address pools with ranges (used by DHCP, VPN, HotSpot)."""
    result = _rest_get("/ip/pool")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_ip_pool_used(pool_name: str) -> str:
    """List addresses currently in use from a specific IP pool."""
    result = _rest_get("/ip/pool/used")
    filtered = [e for e in result if e.get("pool") == pool_name]
    return json.dumps(filtered, indent=2)


# ---------------------------------------------------------------------------
# PPP / VPN Sessions (L2TP, SSTP, PPTP, OpenVPN)
# ---------------------------------------------------------------------------


@mcp.tool()
def get_ppp_active_sessions() -> str:
    """List active PPP sessions (L2TP, SSTP, PPTP, OpenVPN) with user, IP, uptime."""
    result = _rest_get("/ppp/active")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_ppp_secrets() -> str:
    """List PPP user accounts with service type, profile, and local/remote address."""
    result = _rest_get("/ppp/secret")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_ppp_profiles() -> str:
    """List PPP profiles with DNS, rate-limit, address pool assignments."""
    result = _rest_get("/ppp/profile")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_l2tp_server_config() -> str:
    """Get L2TP server configuration and enabled state."""
    result = _rest_get("/interface/l2tp-server/server")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_sstp_server_config() -> str:
    """Get SSTP server configuration: port, certificate, auth methods."""
    result = _rest_get("/interface/sstp-server/server")
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Routing Protocol Detail (OSPF/BGP deep dive)
# ---------------------------------------------------------------------------


@mcp.tool()
def get_ospf_instances() -> str:
    """List OSPF instances with router-id, VRF, and redistribution config."""
    result = _rest_get("/routing/ospf/instance")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_ospf_areas() -> str:
    """List OSPF areas with type (backbone, stub, NSSA) and area-id."""
    result = _rest_get("/routing/ospf/area")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_ospf_lsa() -> str:
    """Get OSPF link-state database (LSDB) with LSA types and advertising routers."""
    result = _rest_get("/routing/ospf/lsa")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_bgp_sessions() -> str:
    """List active BGP sessions with state, remote AS, prefixes, and uptime."""
    result = _rest_get("/routing/bgp/session")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_bgp_advertisements() -> str:
    """List BGP advertised routes with prefix, next-hop, and path attributes."""
    result = _rest_get("/routing/bgp/advertisement")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_routing_rules() -> str:
    """List policy routing rules (routing table selection based on src/dst/mark)."""
    result = _rest_get("/routing/rule")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_routing_filters() -> str:
    """List routing filter rules used for route redistribution and filtering."""
    result = _rest_get("/routing/filter/rule")
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Network Diagnostics (extended)
# ---------------------------------------------------------------------------


@mcp.tool()
def run_traceroute(address: str) -> str:
    """Run traceroute to a target address."""
    try:
        result = _rest_post("/tool/traceroute", {"address": address})
        return json.dumps(result, indent=2)
    except requests.exceptions.HTTPError:
        return json.dumps(
            {
                "info": "Traceroute via REST may not be supported. "
                "Use SSH/CLI for interactive traceroute."
            }
        )


@mcp.tool()
def get_dns_cache() -> str:
    """List cached DNS entries with TTL and resolved addresses."""
    result = _rest_get("/ip/dns/cache")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_dns_static() -> str:
    """List static DNS entries configured on the device."""
    result = _rest_get("/ip/dns/static")
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# MPLS
# ---------------------------------------------------------------------------


@mcp.tool()
def get_mpls_forwarding_table() -> str:
    """Get MPLS forwarding table with label, next-hop, and interface."""
    try:
        result = _rest_get("/mpls/forwarding-table")
        return json.dumps(result, indent=2)
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code == 404:
            return json.dumps({"error": "MPLS not configured or not available"})
        raise


@mcp.tool()
def get_mpls_ldp_neighbors() -> str:
    """List MPLS LDP neighbors with transport address and session state."""
    try:
        result = _rest_get("/mpls/ldp/neighbor")
        return json.dumps(result, indent=2)
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code == 404:
            return json.dumps({"error": "MPLS LDP not configured"})
        raise


@mcp.tool()
def get_mpls_ldp_interfaces() -> str:
    """List interfaces participating in MPLS LDP."""
    try:
        result = _rest_get("/mpls/ldp/interface")
        return json.dumps(result, indent=2)
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code == 404:
            return json.dumps({"error": "MPLS LDP not configured"})
        raise


# ---------------------------------------------------------------------------
# Static Routes & Route Management
# ---------------------------------------------------------------------------


@mcp.tool()
def get_static_routes() -> str:
    """List all statically configured routes with gateway, distance, and scope."""
    routes = _rest_get("/ip/route")
    static = [r for r in routes if r.get("static", "") == "true"]
    return json.dumps(static, indent=2)


# ---------------------------------------------------------------------------
# DHCP Client
# ---------------------------------------------------------------------------


@mcp.tool()
def get_dhcp_client() -> str:
    """List DHCP client instances with obtained address, gateway, and lease status."""
    result = _rest_get("/ip/dhcp-client")
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Firewall RAW & Layer7
# ---------------------------------------------------------------------------


@mcp.tool()
def get_firewall_raw() -> str:
    """List raw firewall rules (prerouting/output, before connection tracking)."""
    result = _rest_get("/ip/firewall/raw")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_firewall_layer7_protocols() -> str:
    """List Layer7 protocol definitions used for DPI-based firewall matching."""
    result = _rest_get("/ip/firewall/layer7-protocol")
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run()
