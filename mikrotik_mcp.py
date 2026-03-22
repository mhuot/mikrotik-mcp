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


if __name__ == "__main__":
    mcp.run()
