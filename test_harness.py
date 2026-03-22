#!/usr/bin/env python3
"""
Test harness for MikroTik MCP Server

Invokes MCP tools directly without needing OpenClaw or an MCP client.
Usage:
    python test_harness.py                    # list all tools
    python test_harness.py get_identity       # call a specific tool
    python test_harness.py get_interface_detail --name ether1

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

import argparse
import inspect
import json
import sys

from dotenv import load_dotenv

load_dotenv()

# Import the MCP server module to access tool functions directly
import mikrotik_mcp


def list_tools():
    """List all registered MCP tools with their descriptions."""
    tools = []
    for name, obj in inspect.getmembers(mikrotik_mcp):
        if callable(obj) and not name.startswith("_"):
            # Check if it's a decorated MCP tool by looking at the module-level functions
            sig = inspect.signature(obj)
            doc = inspect.getdoc(obj) or ""
            if doc and name not in ("load_dotenv", "json", "FastMCP"):
                params = []
                for pname, param in sig.parameters.items():
                    if pname == "self":
                        continue
                    ptype = (
                        param.annotation.__name__
                        if param.annotation != inspect.Parameter.empty
                        else "any"
                    )
                    default = (
                        param.default
                        if param.default != inspect.Parameter.empty
                        else None
                    )
                    params.append(
                        {
                            "name": pname,
                            "type": ptype,
                            "default": str(default) if default is not None else None,
                        }
                    )
                tools.append({"name": name, "description": doc, "params": params})

    print(f"\nMikroTik MCP Tools ({len(tools)} available):\n")
    print("-" * 80)
    for tool in sorted(tools, key=lambda t: t["name"]):
        print(f"  {tool['name']}")
        print(f"    {tool['description']}")
        if tool["params"]:
            param_str = ", ".join(
                f"{p['name']}: {p['type']}"
                + (f" = {p['default']}" if p["default"] else "")
                for p in tool["params"]
            )
            print(f"    params: ({param_str})")
        print()


def call_tool(tool_name: str, kwargs: dict):
    """Call a tool function by name with the given keyword arguments."""
    func = getattr(mikrotik_mcp, tool_name, None)
    if func is None or not callable(func):
        print(f"Error: tool '{tool_name}' not found")
        sys.exit(1)

    print(f"Calling {tool_name}({json.dumps(kwargs) if kwargs else ''})...\n")
    try:
        result = func(**kwargs)
        # Pretty-print if it's JSON
        try:
            parsed = json.loads(result)
            print(json.dumps(parsed, indent=2))
        except (json.JSONDecodeError, TypeError):
            print(result)
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Test harness for MikroTik MCP Server",
        epilog="Run without arguments to list all available tools.",
    )
    parser.add_argument("tool", nargs="?", help="Tool name to invoke")
    # Allow arbitrary --key value pairs for tool parameters
    args, remaining = parser.parse_known_args()

    if not args.tool:
        list_tools()
        return

    # Parse remaining args as --key value pairs
    kwargs = {}
    i = 0
    while i < len(remaining):
        if remaining[i].startswith("--"):
            key = remaining[i][2:].replace("-", "_")
            if i + 1 < len(remaining) and not remaining[i + 1].startswith("--"):
                value = remaining[i + 1]
                # Try to convert to int
                try:
                    value = int(value)
                except ValueError:
                    pass
                kwargs[key] = value
                i += 2
            else:
                kwargs[key] = True
                i += 1
        else:
            i += 1

    call_tool(args.tool, kwargs)


if __name__ == "__main__":
    main()
