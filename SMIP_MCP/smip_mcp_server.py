"""SMIP Automation Template — MCP Server.

Exposes every SMIPMethods query as an MCP tool.

Tool descriptions and dispatch logic live in smip_tools.py — add new tools
there first, then add a typed @mcp.tool() wrapper here (3 lines). The typed
wrapper exists purely so FastMCP can generate the correct JSON schema for the
MCP client from the Python function signature.

Run as a stdio server (Copilot Agent, Claude Desktop, etc.):
    python SMIP_MCP/smip_mcp_server.py

Run as an SSE server (Azure Web App, etc.):
    MCP_TRANSPORT=sse python SMIP_MCP/smip_mcp_server.py
    Azure startup command (run from project root):
        gunicorn -w 1 -k uvicorn.workers.UvicornWorker "SMIP_MCP.smip_mcp_server:app"
"""

import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcp.server.fastmcp import FastMCP

from SMIP_IO.smip_client import SMIPClient
from SMIP_IO.smip_methods import SMIPMethods
from SMIP_MCP.smip_tools import TOOL_REGISTRY
from SMIP_MCP.agent_prompt import SYSTEM_INSTRUCTIONS

# ---------------------------------------------------------------------------
# Initialise SMIP connection and MCP server
# ---------------------------------------------------------------------------

_client  = SMIPClient()
_methods = SMIPMethods(_client)

_R = {t["name"]: t for t in TOOL_REGISTRY}

def _call(name: str, args: dict):
    return _R[name]["fn"](_methods, args)


mcp = FastMCP(
    "SMIP Automation Template",
    instructions=SYSTEM_INSTRUCTIONS,
)

# ---------------------------------------------------------------------------
# Tools — typed wrappers so FastMCP can generate the parameter schema.
# Descriptions come from TOOL_REGISTRY; add new methods to smip_tools.py first.
# ---------------------------------------------------------------------------

@mcp.tool(description=_R["get_libraries"]["description"])
def get_libraries() -> str:
    """Smoke-test query — list every library as {id, displayName}.

    No parameters. Returns a JSON-encoded list of flat rows — full row
    shape lives in TOOL_REGISTRY (smip_tools.py).
    """
    return json.dumps(_call("get_libraries", {}), default=str)


@mcp.tool(description=_R["get_quantities_with_units"]["description"])
def get_quantities_with_units() -> str:
    """Return every quantity with its full unit list and conversion factors.

    No parameters. Returns a JSON-encoded list — full row shape and the
    client-side conversion math live in TOOL_REGISTRY (smip_tools.py).
    """
    return json.dumps(_call("get_quantities_with_units", {}), default=str)


# ASGI app for gunicorn/uvicorn (Azure Web App startup command)
# Must be defined after all @mcp.tool() decorators are applied.
app = mcp.sse_app()

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    transport = os.environ.get('MCP_TRANSPORT', 'stdio')
    port = int(os.environ.get('PORT', 8000))
    if transport == 'sse':
        mcp.run(transport='sse', port=port)
    else:
        mcp.run(transport='stdio')
