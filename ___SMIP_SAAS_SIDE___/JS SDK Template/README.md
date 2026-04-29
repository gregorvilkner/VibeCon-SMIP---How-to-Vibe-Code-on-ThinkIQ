# Take 4 — Descriptor Catalog (recommended template)

> **Vendored snapshot.** This folder is a copy of
> [`Part II / Topic 06 / Take 4 — Descriptor Catalog`](https://github.com/gregorvilkner/DevCon-SMIP---How-to-Code-on-ThinkIQ/tree/main/Part%20II%20-%20Headless%20Scripts/Topic%2006%20-%20OOP%20Techniques%20and%20Project%20Organization/Take%204%20-%20Descriptor%20Catalog)
> from the DevCon-SMIP repo. Treat the GitHub copy as the source of truth —
> make changes there first, then re-vendor into this folder. Edits made
> directly here will drift and be overwritten the next time the snapshot is
> refreshed. The relative `../README.md` link at the bottom of this file
> resolves only in the upstream repo.


Replaces the hand-coded doc page with a generic `v-for` over a descriptor catalog. Each entry declares everything the page needs to render and run a tool — name, description, inputs, output kind, optional image rendering, and a `via:` field that selects the runner (`php`, `graphql`, or `js`). Adding a new tool is one entry in `02 API Tools.html`. No template editing.

## Files

- `00 Guzzle Client.php` — points at PokéAPI (CORS-permissive, distinctive payloads); API-key wiring kept as commented reminders for when you re-target at an authenticated API.
- `01 API Template.php` — PHP dispatch. Demonstrates REST via Guzzle (`GetPokemon`) and server-side GraphQL via `TiqUtilities\GraphQL\GraphQL` (`SearchLibraryByNameViaPhp` — case-insensitive substring search using PostGraphile's `includesInsensitive` filter).
- `02 API Tools.html` — the descriptor catalog (`apiDemoTools[]`) plus the `apiDemoMethods` escape hatch (see below). Single source of truth for what shows up on the doc page.
- `03 API Documentation.html` — generic Vue page that renders any descriptor. Supports image strips, GraphQL query previews, clipboard copy.

## What this take adds

A tool's full UI — input form, runner, output formatting, optional image previews — is one descriptor entry. The same page hosts PHP, GraphQL, and pure-JS tools side-by-side; "doublet" demos (`...ViaPhp` + `...ViaJs`) come for free, which is useful for teaching when each access path makes sense.

The `render.images` field on the GetPokemon descriptor demonstrates the extension hook for richer output. Same hook accommodates Raman spectra (line-chart kind), microscopy images (zoomable viewer kind), camera frames — a new render kind is built once, then declared per-descriptor.

## GraphQL from JS — two flavors

The descriptor catalog supports two ways to call GraphQL directly from the browser. Both bypass the PHP API; pick the one that fits the shape of the work.

**1. Simple call/response — `via: "graphql"`.** Declarative one-liner: the descriptor declares a `query(args) => string` and an optional `transform(response) => any`. The runner does a single `tiqJSHelper.invokeGraphQLAsync(query)` round-trip and hands the transformed result to the page. `showQueryPreview: true` renders the query live below the inputs as you type. Best for "one query in, one shape out". `SearchLibraryByNameViaJs` is the canonical example.

**2. Complex logic via `apiDemoMethods` escape hatch — `via: "js"` with `handler: "<methodName>"`.** When the work is more than one round-trip — multiple GraphQL calls, joins, post-processing, conditional logic — set the descriptor's `handler` to a string and put the actual implementation in the `apiDemoMethods` block declared below `apiDemoTools`. Each method is a free-form `async function(args)` that can call `tiqJSHelper.invokeGraphQLAsync` as many times as needed and return the final shaped result. The runner just awaits whatever you return. `SearchLibraryWithCountsViaJs` is the canonical example: it issues two GraphQL queries (matching libraries; then all types/scripts), tallies counts locally by `partOf.id`, and joins back to produce one row per matched library with `typesCount` and `scriptsCount`.

This mirrors the PHP side: a `via: "graphql"` descriptor is the JS equivalent of a one-shot `MakeRequest()` in `01 API Template.php`, while a `via: "js"` handler in `apiDemoMethods` is the JS equivalent of a switch case that does several `MakeRequest()` calls and merges results before returning. Inline arrow-function handlers are still supported (see `GetEchoViaJs`) for true one-liners — the methods block is just the tidier home when the body grows.

## Try it in your SMIP

`library_export.json` in this folder is an importable SMIP library named `api_demo_take_4`. Import it (Settings → Libraries → Import), then open the "API Documentation" script and try:

- `pikachu`, `mewtwo`, or pokédex `25` against **GetPokemon** — sprites render above the JSON.
- `ThinkIQ` against **SearchLibraryByNameViaPhp / ViaJs** — same query, same result, two round-trip paths.
- `Library` against **SearchLibraryWithCountsViaJs** — one row per matched library, decorated with `typesCount` and `scriptsCount` from a second GraphQL call merged in JS.

See the [topic README](../README.md) for the full four-take progression.
