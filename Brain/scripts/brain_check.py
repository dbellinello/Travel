#!/usr/bin/env python3
"""
brain_check.py — integrity check for the Travel Brain.

Runs at the start of every session (per Rules for Claude.html § 1 Session start) and
before every guide ship (chained into `guide_tools.py ship`). Its only job is
to catch silent drift: rules deleted without permission, files moved out from
under pointers, section-count regressions, ghost references.

It does NOT validate a guide's HTML — that's `validate_itinerary.py`. It does
NOT fetch URLs — that's `verify_urls.py`. This script only looks at the Brain
itself.

Exit codes:
  0  — Brain intact. OK to proceed.
  1  — FAIL. A required section, file, or pointer is missing. Restore it
       additively (from Travel/archive/) before any Brain-dependent work.
  2  — Usage error or unexpected exception.

Warnings (printed but exit 0 still allowed):
  - audit_log.md last entry is >7 days old → recommend running `guide_tools.py audit`.

Usage:
  python3 brain_check.py
  python3 brain_check.py --verbose    # print every check, not just failures
"""

from __future__ import annotations

import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# ─── Validator scope ──────────────────────────────────────────────────────────
# brain_check.py validates ONLY files inside Brain/ (plus the explicit Travel-root
# entry-point files: CLAUDE.md and the To Do List). It does NOT touch:
#   - Brain/CORE RULES/                          — scanned for name mentions only (see check_html_name_mentions)
#   - Travel/Trip Essentials/ — packing list etc.
#   - Travel/Guides/             — past output, never a reference
#   - Travel/On The Go/          — mobile crib territory (Rules/ only as of 2026-05-18)
#   - Travel/shopping_profile_v2.md — shopping profile (moved from On The Go/ on 2026-05-18)
# Per original scope: "the whole validator is to ship the guide... not for personal organization."
# If a future audit pass tempts adding any of those to REQUIRED_FILES — that's drift.
HERE = Path(__file__).resolve().parent          # Brain/scripts/
HTML_RULES_DIR = HERE.parent / "CORE RULES"  # Brain/CORE RULES/ (renamed from HTML Rules Before Conversion/ 2026-05-09)
BRAIN_DIR = HERE.parent                          # Brain/
MDS_DIR = BRAIN_DIR / "mds"                      # Brain/mds/  (renamed from MDs 2026-05-02)
CORE_RULES_DIR = BRAIN_DIR / "CORE RULES"        # Brain/CORE RULES/  (renamed from "core rules" 2026-05-02)
TRAVEL_ROOT = BRAIN_DIR.parent                   # Travel/
MYDRIVE_ROOT = TRAVEL_ROOT.parent                # My Drive/
ON_THE_GO_DIR = TRAVEL_ROOT / "On The Go"  # Travel/On The Go/ — NOT validated; mobile crib territory, validator only audits guide-building infrastructure.
TODO_DIR = TRAVEL_ROOT / "To Do List"            # Travel/To Do List/  (moved from Brain/ 2026-05-01)
CLAUDE_MD = TRAVEL_ROOT / "CLAUDE.md"
# PROFILE: the session entry-point file checked for required sections + ghost refs.
# Was brain_core.md (archived 2026-05-07 — content folded into CLAUDE.md).
# Now points to CLAUDE.md which carries the doc index, glossary, train operators,
# validators table, and all behavioral rules. Ghost-reference scan runs against it.
PROFILE = CLAUDE_MD

# Each entry is a regex matched against `^## ` lines of PROFILE (CLAUDE.md).
# brain_core.md sections retired 2026-05-07 — content moved to CLAUDE.md.
REQUIRED_SECTIONS = [
    r"^## Behavioral rules",
    r"^## ⚠️ DriftyCat",
    r"^## On-demand documents",
    r"^## Shopping",
    r"^## Two-crib architecture",
    r"^## Quick Reference",
]

# ─── Required files under Brain/ (plus CLAUDE.md at Travel root) ─────────────
# html_templates.md retired 2026-04-23 per Rule 25.
REQUIRED_FILES = [
    BRAIN_DIR / "Reference" / "Guide Style.css",
    HERE / "validate_itinerary.py",
    HERE / "verify_urls.py",
    HERE / "verify_booking_links.py",   # ship-gate: log coverage + h1-match (added 2026-04-24)
    HERE / "commons_photo.py",
    HERE / "guide_tools.py",
    HERE / "brain_check.py",
    HERE / "render_pdf.py",
    # bundle_guide.py retired 2026-04-22 — share HTML dropped; PDF is sole artifact
    HERE / "validate_pdf.py",
    BRAIN_DIR / "Reference" / "Platforms.md",
    HERE / "sweep_stray_travel.py",  # enforces HARD RULE (added 2026-04-30): all travel work under Travel/
    HERE / "autofix_itinerary.py",   # mechanically rewrites mis-filed booking boxes (added 2026-04-29)
    # calibration_anchors_catalog.md — retired 2026-05-09 (Dani request)
    # On-the-go rules deliberately NOT in REQUIRED_FILES — they live at On The Go/
    # (My Drive root, outside Travel/) per the "Brain is for guide-building only"
    # HARD RULE in Travel/CLAUDE.md (2026-05-02). The Brain mirror was retired
    # in the 2026-05-02 brain audit.
    TRAVEL_ROOT / "CLAUDE.md",
    # Operational scaffolding files supporting the core rules. Source of truth
    # for guide rules lives ONLY in Brain/CORE RULES/*.html per CLAUDE.md HARD
    # RULE. HTML Snippets.md retired 2026-05-02 (folded into
    # Brain/Reference/, lives outside Brain — those files are
    # not in REQUIRED_FILES because Brain validators only audit guide-building
    # infrastructure inside Brain/, per Rules for Claude.html § 3).
    BRAIN_DIR / "Reference" / "Separation Map.md",               # locator: which core rules Doc owns which rule
    BRAIN_DIR / "Reference" / "Cleanliness Checks.md",           # cross-cutting cleanliness rules used by validators
    MDS_DIR / "audit_log.md",                    # rolling audit log (staleness gate below uses this)
    TODO_DIR / "To_Do_List.md",                  # one parking surface: ✈️ My Tasks · 🔧 Rules for Update · ❓ Questions for Dani
    MDS_DIR / "Heads Up.md",                   # T6 ship-gate input — validate_itinerary.py reads this to gate heads-up section (added 2026-05-03)
    MDS_DIR / "Cities Skip List.md",                 # build-prep input — used at city research phase to skip already-known bad venues (added 2026-05-03)
    BRAIN_DIR / "Reference" / "PDF Render Notes.md",      # WeasyPrint PDF render guide — CSS overrides, install, gotchas (restored 2026-05-07; critical operational ref)
    MDS_DIR / "travel_map.md",                       # Folder/resource briefing — loaded at session start (step 4 of ritual); tells Claude what exists and where (added 2026-05-07)
    MDS_DIR / "decisions.md",                      # judgment call log — required by cleanliness_checks.md rule 128 (added 2026-05-11)
    BRAIN_DIR / "Reference" / "Rule Dependencies.html",   # crib navigation aid — moved out of CORE RULES 2026-05-14 → Brain/ → Reference/ 2026-05-24; indexes every cross-file rule dependency (path updated 2026-05-27)
    BRAIN_DIR / "Reference" / "Validator Index.html",     # living index of every validate_itinerary.py + brain_check.py check; updated every session per Rules for Claude.html § 10 item 5 (added to REQUIRED_FILES 2026-05-24)
    BRAIN_DIR / "Reference" / "Guide Entry Counts.html",        # canonical min/max/exact count reference; moved out of CORE RULES → Brain/ → Reference/ 2026-05-24 (added to REQUIRED_FILES 2026-05-24)
    BRAIN_DIR / "Reference" / "Ship Checklist.html",     # pre-ship gate checklist; moved out of CORE RULES 2026-05-24 (not a rule, a working checklist maintained by Claude)
]

# ─── Audit-log staleness threshold ───────────────────────────────────────────
AUDIT_STALE_DAYS = 7
AUDIT_LOG = MDS_DIR / "audit_log.md"

# ─── Ghost references — filenames mentioned in profile that must exist ───────
# We parse the profile for `Brain/...` and relative paths to .py/.css/.md files
# and check each one resolves. A reference to an archived file is OK only if it
# explicitly lives under `Travel/archive/`.
# (Memory files under /mnt/.auto-memory/ are NOT required — the profile can
# mention them as context without the file existing.)
REFERENCE_PATTERNS = [
    re.compile(r"`(Brain/[A-Za-z0-9_./-]+\.(?:py|css|md))`"),
    re.compile(r"`(Travel/[A-Za-z0-9_./-]+\.(?:md|gdoc))`"),
]

# ─── Rule 26 — RETIRED 2026-05-02 ────────────────────────────────────────────
# Per Dani 2026-05-02: "we allow examples, none of that needs to be checked
# for anymore." Examples are now welcome and load-bearing per Rules for Claude
# § 3. The "no real place names in the Brain" rule is fully retired.
#
# Removed in this commit: RULE26_DENYLIST, RULE26_DENYLIST_RE,
# RULE26_TIER_ANCHOR_TOKENS, RULE26_SKIP_FILES, RULE26_PROFILE_ALLOW_RANGES,
# and the check_rule26_place_names() function.
#
# brain_check.py is now purely about file integrity — required sections,
# required files, ghost references, audit log staleness. No content scanning.


# ──────────────────────────────────────────────────────────────────────────────
# Checks
# ──────────────────────────────────────────────────────────────────────────────
class Report:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.warnings: list[str] = []
        self.passes: list[str] = []

    def fail(self, msg: str) -> None:
        self.failures.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def ok(self, msg: str) -> None:
        self.passes.append(msg)

    def exit_code(self) -> int:
        return 1 if self.failures else 0


def check_profile_sections(report: Report) -> None:
    if not PROFILE.exists():
        report.fail(f"Profile missing: {PROFILE}")
        return
    text = PROFILE.read_text(encoding="utf-8")
    lines = text.splitlines()
    headers = [ln for ln in lines if ln.startswith("## ")]
    for pat in REQUIRED_SECTIONS:
        rx = re.compile(pat)
        if any(rx.match(h) for h in headers):
            report.ok(f"§ present: {pat}")
        else:
            report.fail(
                f"Missing required §: {pat} — search Travel/archive/ and restore additively."
            )


def _display_path(fp: Path) -> str:
    """Render a path relative to TRAVEL_ROOT when possible, else relative to
    MYDRIVE_ROOT."""
    try:
        return str(fp.relative_to(TRAVEL_ROOT))
    except ValueError:
        try:
            return str(fp.relative_to(MYDRIVE_ROOT))
        except ValueError:
            return str(fp)


def check_required_files(report: Report) -> None:
    for fp in REQUIRED_FILES:
        if fp.exists():
            report.ok(f"file present: {_display_path(fp)}")
        else:
            report.fail(f"Missing required file: {_display_path(fp)}")


# ──────────────────────────────────────────────────────────────────────────────
# Doc-index ↔ CORE RULES/ folder integrity (added 2026-05-03)
# ──────────────────────────────────────────────────────────────────────────────
# Catches the drift class surfaced in the 2026-05-03 audit: a new `.html` lands
# (silent unindexed file), OR an indexed file gets renamed/deleted on disk and
# the index keeps pointing at the old name (ghost reference).
#
# Authority order: the on-disk `CORE RULES/` folder is the source of truth —
# CLAUDE.md doc index must mirror the folder. Any divergence = scaffolding drift,
# hard-fail. Note: Google Docs (.gdoc) retired 2026-05-09; source of truth is .html.
DOC_INDEX_HEADER = re.compile(r"^###?\s+CORE RULES HTML file index\s*$", re.MULTILINE)
DOC_INDEX_HTML_REF = re.compile(r"`([^`]+\.html)`")


def _extract_doc_index_block(text: str) -> str | None:
    """Return the body between `## Doc index` and the next `## ` header.

    Returns None if the section header is missing — caller handles that as a
    structural failure separate from the integrity check itself.
    """
    m = DOC_INDEX_HEADER.search(text)
    if not m:
        return None
    start = m.end()
    next_h2 = re.search(r"^## ", text[start:], re.MULTILINE)
    end = start + next_h2.start() if next_h2 else len(text)
    return text[start:end]


def check_doc_index_vs_core_rules(report: Report) -> None:
    """Diff `CORE RULES/*.html` filenames against `.html` refs in CLAUDE.md Doc index.

    - Files present on disk but NOT mentioned in the index → unindexed (fail).
    - Files mentioned in the index but NOT present on disk → ghost (fail).
    Both directions are scaffolding drift. Google Docs (.gdoc) retired 2026-05-09;
    source of truth is now .html files directly in Brain/CORE RULES/.
    """
    if not PROFILE.exists():
        return  # already reported by check_required_files
    if not CORE_RULES_DIR.exists():
        report.fail(
            f"CORE RULES dir missing: {_display_path(CORE_RULES_DIR)} — "
            f"can't run Doc-index integrity check."
        )
        return

    on_disk = {p.name for p in CORE_RULES_DIR.glob("*.html")}
    if not on_disk:
        report.fail(
            f"CORE RULES dir has zero `.html` files at {_display_path(CORE_RULES_DIR)} — "
            f"folder appears empty or not synced."
        )
        return

    text = PROFILE.read_text(encoding="utf-8")
    block = _extract_doc_index_block(text)
    if block is None:
        report.fail(
            "Doc-index ↔ CORE RULES integrity."
        )
        return

    # Only consider bare filenames — skip glob patterns (e.g. `Brain/CORE
    # RULES/*.html`) and any path-form refs. Index entries always cite the
    # filename alone in backticks.
    # Extract bare .html filenames from doc index (skip path-form and glob refs)
    indexed = {
        m.group(1)
        for m in DOC_INDEX_HTML_REF.finditer(block)
        if "*" not in m.group(1) and "/" not in m.group(1)
        and not m.group(1).startswith("_")  # skip _README.md etc.
    }

    unindexed = sorted(on_disk - indexed)
    ghosts = sorted(indexed - on_disk)

    for name in unindexed:
        report.fail(
            f"Unindexed CORE RULES Doc: `{name}` is in CORE RULES/ but not "
            f"listed in the Doc index (CLAUDE.md ### CORE RULES doc index). "
            f"Add it to the table."
        )
    for name in ghosts:
        report.fail(
            f"`{name}` but no such file in CORE RULES/. Repoint or restore."
        )

    if not unindexed and not ghosts:
        report.ok(
            f"Doc-index ↔ CORE RULES match: {len(on_disk)} `.html` files, "
            f"all indexed."
        )


def check_audit_staleness(report: Report) -> None:
    if not AUDIT_LOG.exists():
        report.warn(
            f"audit_log.md not found — create it with the first `## YYYY-MM-DD` entry "
            "via `guide_tools.py audit`."
        )
        return
    text = AUDIT_LOG.read_text(encoding="utf-8")
    dates = re.findall(r"^##\s+(\d{4}-\d{2}-\d{2})", text, re.MULTILINE)
    if not dates:
        report.warn("audit_log.md has no dated entries — run an audit.")
        return
    try:
        parsed = sorted(datetime.strptime(d, "%Y-%m-%d").date() for d in dates)
    except ValueError as e:
        report.warn(f"audit_log.md has an unparseable date: {e}")
        return
    last = parsed[-1]
    today = date.today()
    age = (today - last).days
    if age > AUDIT_STALE_DAYS:
        report.warn(
            f"Last audit was {age} days ago ({last.isoformat()}). "
            f"Threshold is {AUDIT_STALE_DAYS} days — run `guide_tools.py audit`."
        )
    else:
        report.ok(f"Last audit: {last.isoformat()} ({age} days ago).")


def check_ghost_references(report: Report) -> None:
    if not PROFILE.exists():
        return
    text = PROFILE.read_text(encoding="utf-8")
    refs: set[str] = set()
    for pat in REFERENCE_PATTERNS:
        for m in pat.finditer(text):
            refs.add(m.group(1))
    # Resolve each against Travel/ root.
    for ref in sorted(refs):
        # `Brain/...` and `Travel/...` are both relative to TRAVEL_ROOT's parent
        # in profile prose. Treat both as relative to Travel/ itself for
        # path resolution — `Brain/foo.py` → TRAVEL_ROOT / "Brain/foo.py".
        if ref.startswith("Travel/"):
            candidate = TRAVEL_ROOT / ref.removeprefix("Travel/")
        else:
            candidate = TRAVEL_ROOT / ref
        if candidate.exists():
            report.ok(f"ref resolved: {ref}")
        else:
            # `.gdoc` files are pointer stubs — don't fail if absent, warn.
            if ref.endswith(".gdoc"):
                report.warn(f"Profile references stale .gdoc (should be .html): {ref}")
            else:
                report.fail(
                    f"Ghost reference in profile: `{ref}` — file does not exist."
                )


# check_rule26_place_names() retired 2026-05-02. Examples are now welcome
# and load-bearing per Rules for Claude § 3. The "no real place names in
# the Brain" rule is fully retired. Function preserved in version control
# (.bak.2026-05-02) for lineage; not called.


# ──────────────────────────────────────────────────────────────────────────────
# HTML name-mention check (added 2026-05-08)
# Scans Brain/CORE RULES/ for occurrences of the owner's name in rule content.
# Warns (does not fail) — not every occurrence is wrong, but all should be
# reviewed and replaced with neutral phrasing.
# ──────────────────────────────────────────────────────────────────────────────

# The read-only banner on every HTML file contains "DANI'S REQUEST" — structural
# boilerplate that is intentional and should not trigger a warning.
_BANNER_RE = re.compile(r'<p class="banner">[^<]*</p>', re.IGNORECASE)

# Structural / intentional occurrences of the owner's name — not rule content.
# Expanded 2026-05-09: section names, routing labels, personal-fact lines.
_NAME_EXCL_RE = re.compile(
    # Retired 2026-05-14: `Dani Leo Trip` prefix — Trips folder + file were
    # renamed to drop the owner's name (was `Dani Leo Trips/Dani Leo Trips - Data.html`,
    # now `Trips/Trips.html`). The pattern no longer matches anything in active
    # rule content; kept commented for history.
    r'Questions for Dani'       # To-Do section heading
    r'|Tasks \(Dani'            # "✈️ My Tasks (Dani only)"
    r'|Dani only'               # routing label
    r'|Dani and Leo'            # personal fact (loyalty status etc.)
    r"|Dani'?s",                # possessive in section/doc titles
    re.IGNORECASE,
)

# The name to flag in rule content.
_NAME_RE = re.compile(r'\bDani\b')


def check_html_name_mentions(report: Report) -> None:
    """Warn if the owner's name appears in HTML rule-doc content.

    Exclusions (structural / intentional, not rule content):
      - The read-only banner line present on every file.
      - Lines referencing 'Trips' doc pointers.
    """
    if not HTML_RULES_DIR.exists():
        report.warn(
            f"CORE RULES dir not found: {_display_path(HTML_RULES_DIR)}"
            " — skipping name-mention check."
        )
        return

    html_files = sorted(HTML_RULES_DIR.rglob("*.html"))
    if not html_files:
        report.warn(
            "No HTML files found in CORE RULES/ — skipping name-mention check."
        )
        return

    flagged: list[tuple[Path, int]] = []
    for fp in html_files:
        try:
            text = fp.read_text(encoding="utf-8")
        except Exception:
            continue
        # Strip intentional/structural occurrences before scanning.
        cleaned = _BANNER_RE.sub("", text)
        cleaned = _NAME_EXCL_RE.sub("", cleaned)
        count = len(_NAME_RE.findall(cleaned))
        if count:
            flagged.append((fp, count))

    if not flagged:
        report.ok(
            f"HTML name check: no name mentions in rule content across {len(html_files)} HTML files."
        )
    else:
        total = sum(c for _, c in flagged)
        lines = "\n".join(
            f"    {_display_path(fp)} ({c}×)" for fp, c in flagged
        )
        report.warn(
            f"HTML name check: name appears in rule content in {len(flagged)} file(s) "
            f"({total} occurrence(s)). Review and replace with neutral phrasing:\n{lines}"
        )


# ──────────────────────────────────────────────────────────────────────────────
# HTML content-quality checks (added 2026-05-08)
# Four additional patterns that signal non-rule content drifting into the HTML
# rule docs. All warn (do not fail) — occurrences need review, not auto-removal.
# ──────────────────────────────────────────────────────────────────────────────

# 1. Hardcoded MCP tool IDs — mcp__<uuid>__ strings go stale when connectors
#    are updated. Should never appear in a rule doc.
_MCP_TOOL_ID_RE = re.compile(r'mcp__[a-z0-9\-]{8,}__\w+')

# 2. Date stamps in rule content — YYYY-MM-DD inside tag content is almost
#    always a session anchor or attributed quote, not a rule.
#    Matches dates that appear in visible text (after ">"), not in attributes.
# Narrowed 2026-05-09: exclude annotation contexts (version notes, retirement,
# section-header "added/updated" markers). Only flag bare session-anchor dates.
_DATE_IN_CONTENT_RE = re.compile(r'>\s*[^<]*20\d{2}-\d{2}-\d{2}')
_DATE_ANNOT_RE = re.compile(r'(?:v\d+,|retired |added |updated rule |locked |caught |amended |\().*?20\d{2}-\d{2}-\d{2}')

_ATTRIBUTED_QUOTE_RE = re.compile(
    r'—\s+(?!added|updated|locked|retired|amended|wired|merged|renamed)([A-Z][a-z]+)\s+20\d{2}-\d{2}-\d{2}'
)

# 4. First-person pronouns inside <blockquote> — personal voice captured
#    verbatim rather than translated into a neutral rule.
_BLOCKQUOTE_RE = re.compile(r'<blockquote>(.*?)</blockquote>', re.IGNORECASE | re.DOTALL)
_FIRST_PERSON_RE = re.compile(
    r"\bI'm\b|\bI don'?t\b|\bI do\b|\bI have\b|\bI like\b|\bI book\b"
    r"|\bI travel\b|\bI use\b|\bI go\b|\bI stay\b|\bI prefer\b|\bI work\b"
    r"|\bI can'?t\b|\bI set\b|\bwe travel\b|\bwe don'?t\b|\bwe go\b"
    r"|\bmy favorite\b|\bfor me\b",
    re.IGNORECASE,
)


def _load_html_files() -> tuple[list[Path], bool]:
    """Return (html_files, ok). Shared by all HTML content checks."""
    if not HTML_RULES_DIR.exists():
        return [], False
    return sorted(HTML_RULES_DIR.rglob("*.html")), True


def check_html_mcp_tool_ids(report: Report) -> None:
    """Warn if hardcoded MCP tool IDs appear in any HTML rule doc."""
    html_files, ok = _load_html_files()
    if not ok:
        return  # already warned by check_html_name_mentions
    flagged: list[tuple[Path, list[str]]] = []
    for fp in html_files:
        try:
            text = fp.read_text(encoding="utf-8")
        except Exception:
            continue
        hits = _MCP_TOOL_ID_RE.findall(text)
        if hits:
            flagged.append((fp, hits))
    if not flagged:
        report.ok(f"HTML MCP tool ID check: no hardcoded tool IDs across {len(html_files)} files.")
    else:
        lines = "\n".join(
            f"    {_display_path(fp)}: {', '.join(h[:2])}{'…' if len(h) > 2 else ''}"
            for fp, h in flagged
        )
        report.warn(
            f"HTML MCP tool ID check: hardcoded tool IDs found in {len(flagged)} file(s). "
            f"Move to a connector capabilities doc, not a rule:\n{lines}"
        )


def check_html_date_stamps(report: Report) -> None:
    """Warn if YYYY-MM-DD date stamps appear in HTML rule content (session anchors / attributed quotes)."""
    html_files, ok = _load_html_files()
    if not ok:
        return
    flagged: list[tuple[Path, int]] = []
    for fp in html_files:
        try:
            text = fp.read_text(encoding="utf-8")
        except Exception:
            continue
        hits = _DATE_IN_CONTENT_RE.findall(text)
        # Filter out annotation contexts (version notes, retired/added/locked markers)
        real = [h for h in hits if not _DATE_ANNOT_RE.search(h)]
        if real:
            flagged.append((fp, len(real)))
    if not flagged:
        report.ok(f"HTML date-stamp check: no bare date stamps in rule content across {len(html_files)} files.")
    else:
        total = sum(c for _, c in flagged)
        lines = "\n".join(f"    {_display_path(fp)} ({c}×)" for fp, c in flagged)
        report.warn(
            f"HTML date-stamp check: YYYY-MM-DD dates in rule content in {len(flagged)} file(s) "
            f"({total} occurrence(s)). Likely session anchors or attributed quotes — review:\n{lines}"
        )


def check_html_attributed_quotes(report: Report) -> None:
    """Warn if attributed quote signatures (— Name YYYY-MM-DD) appear in HTML rule docs."""
    html_files, ok = _load_html_files()
    if not ok:
        return
    flagged: list[tuple[Path, int]] = []
    for fp in html_files:
        try:
            text = fp.read_text(encoding="utf-8")
        except Exception:
            continue
        count = len(_ATTRIBUTED_QUOTE_RE.findall(text))
        if count:
            flagged.append((fp, count))
    if not flagged:
        report.ok(f"HTML attributed-quote check: no name+date attributions across {len(html_files)} files.")
    else:
        total = sum(c for _, c in flagged)
        lines = "\n".join(f"    {_display_path(fp)} ({c}×)" for fp, c in flagged)
        report.warn(
            f"HTML attributed-quote check: '— Name YYYY-MM-DD' pattern in {len(flagged)} file(s) "
            f"({total} occurrence(s)). Source quotes with attribution should be reviewed:\n{lines}"
        )


def check_html_first_person_blockquotes(report: Report) -> None:
    """Warn if first-person pronouns appear inside <blockquote> tags in HTML rule docs."""
    html_files, ok = _load_html_files()
    if not ok:
        return
    flagged: list[tuple[Path, int]] = []
    for fp in html_files:
        # On Demand files intentionally quote Dani's preferences verbatim —
        # first-person voice is correct there. Skip them. (2026-05-09)
        if "On Demand" in str(fp):
            continue
        try:
            text = fp.read_text(encoding="utf-8")
        except Exception:
            continue
        count = 0
        for bq in _BLOCKQUOTE_RE.finditer(text):
            if _FIRST_PERSON_RE.search(bq.group(1)):
                count += 1
        if count:
            flagged.append((fp, count))
    if not flagged:
        report.ok(
            f"HTML blockquote voice check: no first-person pronouns in blockquotes "
            f"across {len(html_files)} files."
        )
    else:
        lines = "\n".join(f"    {_display_path(fp)} ({c} blockquote(s))" for fp, c in flagged)
        report.warn(
            f"HTML blockquote voice check: first-person pronouns in blockquotes in "
            f"{len(flagged)} file(s). Personal-voice quotes should be translated into "
            f"neutral rules:\n{lines}"
        )


# ──────────────────────────────────────────────────────────────────────────────
# Rule 25 (amended 2026-04-25): no HTML in the profile
# ──────────────────────────────────────────────────────────────────────────────
# The profile is prose-only. Structural shape facts live as comments in
# `Guide Style.css`; runtime invariants live in `validate_itinerary.py`. Past
# Claude instances repeatedly drifted ```html fences back into the profile,
# turning it into "a gigantic, odd mess." This guard counts ```html fences and
# compares against a known baseline.
#
# Stage 4 of the 2026-04-25 slice landed: all 9 HTML example blocks were
# retired with Rule 11 forwarding markers pointing to their CSS § homes.
# The sentinel is now 0 — any ```html fence in the profile is drift and must
# hard-fail. The original baseline (9 fences at lines 638, 831, 848, 877, 1009,
# 1049, 1072, 1143, 1184) is preserved here in the comment for lineage; the
# WARN-mode tolerance band is gone.

def check_no_html_in_profile(report: Report) -> None:
    if not PROFILE.exists():
        report.fail(f"Profile missing: {PROFILE}")
        return
    text = PROFILE.read_text(encoding="utf-8")
    lines = text.splitlines()
    fence_lines = [i + 1 for i, ln in enumerate(lines) if ln.strip() == "```html"]
    count = len(fence_lines)
    if count == 0:
        report.ok("Rule 25: no ```html fences in profile (prose-only).")
        return
    # Stage 4 landed 2026-04-25 — all HTML example blocks retired. Any ```html
    # fence now is drift; hard-fail so it gets cleaned up immediately.
    report.fail(
        f"Rule 25 violation: {count} ```html fence(s) in profile at lines "
        f"{fence_lines}. The profile is prose-only (Stage 4 complete); structural "
        f"shape facts belong in guide_v2.css comments, not in profile fences."
    )


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────


def check_no_archive_subfolders_in_guides(report: Report) -> None:
    """Fail if any archive/ subfolder exists inside Travel/Guides/.
    
    Correct archive destination is always Travel/archive/ — never a per-guide
    subfolder. Added 2026-05-09 per rule: archive destination = Travel/archive/,
    no subfolders inside Guides/ or elsewhere.
    """
    guides_dir = TRAVEL_ROOT / "Guides"
    if not guides_dir.exists():
        return
    for city_dir in guides_dir.iterdir():
        if not city_dir.is_dir():
            continue
        archive_sub = city_dir / "archive"
        if archive_sub.exists():
            report.fail(
                f"Guides/{city_dir.name}/archive/ — per-guide archive subfolder found. "
                f"Move contents to Travel/archive/ and remove the subfolder. "
                f"Archive destination is always Travel/archive/, never inside Guides/."
            )
        # Also catch capitalised variants
        for variant in ("Archive", "ARCHIVE"):
            if (city_dir / variant).exists():
                report.fail(
                    f"Guides/{city_dir.name}/{variant}/ — per-guide archive subfolder found. "
                    f"Move contents to Travel/archive/ and remove the subfolder."
                )



def check_guide_roots(report: Report) -> None:
    """
    Fail if any file other than {city}_vN.html or {city}_vN.pdf exists at the
    root of a guide directory (Travel/Guides/{City}/).

    Allowed at root: *.html, *.pdf, _build/ (subdirectory).
    verification_log.json now lives inside _build/ (moved 2026-05-09); root location
    still tolerated here as a back-compat fallback for any pre-migration guide.
    Everything else belongs in _build/ or Travel/archive/.

    Rule source: Brain/CORE RULES/Guide Structure.html § Guide directory layout.
    Added 2026-05-09.
    """
    guides_dir = TRAVEL_ROOT / "Guides"
    if not guides_dir.exists():
        return

    allowed_suffixes = {".html", ".pdf", ".json"}
    allowed_names = {"_build", "verification_log.json"}  # _build/ = canonical; verification_log.json at root = back-compat only (moved to _build/ 2026-05-09)

    violations = []
    for city_dir in sorted(guides_dir.iterdir()):
        if not city_dir.is_dir():
            continue
        for item in sorted(city_dir.iterdir()):
            name = item.name
            if name.startswith("."):
                continue
            if item.is_dir():
                if name not in allowed_names and not name.startswith("."):
                    # archive subfolders caught by check_no_archive_subfolders_in_guides
                    # only flag unexpected non-allowed dirs here
                    if name.lower() not in {"archive"}:
                        violations.append(
                            f"Guides/{city_dir.name}/{name}/ — unexpected folder at guide root "
                            f"(only _build/ allowed; assets/ lives inside _build/ since 2026-05-09). Move to _build/ or Travel/archive/."
                        )
                continue
            if item.suffix.lower() in allowed_suffixes or name in allowed_names:
                continue
            violations.append(
                f"Guides/{city_dir.name}/{name} — unexpected file at guide root "
                f"(only .html / .pdf / verification_log.json allowed). Move to _build/."
            )

    for v in violations:
        report.fail(v)

    if not violations:
        report.ok("Guide roots clean — only .html / .pdf / verification_log.json at Guides/*/.")

def check_banned_brain_files(report: Report) -> None:
    """Hard-fail if any snippet/scaffold file exists anywhere under Brain/.

    Section Snippets and any equivalent file are permanently banned (archived
    2026-05-24). They cause format drift: when a rule changes, stale snippets
    get copied instead of the current rules being read. The rules are the only
    authoritative source — no copy-paste scaffolds.

    Banned patterns (case-insensitive, anywhere under Brain/):
      - *snippet* (e.g. Section Snippets.html, snippets.html)
      - *scaffold* (e.g. scaffold_getting_around.html)
      - *template* (e.g. section_template.html)

    If you see this fail: archive the offending file to Travel/archive/ and do
    not recreate it. Read the CORE RULES directly instead.
    """
    brain_dir = TRAVEL_ROOT / "Brain"
    if not brain_dir.exists():
        return

    banned_patterns = ("snippet", "scaffold", "template")
    hits: list[str] = []

    for fp in brain_dir.rglob("*"):
        if not fp.is_file():
            continue
        if fp.name.startswith("."):
            continue
        name_lower = fp.name.lower()
        for pat in banned_patterns:
            if pat in name_lower:
                rel = fp.relative_to(TRAVEL_ROOT)
                hits.append(
                    f"{rel} — banned scaffold/snippet file. "
                    f"Archive to Travel/archive/ and do not recreate. "
                    f"Read CORE RULES directly (archived 2026-05-24: snippet files cause drift when rules change)."
                )
                break  # one hit per file

    for h in hits:
        report.fail(h)

    if not hits:
        report.ok("Brain/ — no banned snippet/scaffold/template files found.")


# ──────────────────────────────────────────────────────────────────────────────
# CORE RULES checksum coverage + match (added 2026-05-30 audit)
# ──────────────────────────────────────────────────────────────────────────────
# Before this, brain_check reported "Brain intact" without ever verifying the
# CORE RULES SHA-256 checksum store. A file could be modified (or a new .html
# added and never tracked) and session-start would still say all-clear, while
# validate_itinerary.py hard-failed every guide on the same drift. This wires
# the same guard into the session-start check as a WARNING — surfaced early,
# without hard-blocking work (the ship-gate validator remains the hard gate).
#   - modified  : on-disk SHA-256 != stored  → un-updated or unauthorized edit
#   - untracked : .html in CORE RULES/ not in store → no integrity guard at all
# Fix for either: run update_core_rules_checksums.py (after confirming the edit
# was intentional).
CHECKSUMS_PATH = HERE / "core_rules_checksums.json"


def check_core_rules_checksums(report: Report) -> None:
    import hashlib
    import json

    if not CHECKSUMS_PATH.exists():
        report.warn(
            f"CORE RULES checksum store missing: {_display_path(CHECKSUMS_PATH)} — "
            f"run update_core_rules_checksums.py to generate it."
        )
        return
    if not CORE_RULES_DIR.exists():
        return  # already reported elsewhere
    try:
        stored = json.loads(CHECKSUMS_PATH.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        report.warn(f"CORE RULES checksum store unreadable: {e!r}")
        return

    on_disk = {p.name for p in CORE_RULES_DIR.glob("*.html")}
    modified: list[str] = []
    for name, stored_hash in stored.items():
        fp = CORE_RULES_DIR / name
        if not fp.is_file():
            continue  # missing-from-disk is covered by doc-index/ghost checks
        if hashlib.sha256(fp.read_bytes()).hexdigest() != stored_hash:
            modified.append(name)
    untracked = sorted(on_disk - set(stored.keys()))

    if modified:
        report.warn(
            "CORE RULES modified vs stored checksum: "
            + "; ".join(sorted(modified))
            + " — if the edit was intentional run update_core_rules_checksums.py; "
            "otherwise revert. (validate_itinerary.py hard-fails every guide until resolved.)"
        )
    if untracked:
        report.warn(
            "CORE RULES .html not covered by checksum store: "
            + "; ".join(untracked)
            + " — run update_core_rules_checksums.py to bring under the integrity guard."
        )
    if not modified and not untracked:
        report.ok(
            f"CORE RULES checksums — all {len(on_disk)} .html files tracked and matching."
        )


def check_guides_index_coverage(report: Report) -> None:
    """Fail if any shipped city guide is missing from guides_index.html.

    A city folder is considered SHIPPED when it contains at least one .html file
    directly at the folder root (not inside _build/). Folders that contain only
    _build/ are in-progress builds — multiple cribs may be building simultaneously,
    so in-progress folders must never trigger this check.

    A shipped guide with no index entry means the post-ship step was skipped —
    the chain is broken and the guide is invisible to the index.

    Added 2026-05-30: enforces the 4-step index-update rule in
    Brain/Reference/Navigation.html § 5 and Brain/Reference/Ship Checklist.html § 11.
    Updated 2026-06-02: only flags city folders that contain a shipped .html file;
    in-progress builds (folder contains only _build/) are skipped so concurrent
    crib builds do not cause false brain-check failures.
    """
    guides_dir = TRAVEL_ROOT / "Guides"
    index_file = guides_dir / "guides_index.html"

    if not guides_dir.exists():
        return
    if not index_file.exists():
        report.fail(
            "Guides/guides_index.html missing — the master guide index does not exist."
        )
        return

    index_html = index_file.read_text(encoding="utf-8")

    # Collect city folder names that have at least one .html file at the root
    # (not inside _build/). Folders with only _build/ are in-progress builds.
    city_dirs = sorted(
        d.name for d in guides_dir.iterdir()
        if d.is_dir()
        and not d.name.startswith(".")
        and any(f.suffix == ".html" and f.parent == d for f in d.iterdir())
    )

    missing = []
    for city in city_dirs:
        # Match any href that contains the city folder name (case-insensitive)
        if f"./{city}/" not in index_html and f'href="./{city}/' not in index_html:
            missing.append(city)

    if missing:
        for city in missing:
            report.fail(
                f"Guides/{city}/ — city folder exists but has no entry in "
                f"guides_index.html. Run the 4-step index update: "
                f"Brain/Reference/Navigation.html § 5."
            )
    else:
        report.ok(
            f"guides_index.html coverage — all {len(city_dirs)} shipped guide(s) indexed."
        )


# ──────────────────────────────────────────────────────────────────────────────
# Reference audit R4 — ghost-reference catcher in Reference docs (added 2026-05-30)
# Greps every Brain/Reference/ file for .html and .py filenames and confirms
# each resolves on disk. Catches stale pointers left behind after renames/moves.
# ──────────────────────────────────────────────────────────────────────────────

# Match filenames only in deliberate reference contexts:
#   1. Backtick-quoted:            `Guide Structure.html`  or  `Brain/scripts/foo.py`
#   2. HTML <code> tag content:    <code>foo.html</code>
#   3. href / src attribute value: href="foo.html"  or  href="../Brain/foo.py"
# Template placeholders (containing { or *) are skipped.
_REF_CTX_PATTERNS = [
    re.compile(r'`([^`\n]+\.(?:html|py))`'),                        # backtick
    re.compile(r'<code>([^<\n]+\.(?:html|py))</code>',              # <code>
               re.IGNORECASE),
    re.compile(r'(?:href|src)\s*=\s*["\']([^"\']+\.(?:html|py))',   # href/src
               re.IGNORECASE),
]

# Filenames / patterns that intentionally live outside Brain/ — skip ghost check.
_REF_GHOST_ALLOWLIST: set[str] = {
    "guide_v2.css",         # Guides/ root
    "guides_index.html",    # Guides/ root
    "Trips.html",           # Travel/Trip Essentials/
}

# Reference docs excluded from the ghost-filename scan entirely.
# PDF Render Notes.md contains example paths from on-demand renders — these
# are session-specific and only created when explicitly requested; they are
# not persistent file pointers and should not be checked.
_REF_GHOST_EXCLUDED_DOCS: set[str] = {
    "PDF Render Notes.md",
    # Change Cascade.html uses versioned guide filenames (paris_v7.html, paris_v8.html)
    # as illustrative examples inside <li class="note"> — not real Brain/ pointers.
    # These example names live in Guides/, outside the Brain/ scan scope, so the
    # ghost-filename checker produces false positives. Excluded 2026-06-01.
    "Change Cascade.html",
}

def check_reference_doc_ghost_filenames(report: Report) -> None:
    """Fail if any Brain/Reference/ doc mentions a .html or .py filename
    that does not resolve to a file anywhere under Brain/ or Travel/."""
    ref_dir = BRAIN_DIR / "Reference"
    if not ref_dir.is_dir():
        return

    # Build an index of every .html and .py under Brain/ for fast lookup.
    brain_files: set[str] = set()
    for p in BRAIN_DIR.rglob("*"):
        if p.suffix in {".html", ".py"}:
            brain_files.add(p.name)

    ghosts_found = False
    for doc in sorted(ref_dir.iterdir()):
        if doc.suffix not in {".html", ".md", ".css"}:
            continue
        if doc.name in _REF_GHOST_EXCLUDED_DOCS:
            continue
        try:
            text = doc.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        seen: set[str] = set()
        for pat in _REF_CTX_PATTERNS:
            for m in pat.finditer(text):
                ref = m.group(1).strip()
                # Skip template placeholders and glob patterns.
                if '{' in ref or '*' in ref or '[' in ref:
                    continue
                # Skip shell commands in <code> blocks
                # (e.g. `python3 Brain/scripts/foo.py` or `cd Travel/`).
                _SHELL_CMDS = {
                    'python3', 'python', 'cd', 'git', 'npm', 'node',
                    'bash', 'sh', 'echo', 'export', 'source',
                }
                if ' ' in ref and ref.split()[0] in _SHELL_CMDS:
                    continue
                    continue
                # Normalise: strip leading ../ sequences.
                ref_clean = re.sub(r'^(?:\.\./)+', '', ref)
                fname = Path(ref_clean).name
                if fname in seen or fname in _REF_GHOST_ALLOWLIST:
                    continue
                seen.add(fname)
                # Resolve: if ref includes a path prefix, check from Travel root.
                # Strip a leading "Travel/" prefix so "Travel/Brain/foo.py"
                # resolves correctly against TRAVEL_ROOT (same as check_ghost_references).
                # Otherwise check by filename anywhere under Brain/.
                if '/' in ref_clean:
                    stripped = ref_clean.removeprefix("Travel/")
                    candidate = TRAVEL_ROOT / stripped
                    exists = candidate.exists()
                else:
                    exists = fname in brain_files
                if not exists:
                    report.fail(
                        f"Ghost filename in {doc.name}: `{ref}` — not found on disk"
                    )
                    ghosts_found = True

    if not ghosts_found:
        report.ok("Reference doc ghost-filename scan — all .html/.py references resolve")


def main(argv: list[str]) -> int:
    verbose = "--verbose" in argv or "-v" in argv

    report = Report()
    check_required_files(report)
    check_profile_sections(report)
    check_doc_index_vs_core_rules(report)   # was defined but never called — wired in 2026-05-07
    check_ghost_references(report)
    check_no_html_in_profile(report)
    check_audit_staleness(report)
    check_html_name_mentions(report)        # warns on name in HTML rule content (added 2026-05-08)
    check_html_mcp_tool_ids(report)         # warns on hardcoded MCP tool IDs (added 2026-05-08)
    check_html_date_stamps(report)          # warns on YYYY-MM-DD session anchors (added 2026-05-08)
    check_html_attributed_quotes(report)    # warns on — Name YYYY-MM-DD pattern (added 2026-05-08)
    check_html_first_person_blockquotes(report)  # warns on personal voice in blockquotes (added 2026-05-08)
    check_no_archive_subfolders_in_guides(report)  # fails on archive/ inside Guides/ (added 2026-05-09)
    check_guide_roots(report)                       # fails on stray files at guide root (added 2026-05-09)
    check_banned_brain_files(report)                # fails on snippet/scaffold/template files in Brain/ (added 2026-05-24)
    check_core_rules_checksums(report)              # warns on CORE RULES checksum drift / untracked .html (added 2026-05-30)
    # check_guides_index_coverage — REMOVED 2026-06-02: moved to ship gate in guide_tools.py.
    # Checking index coverage at session start is the wrong place — multiple cribs build
    # simultaneously and each crib should only check its own guide at ship time.
    # The targeted per-guide check now lives in guide_tools.py _check_guide_indexed().
    check_reference_doc_ghost_filenames(report)     # fails on .html/.py filename in Reference/ that doesn't exist under Brain/ (added 2026-05-30)

    # Render output.
    print("━━━ brain_check ━━━")
    if verbose:
        for line in report.passes:
            print(f"  ✓ {line}")
    for line in report.warnings:
        print(f"  ⚠ {line}")
    for line in report.failures:
        print(f"  ✗ {line}")

    passes = len(report.passes)
    warns = len(report.warnings)
    fails = len(report.failures)
    total = passes + warns + fails

    print(f"━━━ result: {passes}/{total} ok · {warns} warn · {fails} fail ━━━")

    if fails:
        print(
            "\nBrain integrity FAILED. Do not proceed with task work.\n"
            "Restore missing content additively from Travel/archive/ per Rules for Claude.html § 3 Working for Dani.\n"
            "Re-run `brain_check` once restored."
        )
        return 1
    if warns:
        print("\nBrain intact, but warnings above deserve attention.")
    else:
        print("\nBrain intact.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as e:  # noqa: BLE001
        print(f"brain_check: unexpected error — {e!r}", file=sys.stderr)
        sys.exit(2)
