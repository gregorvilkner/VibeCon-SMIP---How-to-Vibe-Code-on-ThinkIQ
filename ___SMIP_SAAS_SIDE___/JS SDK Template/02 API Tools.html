<script>
//
// apiDemoTools — descriptor catalog for the API Demo Documentation page.
//
// The catalog deliberately mixes data-access methods so the page doubles as a
// teaching demo. Where possible, tools are paired ("…ViaPhp" + JS twin) so the
// reader can compare server-side vs. browser-side access to the same thing.
//
//   Plumbing            GetEchoViaPhp                +  GetEchoViaJs
//   GraphQL             SearchLibraryByNameViaPhp    +  SearchLibraryByNameViaJs
//   GraphQL (multi)     SearchLibraryWithCountsViaJs    (no PHP twin — JS demo)
//   REST (no twin)      GetPokemon
//
// GetPokemon has no JS twin on purpose — a browser-side fetch to a third-party
// REST host gets blocked by CORS in almost every case. Server-to-server HTTP
// is not subject to CORS, so the PHP path is the natural home for REST.
//
// Schema:
//   key          — camelCase identifier; used internally for state keys (must be unique).
//   name         — display name shown in the H1.
//   category     — short badge string rendered next to the name (e.g. "GraphQL (PHP)").
//   description  — H6 blurb shown next to the toggle caret.
//   via          — runner selector:
//                    "php"     → tiqJSHelper.invokeScriptAsync(apiFileName, fn, argument)
//                    "graphql" → tiqJSHelper.invokeGraphQLAsync(query(args)) → transform()
//                    "js"      → handler(args). Pure browser-side; never hits the server.
//   inputs       — array of input declarations (see below). Empty = no input form.
//                  When `via:"php"` and inputs is empty, the third arg to
//                  invokeScriptAsync is `null`.
//   output       — { kind } where kind is one of:
//                    "array"        — array result; clear → []; counter "{N} results."
//                    "single"       — single object or null; clear → null; counter.
//                    "single-quiet" — single value; clear → null; no counter (Echo-style).
//   render       — optional. Declarative hints for how to display the output above
//                  the raw JSON dump. The JSON dump is always shown — render is
//                  additive. Currently supported:
//                    images — array of { label, path } where path is a list of
//                             keys into the output object (e.g. ["sprites","front_default"]).
//                             Missing paths are silently skipped, so half-populated
//                             responses don't break the layout. Path is an array
//                             of segments (not a dotted string) so keys with
//                             hyphens like "official-artwork" work without escaping.
//
// PHP-specific fields (via: "php"):
//   fn           — string passed as the second argument to invokeScriptAsync;
//                  must match a "case" label in api_demo_take_4.api_template.
//
// GraphQL-specific fields (via: "graphql"):
//   query            — function (args) => string. Receives the parsed inputs object
//                      keyed by argName/key and returns the rendered GraphQL query.
//                      Use JSON.stringify() to interpolate string scalars safely.
//   transform        — optional function (response) => any. Pulls the meaningful
//                      result out of the GraphQL envelope. Defaults to r => r?.data.
//   showQueryPreview — if true, renders the rendered GraphQL query in a live <pre>
//                      below the inputs (mirrors the showJsonPreview behaviour).
//
// JS-specific fields (via: "js"):
//   handler          — either an inline function (args) => any  (or async),
//                      or a string method name resolved against apiDemoMethods
//                      (see escape-hatch block below). Use the inline form for
//                      one-liners (echo, trivial shaping); use the methods
//                      block when the logic needs multiple GraphQL round-trips,
//                      joins, or substantial post-processing — anything that
//                      would clutter the descriptor catalog.
//
// apiDemoMethods escape hatch (declared below the apiDemoTools array):
//   A plain object of { methodName: async function(args){...} } entries.
//   Each method gets the parsed inputs object and is free to call
//   tiqJSHelper.invokeGraphQLAsync() as many times as needed, shape the
//   result however it wants, and return the final value. The runner just
//   awaits whatever the method returns.
//
// Input declaration:
//   key             — camelCase key under inputs (used for v-model state binding).
//   argName         — name of the field on the args object passed to the runner.
//                       PHP runner    → matches $a->… in the API Template.
//                       GraphQL runner→ matches the property name read by query(args).
//                       JS runner     → matches the property name read by handler(args).
//                     Defaults to `key` if omitted.
//   label           — text shown in the <label> before the input.
//   type            — HTML input type ("text" | "number").
//   default         — initial v-model value (string).
//   parse           — "raw" | "json" | "number". The doc page parses this before
//                     building the args object.
//   showJsonPreview — if true, renders a live JSON-validation <pre> below the input.
//

var apiDemoTools = [

    //
    // Plumbing doublet — Echo
    //

    {
        key:         "getEchoViaPhp",
        name:        "GetEchoViaPhp",
        category:    "Plumbing (PHP)",
        description: "Round-trip echo through the PHP API. Browser → tiqJSHelper.invokeScriptAsync → api_demo_take_4.api_template → back. SDK plumbing check; touches no library or external service.",
        via:         "php",
        fn:          "GetEchoViaPhp",
        inputs: [
            { key: "input", argName: "hello", label: "Input: ", type: "text",
              default: '{"a":[23, 23, "asd"]}',
              parse: "json", showJsonPreview: true }
        ],
        output: { kind: "single-quiet" }
    },

    {
        key:         "getEchoViaJs",
        name:        "GetEchoViaJs",
        category:    "Plumbing (JS)",
        description: "Round-trip echo entirely in the browser — never leaves the page. JS twin of GetEchoViaPhp; demonstrates the descriptor system can host pure-JS tools alongside server-backed ones.",
        via:         "js",
        handler:     (args) => args.hello,
        inputs: [
            { key: "input", argName: "hello", label: "Input: ", type: "text",
              default: '{"a":[23, 23, "asd"]}',
              parse: "json", showJsonPreview: true }
        ],
        output: { kind: "single-quiet" }
    },

    //
    // GraphQL doublet — library search by display name (case-insensitive substring)
    //

    {
        key:         "searchLibraryByNameViaPhp",
        name:        "SearchLibraryByNameViaPhp",
        category:    "GraphQL (PHP)",
        description: "Same search, same query, but the GraphQL round-trip happens server-side. Browser → api_demo_take_4.api_template → TiqUtilities\\GraphQL\\GraphQL::MakeRequest → SMIP PostGraphile. The natural path for callers that have no browser (cron jobs, integrations, server-to-server).",
        via:         "php",
        fn:          "SearchLibraryByNameViaPhp",
        inputs: [
            { key: "input", argName: "search", label: "Search: ", type: "text",
              default: 'ThinkIQ',
              parse: "raw" }
        ],
        output: { kind: "array" }
    },

    {
        key:         "searchLibraryByNameViaJs",
        name:        "SearchLibraryByNameViaJs",
        category:    "GraphQL (JS)",
        description: "Searches libraries by display name via direct GraphQL — bypasses the PHP API entirely. Returns every library whose displayName lowercase contains the search string lowercase. Browser → tiqJSHelper.invokeGraphQLAsync → SMIP PostGraphile endpoint.",
        via:         "graphql",
        inputs: [
            { key: "input", argName: "search", label: "Search: ", type: "text",
              default: 'ThinkIQ',
              parse: "raw" }
        ],
        // (args) => GraphQL query string. JSON.stringify quotes & escapes the
        // scalar correctly for a GraphQL string literal.
        query: (args) => `
            query SearchLibraryByName {
                libraries(filter: { displayName: { includesInsensitive: ${JSON.stringify(args.search)} } }) {
                    id
                    displayName
                }
            }
        `,
        // PostGraphile returns an array under data.libraries; pass it through.
        transform:        r => (r && r.data && r.data.libraries) || [],
        showQueryPreview: true,
        output:           { kind: "array" }
    },

    //
    // GraphQL (multi-call) — JS-only demo of the apiDemoMethods escape hatch.
    // Same search, but each row is decorated with typesCount and scriptsCount.
    // The handler in apiDemoMethods makes two GraphQL round-trips and tallies
    // counts locally — see the methods block below for the full implementation.
    //

    {
        key:         "searchLibraryWithCountsViaJs",
        name:        "SearchLibraryWithCountsViaJs",
        category:    "GraphQL (JS — multi-call)",
        description: "Search libraries by name and decorate each row with typesCount and scriptsCount. Demonstrates the apiDemoMethods escape hatch: when via:'js' and handler is a string, the runner resolves it from the apiDemoMethods block — making room for multi-step logic (multiple GraphQL round-trips, joins, post-processing) that doesn't fit in a single declarative query/transform.",
        via:         "js",
        handler:     "searchLibraryWithCounts",
        inputs: [
            { key: "input", argName: "search", label: "Search: ", type: "text",
              default: 'Library',
              parse: "raw" }
        ],
        output: { kind: "array" }
    },

    //
    // REST — no JS twin, intentionally. Browser fetch to a third-party REST host
    // gets blocked by CORS; PHP is the only home for this path.
    //

    {
        key:         "getPokemon",
        name:        "GetPokemon",
        category:    "REST (PHP only — CORS)",
        description: "Looks up a Pokémon by name or Pokédex number on PokéAPI (https://pokeapi.co). PHP-side: api_demo_take_4.api_template → Guzzler::GetAsync(\"pokemon/{nameOrId}\"). Try: pikachu (25), charizard (6), bulbasaur (1), eevee (133), mewtwo (150), mew (151), snorlax (143), gengar (94). General principle: REST goes through PHP because a browser-side fetch to a third-party host typically gets blocked by CORS. (PokéAPI happens to be CORS-permissive, so a JS twin would work for this specific endpoint — but you can't assume that for third-party APIs in general.)",
        via:         "php",
        fn:          "GetPokemon",
        inputs: [
            { key: "input", argName: "nameOrId", label: "Name or Pokédex #: ", type: "text",
              default: 'pikachu',
              parse: "raw" }
        ],
        output: { kind: "single" },
        render: {
            images: [
                { label: "Default",        path: ["sprites", "front_default"] },
                { label: "Shiny",          path: ["sprites", "front_shiny"] },
                { label: "Back",           path: ["sprites", "back_default"] },
                { label: "Official art",   path: ["sprites", "other", "official-artwork", "front_default"] }
            ]
        }
    }

];


//
// apiDemoMethods — the "escape hatch" for via:"js" tools whose logic is too
// chunky to inline in the descriptor catalog above.
//
// Descriptors with via:"js" can set handler to either:
//   • an inline function (args) => any  — fine for one-liners (see GetEchoViaJs).
//   • a string method name              — resolved against this object at run
//                                          time by 03 API Documentation.php.
//
// Each method here gets the parsed inputs object and is free to:
//   • call tiqJSHelper.invokeGraphQLAsync(query) as many times as needed,
//   • shape, join, and post-process the results,
//   • return the final value the page should render.
//
// This is the JS-side counterpart to a switch case in 01 API Template.php:
// when the PHP function would do "query GraphQL → fan out → merge → return",
// you can do the same here without bouncing through PHP.
//
var apiDemoMethods = {

    // SearchLibraryWithCountsViaJs — search libraries by name and decorate
    // each matched row with typesCount and scriptsCount.
    //
    // Two GraphQL round-trips:
    //   1. libraries(filter: includesInsensitive)           → narrow the row set.
    //   2. tiqTypes + scripts (with partOf id only)         → tally locally.
    //
    // The local tally groups types/scripts by partOf.id, then we join back to
    // the matched libraries by id. We could push the count work to the server
    // by issuing per-library queries with totalCount, but that's an N+1 — for
    // a teaching demo, the two-call shape is plenty.
    searchLibraryWithCounts: async function(args){

        // Round-trip #1 — find the matching libraries.
        const libQuery = `
            query SearchLibrariesByName {
                libraries(filter: { displayName: { includesInsensitive: ${JSON.stringify(args.search)} } }) {
                    id
                    displayName
                }
            }
        `;
        const libResp   = await tiqJSHelper.invokeGraphQLAsync(libQuery);
        const libraries = (libResp && libResp.data && libResp.data.libraries) || [];
        if (libraries.length === 0) return [];

        // Round-trip #2 — pull every type and script with its partOf.id, then
        // tally locally. We only ask for the keys we need, so the payload is
        // small even on a big model.
        const countsQuery = `
            query AllTypesAndScripts {
                tiqTypes { id partOf { id } }
                scripts  { id partOf { id } }
            }
        `;
        const countsResp = await tiqJSHelper.invokeGraphQLAsync(countsQuery);
        const tiqTypes   = (countsResp && countsResp.data && countsResp.data.tiqTypes) || [];
        const scripts    = (countsResp && countsResp.data && countsResp.data.scripts)  || [];

        // Tally by partOf.id.
        const typesByLibId = {};
        tiqTypes.forEach(t => {
            const k = t && t.partOf && t.partOf.id;
            if (k != null) typesByLibId[k] = (typesByLibId[k] || 0) + 1;
        });
        const scriptsByLibId = {};
        scripts.forEach(s => {
            const k = s && s.partOf && s.partOf.id;
            if (k != null) scriptsByLibId[k] = (scriptsByLibId[k] || 0) + 1;
        });

        // Join: one row per matched library, with rolled-up counts.
        return libraries.map(lib => ({
            id:           lib.id,
            displayName:  lib.displayName,
            typesCount:   typesByLibId[lib.id]   || 0,
            scriptsCount: scriptsByLibId[lib.id] || 0
        }));
    }

};

</script>
