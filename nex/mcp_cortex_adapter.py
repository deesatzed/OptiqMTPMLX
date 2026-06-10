"""
Lightweight MCP-Cortex style adapter for Nex tools.

Produces CapabilityContract-like structures for the built-in safe tools
so they can be fed into policy engines (e.g. from gemOptq) or used for
Grok escalation context.

This makes Nex agents "MCP-Cortex aware" without requiring the full gemOptq dependency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .tools import TOOLS


@dataclass
class CapabilityContract:
    capability: str
    version: str = "0.1.0"
    effects: List[str] = field(default_factory=list)
    forbidden_effects: List[str] = field(default_factory=list)
    assurance_level: str = "A1"
    risk: str = "medium"


def get_capability_for_tool(tool_name: str, args: Dict[str, Any]) -> CapabilityContract:
    """Return a Cortex-style contract for one of Nex's built-in tools."""
    effects = ["tool:call"]
    forbidden = []

    if tool_name == "write_file":
        path = args.get("path", "")
        if any(x in path for x in [".env", ".ssh", "production", "secret"]):
            forbidden.append("write:secrets")
        effects.append("write:workspace")
    elif tool_name == "read_file":
        path = args.get("path", "")
        if any(x in path for x in [".env", ".ssh"]):
            effects.append("read:secrets")
        else:
            effects.append("read:workspace")
    elif tool_name == "run_python":
        effects.append("execute:test")
    elif tool_name == "shell":
        cmd = args.get("command", "").lower()
        if any(x in cmd for x in ["curl", "wget", "ssh", "nc "]):
            forbidden.append("network:external")
        effects.append("execute:shell")

    return CapabilityContract(
        capability=f"capability://nex/tools/{tool_name}",
        effects=effects,
        forbidden_effects=forbidden,
        assurance_level="A2",
        risk="medium" if forbidden else "low",
    )


def wrap_nex_tool_as_capability(tool_name: str) -> CapabilityContract:
    """Simple wrapper for static registration."""
    return get_capability_for_tool(tool_name, {})


# Example: get contracts for all built-in tools
def get_all_nex_capabilities() -> Dict[str, CapabilityContract]:
    return {name: wrap_nex_tool_as_capability(name) for name in TOOLS.keys()}