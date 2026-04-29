"""Shared tool definitions consumed by every SMIP agent / doc surface.

Single source of truth for:
  * MCP tool descriptions    (smip_mcp_server.py)
  * OpenAI tool schemas      (SMIP_API/smip_flask_api.py /api/chat)
  * Generic HTTP dispatch    (SMIP_API/smip_flask_api.py /api/tool/<name>)
  * Python IDE docstrings    (SMIP_IO/smip_methods.py — attached at import)

Adding a new SMIPMethods tool
-----------------------------
1. Add an entry to TOOL_REGISTRY below
   (name, summary, description, parameters, ui, fn).
2. Add a typed @mcp.tool() wrapper in smip_mcp_server.py (3 lines) so
   FastMCP can read the Python signature for its JSON schema.
Everything else — the generic /api/tool/<name> endpoint, the OpenAI tool
spec, the Python method's __doc__ — is derived.

Field reference
---------------
name         : snake_case identifier. Also the method name on SMIPMethods
               and the URL segment on /api/tool/<name>.
summary      : one-line human blurb. Plain prose, no markdown.
description  : full LLM-facing description. May include "IMPORTANT:" callouts
               and calling protocol. Also copied onto the SMIPMethods method
               as its __doc__.
parameters   : OpenAI/MCP JSON-schema object describing arguments.
ui           : hints for any future docs page. {"inputs": [ {param, kind,
               label, placeholder?, default?} ]}. kind is "text" | "json"
               | "number". Empty list => no-input tool.
fn           : lambda(methods, args_dict) -> serialisable value.
llm_exposed  : optional, default True. When False the tool still appears in
               /api/tool/<name> dispatch but is excluded from OPENAI_TOOLS
               and requires no @mcp.tool() wrapper.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

TOOL_REGISTRY = [
    {
        # Smoke-test query — return every library as a slim {id, displayName}
        # row. No parameters; one GraphQL round-trip. Currently the only
        # registered tool — project-specific tools will be added here
        # incrementally.
        "name": "get_libraries",
        "summary": "Return every library as a {id, displayName} row. No parameters. Smoke-test query for verifying the SMIP wiring end-to-end.",
        "description": (
            "Return every library in the SoR as a flat list of "
            "{id, displayName} dicts.\n\n"
            "Stub / smoke-test tool — the GraphQL field shape may need to "
            "be widened (relativeName, description, idPath, ...) once the "
            "project's library workflows are defined. For now it's the "
            "minimum needed to confirm SMIPClient + TOOL_REGISTRY + MCP / "
            "Flask plumbing all work end-to-end.\n\n"
            "One GraphQL round-trip:\n"
            "  query GetLibraries { libraries { id displayName } }\n\n"
            "Returns: list of {id, displayName}."
        ),
        "parameters": {"type": "object", "properties": {}, "required": []},
        "ui": {"inputs": []},
        "fn": lambda m, a: m.get_libraries(),
    },
]


# ---------------------------------------------------------------------------
# Derived helpers used by consumers
# ---------------------------------------------------------------------------

def _pascal(snake: str) -> str:
    """`get_libraries` -> `GetLibraries`. Used for docs page section headers."""
    return "".join(p[:1].upper() + p[1:] for p in snake.split("_") if p)


# LLM-facing tool specs — only tools with llm_exposed=True (the default).
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["parameters"],
        },
    }
    for t in TOOL_REGISTRY
    if t.get("llm_exposed", True)
]


# Public projection for any docs page. Includes every registry entry
# (LLM-exposed or not). Excludes callables so it's safe to pass through
# Jinja / JSON.
TOOL_REGISTRY_PUBLIC = [
    {
        "name": t["name"],
        "display_name": _pascal(t["name"]),
        "summary": t["summary"],
        "description": t["description"],
        "parameters": t["parameters"],
        "ui": t["ui"],
        "llm_exposed": t.get("llm_exposed", True),
    }
    for t in TOOL_REGISTRY
]


def make_dispatch(methods: object) -> dict:
    """Return a {name: callable(args)} dict for the Flask /api/chat agentic loop."""
    return {
        t["name"]: (lambda args, fn=t["fn"]: fn(methods, args))
        for t in TOOL_REGISTRY
    }


def attach_docstrings_to(cls: type) -> None:
    """Copy each tool's `description` onto the matching method's __doc__."""
    for t in TOOL_REGISTRY:
        method = getattr(cls, t["name"], None)
        if callable(method):
            try:
                method.__doc__ = t["description"]
            except (AttributeError, TypeError):
                pass


__all__ = [
    "TOOL_REGISTRY",
    "TOOL_REGISTRY_PUBLIC",
    "OPENAI_TOOLS",
    "make_dispatch",
    "attach_docstrings_to",
]
