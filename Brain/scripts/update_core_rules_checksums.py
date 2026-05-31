#!/usr/bin/env python3
"""
update_core_rules_checksums.py
──────────────────────────────
Run this ONLY after a CORE RULES file has been edited with explicit
permission from Dani. Updates core_rules_checksums.json to match the
current state of every HTML file in Brain/CORE RULES/.

Usage (from Brain/scripts/):
    python3 update_core_rules_checksums.py

The validator (validate_itinerary.py) will fail if any CORE RULES file
has been modified without the checksums being updated — that's the point.
This script is the authorised way to accept a change.
"""

import hashlib
import json
import sys
from pathlib import Path

SCRIPTS_DIR   = Path(__file__).parent
CORE_RULES    = SCRIPTS_DIR.parent / "CORE RULES"
CHECKSUMS_OUT = SCRIPTS_DIR / "core_rules_checksums.json"

def main():
    if not CORE_RULES.is_dir():
        print(f"ERROR: CORE RULES directory not found at: {CORE_RULES}", file=sys.stderr)
        sys.exit(1)

    files = sorted(CORE_RULES.rglob("*.html"))
    if not files:
        print("ERROR: No HTML files found in CORE RULES.", file=sys.stderr)
        sys.exit(1)

    # Load existing checksums to report what changed.
    old = {}
    if CHECKSUMS_OUT.is_file():
        try:
            old = json.loads(CHECKSUMS_OUT.read_text(encoding="utf-8"))
        except Exception:
            pass

    new = {}
    changed = []
    added   = []
    for f in files:
        rel  = str(f.relative_to(CORE_RULES))
        sha  = hashlib.sha256(f.read_bytes()).hexdigest()
        new[rel] = sha
        if rel not in old:
            added.append(rel)
        elif old[rel] != sha:
            changed.append(rel)

    removed = [r for r in old if r not in new]

    CHECKSUMS_OUT.write_text(json.dumps(new, indent=2, sort_keys=True))

    print(f"core_rules_checksums.json updated — {len(new)} file(s) hashed.")
    if changed:
        print(f"  CHANGED  ({len(changed)}): " + ", ".join(changed))
    if added:
        print(f"  ADDED    ({len(added)}):   " + ", ".join(added))
    if removed:
        print(f"  REMOVED  ({len(removed)}): " + ", ".join(removed))
    if not (changed or added or removed):
        print("  No changes detected — checksums already matched.")

if __name__ == "__main__":
    main()
