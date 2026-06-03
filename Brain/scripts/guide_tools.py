#!/usr/bin/env python3
"""
guide_tools.py — single entry point for the Dani-travel toolchain.

Dispatches to the underlying scripts that each do one thing well:

  validate       →  validate_itinerary.py    (static HTML checks, no network)
  verify         →  verify_urls.py           (fetches every href/src, content-quality gate:
                                              200-status + non-empty prose. Does NOT verify
                                              the page is about the stop's subject — that
                                              gap is closed by verify-booking below.)
  verify-booking →  verify_booking_links.py  (booking-link log coverage + live h1 match for
                                              TripAdvisor/Wikipedia URLs — catches the "URL
                                              returns 200 but points at the wrong subject"
                                              class of bug that verify-urls cannot detect.
                                              Wired into the ship chain 2026-04-24 after
                                              Dani confirmed the gap — prior to this it
                                              existed as an orphan script with no single-
                                              entry-point callability. Enforcement anchors:
                                              cleanliness_checks.md rules 157/158/159.)
  photo          →  commons_photo.py         (Wikimedia Commons filename → canonical thumb URL)
  brain-check    →  brain_check.py           (Brain integrity: required §§, files, pointers)
  sweep-stray    →  sweep_stray_travel.py    (enforces CLAUDE.md § HARD RULE: scan ~/Downloads,
                                              ~/Desktop, ~/Documents, and the Drive root outside
                                              Travel/ for travel-named files that escaped the
                                              behavioral push-back rule — Drive sync byproducts,
                                              browser downloads, manual copies. Added 2026-04-30
                                              after Dani found 75 stray files outside Travel/.
                                              Runs at every session start per CLAUDE.md
                                              § Session start step 2. Pass --apply to relocate
                                              found strays to Travel/archive/)
  pdf            →  render_pdf.py            (render the dev guide to PDF via headless Chromium
                                              at 500px viewport — inherits the mobile CSS — at
                                              5.5"×11" portrait; output written next to source
                                              as {name}.pdf. This is the canonical phone-reading
                                              artifact — see Rules for Claude.html § 8.
                                              ON-DEMAND ONLY per Dani 2026-04-24 — NOT wired
                                              into the ship chain; callable as a standalone
                                              subcommand only when Dani asks for a PDF)
  validate-pdf   →  validate_pdf.py          (post-render gate — re-renders the dev guide in
                                              headless Chromium at the same 500px/@media-screen
                                              setup `render_pdf.py` uses, then verifies every
                                              .stop-photos img renders in the 370-400px band
                                              and every .stop-block/.stop-photos has computed
                                              break-inside: avoid. Catches the flex-basis-kills-
                                              height class of bug that static HTML checks miss.
                                              ON-DEMAND ONLY — runs only after `pdf` is invoked
                                              on demand; not part of the automatic ship chain)
  ship           →  validate + verify + verify-booking
                                              (pre-ship pipeline: static HTML checks, then live
                                              URL/content checks, then booking-link log coverage
                                              + subject-drift catch. Fails fast on the first
                                              non-zero script. Retired 2026-04-24 — the former
                                              `validate + verify + pdf + validate-pdf` chain
                                              was cut to `validate + verify` per Dani's direction
                                              that PDF rendering should be on-demand only.
                                              Extended 2026-04-24 — `verify-booking` added to
                                              close the subject-drift gap; prior chain let
                                              guides ship with URLs that returned 200 but
                                              pointed at the wrong subject — see `ship` function
                                              body for both retirement/extension markers)
  start          →  session startup         (runs brain-check + sweep-stray, then prints
                                              open To Do items. One command replaces the
                                              manual 7-step session ritual. Added 2026-05-09.)
  audit          →  open the deep-review     (prints the four audit questions and the file
                                              inventory, stamps a new dated entry into
                                              Brain/mds/audit_log.md; Claude does the actual
                                              review in conversation per §Brain Audit)

Rationale: one entry point, but the underlying
modules stay separate so each can be reasoned about, tested, and debugged
independently. This file is a router.

Usage:
  python3 guide_tools.py validate       <file.html>
  python3 guide_tools.py verify         <file.html>
  python3 guide_tools.py verify-booking <file.html>    # log coverage + h1 match
  python3 guide_tools.py photo          "File:{Commons_File_Name}.jpg"
  python3 guide_tools.py brain-check    [--verbose]
  python3 guide_tools.py sweep-stray    [--apply] [--scan PATH] [--quiet]
  python3 guide_tools.py pdf            <file.html>    # render {name}.pdf for phone
  python3 guide_tools.py validate-pdf   <file.html>    # post-render gate (no output file)
  python3 guide_tools.py ship           <file.html>    # full pre-ship pipeline
  python3 guide_tools.py start                          # session startup: brain-check + sweep-stray + to-do summary
  python3 guide_tools.py init            <City>         # create build-state tracker for a new guide build
  python3 guide_tools.py audit                         # open audit workflow

Exit code matches the underlying script; `ship` fails fast on the first
non-zero script from the gate chain (validate/verify/verify-booking). PDF
production is on-demand only per Dani 2026-04-24 — `pdf` and `validate-pdf`
are no longer part of the automatic `ship` chain; they run only as standalone
subcommands when Dani asks for a PDF.
"""

import datetime as _dt
import json
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent       # Brain/scripts/  (was Brain/ pre-2026-04-30)
BRAIN_DIR = HERE.parent                       # Brain/
TRAVEL_ROOT = BRAIN_DIR.parent                # Travel/
MDS_DIR = BRAIN_DIR / "mds"                   # Brain/mds/
AUDIT_LOG = MDS_DIR / "audit_log.md"          # 2026-05-03: corrected from Brain/mds/audit_log.md — path mismatched the on-disk file (which lives at Brain/mds/audit_log.md per brain_check.py REQUIRED_FILES). `guide_tools.py audit` was writing to the wrong location.

SUBCOMMANDS = {
    "validate":       "validate_itinerary.py",
    "verify":         "verify_urls.py",
    "verify-booking": "verify_booking_links.py",
    "photo":          "commons_photo.py",
    "brain-check":    "brain_check.py",
    "sweep-stray":    "sweep_stray_travel.py",   # added 2026-04-30: enforces HARD RULE (all travel work under Travel/)
    "pdf":            "render_pdf.py",
    "validate-pdf":   "validate_pdf.py",
    # bundle_guide.py — retired 2026-04-22; share HTML dropped in favour of PDF
    # as the sole shippable artifact. Archived at Travel/archive/bundle_guide_retired_2026-04-22.py.
}

USAGE = __doc__.strip()

AUDIT_QUESTIONS = """\
The four audit questions — baked in, never needs re-prompting (per §Brain Audit):

  1. Conduct a thorough review of all the documents under the Travel folder
     to identify what is wrong and what needs fixing.
  2. Are there any other rules or pointers that you need to fix or build?
     Anything else you can think of to improve this system?
  3. What is wrong, outdated, or broken? (file paths that no longer match,
     pointers to retired sources, validators that silently skip, rules that
     contradict each other, rules whose reason is a resolved one-off incident)
  4. Can any document be polished further without losing important content?
     (polish = clearer phrasing, tightening within a paragraph — NOT removing
     or consolidating rules; removals require explicit permission per
     §Permissioning)
"""


def _patch_verification_log(guide_path: Path) -> None:
    """
    Auto-sync _meta.guide and _meta.updated in verification_log.json before the
    ship gate runs. This prevents the log from going stale on version bumps
    (e.g. pasadena_v1 → pasadena_v2) without any manual step.

    Log lives at _build/verification_log.json (moved 2026-05-09; root is back-compat fallback).
    Silent no-op if the log doesn't exist yet (guides with no bot-blocked booking
    URLs don't need one).
    """
    # verification_log.json lives inside _build/ (moved 2026-05-09 when assets/ moved there too).
    # Fallback to guide root for any pre-migration guide that still has it there.
    log_path = guide_path.parent / "_build" / "verification_log.json"
    if not log_path.exists():
        log_path = guide_path.parent / "verification_log.json"
    if not log_path.exists():
        return
    try:
        data = json.loads(log_path.read_text(encoding="utf-8"))
        meta = data.setdefault("_meta", {})
        old_guide = meta.get("guide", "")
        new_guide = guide_path.name
        today = _dt.date.today().isoformat()
        if old_guide != new_guide or meta.get("updated") != today:
            meta["guide"] = new_guide
            meta["updated"] = today
            log_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            if old_guide and old_guide != new_guide:
                print(f"  ℹ️  verification_log.json: _meta.guide patched "
                      f"{old_guide!r} → {new_guide!r}")
    except Exception as e:
        print(f"⚠️  Could not patch verification_log.json _meta: {e}", file=sys.stderr)


def _run(script: str, argv_tail: list[str]) -> int:
    """Run a sibling script with argv[0]=script and argv[1:]=tail."""
    target = HERE / script
    if not target.exists():
        print(f"❌ Missing companion script: {target}", file=sys.stderr)
        return 2
    # Wire argv so the target script sees itself as invoked directly.
    saved = sys.argv
    sys.argv = [str(target), *argv_tail]
    try:
        runpy.run_path(str(target), run_name="__main__")
        return 0
    except SystemExit as e:  # scripts use sys.exit() for non-zero codes
        code = e.code
        return int(code) if isinstance(code, int) else (0 if code is None else 1)
    finally:
        sys.argv = saved


def _audit_file_inventory() -> list[str]:
    """List every file under Travel/ grouped by folder — the audit's review surface."""
    lines: list[str] = []
    # Walk all immediate subdirectories (skip __pycache__ and hidden dirs).
    subdirs = sorted(
        p for p in TRAVEL_ROOT.iterdir()
        if p.is_dir() and not p.name.startswith(".")
        and "__pycache__" not in p.parts
    )
    for sub in subdirs:
        lines.append(f"\n### {sub.name}/")
        for p in sorted(sub.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts and not p.name.startswith("."):
                rel = p.relative_to(TRAVEL_ROOT)
                lines.append(f"  - {rel}")
    # Root-level files (CLAUDE.md, .html rule files, etc.).
    lines.append("\n### Travel/ (root)")
    for p in sorted(TRAVEL_ROOT.iterdir()):
        if p.is_file() and not p.name.startswith("."):
            lines.append(f"  - {p.name}")
    return lines


def _open_audit() -> int:
    """Open the audit workflow: print questions + inventory, stamp audit_log.md."""
    today = _dt.date.today().isoformat()
    print("━━━ audit ━━━")
    print(AUDIT_QUESTIONS)
    print("\nReview surface — every file under Travel/:")
    for line in _audit_file_inventory():
        print(line)
    print(f"\nToday: {today}")
    print(f"Audit log: {AUDIT_LOG.relative_to(TRAVEL_ROOT)}")

    # Stamp a placeholder entry so Claude can fill in findings during conversation.
    # Don't overwrite an existing entry for today; append a fresh sub-heading instead.
    stamp = f"\n## {today}\n**Trigger.** keyword\n_(audit in progress — Claude fills in findings, fixes-in-session, and parked items per §Brain Audit)_\n"
    try:
        existing = AUDIT_LOG.read_text(encoding="utf-8") if AUDIT_LOG.exists() else ""
        if f"## {today}" not in existing:
            # Prepend after the preamble: find the first "---" divider and insert below.
            if "---\n" in existing:
                head, _, rest = existing.partition("---\n")
                AUDIT_LOG.write_text(f"{head}---\n{stamp}\n{rest}", encoding="utf-8")
            else:
                AUDIT_LOG.write_text(existing + stamp, encoding="utf-8")
            print(f"\nStamped new entry: ## {today}")
        else:
            print(f"\nEntry ## {today} already present — Claude will append findings under it.")
    except OSError as e:
        print(f"\n⚠ could not stamp audit log: {e}", file=sys.stderr)
        return 2
    return 0



def _run_start() -> int:
    """
    Session startup in one command — replaces the manual multi-step ritual.

    Steps:
      1. brain-check  (must exit 0 before anything else)
      2. sweep-stray  (surface strays; does NOT auto-apply — still needs --apply to move)
      3. Print open To Do items (🔧 Rules for Update + ❓ Questions for Dani sections)
    """
    import subprocess

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  🧠  Session startup — guide_tools.py start")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    # Step 1: brain-check
    print("▶ Step 1/3 — brain-check")
    rc1 = _run(SUBCOMMANDS["brain-check"], [])
    if rc1 != 0:
        print("\n🚫  brain-check failed — fix before any task work.\n", file=sys.stderr)
        return rc1

    # Step 2: sweep-stray (dry run — no --apply)
    print("\n▶ Step 2/3 — sweep-stray (dry run)")
    rc2 = _run(SUBCOMMANDS["sweep-stray"], [])
    # sweep-stray exit 1 means strays found — surface them but don't block session
    if rc2 not in (0, 1):
        print("\n⚠  sweep-stray returned unexpected exit code — check output above.", file=sys.stderr)

    # Step 3: open To Do items
    print("\n▶ Step 3/3 — open To Do items")
    todo_path = TRAVEL_ROOT / "To Do List" / "To_Do_List.md"
    if not todo_path.exists():
        print("  ⚠  To_Do_List.md not found — skipping.")
    else:
        text = todo_path.read_text(encoding="utf-8")
        sections = {
            "🔧 Rules for Update": [],
            "❓ Open Questions": [],
            "✈️ My Tasks": [],
        }
        current = None
        SKIP = {
            "*(empty — all rules applied)*",
            "*(empty — no open questions)*",
            "*(empty)*",
        }
        for line in text.splitlines():
            for heading in sections:
                if heading in line and line.startswith("#"):
                    current = heading
                    break
            else:
                stripped = line.strip()
                if (current and stripped
                        and not line.startswith("#")
                        and not line.startswith(">")
                        and not (stripped.startswith("*") and stripped.endswith("*"))  # skip italic instructions
                        and stripped not in SKIP
                        and not stripped.startswith("---")):
                    sections[current].append(line)

        for heading, lines in sections.items():
            real = [l for l in lines if l.strip() and l.strip() not in SKIP]
            if real:
                print(f"\n  {heading}:")
                for l in real[:8]:  # cap at 8 lines per section
                    print(f"    {l}")
            else:
                print(f"\n  {heading}: (empty)")

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  ✅  Session startup complete.")
    print()
    print("  📖  Session reads (complete ritual steps 3–6):")
    print("       Read  Brain/CORE RULES/Rules for Claude.html")
    print("       Check Brain/Reference/Platforms.md     (note any ❌ or ⏳)")
    print("       Read  Brain/Reference/Connectors.html")
    print("       Check Brain/mds/audit_log.md           (note if last entry > 7 days ago)")
    print()
    print("  🏗   Before ANY guide build — Phase 1 reads (in this order, before researching):")
    print("       1. Brain/CORE RULES/Links.html")
    print("       2. Brain/CORE RULES/Photos Rules.html")
    print("       3. Brain/Reference/Connectors.html   ← connectors + research workflow")
    print("       4. Brain/Reference/Platforms.md      ← which platforms need site: search")
    print()
    print("       Then run: python3 Brain/scripts/guide_tools.py init {City}")
    print("       This creates the build-state tracker. Do it before researching anything.")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    return 0


def _run_init(city: str) -> int:
    """
    Create a pre-filled build-state tracker for a new guide build.

    Creates Guides/{City}/_build/build_state.md with all Phase 0–6 checkboxes
    unchecked. Claude checks them off as it reads each file and completes each
    phase. The validator reads this file at ship time and fails if any required
    entry is unchecked.

    Added 2026-06-01: removes the friction of manually writing the tracker,
    which caused Claude to skip creating it and bypass the phase-read enforcement.
    """
    today = _dt.date.today().isoformat()
    build_dir = TRAVEL_ROOT / "Guides" / city / "_build"
    build_dir.mkdir(parents=True, exist_ok=True)
    tracker_path = build_dir / "build_state.md"

    if tracker_path.exists():
        print(f"⚠  build_state.md already exists at {tracker_path}")
        print("   Delete or rename it before running init for a fresh build.")
        return 1

    content = f"""# Build state — {city}
Started: {today}
Last updated: {today}

## Phase 0 — Session start
- [ ] Rules for Claude.html

## Phase 1 — Technical prerequisites
- [ ] Links.html
- [ ] Photos Rules.html
- [ ] Connectors.html
- [ ] Platforms.md

## Phase 2 — Guide structure
- [ ] Guide Structure.html
- [ ] Stops Structure.html
- [ ] Hotel Banner.html
- [ ] Trip at a Glance.html
- [ ] Toolbar.html
- [ ] Navigation.html

## Phase 3 — Day shape
- [ ] Day Structure.html

## Phase 4 — Per-stop build
- [ ] Tickets.html
- [ ] Motion Rule.html
- [ ] Icon Order and Format.html

## Phase 5 — Per-section build
- [ ] Weekly Closures - Extra Section.html
- [ ] Tours - Extra Section.html
- [ ] Cappuccino - Extra Section.html
- [ ] Restaurants Near Hotel - Extra Section.html
- [ ] Downtown Restaurants - Extra Section.html
- [ ] Local Tastes - Extra Section.html
- [ ] Food Delivery - Extra Section.html
- [ ] Shows, Performances & Concerts - Extra Section.html
- [ ] Getting Around - Extra Section.html
- [ ] Train Stations Near Hotel - Extra Section.html
- [ ] Day Trips by Train - Extra Section.html
- [ ] Michelin Restaurants - Extra Section.html
- [ ] Heads Up - Extra Section.html
- [ ] Claude Inspiration - Extra Section.html

## Phase 6 — Ship gate
- [ ] Brain/Reference/Ship Checklist.html
- [ ] validate_itinerary.py passes
- [ ] every extra populated or carries negative-finding line
"""
    tracker_path.write_text(content, encoding="utf-8")
    print(f"✅  Build-state tracker created: {tracker_path}")
    print()
    print("   Next steps:")
    print("   1. Read Phase 1 files and check them off as [x]")
    print("   2. Read Phase 2 files and check them off as [x]")
    print("   3. Look up the hotel in Travel/Trip Essentials/Trips.html")
    print("   4. Start researching stops — check Brain/mds/Cities Skip List.md first")
    return 0


def _check_guide_indexed(guide_path: Path) -> int:
    """
    Ship gate: verify this specific guide's city folder is in guides_index.html.

    Each crib checks only its own guide — not all guides. Fires at ship time only.
    The city folder is the parent directory of the guide HTML file
    (e.g. Guides/Edinburgh/ for Guides/Edinburgh/edinburgh_v1.html).

    Added 2026-06-02: replaced check_guides_index_coverage in brain_check.py,
    which ran at session start and incorrectly flagged other cribs' in-progress
    builds. This check is scoped to one guide, runs only at ship time, and each
    crib only validates its own guide's entry.
    """
    guides_dir = TRAVEL_ROOT / "Guides"
    index_file = guides_dir / "guides_index.html"

    if not index_file.exists():
        print(
            "\n🚫  SHIP BLOCKED — Guides/guides_index.html missing.\n"
            "    The master index does not exist.\n",
            file=sys.stderr,
        )
        return 1

    city_folder = guide_path.parent.name  # e.g. "Edinburgh"
    index_html = index_file.read_text(encoding="utf-8")

    if f"./{city_folder}/" not in index_html and f'href="./{city_folder}/' not in index_html:
        print(
            f"\n🚫  SHIP BLOCKED — guides_index.html has no entry for Guides/{city_folder}/.\n"
            f"    Complete the 4-step index update before shipping:\n"
            f"    Brain/Reference/Navigation.html § 5\n",
            file=sys.stderr,
        )
        return 1

    print(f"  ✅  guides_index.html — {city_folder} entry found.")
    return 0


def _check_guide_pinned(guide_path: Path) -> int:
    """
    Ship gate: verify this guide's city has a pin in at least one map file.

    All six continent maps are checked:
      Europe Map, US Map, Asia Map, Africa Map, Oceania Map, South America Map.
    The city name just needs to be present in one of them.

    Added 2026-06-02: enforces Navigation.html § 5 step 5 (map pin rule).
    Updated 2026-06-02: expanded from 2 maps to all 6 continent maps.
    """
    city_folder = guide_path.parent.name  # e.g. "Amsterdam"
    essentials = TRAVEL_ROOT / "Trip Essentials"
    maps_dir  = essentials / "Maps"
    map_files = [
        maps_dir  / "Europe Map.html",
        maps_dir  / "US Map.html",
        maps_dir  / "Asia Map.html",
        maps_dir  / "Africa Map.html",
        maps_dir  / "Oceania Map.html",
        maps_dir  / "South America Map.html",
        essentials / "Europe Map.html",
        essentials / "US Map.html",
    ]

    found_in = None
    for map_file in map_files:
        if not map_file.exists():
            continue
        content = map_file.read_text(encoding="utf-8")
        # PINS entries look like: ['CityName', lon, lat, ...] or ["CityName", ...]
        if f"['{city_folder}'" in content or f'["{city_folder}"' in content:
            found_in = map_file.name
            break

    if found_in:
        print(f"  ✅  Map pin — {city_folder} found in {found_in}.")
        return 0

    print(
        f"\n🚫  SHIP BLOCKED — no map pin found for {city_folder}.\n"
        f"    Add a pin to the appropriate continent map before shipping:\n"
        f"    • European guides   → Trip Essentials/Europe Map.html\n"
        f"    • US/Canada guides  → Trip Essentials/US Map.html\n"
        f"    • Asian guides      → Trip Essentials/Asia Map.html\n"
        f"    • African guides    → Trip Essentials/Africa Map.html\n"
        f"    • Oceania guides    → Trip Essentials/Oceania Map.html\n"
        f"    • S. America guides → Trip Essentials/South America Map.html\n"
        f"    Entry format in the PINS array:\n"
        f"    ['{city_folder}', lon, lat, '../Guides/{city_folder}/file.html']\n"
        f"    Full rule: Brain/Reference/Navigation.html § 5 step 5\n",
        file=sys.stderr,
    )
    return 1


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help", "help"}:
        print(USAGE)
        return 0

    cmd, tail = sys.argv[1], sys.argv[2:]

    if cmd == "ship":
        if not tail:
            print("Usage: guide_tools.py ship <file.html>", file=sys.stderr)
            return 2
        # Three-gate pipeline: static HTML checks → live URL/content verification →
        # booking-link log coverage + subject-drift catch. Fail-fast: any non-zero
        # returns immediately.
        #
        # Retired 2026-04-24 — the `pdf` + `validate-pdf` steps previously ran
        # after `verify` so a PDF landed on disk every `ship`. Dani's direction:
        # *"the Doc should be done on demand only. only when I ask and not
        # automatic."* PDF rendering is now on-demand only — `render_pdf.py` and
        # `validate_pdf.py` remain callable as standalone subcommands (see
        # SUBCOMMANDS dict) but are no longer part of the automatic chain.
        # Enforced by `Cleanliness Checks.md` Rule 172.
        #
        # Extended 2026-04-24 — `verify-booking` added as the third gate, closing
        # the enforcement gap Dani surfaced during a 2026-04-24 audit (logged at
        # the time in OPEN_ITEMS.md, retired 2026-05-01 and merged into
        # Travel/To Do List/To_Do_List.md). Prior chain ran `validate + verify` only, which let guides ship
        # with booking URLs that returned 200-status (and so passed verify_urls)
        # but resolved to the wrong subject (TripAdvisor d-ID reassignment,
        # Wikipedia slug drift) OR lacked a human verification-log entry on
        # bot-blocked platforms (Viator / GetYourGuide / Michelin). Dani 2026-04-24
        # confirmed hard-fail semantics: *"i agree hard fail"* — any FAIL from
        # verify_booking_links.py blocks the ship the same as validate/verify FAIL.
        # Enforced by `Cleanliness Checks.md` Rule 173 (ship chain shape) +
        # Rules 157/158/159 (the individual log-coverage + h1-match gates).
        # See Rules for Claude.html § 8 for the full context.
        # Auto-patch verification_log.json _meta before the gates run so
        # _meta.guide always matches the guide being shipped and _meta.updated
        # is always today. No manual step needed on version bumps.
        # ── Validation stamp gate (added 2026-05-07) ──────────────────────────
        # validate_itinerary.py writes <!-- validation: passed YYYY-MM-DD HH:MM -->
        # into the guide when it exits clean. If that stamp is absent or still
        # "pending", this guide has never passed validation — hard-fail before
        # running the rest of the pipeline.
        _guide_path = Path(tail[0]).resolve()
        try:
            _guide_html = _guide_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            print(f"❌ File not found: {tail[0]}", file=sys.stderr)
            return 2
        if "<!-- validation: pending -->" in _guide_html:
            print(
                "\n🚫  SHIP BLOCKED — guide has never been validated.\n"
                "    Run:  python3 guide_tools.py validate <file.html>\n"
                "    Then: python3 guide_tools.py ship <file.html>\n",
                file=sys.stderr,
            )
            return 1
        if "<!-- validation: passed" not in _guide_html:
            print(
                "\n🚫  SHIP BLOCKED — no validation stamp found in this guide.\n"
                "    Add <!-- validation: pending --> near the top of the HTML,\n"
                "    run validate, then ship.\n",
                file=sys.stderr,
            )
            return 1
        # ──────────────────────────────────────────────────────────────────────

        _patch_verification_log(Path(tail[0]).resolve())

        # ── brain-check gate (added 2026-05-30) ──────────────────────────────
        # Verifies Brain integrity (required files, checksums, pointers) before
        # running the full validate/verify pipeline. Note: guides_index coverage
        # is NOT checked here — that check was moved to _check_guide_indexed()
        # below (runs after verify-booking) so each crib only checks its own
        # guide at ship time. Updated 2026-06-02.
        rc_brain = _run(SUBCOMMANDS["brain-check"], [])
        if rc_brain != 0:
            print(
                "\n🚫  SHIP BLOCKED — brain-check failed.\n"
                "    Fix brain integrity issues (e.g. missing guides_index.html entry),\n"
                "    then re-run ship.\n",
                file=sys.stderr,
            )
            return rc_brain
        # ──────────────────────────────────────────────────────────────────────

        for sub in ("validate", "verify", "verify-booking"):
            rc = _run(SUBCOMMANDS[sub], tail)
            if rc != 0:
                return rc

        # ── guides_index.html gate (added 2026-06-02) ─────────────────────────
        # Each crib checks only its own guide. Verifies that guides_index.html
        # has an entry for the city folder containing the guide being shipped.
        # Fires at ship time — never at session start. Replaced the old
        # check_guides_index_coverage in brain_check.py which ran at session
        # start and incorrectly flagged other cribs' in-progress builds.
        rc_idx = _check_guide_indexed(Path(tail[0]).resolve())
        if rc_idx != 0:
            return rc_idx
        # ──────────────────────────────────────────────────────────────────────

        # ── map pin gate (added 2026-06-02) ───────────────────────────────────
        # Verifies the city has a pin in Europe Map.html or US Map.html.
        # Full rule: Brain/Reference/Navigation.html § 5 step 5.
        rc_pin = _check_guide_pinned(Path(tail[0]).resolve())
        if rc_pin != 0:
            return rc_pin
        # ──────────────────────────────────────────────────────────────────────

        return 0

    if cmd == "start":
        return _run_start()

    if cmd == "init":
        if not tail:
            print("Usage: guide_tools.py init <City>", file=sys.stderr)
            return 2
        return _run_init(" ".join(tail))

    if cmd == "audit":
        return _open_audit()

    if cmd in SUBCOMMANDS:
        return _run(SUBCOMMANDS[cmd], tail)

    print(f"❌ Unknown subcommand: {cmd!r}\n\n{USAGE}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
