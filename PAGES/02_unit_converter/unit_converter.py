"""Sample browser page — interactive SMIP unit converter.

Demonstrates a richer PAGES/ use case than 01_list_libraries: two
coupled dropdowns (quantity → from-unit / to-unit), a numeric input,
and live conversion using each unit's `conversionOffset` and
`conversionMultiplier` from the SMIP.

The page calls `/api/tool/get_quantities_with_units` once on mount,
caches the full quantity tree, then converts entirely client-side —
no further round-trips needed for picker changes or value edits.

Run from project root:
    python PAGES/02_unit_converter/unit_converter.py
    # then visit http://localhost:5102/unit_converter

This is exactly the kind of page that earns a round-trip back to the
SMIP side as a first-class browser script — see WORKFLOW step 5. The
get_quantities_with_units tool would also need to be mirrored in the
JS SDK Template at that point.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Project root so SMIP_API / SMIP_MCP / SMIP_IO resolve regardless of cwd.
_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT))

from flask import send_from_directory                       # noqa: E402

from SMIP_API.smip_flask_api import app                     # noqa: E402

PAGE_DIR  = Path(__file__).resolve().parent
PAGE_HTML = "unit_converter.html"
PAGE_PATH = "/unit_converter"
PAGE_PORT = 5102


@app.route(PAGE_PATH, endpoint="unit_converter")
def unit_converter_page():
    """Serve the Vue single-file page as a static file (no Jinja)."""
    return send_from_directory(str(PAGE_DIR), PAGE_HTML)


if __name__ == "__main__":
    print(
        f"Sample page running at "
        f"http://localhost:{PAGE_PORT}{PAGE_PATH}"
    )
    app.run(debug=True, port=PAGE_PORT)
