# Quickstart

Getting from `git clone` to a working chat agent calling tools against your
SMIP, in five steps. Each step adds exactly one new dependency and verifies it
before moving on — if a step fails, you know which layer to debug.

You'll need: Python 3.10+, an SMIP (ThinkIQ) tenant with API credentials, and
optionally an Azure OpenAI deployment (only needed for steps 4–5).

## Step 1 — Install dependencies

From the project root:

```
pip install -r requirements.txt
```

That's it for tooling — no Node, no build step.

## Step 2 — Connect to your SMIP

The transport layer needs credentials for your tenant. Copy the example config
and fill it in with your real values:

```
cp SMIP_IO/config.example.json SMIP_IO/config.json
```

Open `SMIP_IO/config.json` and replace each `REPLACE_WITH_*` placeholder:

```json
{
  "SMIP": {
    "graphQlEndpoint": "https://YOUR_INSTANCE.thinkiq.net/graphql",
    "clientId":        "...",
    "clientSecret":    "...",
    "role":            "...",
    "userName":        "..."
  }
}
```

`config.json` is gitignored, so your secrets stay local.

**Don't have these values yet?** You'll need to set up an *authenticator* in
your ThinkIQ tenant first — that's what produces the `clientId` /
`clientSecret` pair the SMIP uses for its JWT challenge/response auth flow.
See the CESMII guide:
[Accessing the SMIP GraphQL API remotely](https://github.com/cesmii/GraphQL-API/blob/main/Docs/jwt.md#accessing-the-smip-graphql-api-remotely).
Once you've created an authenticator, paste its values into `config.json`.

**Verify it.** Run the sample script:

```
python SCRIPTS/01_list_libraries.py
```

If you see something like:

```
3 library/-ies:
        12  My Library
        13  Another Library
        14  Project Library
```

…then transport, JWT auth, and GraphQL all work. If you see an error, fix it
here before moving on — every later step depends on this.

## Step 3 — Start the Flask app and verify the page workflow

The Flask app is what serves the docs page, the chat UIs, and the
`/api/tool/<name>` endpoint that pages call. Boot the sample page (which
imports the same Flask `app` and mounts itself on its own port):

```
python PAGES/01_list_libraries/list_libraries.py
```

Then open <http://localhost:5101/list_libraries> in your browser.

You should see the same library rows you got from the script in step 2,
rendered as an HTML table. Same data, browser shape — that confirms the
PAGES launcher pattern works (sys.path, route decoration, same-origin
fetch through `/api/tool/get_libraries`, Vue 3 from CDN).

If the page loads but the table is empty or shows an error, open the
browser devtools console — the page logs the failed `fetch` clearly.

## Step 4 — Add the .env and verify the chat agent

The `/api/chat` endpoint runs an agentic loop backed by Azure OpenAI: the
LLM is given your TOOL_REGISTRY as OpenAI tool specs and decides when to call
them. To wire it up, drop a `.env` at the project root:

```
cp .env.example .env
```

Edit `.env` with your Azure OpenAI credentials:

```
AZURE_OPENAI_ENDPOINT=https://YOUR_RESOURCE.openai.azure.com/
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_API_VERSION=2025-01-01-preview     # optional
AZURE_OPENAI_DEPLOYMENT=gpt-4o                   # optional
```

Stop the page launcher from step 3 (Ctrl-C) and start the main API instead:

```
python SMIP_API/smip_flask_api.py
```

It runs on <http://localhost:5000>. Visit <http://localhost:5000/> first —
that's the auto-generated documentation page (sections rendered from
`TOOL_REGISTRY_PUBLIC`). You should see a section for `get_libraries` with its
description and a "Run" button you can press to invoke it directly.

Then visit <http://localhost:5000/chat> and ask:

> What libraries are in the SMIP?

The agent should call `get_libraries`, get the rows back, and answer in
natural language. If you watch the network panel, you'll see the
`/api/chat` request return both the answer and the tool-call history.

If you get a 500 from `/api/chat`, the most common cause is missing or
typo'd Azure OpenAI env vars — check the Flask terminal output, the
error message names which key is missing.

## Step 5 — Import a library, build your first tool

The smoke tests are passing. Now make the template *yours* by adding one
project-specific tool.

**5a. Drop your library export.** Export a library from ThinkIQ as JSON,
and drop it into the repo where an LLM with project context can read it.
A reasonable home is alongside the existing one:

```
___SMIP_SAAS_SIDE___/JS SDK Template/library_export.json     # already there for reference
```

…or under a new `data/` folder if you want to keep it cleanly separated.
The point is just that the file lives in the repo so any
whole-project-mode LLM session sees it as context.

**5b. Add the method.** Open `SMIP_IO/smip_methods.py` and add a method
on `SMIPMethods` — copy the shape of `get_libraries`. For example, a
"list every quantity" tool:

```python
def get_quantities(self):
    """Return every measurement quantity as a flat list of {id, displayName}."""
    query = "query GetQuantities { quantities { id displayName } }"
    resp = self.client.query(query)
    return ((resp or {}).get("data") or {}).get("quantities") or []
```

**5c. Register it.** Open `SMIP_MCP/smip_tools.py` and add a `TOOL_REGISTRY`
entry — copy the existing `get_libraries` entry and rename:

```python
{
    "name": "get_quantities",
    "summary": "Return every measurement quantity as {id, displayName}.",
    "description": (
        "Return every measurement quantity in the SoR as a flat list of "
        "{id, displayName} dicts. No parameters."
    ),
    "parameters": {"type": "object", "properties": {}, "required": []},
    "ui": {"inputs": []},
    "fn": lambda m, a: m.get_quantities(),
},
```

**5d. Add the MCP wrapper.** Open `SMIP_MCP/smip_mcp_server.py` and add
three lines — copy the `get_libraries` wrapper and rename:

```python
@mcp.tool(description=_R["get_quantities"]["description"])
def get_quantities() -> str:
    return json.dumps(_call("get_quantities", {}), default=str)
```

**5e. Verify.** Restart the Flask app:

```
python SMIP_API/smip_flask_api.py
```

Visit <http://localhost:5000/> — your new `get_quantities` section appears
in the docs page automatically. Visit <http://localhost:5000/chat> and ask:

> What quantities are defined in the SMIP?

The agent picks up the new tool, calls it, and answers. You're now
operating the template the way it's meant to be operated.

## You're up

If all five steps worked, you have a working VibeCon-SMIP. From here:

- **[WORKFLOW.md](WORKFLOW.md)** — the recommended way to grow this.
  Strategic / best-practice content: bootstrapping with library exports,
  vibe-coding thin pages and scripts that call your tools (instead of raw
  GraphQL), validating via the chat agent, the round-trip back to SMIP-side
  scripts, the JS SDK parity convention.
- **[ARCHITECTURE.md](ARCHITECTURE.md)** — what's where and why. Reference
  for when you need to understand a piece of the wiring.
