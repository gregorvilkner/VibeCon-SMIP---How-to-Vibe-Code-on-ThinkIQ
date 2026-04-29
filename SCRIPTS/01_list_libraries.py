"""Sample worker script — print every library in the SMIP.

Demonstrates the SCRIPTS/ convention: one runnable .py per task, headless
(no Vue, no Flask, no port), imports SMIPClient/SMIPMethods, runs, and
exits with 0 on success / non-zero on failure so it can be wired into
pipelines.

Run from project root:
    python SCRIPTS/01_list_libraries.py

Pattern to copy when adding the next script (02_..., 03_..., etc.):
    1. Drop a single .py at SCRIPTS/<NN>_<task>.py
    2. Add the project root to sys.path so SMIP_IO resolves from any cwd.
    3. Build a SMIPMethods around a SMIPClient.
    4. Do the work in main(); return an exit code.
    5. Keep it idempotent where you can — these scripts get re-run.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Project root so `from SMIP_IO...` works regardless of where the script
# is launched from.
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from SMIP_IO.smip_client import SMIPClient        # noqa: E402
from SMIP_IO.smip_methods import SMIPMethods      # noqa: E402


def main() -> int:
    methods = SMIPMethods(SMIPClient())
    libraries = methods.get_libraries()

    if not libraries:
        print("No libraries returned.")
        return 0

    print(f"{len(libraries)} library/-ies:")
    for lib in libraries:
        lib_id   = lib.get("id", "?")
        lib_name = lib.get("displayName", "")
        print(f"  {lib_id:>10}  {lib_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
