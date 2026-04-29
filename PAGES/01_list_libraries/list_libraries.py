"""Sample browser page — lists every library in the SMIP.

Demonstrates the PAGES/ convention: a folder under PAGES/ containing
HTML + Vue + a tiny Python launcher. The launcher boots the SMIP_API
Flask app on its own port with this page mounted, so same-origin
fetches to /api/tool/<name> work directly with relative URLs (no CORS
dance, no proxy). One process per page — a buggy page can't break
sibling pages or the backend.

Run from project root:
    python PAGES/01_list_libraries/list_libraries.py
    # then visit http://localhost:5101/list_libraries

Pattern to copy when adding the next page (02_..., 03_..., etc.):
    1. mkdir PAGES/<NN>_<page_name>/
    2. Drop <page_name>.html (Vue single-file page) and <page_name>.py
       (this launcher) inside.
    3. Add the project root to sys.path, import `app` from
       SMIP_API.smip_flask_api, decorate it with @app.route(PAGE_PATH,
       endpoint=...), run on a port no other page is using.
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
PAGE_HTML = "list_libraries.html"
PAGE_PATH = "/list_libraries"
PAGE_PORT = 5101


@app.route(PAGE_PATH, endpoint="list_libraries")
def list_libraries_page():
    """Serve the Vue single-file page as a static file (no Jinja)."""
    return send_from_directory(str(PAGE_DIR), PAGE_HTML)


if __name__ == "__main__":
    print(
        f"Sample page running at "
        f"http://localhost:{PAGE_PORT}{PAGE_PATH}"
    )
    app.run(debug=True, port=PAGE_PORT)
