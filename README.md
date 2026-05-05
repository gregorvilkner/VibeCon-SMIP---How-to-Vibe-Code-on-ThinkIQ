# VibeCon-SMIP — How to Vibe-Code on ThinkIQ

A localhost-first automation template for the CESMII SMIP (ThinkIQ).
Sibling to [DevCon-SMIP](https://github.com/gregorvilkner/DevCon-SMIP---How-to-Code-on-ThinkIQ):
DevCon teaches you to code on ThinkIQ, VibeCon teaches you to vibe-code
on it. Three pillars:

1. **Vibe-code, fast.** A `PAGES/` convention for browser pages (Vue +
   GraphQL via the Flask app) and a `SCRIPTS/` convention for headless
   worker tasks (migrations, model refactors, data fixups). Every layer
   reloads on file save — no build steps, no deploy ceremony.
2. **Built-in MCP server.** `SMIP_MCP/smip_mcp_server.py` exposes every
   registered tool to MCP clients (Claude Desktop, Cursor, your own
   agent) over stdio + SSE. One `TOOL_REGISTRY` is the single source of
   truth for MCP + REST + the agentic `/api/chat` loop — add a tool
   once, all three surfaces pick it up.
3. **A clean path back to first-class SMIP scripts.** Once a vibe-coded
   page or script earns its keep, port it into the SMIP browser-script
   or display-script templates under `___SMIP_SAAS_SIDE___/Sample
   Scripts/` so it ships on the SMIP side as a real, server-rendered
   Joomla page — no longer a localhost toy.

Add your own queries and mutations to `SMIP_IO/smip_methods.py` and
`SMIP_MCP/smip_tools.py`; everything else (REST endpoint, MCP wrapper,
OpenAI tool spec, docs page section) is derived.

## Read next

- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** — get from `git clone` to
  a working chat agent calling tools against your SMIP, in five steps.
  Each step adds one new dependency and verifies it before moving on.
- **[docs/WORKFLOW.md](docs/WORKFLOW.md)** — how to actually use the
  template well. Bootstrapping with library exports, building tools
  before pages, vibe-coding thin shells, the round-trip back to SMIP-side
  scripts, the **two-layer JS SDK** convention (generic SMIP plumbing
  in `___SMIP_SAAS_SIDE___/SMIP JS SDK/` grows in this repo;
  domain-specific methods live in `___SMIP_SAAS_SIDE___/JS SDK Template/`),
  and the anti-patterns to avoid.
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — what's where and
  why. Reference for the tool registry mechanics, the PAGES + SCRIPTS
  conventions, the directory layout, and the design choices that thread
  through the codebase.
