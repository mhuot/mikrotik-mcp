#!/usr/bin/env python3
# pylint: disable=too-many-lines,too-many-arguments,too-many-positional-arguments
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

import librouteros
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
    """Make a POST request to the RouterOS REST API (commands like ping, traceroute)."""
    base_url, user, password, verify_ssl = _get_connection_params()
    url = f"{base_url}{path}"
    resp = requests.post(
        url, auth=(user, password), verify=verify_ssl, json=data, timeout=30
    )
    resp.raise_for_status()
    return resp.json()


def _rest_put(path: str, data: Optional[dict] = None) -> dict:
    """Make a PUT request to the RouterOS REST API (create/add items)."""
    base_url, user, password, verify_ssl = _get_connection_params()
    url = f"{base_url}{path}"
    resp = requests.put(
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
# RouterOS API helpers (librouteros) — used for write operations
# ---------------------------------------------------------------------------


def _get_api():
    """Connect to the RouterOS API (port 8728) for write operations."""
    host = os.environ.get("MIKROTIK_HOST", "192.168.88.1")
    user = os.environ.get("MIKROTIK_USER", "admin")
    password = os.environ.get("MIKROTIK_PASSWORD", "")
    port = int(os.environ.get("MIKROTIK_API_PORT", "8728"))
    return librouteros.connect(
        host=host, username=user, password=password, port=port, timeout=30
    )


def _api_add(path: str, params: dict) -> dict:
    """Add an item via RouterOS API. Returns the created item."""
    api = _get_api()
    try:
        resource = api.path(path)
        new_id = resource.add(**params)
        # Fetch the created item to return its full details
        for item in resource:
            if item.get(".id") == new_id:
                return dict(item)
        return {".id": new_id, "status": "created"}
    finally:
        api.close()


def _api_set(path: str, item_id: str, params: dict) -> dict:
    """Update an item via RouterOS API."""
    api = _get_api()
    try:
        resource = api.path(path)
        resource.update(**{".id": item_id, **params})
        # Fetch updated item
        for item in resource:
            if item.get(".id") == item_id:
                return dict(item)
        return {".id": item_id, "status": "updated"}
    finally:
        api.close()


def _api_remove(path: str, item_id: str) -> dict:
    """Remove an item via RouterOS API."""
    api = _get_api()
    try:
        resource = api.path(path)
        resource.remove(item_id)
        return {".id": item_id, "status": "removed"}
    finally:
        api.close()


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


# ===========================================================================
# WRITE OPERATIONS (CRUD) — via RouterOS API (librouteros, port 8728)
# ===========================================================================


def _build_params(**kwargs):
    """Build a params dict from kwargs, skipping None values."""
    return {k: v for k, v in kwargs.items() if v is not None}


# ---------------------------------------------------------------------------
# Firewall Filter CRUD
# ---------------------------------------------------------------------------


@mcp.tool()
def add_firewall_filter_rule(
    chain: str,
    action: str,
    src_address: Optional[str] = None,
    dst_address: Optional[str] = None,
    protocol: Optional[str] = None,
    dst_port: Optional[str] = None,
    src_port: Optional[str] = None,
    in_interface: Optional[str] = None,
    out_interface: Optional[str] = None,
    comment: Optional[str] = None,
) -> str:
    """Add a firewall filter rule. Chain: input/forward/output. Action: accept/drop/reject/log."""
    params = _build_params(
        chain=chain,
        action=action,
        **{"src-address": src_address, "dst-address": dst_address},
        protocol=protocol,
        **{"dst-port": dst_port, "src-port": src_port},
        **{"in-interface": in_interface, "out-interface": out_interface},
        comment=comment,
    )
    result = _api_add("/ip/firewall/filter", params)
    return json.dumps(result, indent=2)


@mcp.tool()
def update_firewall_filter_rule(
    rule_id: str,
    action: Optional[str] = None,
    src_address: Optional[str] = None,
    dst_address: Optional[str] = None,
    protocol: Optional[str] = None,
    dst_port: Optional[str] = None,
    comment: Optional[str] = None,
) -> str:
    """Update an existing firewall filter rule by its .id."""
    params = _build_params(
        action=action,
        **{"src-address": src_address, "dst-address": dst_address},
        protocol=protocol,
        **{"dst-port": dst_port},
        comment=comment,
    )
    result = _api_set("/ip/firewall/filter", rule_id, params)
    return json.dumps(result, indent=2)


@mcp.tool()
def remove_firewall_filter_rule(rule_id: str) -> str:
    """Remove a firewall filter rule by its .id."""
    return json.dumps(_api_remove("/ip/firewall/filter", rule_id), indent=2)


@mcp.tool()
def enable_firewall_filter_rule(rule_id: str) -> str:
    """Enable a disabled firewall filter rule."""
    return json.dumps(
        _api_set("/ip/firewall/filter", rule_id, {"disabled": "false"}), indent=2
    )


@mcp.tool()
def disable_firewall_filter_rule(rule_id: str) -> str:
    """Disable a firewall filter rule without removing it."""
    return json.dumps(
        _api_set("/ip/firewall/filter", rule_id, {"disabled": "true"}), indent=2
    )


# ---------------------------------------------------------------------------
# Firewall NAT CRUD
# ---------------------------------------------------------------------------


@mcp.tool()
def add_firewall_nat_rule(
    chain: str,
    action: str,
    src_address: Optional[str] = None,
    dst_address: Optional[str] = None,
    protocol: Optional[str] = None,
    dst_port: Optional[str] = None,
    to_addresses: Optional[str] = None,
    to_ports: Optional[str] = None,
    out_interface: Optional[str] = None,
    in_interface: Optional[str] = None,
    comment: Optional[str] = None,
) -> str:
    """Add a NAT rule. Chain: srcnat/dstnat. Action: masquerade/dst-nat/src-nat/netmap."""
    params = _build_params(
        chain=chain,
        action=action,
        **{"src-address": src_address, "dst-address": dst_address},
        protocol=protocol,
        **{"dst-port": dst_port},
        **{"to-addresses": to_addresses, "to-ports": to_ports},
        **{"out-interface": out_interface, "in-interface": in_interface},
        comment=comment,
    )
    result = _api_add("/ip/firewall/nat", params)
    return json.dumps(result, indent=2)


@mcp.tool()
def update_firewall_nat_rule(
    rule_id: str,
    action: Optional[str] = None,
    to_addresses: Optional[str] = None,
    to_ports: Optional[str] = None,
    comment: Optional[str] = None,
) -> str:
    """Update an existing NAT rule by its .id."""
    params = _build_params(
        action=action,
        **{"to-addresses": to_addresses, "to-ports": to_ports},
        comment=comment,
    )
    result = _api_set("/ip/firewall/nat", rule_id, params)
    return json.dumps(result, indent=2)


@mcp.tool()
def remove_firewall_nat_rule(rule_id: str) -> str:
    """Remove a NAT rule by its .id."""
    return json.dumps(_api_remove("/ip/firewall/nat", rule_id), indent=2)


@mcp.tool()
def enable_firewall_nat_rule(rule_id: str) -> str:
    """Enable a disabled NAT rule."""
    return json.dumps(
        _api_set("/ip/firewall/nat", rule_id, {"disabled": "false"}), indent=2
    )


@mcp.tool()
def disable_firewall_nat_rule(rule_id: str) -> str:
    """Disable a NAT rule without removing it."""
    return json.dumps(
        _api_set("/ip/firewall/nat", rule_id, {"disabled": "true"}), indent=2
    )


# ---------------------------------------------------------------------------
# Firewall Address List CRUD
# ---------------------------------------------------------------------------


@mcp.tool()
def add_firewall_address_list_entry(
    list_name: str,
    address: str,
    comment: Optional[str] = None,
    timeout: Optional[str] = None,
) -> str:
    """Add an entry to a firewall address-list."""
    params = _build_params(
        list=list_name, address=address, comment=comment, timeout=timeout
    )
    return json.dumps(_api_add("/ip/firewall/address-list", params), indent=2)


@mcp.tool()
def remove_firewall_address_list_entry(entry_id: str) -> str:
    """Remove an address-list entry by its .id."""
    return json.dumps(_api_remove("/ip/firewall/address-list", entry_id), indent=2)


# ---------------------------------------------------------------------------
# DNS CRUD
# ---------------------------------------------------------------------------


@mcp.tool()
def set_dns_servers(
    servers: str,
    allow_remote_requests: Optional[bool] = None,
) -> str:
    """Set upstream DNS server IPs (comma-separated, e.g. '8.8.8.8,8.8.4.4').
    Optionally set allow-remote-requests (True/False) to control whether the
    router acts as a DNS resolver for LAN clients."""
    api = _get_api()
    try:
        dns = api.path("/ip/dns")
        kwargs: dict = {"servers": servers}
        if allow_remote_requests is not None:
            kwargs["allow-remote-requests"] = str(allow_remote_requests).lower()
        dns.update(**kwargs)
        for item in dns:
            return json.dumps(dict(item), indent=2)
        return json.dumps({"status": "dns servers updated"})
    finally:
        api.close()


@mcp.tool()
def add_dns_static_entry(
    name: str,
    address: str,
    record_type: Optional[str] = None,
    ttl: Optional[str] = None,
    comment: Optional[str] = None,
) -> str:
    """Add a static DNS entry (A, AAAA, CNAME, etc.)."""
    params = _build_params(
        name=name, address=address, type=record_type, ttl=ttl, comment=comment
    )
    return json.dumps(_api_add("/ip/dns/static", params), indent=2)


@mcp.tool()
def add_dns_forwarder(
    name: str,
    forward_to: str,
    match_subdomain: bool = True,
    comment: Optional[str] = None,
) -> str:
    """Add a DNS FWD (forwarder) entry for conditional zone forwarding.
    Routes DNS queries for a domain zone to a specific upstream resolver.
    Example: forward privatelink.vaultcore.azure.net to 10.0.4.4."""
    data: dict = {
        "name": name,
        "type": "FWD",
        "forward-to": forward_to,
        "match-subdomain": "yes" if match_subdomain else "no",
    }
    if comment:
        data["comment"] = comment
    return json.dumps(_rest_post("/ip/dns/static", data), indent=2)


@mcp.tool()
def update_dns_static_entry(
    entry_id: str,
    name: Optional[str] = None,
    address: Optional[str] = None,
    comment: Optional[str] = None,
) -> str:
    """Update a static DNS entry by its .id."""
    params = _build_params(name=name, address=address, comment=comment)
    return json.dumps(_api_set("/ip/dns/static", entry_id, params), indent=2)


@mcp.tool()
def remove_dns_static_entry(entry_id: str) -> str:
    """Remove a static DNS entry by its .id."""
    return json.dumps(_api_remove("/ip/dns/static", entry_id), indent=2)


@mcp.tool()
def enable_dns_static_entry(entry_id: str) -> str:
    """Enable a disabled static DNS entry."""
    return json.dumps(
        _api_set("/ip/dns/static", entry_id, {"disabled": "false"}), indent=2
    )


@mcp.tool()
def disable_dns_static_entry(entry_id: str) -> str:
    """Disable a static DNS entry without removing it."""
    return json.dumps(
        _api_set("/ip/dns/static", entry_id, {"disabled": "true"}), indent=2
    )


@mcp.tool()
def flush_dns_cache() -> str:
    """Flush the DNS cache on the device."""
    api = _get_api()
    try:
        api.path("/ip/dns/cache")("flush")
    except librouteros.exceptions.TrapError:
        pass
    finally:
        api.close()
    return json.dumps({"status": "dns cache flushed"})


# ---------------------------------------------------------------------------
# IP Address CRUD
# ---------------------------------------------------------------------------


@mcp.tool()
def add_ip_address(address: str, interface: str, comment: Optional[str] = None) -> str:
    """Add an IP address to an interface (e.g. '192.168.1.1/24' on 'ether1')."""
    params = _build_params(address=address, interface=interface, comment=comment)
    return json.dumps(_api_add("/ip/address", params), indent=2)


@mcp.tool()
def update_ip_address(
    address_id: str,
    address: Optional[str] = None,
    interface: Optional[str] = None,
    comment: Optional[str] = None,
) -> str:
    """Update an IP address entry by its .id."""
    params = _build_params(address=address, interface=interface, comment=comment)
    return json.dumps(_api_set("/ip/address", address_id, params), indent=2)


@mcp.tool()
def remove_ip_address(address_id: str) -> str:
    """Remove an IP address by its .id."""
    return json.dumps(_api_remove("/ip/address", address_id), indent=2)


# ---------------------------------------------------------------------------
# Route CRUD
# ---------------------------------------------------------------------------


@mcp.tool()
def add_route(
    dst_address: str,
    gateway: str,
    distance: Optional[int] = None,
    comment: Optional[str] = None,
) -> str:
    """Add a static route (e.g. dst '10.0.0.0/8' gateway '192.168.1.1')."""
    params = _build_params(
        **{"dst-address": dst_address},
        gateway=gateway,
        distance=str(distance) if distance is not None else None,
        comment=comment,
    )
    return json.dumps(_api_add("/ip/route", params), indent=2)


@mcp.tool()
def update_route(
    route_id: str,
    gateway: Optional[str] = None,
    distance: Optional[int] = None,
    comment: Optional[str] = None,
) -> str:
    """Update a static route by its .id."""
    params = _build_params(
        gateway=gateway,
        distance=str(distance) if distance is not None else None,
        comment=comment,
    )
    return json.dumps(_api_set("/ip/route", route_id, params), indent=2)


@mcp.tool()
def remove_route(route_id: str) -> str:
    """Remove a static route by its .id."""
    return json.dumps(_api_remove("/ip/route", route_id), indent=2)


@mcp.tool()
def enable_route(route_id: str) -> str:
    """Enable a disabled static route."""
    return json.dumps(_api_set("/ip/route", route_id, {"disabled": "false"}), indent=2)


@mcp.tool()
def disable_route(route_id: str) -> str:
    """Disable a static route without removing it."""
    return json.dumps(_api_set("/ip/route", route_id, {"disabled": "true"}), indent=2)


# ---------------------------------------------------------------------------
# VLAN CRUD
# ---------------------------------------------------------------------------


@mcp.tool()
def add_vlan(
    name: str, vlan_id: int, interface: str, comment: Optional[str] = None
) -> str:
    """Create a VLAN interface on a parent interface."""
    params = _build_params(
        name=name, **{"vlan-id": str(vlan_id)}, interface=interface, comment=comment
    )
    return json.dumps(_api_add("/interface/vlan", params), indent=2)


@mcp.tool()
def update_vlan(
    vlan_item_id: str,
    name: Optional[str] = None,
    vlan_id: Optional[int] = None,
    comment: Optional[str] = None,
) -> str:
    """Update a VLAN interface by its .id."""
    params = _build_params(name=name, comment=comment)
    if vlan_id is not None:
        params["vlan-id"] = str(vlan_id)
    return json.dumps(_api_set("/interface/vlan", vlan_item_id, params), indent=2)


@mcp.tool()
def remove_vlan(vlan_item_id: str) -> str:
    """Remove a VLAN interface by its .id."""
    return json.dumps(_api_remove("/interface/vlan", vlan_item_id), indent=2)


# ---------------------------------------------------------------------------
# DHCP CRUD
# ---------------------------------------------------------------------------


@mcp.tool()
def get_dhcp_networks() -> str:
    """List DHCP server networks with address, gateway, DNS, and domain."""
    return json.dumps(_rest_get("/ip/dhcp-server/network"), indent=2)


@mcp.tool()
def add_dhcp_lease(
    address: str,
    mac_address: str,
    server: Optional[str] = None,
    comment: Optional[str] = None,
) -> str:
    """Add a static DHCP lease binding a MAC to an IP."""
    params = _build_params(
        address=address, **{"mac-address": mac_address}, server=server, comment=comment
    )
    return json.dumps(_api_add("/ip/dhcp-server/lease", params), indent=2)


@mcp.tool()
def remove_dhcp_lease(lease_id: str) -> str:
    """Remove a DHCP lease by its .id."""
    return json.dumps(_api_remove("/ip/dhcp-server/lease", lease_id), indent=2)


@mcp.tool()
def add_dhcp_network(
    address: str,
    gateway: str,
    dns_server: Optional[str] = None,
    domain: Optional[str] = None,
    comment: Optional[str] = None,
) -> str:
    """Add a DHCP server network definition."""
    params = _build_params(
        address=address,
        gateway=gateway,
        **{"dns-server": dns_server},
        domain=domain,
        comment=comment,
    )
    return json.dumps(_api_add("/ip/dhcp-server/network", params), indent=2)


@mcp.tool()
def remove_dhcp_network(network_id: str) -> str:
    """Remove a DHCP server network by its .id."""
    return json.dumps(_api_remove("/ip/dhcp-server/network", network_id), indent=2)


# ---------------------------------------------------------------------------
# IP Pool CRUD
# ---------------------------------------------------------------------------


@mcp.tool()
def add_ip_pool(name: str, ranges: str, comment: Optional[str] = None) -> str:
    """Create an IP pool with address ranges (e.g. '192.168.1.100-192.168.1.200')."""
    params = _build_params(name=name, ranges=ranges, comment=comment)
    return json.dumps(_api_add("/ip/pool", params), indent=2)


@mcp.tool()
def update_ip_pool(
    pool_id: str,
    name: Optional[str] = None,
    ranges: Optional[str] = None,
    comment: Optional[str] = None,
) -> str:
    """Update an IP pool by its .id."""
    params = _build_params(name=name, ranges=ranges, comment=comment)
    return json.dumps(_api_set("/ip/pool", pool_id, params), indent=2)


@mcp.tool()
def remove_ip_pool(pool_id: str) -> str:
    """Remove an IP pool by its .id."""
    return json.dumps(_api_remove("/ip/pool", pool_id), indent=2)


# ---------------------------------------------------------------------------
# User CRUD
# ---------------------------------------------------------------------------


@mcp.tool()
def add_user(
    name: str, group: str, password: str, comment: Optional[str] = None
) -> str:
    """Add a user account with group and password."""
    params = _build_params(name=name, group=group, password=password, comment=comment)
    return json.dumps(_api_add("/user", params), indent=2)


@mcp.tool()
def update_user(
    user_id: str,
    group: Optional[str] = None,
    password: Optional[str] = None,
    comment: Optional[str] = None,
) -> str:
    """Update a user account by its .id."""
    params = _build_params(group=group, password=password, comment=comment)
    return json.dumps(_api_set("/user", user_id, params), indent=2)


@mcp.tool()
def remove_user(user_id: str) -> str:
    """Remove a user account by its .id. Cannot remove the admin user."""
    users = _rest_get("/user")
    target = [u for u in users if u.get(".id") == user_id]
    if target and target[0].get("name") == "admin":
        return json.dumps({"error": "Cannot remove the admin user"})
    return json.dumps(_api_remove("/user", user_id), indent=2)


@mcp.tool()
def enable_user(user_id: str) -> str:
    """Enable a disabled user account."""
    return json.dumps(_api_set("/user", user_id, {"disabled": "false"}), indent=2)


@mcp.tool()
def disable_user(user_id: str) -> str:
    """Disable a user account without removing it."""
    return json.dumps(_api_set("/user", user_id, {"disabled": "true"}), indent=2)


# ---------------------------------------------------------------------------
# WireGuard CRUD
# ---------------------------------------------------------------------------


@mcp.tool()
def get_wireguard_interfaces() -> str:
    """List WireGuard interfaces with public key, listen port, and status."""
    try:
        return json.dumps(_rest_get("/interface/wireguard"), indent=2)
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code == 404:
            return json.dumps({"error": "WireGuard not available on this device"})
        raise


@mcp.tool()
def add_wireguard_interface(
    name: str, listen_port: int, comment: Optional[str] = None
) -> str:
    """Create a WireGuard interface with a listen port. Keys auto-generated."""
    params = _build_params(
        name=name, **{"listen-port": str(listen_port)}, comment=comment
    )
    return json.dumps(_api_add("/interface/wireguard", params), indent=2)


@mcp.tool()
def remove_wireguard_interface(interface_id: str) -> str:
    """Remove a WireGuard interface by its .id."""
    return json.dumps(_api_remove("/interface/wireguard", interface_id), indent=2)


@mcp.tool()
def get_wireguard_peers() -> str:
    """List WireGuard peers with public key, endpoint, allowed addresses."""
    try:
        return json.dumps(_rest_get("/interface/wireguard/peers"), indent=2)
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code == 404:
            return json.dumps({"error": "WireGuard not available on this device"})
        raise


@mcp.tool()
def add_wireguard_peer(
    interface: str,
    public_key: str,
    allowed_address: str,
    endpoint_address: Optional[str] = None,
    endpoint_port: Optional[int] = None,
    persistent_keepalive: Optional[int] = None,
    comment: Optional[str] = None,
) -> str:
    """Add a WireGuard peer to an interface."""
    params = _build_params(
        interface=interface,
        **{"public-key": public_key, "allowed-address": allowed_address},
        **{"endpoint-address": endpoint_address},
        **{"endpoint-port": str(endpoint_port) if endpoint_port else None},
        **{
            "persistent-keepalive": (
                str(persistent_keepalive) if persistent_keepalive else None
            )
        },
        comment=comment,
    )
    return json.dumps(_api_add("/interface/wireguard/peers", params), indent=2)


@mcp.tool()
def update_wireguard_peer(
    peer_id: str,
    allowed_address: Optional[str] = None,
    endpoint_address: Optional[str] = None,
    endpoint_port: Optional[int] = None,
    comment: Optional[str] = None,
) -> str:
    """Update a WireGuard peer by its .id."""
    params = _build_params(
        **{"allowed-address": allowed_address, "endpoint-address": endpoint_address},
        **{"endpoint-port": str(endpoint_port) if endpoint_port else None},
        comment=comment,
    )
    return json.dumps(_api_set("/interface/wireguard/peers", peer_id, params), indent=2)


@mcp.tool()
def remove_wireguard_peer(peer_id: str) -> str:
    """Remove a WireGuard peer by its .id."""
    return json.dumps(_api_remove("/interface/wireguard/peers", peer_id), indent=2)


@mcp.tool()
def enable_wireguard_peer(peer_id: str) -> str:
    """Enable a disabled WireGuard peer."""
    return json.dumps(
        _api_set("/interface/wireguard/peers", peer_id, {"disabled": "false"}), indent=2
    )


@mcp.tool()
def disable_wireguard_peer(peer_id: str) -> str:
    """Disable a WireGuard peer without removing it."""
    return json.dumps(
        _api_set("/interface/wireguard/peers", peer_id, {"disabled": "true"}), indent=2
    )


# ---------------------------------------------------------------------------
# Backup & System
# ---------------------------------------------------------------------------


@mcp.tool()
def create_backup(name: Optional[str] = None) -> str:
    """Create a system backup file on the device."""
    api = _get_api()
    try:
        params = {}
        if name:
            params["name"] = name
        api.path("/system/backup")("save", **params)
        return json.dumps({"status": "backup created", "name": name or "auto"})
    except librouteros.exceptions.TrapError as exc:
        return json.dumps({"error": str(exc)})
    finally:
        api.close()


@mcp.tool()
def get_files(name_filter: Optional[str] = None) -> str:
    """List files on the device. Optionally filter by name substring."""
    result = _rest_get("/file")
    if name_filter:
        result = [f for f in result if name_filter.lower() in f.get("name", "").lower()]
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# IPsec Writes
# ---------------------------------------------------------------------------


@mcp.tool()
def update_ipsec_peer(
    peer_id: str,
    address: Optional[str] = None,
    local_address: Optional[str] = None,
    profile: Optional[str] = None,
    exchange_mode: Optional[str] = None,
    send_initial_contact: Optional[bool] = None,
    disabled: Optional[bool] = None,
    comment: Optional[str] = None,
) -> str:
    """Update an IPsec peer by its .id. Provide only fields to change."""
    params = _build_params(
        address=address,
        **{"local-address": local_address},
        profile=profile,
        **{"exchange-mode": exchange_mode},
        **{
            "send-initial-contact": (
                str(send_initial_contact).lower() if send_initial_contact is not None else None
            )
        },
        **{"disabled": str(disabled).lower() if disabled is not None else None},
        comment=comment,
    )
    return json.dumps(_api_set("/ip/ipsec/peer", peer_id, params), indent=2)


@mcp.tool()
def update_ipsec_identity(
    identity_id: str,
    peer: Optional[str] = None,
    auth_method: Optional[str] = None,
    secret: Optional[str] = None,
    certificate: Optional[str] = None,
    remote_certificate: Optional[str] = None,
    policy_template_group: Optional[str] = None,
    generate_policy: Optional[str] = None,
    disabled: Optional[bool] = None,
    comment: Optional[str] = None,
) -> str:
    """Update an IPsec identity by its .id. Provide only fields to change."""
    params = _build_params(
        peer=peer,
        **{"auth-method": auth_method},
        secret=secret,
        certificate=certificate,
        **{"remote-certificate": remote_certificate},
        **{"policy-template-group": policy_template_group},
        **{"generate-policy": generate_policy},
        **{"disabled": str(disabled).lower() if disabled is not None else None},
        comment=comment,
    )
    return json.dumps(_api_set("/ip/ipsec/identity", identity_id, params), indent=2)


@mcp.tool()
def remove_ipsec_policy(policy_id: str) -> str:
    """Remove an IPsec policy by its .id."""
    return json.dumps(_api_remove("/ip/ipsec/policy", policy_id), indent=2)


@mcp.tool()
def add_ipsec_policy(
    src_address: str,
    dst_address: str,
    peer: Optional[str] = None,
    tunnel: Optional[bool] = None,
    action: Optional[str] = None,
    proposal: Optional[str] = None,
    sa_src_address: Optional[str] = None,
    sa_dst_address: Optional[str] = None,
    protocol: Optional[str] = None,
    disabled: Optional[bool] = None,
    comment: Optional[str] = None,
) -> str:
    """Add an IPsec policy (traffic selector). src_address and dst_address are required."""
    params = _build_params(
        **{"src-address": src_address, "dst-address": dst_address},
        peer=peer,
        **{"tunnel": str(tunnel).lower() if tunnel is not None else None},
        action=action,
        proposal=proposal,
        **{"sa-src-address": sa_src_address, "sa-dst-address": sa_dst_address},
        protocol=protocol,
        **{"disabled": str(disabled).lower() if disabled is not None else None},
        comment=comment,
    )
    return json.dumps(_api_add("/ip/ipsec/policy", params), indent=2)


if __name__ == "__main__":
    mcp.run()
