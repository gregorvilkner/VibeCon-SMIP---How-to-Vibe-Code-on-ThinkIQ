"""High-level SMIP operations (wraps a `SMIPClient`).

Keep transport/auth in `SMIPClient` and GraphQL operations here so the client
file can be reused as a template across projects.
"""

import json

# SMIPClient is required for SMIPMethods to be useful at all, so import it
# eagerly. Try the package-mode path first, then the flat-mode fallback.
try:
    # Package-mode (e.g. `from SMIP_IO.smip_methods ...`)
    from .smip_client import SMIPClient
except ImportError:
    # Flat-mode (SMIP_IO itself on sys.path)
    from smip_client import SMIPClient                  # type: ignore


class SMIPMethods:
    """Higher-level SMIP operations (wraps a `SMIPClient`)."""

    def __init__(self, client: SMIPClient):
        self.client = client

    # ---------------------------------------------------------------------
    # Libraries — minimal smoke-test query. One GraphQL round-trip; no
    # parameters. Returns the bare `libraries` root field with id +
    # displayName so we can verify the SMIPClient + TOOL_REGISTRY +
    # MCP / Flask wiring end-to-end before adding anything domain-specific.
    # ---------------------------------------------------------------------
    def get_libraries(self):
        """Return every library in the SoR as a flat list of `{id, displayName}`
        dicts.

        Stub / smoke-test method — the GraphQL field shape may need to be
        widened (e.g. `relativeName`, `description`, `idPath`) once the
        project's library workflows are defined. For now this is a single
        round-trip with the minimum fields needed to confirm the plumbing
        works.

        One GraphQL round-trip:
            query GetLibraries {
              libraries { id displayName }
            }

        Returns: list of {id, displayName}.
        """
        query = "query GetLibraries { libraries { id displayName } }"
        resp = self.client.query(query)
        return ((resp or {}).get("data") or {}).get("libraries") or []

    # ---------------------------------------------------------------------
    # Quantities + units — every quantity with its full unit list and
    # conversion factors (conversionOffset, conversionMultiplier) so a
    # caller can do real numeric unit conversions client-side. Used by
    # PAGES/02_unit_converter/.
    # ---------------------------------------------------------------------
    def get_quantities_with_units(self):
        """Return every measurement quantity with its full unit list,
        including conversion factors.

        One GraphQL round-trip:
            query GetQuantitiesWithUnits {
              quantities {
                id displayName description quantitySymbol
                measurementUnits {
                  id displayName description
                  conversionOffset conversionMultiplier symbol
                }
              }
            }

        Returns a list of:
            {
              "id", "displayName", "description", "quantitySymbol",
              "measurementUnits": [
                {
                  "id", "displayName", "description",
                  "conversionOffset", "conversionMultiplier", "symbol"
                }, ...
              ]
            }

        Conversion math (client side):
            base   = (value + fromOffset) * fromMultiplier
            target = base / toMultiplier - toOffset
        """
        query = (
            "query GetQuantitiesWithUnits { "
            "  quantities { "
            "    id displayName description quantitySymbol "
            "    measurementUnits { "
            "      id displayName description "
            "      conversionOffset conversionMultiplier symbol "
            "    } "
            "  } "
            "}"
        )
        resp = self.client.query(query)
        return ((resp or {}).get("data") or {}).get("quantities") or []

    # =====================================================================
    # Internal / automation-only methods.
    # Intentionally NOT registered in SMIP_MCP/smip_tools.py — these are
    # direct-call only (scripts, notebooks, batch jobs). Do not add
    # TOOL_REGISTRY entries or @mcp.tool wrappers for anything below.
    # =====================================================================

    def get_enum_type_by_display_name(self, filter_string: str = ""):
        """Return enumeration types whose displayName exactly equals
        `filter_string` — e.g. "CMMS Available Status".

        Internal / automation-only: not exposed via Flask or MCP. Used by
        scripts that need to resolve an enum type by name to its id, full
        enum value list, color codes, default values, etc.

        `filter_string` is REQUIRED and matched exactly (PostGraphile's
        `condition: { displayName: ... }` is an equality test). Empty
        input raises ValueError to stop accidental "list everything" calls.

        Returns a list of dicts (typically 0 or 1 element):
            [{
              "id", "displayName", "relativeName", "description",
              "fqn", "idPath",
              "enumerationNames", "enumerationColorCodes",
              "enumerationDescriptions", "defaultEnumerationValues",
            }, ...]

        One GraphQL round-trip:
            enumerationTypes(condition: { displayName: "<filter_string>" }) {
              id displayName relativeName description fqn idPath
              enumerationNames enumerationColorCodes enumerationDescriptions
              defaultEnumerationValues
            }
        """
        filter_string = (filter_string or "").strip()
        if not filter_string:
            raise ValueError(
                "filter_string is required (exact-match displayName)"
            )

        query = (
            "query GetEnumTypeByDisplayName { "
            "  enumerationTypes(condition: { displayName: "
            + json.dumps(filter_string) +
            " }) { "
            "    id displayName relativeName description fqn idPath "
            "    enumerationNames enumerationColorCodes enumerationDescriptions "
            "    defaultEnumerationValues "
            "  } "
            "}"
        )
        resp = self.client.query(query)
        return ((resp or {}).get("data") or {}).get("enumerationTypes") or []

    def get_type_by_display_name(self, filter_string: str = ""):
        """Return TiQ types whose displayName exactly equals `filter_string`.

        Internal / automation-only: not exposed via Flask or MCP. Used by
        scripts that need to resolve a type to its id / fqn / idPath for
        further drill-in (e.g. listing every record of a given type), and
        to read the type's attribute schema (`typeToAttributeTypes`) for
        migration / replacement workflows.

        `filter_string` is REQUIRED and matched exactly. Empty input
        raises ValueError.

        Returns a list of dicts (typically 0 or 1 element):
            [{
              "id", "displayName", "relativeName", "description",
              "fqn", "idPath",
              "typeToAttributeTypes": [
                {"id", "displayName", "dataType", "importance"}, ...
              ],
            }, ...]

        `dataType` is the SMIP scalar kind for that attribute slot —
        commonly "STRING" or "ENUMERATION" (others exist). When writing
        instances:
          - dataType == "STRING"      -> set stringValue
          - dataType == "ENUMERATION" -> set enumerationValue (also a
                                         string, e.g. "1")
        update_attribute() takes both as separate kwargs; pick based on
        the source attribute's dataType.

        `importance` is the SMIP-defined sort key (lower = more
        important / shown first). The slots come back unordered from
        the server — sort by `importance` client-side when display
        order matters.

        One GraphQL round-trip:
            tiqTypes(condition: { displayName: "<filter_string>" }) {
              id displayName relativeName description fqn idPath
              typeToAttributeTypes { id displayName dataType importance }
            }
        """
        filter_string = (filter_string or "").strip()
        if not filter_string:
            raise ValueError(
                "filter_string is required (exact-match displayName)"
            )

        query = (
            "query GetTypeByDisplayName { "
            "  tiqTypes(condition: { displayName: "
            + json.dumps(filter_string) +
            " }) { "
            "    id displayName relativeName description fqn idPath "
            "    typeToAttributeTypes { id displayName dataType importance } "
            "  } "
            "}"
        )
        resp = self.client.query(query)
        return ((resp or {}).get("data") or {}).get("tiqTypes") or []

    # ---------------------------------------------------------------------
    # Mutating internal methods. DESTRUCTIVE — they create / delete / modify
    # records in the SoR. Same internal-only contract as the lookups above:
    # NO TOOL_REGISTRY entries, NO @mcp.tool wrappers, NO Flask routes.
    # Direct-call only (scripts, notebooks, batch jobs). Treat with care —
    # a typo in a part_of_id can land an object in the wrong subtree, and
    # delete_object has no undo.
    # ---------------------------------------------------------------------

    def create_object(
        self,
        display_name: str,
        type_id: str,
        part_of_id: str,
        description: str = "",
    ):
        """Create an object under a parent. Internal / automation-only.

        DESTRUCTIVE: writes a new row to the SoR. There is no dry-run mode
        here — call site is responsible for validating inputs.

        Parameters
            display_name : the new object's displayName (required, trimmed)
            type_id      : TiQ type id (digits-only string). Resolve from a
                           name with get_type_by_display_name first.
            part_of_id   : parent object id (digits-only string) — where in
                           the tree this object is mounted.
            description  : optional free-text description. Empty string is
                           sent through as-is so the SoR field is set.

        All three required fields must be non-empty. `type_id` and
        `part_of_id` must be digits — display names are NOT accepted.

        Returns the `object` payload of the mutation (id, displayName,
        typeId, partOfId, attributes), or None if the server returned no
        object (treat that as a failed create and inspect the response).

        One GraphQL round-trip:
            mutation CreateObject {
              createObject(input: { object: {
                displayName: "<display_name>"
                description: "<description>"
                typeId:      "<type_id>"
                partOfId:    "<part_of_id>"
              } }) {
                clientMutationId
                object {
                  id displayName typeId partOfId
                  attributes { id displayName }
                }
              }
            }
        """
        display_name = (display_name or "").strip()
        type_id      = (type_id or "").strip()
        part_of_id   = (part_of_id or "").strip()
        description  = description or ""   # allow empty; do NOT strip user spaces

        if not display_name:
            raise ValueError("display_name is required")
        if not type_id or not type_id.isdigit():
            raise ValueError(
                f"type_id must be a node id (digits only); got {type_id!r}"
            )
        if not part_of_id or not part_of_id.isdigit():
            raise ValueError(
                f"part_of_id must be a node id (digits only); got {part_of_id!r}"
            )

        mutation = (
            "mutation CreateObject { "
            "  createObject(input: { object: { "
            "    displayName: " + json.dumps(display_name) + " "
            "    description: " + json.dumps(description)  + " "
            "    typeId: \""    + type_id    + "\" "
            "    partOfId: \""  + part_of_id + "\" "
            "  } }) { "
            "    clientMutationId "
            "    object { "
            "      id displayName typeId partOfId "
            "      attributes { id displayName } "
            "    } "
            "  } "
            "}"
        )
        resp = self.client.query(mutation, op_type="mutation")
        payload = ((resp or {}).get("data") or {}).get("createObject") or {}
        return payload.get("object")

    def delete_object(self, object_id: str):
        """Delete an object by id. Internal / automation-only.

        DESTRUCTIVE and IRREVERSIBLE: the SoR row is removed. There is no
        soft-delete here. Verify the id before calling.

        `object_id` is REQUIRED and must be digits. Display names are NOT
        accepted.

        Returns the `deleteObject` payload (typically just
        `{"clientMutationId": null}`). Errors from the server propagate up
        as exceptions from SMIPClient.

        One GraphQL round-trip:
            mutation DeleteObject {
              deleteObject(input: { id: "<object_id>" }) {
                clientMutationId
              }
            }
        """
        object_id = (object_id or "").strip()
        if not object_id or not object_id.isdigit():
            raise ValueError(
                f"object_id must be a node id (digits only); got {object_id!r}"
            )

        mutation = (
            "mutation DeleteObject { "
            "  deleteObject(input: { id: \"" + object_id + "\" }) { "
            "    clientMutationId "
            "  } "
            "}"
        )
        resp = self.client.query(mutation, op_type="mutation")
        return ((resp or {}).get("data") or {}).get("deleteObject") or {}

    def update_attribute(
        self,
        attribute_id: str,
        string_value=None,
        enumeration_value=None,
    ):
        """Update an attribute by id. Internal / automation-only.

        DESTRUCTIVE: overwrites the attribute's existing value(s). At
        least one of `string_value` / `enumeration_value` must be supplied
        (None means "leave that field alone"; "" means "set the field to
        empty string").

        Parameters
            attribute_id      : attribute id (digits-only string).
            string_value      : new stringValue, or None to leave unchanged.
            enumeration_value : new enumerationValue, or None to leave
                                unchanged. THIS IS NOT AN ARRAY INDEX —
                                it's the stored value defined on the enum
                                type. Look it up via
                                get_enum_type_by_display_name(...) and
                                use `defaultEnumerationValues[i]` paired
                                with `enumerationNames[i]` (i.e., the
                                value at the same index as the desired
                                name). Sending an index that doesn't
                                appear in `defaultEnumerationValues`
                                silently no-ops (the server returns no
                                attribute payload).

        Returns the `attribute` payload of the mutation (id, displayName,
        stringValue, enumerationName), or None if the server returned no
        attribute.

        One GraphQL round-trip:
            mutation UpdateAttribute {
              updateAttribute(input: {
                id: "<attribute_id>"
                patch: { stringValue: "...", enumerationValue: "..." }   # only fields actually supplied
              }) {
                clientMutationId
                attribute { id displayName stringValue enumerationName }
              }
            }
        """
        attribute_id = (attribute_id or "").strip()
        if not attribute_id or not attribute_id.isdigit():
            raise ValueError(
                f"attribute_id must be a node id (digits only); "
                f"got {attribute_id!r}"
            )
        if string_value is None and enumeration_value is None:
            raise ValueError(
                "at least one of string_value / enumeration_value is required"
            )

        # Build the patch dynamically so we only send fields the caller
        # actually wants to change. Empty string is a real value (clears
        # the field); only None means "skip".
        patch_parts = []
        if string_value is not None:
            patch_parts.append("stringValue: " + json.dumps(string_value))
        if enumeration_value is not None:
            patch_parts.append("enumerationValue: " + json.dumps(enumeration_value))
        patch_str = "{ " + ", ".join(patch_parts) + " }"

        mutation = (
            "mutation UpdateAttribute { "
            "  updateAttribute(input: { "
            "    id: \"" + attribute_id + "\" "
            "    patch: " + patch_str + " "
            "  }) { "
            "    clientMutationId "
            "    attribute { "
            "      id displayName stringValue enumerationName "
            "    } "
            "  } "
            "}"
        )
        resp = self.client.query(mutation, op_type="mutation")
        payload = ((resp or {}).get("data") or {}).get("updateAttribute") or {}
        return payload.get("attribute")


__all__ = ["SMIPMethods"]
