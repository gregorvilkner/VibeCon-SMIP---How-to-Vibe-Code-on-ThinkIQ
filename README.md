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

## Architecture at a glance

```
SMIP_IO/      transport
  smip_client.py        SMIPClient — auth (JWT challenge/response) + GraphQL POST.
                        Based on the CESMII "Simple SMIP Client Example" template
                        (link in the file header).
  smip_methods.py       SMIPMethods — high-level operations (one method per business question)
  model/                Optional: Python dataclasses for typed responses (project-specific)

SMIP_MCP/     single source of truth for tools
  smip_tools.py         TOOL_REGISTRY — descriptions, params, dispatch fns
  smip_mcp_server.py    FastMCP server exposing each tool to MCP clients
  agent_prompt.py       SYSTEM_INSTRUCTIONS shared by chat agent + MCP

SMIP_API/     Flask surface
  smip_flask_api.py                   /, /chat[/_stack/_canvas], /api/tool/<name>, /api/chat
  smip_flask_api_documentation.html   Vue docs page (rendered from TOOL_REGISTRY_PUBLIC)
  smip_chat[/_stack/_canvas].html     three chat UIs

PAGES/        browser-side pages — runnable .py per page
  <NN>_<page_name>/                   one folder per page
    <page_name>.py                    standalone runner
    <page_name>.html                  Vue single-file page

SCRIPTS/      worker / automation scripts — runnable .py per task
  <NN>_<task>.py                      e.g. 01_migrate_units.py,
                                      02_refactor_model.py — one-shot
                                      or batch operations against the SMIP
                                      (migrations, model refactors, data
                                      fixups). Headless; no Vue, no Flask.

___SMIP_SAAS_SIDE___/   reference material that lives on the SMIP side
  GraphQL Schema/         introspection export of the SMIP GraphQL API
  JS SDK Template/        SMIP-side templates (Guzzle client, API templates,
                          library exports, future display-script conversions)
  Sample Scripts/         vendored SMIP browser-script + display-script
                          templates — the conversion targets for PAGES.
                          Vibe-code a page in Python under PAGES/, then port
                          it back into one of these templates so it lives on
                          the SMIP side as a first-class script.
```

The directional convention: data flows in via SMIP_IO, business semantics live
in SMIP_MCP's TOOL_REGISTRY (one source of truth), and SMIP_API + PAGES are the
surfaces. Adding a new tool means editing `smip_tools.py` and `smip_methods.py`;
everything else (REST endpoint, OpenAI tool spec, MCP wrapper schema, docs page
section) is derived.

## Quickstart

Requires Python 3.10+. From the project root:

```
pip install -r requirements.txt
```

Drop a `config.json` in `SMIP_IO/` with your SMIP credentials (mirror
`SMIP_IO/config.example.json`). For the `/api/chat` agentic loop, also add
Azure OpenAI credentials to a `.env` at the project root:

```
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_API_VERSION=2025-01-01-preview     # optional
AZURE_OPENAI_DEPLOYMENT=gpt-4o                   # optional
```

Then start the API:

```
python SMIP_API/smip_flask_api.py
```

Visit:

| URL                                  | What it is                                          |
| ------------------------------------ | --------------------------------------------------- |
| `http://localhost:5000/`             | Interactive docs page (sections from TOOL_REGISTRY) |
| `http://localhost:5000/chat`         | Baseline chat UI (calls `/api/chat`)                |
| `http://localhost:5000/chat_stack`   | Experimental "stack" chat layout                    |
| `http://localhost:5000/chat_canvas`  | Experimental canvas/timeseries chat layout          |
| `http://localhost:5000/api/tool/<n>` | Generic per-tool POST endpoint                      |
| `http://localhost:5000/api/chat`     | Agentic chat (Azure OpenAI + tool-calling loop)     |

### Smoke-test the wiring

Two ready-to-run samples exercise the same `get_libraries` query through the
two intended shapes — pick one (or run both) to confirm SMIPClient + auth +
GraphQL + tool registry all line up:

```
python SCRIPTS/01_list_libraries.py                          # headless: prints rows and exits
python PAGES/01_list_libraries/list_libraries.py             # browser: http://localhost:5101/list_libraries
```

If either returns library rows, the rest of the template is good to build on.
Details on what each sample does and how to copy them are in the PAGES and
SCRIPTS sections below.

## The PAGES convention

A "page" is a folder under `PAGES/` containing HTML + Vue + a tiny Python
launcher. Each page is its own runnable entry point:

```
python PAGES/<NN>_<page_name>/<page_name>.py     # boots its own port with the page mounted
```

The launcher pattern: add the project root to `sys.path`, import `app` from
`SMIP_API.smip_flask_api`, decorate it with `@app.route(PAGE_PATH,
endpoint=...)`, and run the combined app on its own port. Same-origin fetches
with relative URLs, no CORS dance, no proxy. Each page run is its own
process, so a buggy page can't break sibling pages.

To add a new page: copy an existing one, rename the folder + Python file,
update the route, and you're off.

**Worked example — `PAGES/01_list_libraries/`.** A two-file sample page:
`list_libraries.py` (the launcher — sys.path, import `app`,
`@app.route("/list_libraries")`, run on port 5101) and `list_libraries.html`
(Vue 3 from CDN, fetches `/api/tool/get_libraries` on mount, renders the
result as an `id` / `displayName` table). Run it:

```
python PAGES/01_list_libraries/list_libraries.py
# then http://localhost:5101/list_libraries
```

Doubles as an end-to-end smoke test — if rows show up, the SMIP wiring is good.

## The SCRIPTS convention

A "script" is a single runnable Python file directly under `SCRIPTS/`,
numbered for ordering:

```
SCRIPTS/
  01_migrate_units.py
  02_refactor_model.py
  03_backfill_displaynames.py
```

Scripts are for **worker / automation** use cases — migrations, model
refactors, data fixups, one-off batch operations. They are headless: no Vue,
no Flask, no port. Each script imports `SMIPClient` (or `SMIPMethods`) from
`SMIP_IO/`, does its work, prints/logs progress, and exits.

Run one with:

```
python SCRIPTS/01_migrate_units.py
```

The numeric prefix is just for sort order and rough chronology — it isn't a
required execution sequence (each script should be independently runnable
and idempotent where practical). To add a new script: pick the next number,
drop in a `.py`, import what you need from `SMIP_IO`, and run it.

**Worked example — `SCRIPTS/01_list_libraries.py`.** Builds a `SMIPMethods`
around a `SMIPClient`, calls `get_libraries()`, prints `id  displayName`
rows, exits 0/non-zero so it can be wired into a pipeline. Run it:

```
python SCRIPTS/01_list_libraries.py
```

Same data as the sample page above — the page is the browser shape, the
script is the headless shape. Both are end-to-end smoke tests for the
SMIP wiring.

## The tool registry

Adding a new query to the agent + REST + MCP at the same time is a three-step
job:

1. **Add the method** to `SMIPMethods` in `SMIP_IO/smip_methods.py` — does the
   GraphQL round-trip(s) and returns plain Python (list of dicts is the
   standard shape).
2. **Add the registry entry** in `SMIP_MCP/smip_tools.py` —
   `name / summary / description / parameters / ui / fn`. The `description`
   is what the LLM sees; the `fn` lambda dispatches to the SMIPMethods
   method.
3. **Add the typed MCP wrapper** in `SMIP_MCP/smip_mcp_server.py` (3 lines)
   so FastMCP can build the JSON schema from the Python signature.

Everything else is derived: the `/api/tool/<name>` endpoint picks it up
automatically, the OpenAI tool spec for `/api/chat` includes it, the docs
page renders a section for it, and `attach_docstrings_to(SMIPMethods)` would
copy the description onto the method's `__doc__` for IDE tooltips.

### Conventions across the registry

- **Empty input means "all"** wherever it makes sense. Keeps callers from
  threading the needle of "what's the magic word for unfiltered?".
- **Server-side filters where possible.** PostGraphile's `*Filter` types
  expose `includesInsensitive`, `contains`, `overlaps` and friends — push
  the filter to the GraphQL layer rather than fetching everything and
  trimming client-side.
- **Flat rows over nested trees.** A row should be self-contained where
  practical so callers don't have to cross-reference a tree to get useful
  results.

## Tools available today

| Tool             | What it does                                                          |
| ---------------- | --------------------------------------------------------------------- |
| `get_libraries`  | Smoke-test query — every library as `{id, displayName}`. No parameters |

This is a starter kit — add project-specific tools as you go.

## Sample SMIP browser scripts

Vendored under `___SMIP_SAAS_SIDE___/Sample Scripts/` are two minimal templates
for the SMIP browser-script runtime — Joomla/PHP files that the SMIP server
renders into a Vue page with a GraphQL context already wired up.

These are the **conversion targets** for the `PAGES/` workflow: vibe-code a
page in Python first (fast iteration, localhost reload, no SMIP round-trips),
then once it earns its keep, port it into one of these templates so it lives
on the SMIP side as a first-class script (browser script or display script,
depending on whether it stands alone or is bound to an instance via
`context.std_inputs.node_id`).

| File                          | Upstream (DevCon-SMIP, Part I / Topic 01)                                           | What it does                                                  |
| ----------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| `sample_browser_script.html`  | `02 Template with Vue GraphQL Context.php`                                          | Lists every `quantity` and its `measurementUnits`             |
| `sample_display_script.html`  | `02.2 Display Script Template with Vue GraphQL Context.php`                         | Renders the instance at `context.std_inputs.node_id` + children |

Both files carry their upstream URL in a header comment. The `.html` extension
is for editor convenience — the contents are SMIP-runtime templates, not
browser-loadable HTML. **Edits go upstream first, then re-vendor here.**

Upstream repo: <https://github.com/gregorvilkner/DevCon-SMIP---How-to-Code-on-ThinkIQ>

## Repository layout

```
.
├── README.md                       # this file
├── requirements.txt                # union of every surface's deps
├── .env / .env.example             # AZURE_OPENAI_* for /api/chat
├── .gitignore                      # ignores .env, __pycache__, .venv, etc.
│
├── SMIP_IO/                        # transport
│   ├── smip_client.py
│   ├── smip_methods.py
│   ├── model/                      # optional: typed dataclasses (project-specific)
│   ├── config.json (gitignored)
│   └── config.example.json
│
├── SMIP_MCP/                       # single source of truth for tools
│   ├── smip_tools.py               # TOOL_REGISTRY + derived OPENAI_TOOLS / make_dispatch
│   ├── smip_mcp_server.py          # FastMCP stdio + SSE entry points
│   └── agent_prompt.py             # SYSTEM_INSTRUCTIONS
│
├── SMIP_API/                       # Flask app
│   ├── smip_flask_api.py
│   └── smip_flask_api_documentation.html, smip_chat[/_stack/_canvas].html
│
├── PAGES/                          # one folder per browser-side page
│   └── 01_list_libraries/          #   sample page — lists libraries
│       ├── list_libraries.py       #     launcher (port 5101, /list_libraries)
│       └── list_libraries.html     #     Vue page (calls /api/tool/get_libraries)
│
├── SCRIPTS/                        # one runnable .py per worker/automation task
│   └── 01_list_libraries.py        #   sample script — prints every library
│
└── ___SMIP_SAAS_SIDE___/           # SMIP-side reference material
    ├── GraphQL Schema/             #   introspection export of the SMIP GraphQL API
    ├── JS SDK Template/            #   vendored snapshot of DevCon-SMIP Topic 06 / Take 4
    │                               #   (https://github.com/gregorvilkner/DevCon-SMIP---How-to-Code-on-ThinkIQ)
    │                               #   edits go upstream first, then re-vendor
    └── Sample Scripts/             #   vendored SMIP browser-script samples
                                    #   (Joomla/PHP templates rendered by the SMIP runtime)
                                    #   sample_browser_script.html  — Topic 01 / 02   "Template with Vue GraphQL Context"
                                    #   sample_display_script.html  — Topic 01 / 02.2 "Display Script Template with Vue GraphQL Context"
                                    #   upstream: github.com/gregorvilkner/DevCon-SMIP---How-to-Code-on-ThinkIQ
```

## Key dependencies

- `flask`, `python-dotenv` — the API server
- `openai` — Azure OpenAI for `/api/chat`
- `requests` — SMIPClient HTTP transport
- `mcp` — FastMCP server framework
- `gunicorn`, `uvicorn` — for serving the MCP SSE app on Azure

## Conventions that travel through the codebase

- **One process, one purpose.** SMIP_API runs the backend; each page py
  runs its own combined process for that page.
- **Empty input means "all".** The default pattern for filter parameters.
- **Vibe-code pages freely.** Pages live under `PAGES/`, each in its own
  process when run, using the standalone launcher pattern. The backend is
  unaffected by what they do.
- **Numbered scripts under `SCRIPTS/`.** Worker / automation tasks live as
  `01_do_this.py`, `02_do_that.py` — one-shot or batch operations like
  migrations or model refactors. Headless, run-and-exit; not pages, not
  long-running services.
