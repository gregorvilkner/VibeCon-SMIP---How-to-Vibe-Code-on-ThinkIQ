# SMIP JS SDK — generic, tenant-agnostic apiDemoMethods helpers + descriptors

A library of methods that abstract directly against the SMIP — generic type and instance lookups and mutations for creating and editing instances. Tenant-specific vocabularies and descriptors belong in a separate tenant SDK; the generic SMIP plumbing lives here.

The library carries the bits of the descriptor-driven SDK pattern that don't depend on what's in the tenant. Three generic mutations wrap PostGraphile's `updateAttribute` / `createAttribute` / `updateObject`, with `_buildPatchLiteral` translating a JS patch object into a GraphQL `patch: {…}` literal with proper undefined / null / scalar semantics. One generic query (`getTypes`) lists tiqTypes with optional toggles for typeToAttributeTypes, objectsByTypeId, subTypes, subTypeOf, and childEquipment.

## Files

- `00 Guzzle Client.php` — generic Guzzle PHP client. API-key wiring kept as commented-out reminders for when you re-target it at an authenticated REST API. Endpoint defaults to `https://example.com/api/v1/` — edit the two private fields when consuming.
- `01 API Template.php` — generic PHP dispatch skeleton with no cases (SMIP JS SDK is JS-only; PHP cases are the tenant's to fill in). Tenant-specific libraries that want their own PHP-side methods can either fork this template or `includeScript` it and add `case "<MethodName>":` blocks.
- `02 API Tools.html` — the SDK proper. Defines (or extends) `apiDemoMethods` with `_buildPatchLiteral` + the three mutations + `getTypes` via the additive merge pattern below. Adds 4 descriptors to `apiDemoTools` (one per non-helper method) so the doc page renders an interactive form for each. The descriptors are explicitly developer-facing — the mutation forms can write to the SoR if exercised carelessly.
- `03 API Documentation.html` — generic Vue page that renders any descriptor catalog. Reused by tenant-specific SDKs that want a doc page; on its own it shows the four SMIP JS SDK tools.
- `edgedenergy_thinkiq_net_smip_js_sdk_export.json` — importable SMIP library named `smip_js_sdk` containing the four scripts above.

## Additive merge pattern

Both `02 API Tools.html` (this library) and any tenant-specific equivalents use the same guard at the top:

```js
var apiDemoTools   = (typeof apiDemoTools   !== 'undefined') ? apiDemoTools   : [];
var apiDemoMethods = (typeof apiDemoMethods !== 'undefined') ? apiDemoMethods : {};
apiDemoTools.push( /* this library's descriptors */ );
Object.assign(apiDemoMethods, { /* this library's methods */ });
```

Whichever library loads first establishes the global; later loads merge their contributions in. Same-named fields are last-one-wins. Order of `includeScript` calls in a consumer script doesn't matter.

## What ships in `apiDemoTools` (descriptors visible on the doc page)

- **`UpdateAttributeViaJs`** — Mutation. `attributeId` (digits) + `patch` (JSON). DESTRUCTIVE.
- **`CreateAttributeViaJs`** — Mutation. `ownerId` (digits) + `attributeTypeDisplayName`. Returns the freshly-created `{ id, displayName }`.
- **`UpdateObjectViaJs`** — Mutation. `id` (digits) + `patch` (JSON, e.g. `{"importance": -260420}`). DESTRUCTIVE.
- **`GetTypesViaJs`** — Query. `typeNameSearch` (optional substring) + 6 toggles for what to include alongside each type: typeToAttributeTypes, objectsByTypeId (+ instanceNameSearch + per-instance attributes), subTypes, subTypeOf, childEquipment.

## What ships in `apiDemoMethods` (callable from any consumer script)

- `_buildPatchLiteral(patch)` — internal helper. Translates `{ floatValue: 12.5, datetimeValue: null }` into the GraphQL literal `{ floatValue: 12.5, datetimeValue: null }` with proper `undefined`-skip / `null`-emit / scalar-encoding semantics.
- `updateAttribute({ attributeId, patch })` — wraps `mutation updateAttribute(input: { id, patch })`.
- `createAttribute({ ownerId, attributeTypeDisplayName })` — wraps `mutation createAttribute(input: { attribute: { ownerId, attributeTypeDisplayName } })`.
- `updateObject({ id, patch })` — wraps `mutation updateObject(input: { id, patch })`.
- `getTypes(args)` — wraps `query tiqTypes(filter: { displayName: { includesInsensitive: ... } }) { ... }` with optional related-data subselections (typeToAttributeTypes, objectsByTypeId + per-instance attributes, subTypes, subTypeOf, childEquipment). Each toggle adds a fragment to the query body; defaults all OFF for a lean response.

## Importing into your SMIP

1. Settings → Libraries → Import → choose `edgedenergy_thinkiq_net_smip_js_sdk_export.json`.
2. **After every re-import**, open each of the four scripts in the SMIP IDE so the script body manifests from the database to disk. (SMIP defers writing the script body to disk until the script is opened in the IDE; consumers like Joomla / `includeScript` need the on-disk file.)
3. Open the API Documentation script to exercise the four tools interactively. Try `GetTypesViaJs` with `typeNameSearch='Storage Shelf'` and `includeSubTypes=true` to see the abstract type and its leaf subtypes — if that comes back populated, the SDK is wired correctly.
4. To consume from a tenant-specific library or display script:

   ```php
   TiqUtilities\Model\Script::includeScript('smip_js_sdk.api_tools');
   ```

   …after which `apiDemoMethods.updateAttribute(...)` / `createAttribute` / `updateObject` / `getTypes` are globally available.
