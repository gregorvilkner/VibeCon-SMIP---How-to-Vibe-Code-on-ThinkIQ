# Workflow

How to actually use this template well. The
[QUICKSTART](QUICKSTART.md) gets you to "rows on the screen"; this doc
covers what you should do *next*, and the discipline that keeps a
VibeCon-SMIP project from turning into spaghetti.

## Recommended setup — give your LLM the whole repo

The big shift isn't "use an LLM to write code." It's the move from
copy-pasting snippets into a chat to having the LLM **inhale the whole
project** and cross-reason across files. This template is built for that
mode.

The repo is dense in a deliberate way: one `TOOL_REGISTRY` entry fans out
to a REST endpoint, an MCP wrapper, an OpenAI tool spec, and a docs-page
section, plus a dual-mode import pattern in `SMIP_IO/`. A snippet-mode LLM
will guess at how it all fits. A whole-project-mode LLM, with every file in
context, will name the three places to edit and copy the existing registry
entry's shape into them.

So open the folder in something that can hold the whole tree in context —
Claude Desktop with the folder mounted as a project, Cursor or Claude Code
in the project root, or any LLM-aware editor where the model has read
access to every file.

Bonus: the built-in MCP server gives that same in-context LLM a live channel
into the SMIP itself — read the registry to know *what* tools exist, then
*call* them through MCP to see real data. Source code plus live introspection
in one chat session.

## The recommended path

The temptation, especially with an LLM in the loop, is to skip straight to
"build a page that does X" and let the LLM stuff raw GraphQL queries into
the Vue component. That works and produces something on screen quickly.
It also produces spaghetti — every page reinvents the same queries, the
chat agent can't help you because nothing is registered as a tool, and the
round-trip back to SMIP-side scripts becomes a rewrite rather than a port.

The disciplined path is six steps:

### 1. Bootstrap with a library export

Export a library from ThinkIQ as JSON and drop it into the repo. A
reasonable home is alongside the existing reference one in
`___SMIP_SAAS_SIDE___/JS SDK Template/library_export.json`, or under a
project-specific `data/` folder.

The reason this matters: it gives any whole-project-mode LLM your actual
domain vocabulary. "What tools should I build?" goes from a generic
GraphQL conversation to "given that your library has *these* types and
*these* attributes, here are the four tools that cover 80% of your
foreseeable queries."

Skip this step and your tools end up generic; do it once and the LLM
becomes a competent collaborator on *your* domain, not GraphQL-in-the-
abstract.

### 2. Build tools first, not pages

Spend a session — sometimes just 30 minutes with a good LLM — building
3–6 tools in `SMIPMethods` + `TOOL_REGISTRY` *before* you build any page
or script that uses them. Use the QUICKSTART step-5 pattern:

1. Method on `SMIPMethods` (`SMIP_IO/smip_methods.py`)
2. Registry entry (`SMIP_MCP/smip_tools.py`)
3. Typed MCP wrapper (`SMIP_MCP/smip_mcp_server.py`, 3 lines)

Once a tool is in the registry it's reachable from the REST endpoint, the
agentic chat, the MCP server, and the docs page — automatically. That
fan-out is the whole point of doing this work first; you're not just
abstracting GraphQL, you're producing a single artifact that four
different surfaces consume.

Naming and shape conventions to follow:

- **Empty input means "all"** wherever it makes sense.
- **Server-side filters where possible** — push filtering down to the
  GraphQL layer rather than fetching everything and trimming client-side.
- **Flat rows over nested trees** — a row should be self-contained where
  practical so callers don't cross-reference a tree to get useful results.

### 3. Vibe-code thin pages and scripts

Now you can build pages and scripts freely, and the discipline is simple:
they should be **thin shells around tool calls**, not GraphQL clients.

A page should look like:

```js
const resp = await fetch('/api/tool/your_tool_name', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ args: { ... } }),
});
const json = await resp.json();
this.rows = json.data;
```

Not like:

```js
// avoid: raw GraphQL in the page
const resp = await fetch('/graphql', { ...giant query string... });
```

A script should look like:

```python
methods = SMIPMethods(SMIPClient())
rows = methods.your_tool_name(...)
```

Not like:

```python
# avoid: ad-hoc GraphQL in the script
client.query("query { ... }")
```

Pages live under `PAGES/<NN>_<page_name>/` (folder per page, `.py`
launcher + `.html` Vue file). Scripts live directly under `SCRIPTS/` as
`<NN>_<task>.py`. Both are vibe-code-friendly: each runs in its own
process, the backend is unaffected, and a buggy page can't break sibling
pages. See [ARCHITECTURE](ARCHITECTURE.md) for the full launcher pattern.

### 4. Validate the tool surface via /chat

After every meaningful tool registry change, open `/chat` (or
`/chat_canvas`) and ask the agentic loop questions in natural language.
This validates the registry from a different angle than your pages do —
your pages know exactly which tool to call; the agent has to *choose*
based on the tool descriptions. If the agent can't pick the right tool,
your descriptions are too vague.

This is one of the cheapest, highest-signal feedback loops in the
template. Use it.

### 5. Round-trip to SMIP-side scripts

Once a page or script earns its keep — meaning it's done a job a few times
and you want it on the SMIP side rather than running on localhost — port
it to one of the vendored Joomla/PHP browser-script templates under
`___SMIP_SAAS_SIDE___/Sample Scripts/`:

| Sample                          | Use it for                                          |
| ------------------------------- | --------------------------------------------------- |
| `sample_browser_script.html`    | Standalone pages (no specific instance binding)     |
| `sample_display_script.html`    | Pages bound to an instance via `context.std_inputs.node_id` |

The conversion is largely mechanical — Vue + GraphQL is on both sides —
but the SMIP-side script uses the JS SDK rather than your Python tools.
Which leads to the parity question…

### 6. Keep the JS SDK in lockstep with TOOL_REGISTRY

For step 5 to work, every tool a SMIP-side script needs must also exist
in the JS SDK Template under `___SMIP_SAAS_SIDE___/JS SDK Template/`.
Conventions for managing that:

**Keep starter tools, hide them from the docs page.** The Python side
already does this: `SMIPMethods` has plenty of internal-only methods
(`get_enum_type_by_display_name`, `create_object`, `delete_object`,
`update_attribute`) that are intentionally NOT in `TOOL_REGISTRY`. They
exist as scaffolding; they're not part of the public, LLM-facing,
docs-page surface.

The JS SDK should mirror that. The starter tools that ship with the
template should stay in the JS-side registry — they're a permanent
smoke test you can always run to answer "is the JS SDK alive?". But
they should be hidden from the docs page (a `documented: false` flag
or equivalent), so the docs page only shows the project's actual
surface, not the template's scaffolding.

This convention preserves three things at once:

- **The smoke test.** Any project can always verify the SMIP-side
  wiring with the same starter tool.
- **Python ↔ JS parity.** Both sides have the same "registry but
  filtered for docs" pattern, so a developer working on either side
  doesn't have to relearn the convention.
- **A clean public contract.** The docs page reflects the project's
  real API, not "here's our project plus everything that came in the
  template box."

When you build a new Python tool that you know will round-trip, mirror
it on the JS side at the same time — same name, same parameters, same
return shape. Future-you will thank present-you for the discipline.

## Anti-patterns to watch for

A few failure modes worth naming so you can spot them early:

**Pages with raw GraphQL.** First red flag of the discipline slipping.
The fix is always the same: extract the query into a tool. Your future
chat agent will thank you, and so will the next page that needs the
same data.

**Tools with vague descriptions.** "Get stuff from the SMIP" is not a
description. The agent in `/chat` is the test — if it can't pick your
tool reliably given the user's natural-language question, the
description needs more specifics about *what* and *when to use*.

**One giant tool that does everything.** The temptation when you have
a complex query is to expose it as one big tool with twelve optional
parameters. Resist. Smaller tools with sharper purpose compose better
in agent conversations and are easier to round-trip into JS SDK
parity.

**Scripts that don't exit cleanly.** A `SCRIPTS/` script should `return
0` on success and non-zero on failure so it can be wired into a
pipeline or scheduled task. If it just hangs or prints "Done" without
exiting, that's not yet a worker script.
