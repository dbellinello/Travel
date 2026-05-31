#!/usr/bin/env python3
"""
CORE RULES enforcer — checks every .html in this folder against the
Universal Formatting Rules.

Single source of truth for the rules:
    Brain/Reference/Core Rules Formatting.html
The canonical CSS lives at:
    Brain/Reference/Core Rules Style.css
Every CORE RULES HTML must link that file (E1). When the external stylesheet
changes, E1 will catch any file that still uses a stale link.

Scope: ONLY the .html files in this folder. Not a guide validator. Does not
import from Brain/ or read anything outside CORE RULES/. Safe to delete at
any time.

Usage (from anywhere):
    python3 "doc_workshop_validator.py"                    # check every .html in this folder
    python3 "doc_workshop_validator.py" Tour\ Rules.html   # check one file
    python3 "doc_workshop_validator.py" --quiet            # only show files with violations
    python3 "doc_workshop_validator.py" --warn-only        # downgrade ERRORs to warnings
"""

from __future__ import annotations

import argparse
import datetime as dt
import html.parser
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


# ──────────────────────────────────────────────────────────────────────────
# Canonical external stylesheet path (E1). When the UFR canonical changes,
# update this constant and re-run.
# ──────────────────────────────────────────────────────────────────────────

CANONICAL_CSS_HREF = "../Reference/Core Rules Style.css"

# The canonical banner class and required text content.
# Files must use <p class="banner"> — NOT <p class="footer"> with inline style.
# Case-insensitive match on the text — CSS text-transform renders it visually
# uppercased either way.
CANONICAL_BANNER_TEXT = "This document is read-only and can only be edited by request"

# Legacy class names that are explicitly forbidden — replaced by the current
# canonical structure. (.meta is NOT legacy; it's the canonical meta block.)
LEGACY_CLASSES = ("titlebar", "title", "locked", "read-only-notice")

# ──────────────────────────────────────────────────────────────────────────
# Format-exception files — Claude reference files, not guide-builder rule docs.
# These use curly-brace notation ({like this}) as intentional technical notation,
# <em> for illustrative phrases, and may contain JSON/URL/HTML examples that
# standard checks would flag as violations. Checks that do not apply to these
# files gate themselves with: if path.name not in FORMAT_EXCEPTION_FILES
# Documented in Rules for Claude.html § 12.
# ──────────────────────────────────────────────────────────────────────────
FORMAT_EXCEPTION_FILES = {"Links.html", "Photos Rules.html", "Rules for Claude.html", "Toolbar.html"}


# ──────────────────────────────────────────────────────────────────────────
# CSS parsing — used only for E11 (display:none in inline style blocks)
# ──────────────────────────────────────────────────────────────────────────

def parse_css(css: str) -> dict[str, dict[str, str]]:
    """Parse flat CSS into {selector: {prop: value}}. Tolerant of whitespace.
    Strips /* ... */ comments. Does NOT handle @media or nested rules — the
    canonical CSS is flat by design."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    rules: dict[str, dict[str, str]] = {}
    for chunk in css.split("}"):
        chunk = chunk.strip()
        if not chunk or "{" not in chunk:
            continue
        sel, body = chunk.split("{", 1)
        selectors = [s.strip() for s in sel.split(",") if s.strip()]
        decls: dict[str, str] = {}
        for d in body.split(";"):
            d = d.strip()
            if not d or ":" not in d:
                continue
            k, v = d.split(":", 1)
            decls[k.strip().lower()] = " ".join(v.strip().split())
        for s in selectors:
            rules.setdefault(s, {}).update(decls)
    return rules


# ──────────────────────────────────────────────────────────────────────────
# HTML walker — collects everything we need in one pass
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class Walk:
    style_blocks: list[str] = field(default_factory=list)
    stylesheet_links: list[str] = field(default_factory=list)
    has_h1: bool = False
    h1_text: str = ""
    h1_starts_with_visual: bool = False     # leading emoji or <img>
    headings: list[tuple[int, str]] = field(default_factory=list)
    # Banner tracking: first <p class="banner"> seen
    p_banner_text: str | None = None
    # Legacy footer-as-banner: <p class="footer"> containing read-only text
    p_footer_with_readonly: bool = False
    legacy_class_hits: list[tuple[str, str]] = field(default_factory=list)   # (tag, class)
    spacer_count: int = 0
    external_imgs: list[str] = field(default_factory=list)
    p_density_runs: list[int] = field(default_factory=list)                  # length of each run of short <p>
    has_doctype: bool = True   # set by raw scan, not parser
    has_charset: bool = False
    has_lang: bool = False
    has_title_tag: bool = False


class _Walker(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.w = Walk()
        self._capture: str | None = None     # current capture: "style" | "h" | "p" | "title"
        self._h_level: int | None = None
        self._buf: list[str] = []
        self._h1_first_token: str | None = None
        self._consec_short_p = 0
        self._p_is_banner: bool = False
        self._p_is_footer: bool = False
        self._p_banner_seen: bool = False    # track whether we've seen the FIRST banner

    # — start tags —
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()

        if tag == "html" and a.get("lang"):
            self.w.has_lang = True
        if tag == "meta" and (a.get("charset") or "").lower() == "utf-8":
            self.w.has_charset = True
        if tag == "title":
            self._capture = "title"
            self._buf = []
        if tag == "style":
            self._capture = "style"
            self._buf = []
        if tag == "link" and (a.get("rel") or "").lower() == "stylesheet":
            self.w.stylesheet_links.append(a.get("href") or "")
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._capture = "h"
            self._h_level = int(tag[1])
            self._buf = []
            if tag == "h1":
                self.w.has_h1 = True
                self._h1_first_token = None
        if tag == "img":
            src = a.get("src") or ""
            # External image only flagged when src is non-empty and not data:
            if src and not src.lower().startswith("data:"):
                self.w.external_imgs.append(src)
            if self._capture == "h" and self._h_level == 1 and not self._buf:
                self.w.h1_starts_with_visual = True
        if tag == "p":
            self._capture = "p"
            self._buf = []
            self._p_is_banner = "banner" in cls
            self._p_is_footer = "footer" in cls
            if "spacer" in cls:
                self.w.spacer_count += 1
        if tag == "div":
            for legacy in LEGACY_CLASSES:
                if legacy in cls:
                    self.w.legacy_class_hits.append((tag, legacy))
        if tag == "p":
            for legacy in LEGACY_CLASSES:
                if legacy in cls and legacy != "banner":
                    self.w.legacy_class_hits.append((tag, legacy))

    # — end tags —
    def handle_endtag(self, tag):
        if tag == "title" and self._capture == "title":
            self.w.has_title_tag = True
            self._capture = None
            self._buf = []
        elif tag == "style" and self._capture == "style":
            self.w.style_blocks.append("".join(self._buf))
            self._capture = None
            self._buf = []
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._capture == "h":
            text = "".join(self._buf).strip()
            if self._h_level == 1:
                self.w.h1_text = text
                # leading visual = leading <img> (set above) OR leading emoji char
                if not self.w.h1_starts_with_visual and text:
                    if _starts_with_emoji(text):
                        self.w.h1_starts_with_visual = True
            self.w.headings.append((self._h_level or 0, text))
            self._capture = None
            self._h_level = None
            self._buf = []
            self._consec_short_p = 0
        elif tag == "p" and self._capture == "p":
            text = "".join(self._buf).strip()
            if self._p_is_banner and not self._p_banner_seen:
                # Capture FIRST <p class="banner"> only — not subsequent repeats.
                self.w.p_banner_text = text
                self._p_banner_seen = True
            if self._p_is_footer:
                # Check if this footer paragraph is actually serving as the read-only
                # banner — legacy pattern: <p class="footer" style="color:#cc0000; …">
                # Files should use class="banner" instead.
                # Detection: both "read-only" AND "edited by request" must appear.
                # This is unique to the banner text and avoids false positives on
                # unrelated footer paragraphs that happen to contain "this".
                _tl = text.lower()
                if ("read-only" in _tl or "read only" in _tl) and "edited by request" in _tl:
                    self.w.p_footer_with_readonly = True
            # density tracking (skip banner & template & list-context paragraphs)
            if not self._p_is_banner and len(text) <= 80 and text:
                self._consec_short_p += 1
            else:
                if self._consec_short_p >= 3:
                    self.w.p_density_runs.append(self._consec_short_p)
                self._consec_short_p = 0
            self._capture = None
            self._buf = []
        elif tag in ("ul", "ol", "div", "h2", "h3", "body"):
            # any block boundary (or end of body) breaks the short-p run
            if self._consec_short_p >= 3:
                self.w.p_density_runs.append(self._consec_short_p)
            self._consec_short_p = 0

    # — text —
    def handle_data(self, data):
        if self._capture in ("style", "h", "p", "title"):
            self._buf.append(data)


def _starts_with_emoji(s: str) -> bool:
    """Crude emoji detection — first char in supplementary planes or in the
    common emoji ranges. Good enough for "did the title start with an emoji?"."""
    if not s:
        return False
    c = s[0]
    cp = ord(c)
    # Common emoji / pictograph ranges used in these files
    if cp >= 0x1F300:                     # supplementary multilingual plane symbols
        return True
    if 0x2600 <= cp <= 0x27BF:            # misc symbols & dingbats (☕ ⚠ ✈ etc.)
        return True
    if 0x2B00 <= cp <= 0x2BFF:            # misc symbols & arrows (⭐ ⬆ etc.)
        return True
    if 0x2300 <= cp <= 0x23FF:            # misc technical (⏳ ⌚ etc.)
        return True
    if cp == 0x00A7:                      # § itself
        return True
    return False


# ──────────────────────────────────────────────────────────────────────────
# Per-file checks
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class Finding:
    level: str          # "ERROR" or "WARN"
    rule: str           # e.g. "E2 [§3,§7]"
    message: str


def check_file(path: Path) -> list[Finding]:
    raw = path.read_text(encoding="utf-8", errors="replace")

    # raw scans (don't need the parser)
    has_doctype = bool(re.match(r"\s*<!doctype\s+html", raw, flags=re.I))

    # walk
    walker = _Walker()
    try:
        walker.feed(raw)
        walker.close()
    except Exception as e:  # noqa: BLE001
        return [Finding("ERROR", "E0 [parse]", f"HTML parse failed: {type(e).__name__}: {e}")]

    w = walker.w
    findings: list[Finding] = []

    # E0 — shell sanity
    if not has_doctype:
        findings.append(Finding("ERROR", "E0a [§3]", "missing `<!DOCTYPE html>`"))
    if not w.has_lang:
        findings.append(Finding("ERROR", "E0b [§3]", "`<html>` missing `lang=\"en\"`"))
    if not w.has_charset:
        findings.append(Finding("ERROR", "E0c [§3]", "missing `<meta charset=\"UTF-8\">`"))
    if not w.has_title_tag:
        findings.append(Finding("ERROR", "E0d [§3]", "missing `<title>` in `<head>`"))

    # E1 — linked canonical stylesheet required (2026-05-14: CSS extracted from
    # inline to external link, one source of truth at
    # Brain/Reference/Core Rules Style.css)
    if not w.stylesheet_links:
        findings.append(Finding(
            "ERROR", "E1 [§1,§3]",
            f'missing `<link rel="stylesheet" href="{CANONICAL_CSS_HREF}">` in `<head>` — '
            "CSS lives in the canonical stylesheet, linked from every file",
        ))
    elif not any(CANONICAL_CSS_HREF in href for href in w.stylesheet_links):
        findings.append(Finding(
            "ERROR", "E1 [§1,§3]",
            f"stylesheet link does not point to canonical "
            f"(→ {', '.join(w.stylesheet_links)}; should be `{CANONICAL_CSS_HREF}`)",
        ))

    # W1 — unexpected inline <style> declarations.
    # UFR §8 explicitly requires every CORE RULES file to carry a local <style>
    # block with these sanctioned per-file overrides of the canonical values:
    #   code { font-size: inherit; }          — overrides canonical 13px
    #   .entry { background: #fef9e0; }       — overrides canonical #f9f9f9
    #   li { margin-bottom: 12px; }           — spacing override
    # The .retired-notice class is also sanctioned for files that mark retired
    # content blocks. Any declaration outside these known-allowed (selector,
    # property) pairs is unexpected and warrants a warning.
    # W1-exempt files: these carry intentional full <style> blocks that must be
    # preserved exactly as-is. W1 is suppressed entirely for these files.
    # Icon Order and Format.html — special standalone format; full CSS block
    # required for its rich icon-table presentation. Do not modify its styles.
    _W1_FULL_CSS_FILES = {"Icon Order and Format.html"}
    _W1_ALLOWED_PAIRS = {
        ("code", "font-size"),
        (".entry", "background"),
        ("li", "margin-bottom"),
    }
    _W1_ALLOWED_SELECTORS = {".retired-notice"}
    if w.style_blocks and path.name not in _W1_FULL_CSS_FILES:
        actual_rules = parse_css("\n".join(w.style_blocks))
        unexpected = []
        for sel, props in actual_rules.items():
            if sel in _W1_ALLOWED_SELECTORS:
                continue
            for prop in props:
                if (sel, prop) not in _W1_ALLOWED_PAIRS:
                    unexpected.append(f"`{sel} {{ {prop} }}`")
        if unexpected:
            findings.append(Finding(
                "WARN", "W1 [§3]",
                f"unexpected declaration(s) in inline `<style>` — sanctioned overrides are "
                f"code/font-size, .entry/background, li/margin-bottom, and .retired-notice; "
                f"unexpected: {', '.join(sorted(set(unexpected))[:5])}",
            ))

    # E3 — RETIRED 2026-05-14. With CSS in the external canonical stylesheet
    # there is no per-file CSS to compare against canonical — the canonical IS
    # the file's CSS. Drift between files is structurally impossible now.

    # E4 — banner is <p class="banner"> with the canonical text.
    # Case-insensitive match: source text may be stored lower or upper case;
    # the CSS text-transform renders it visually uppercased either way.
    #
    # MIGRATION NOTE: files that pre-date 2026-05-14 used <p class="footer"
    # style="color:#cc0000; ..."> as the banner — wrong class, inline style
    # override. The correct class is `banner`. Run doc_workshop_fixer.py
    # (with permission for CORE RULES files) to migrate.
    if w.p_banner_text is None:
        hint = ""
        if w.p_footer_with_readonly:
            hint = (
                " — hint: found `<p class=\"footer\">` containing read-only text; "
                "rename class to `banner` and remove inline style override"
            )
        findings.append(Finding(
            "ERROR", "E4 [§3,§6]",
            f"missing `<p class=\"banner\">` read-only notice at top of `<body>`{hint}",
        ))
    elif not (
        "read-only" in w.p_banner_text.lower()
        and "edited by request" in w.p_banner_text.lower()
    ):
        # W3 checks for the two required phrases rather than exact text — the banner
        # may include additional reminder lines (e.g. "Read the formatting rules first…")
        # beyond the canonical single line, which is legitimate. Exact-match would
        # trigger spuriously on every multi-line banner.
        findings.append(Finding(
            "WARN", "W3 [§6]",
            f"banner text missing required phrases 'read-only' and/or 'edited by request' — "
            f"got: {w.p_banner_text[:80]!r}",
        ))

    # W_footer — <p class="footer"> used as banner (wrong class)
    # Separate from E4 so this fires even when E4 doesn't (unlikely but complete).
    if w.p_footer_with_readonly and w.p_banner_text is not None:
        findings.append(Finding(
            "WARN", "W_footer [§3,§6]",
            '`<p class="footer">` with read-only text found alongside a correct '
            '`<p class="banner">` — remove the duplicate `footer` banner',
        ))

    # E5 — no legacy <div class=titlebar/title/meta/locked/read-only-notice>
    if w.legacy_class_hits:
        seen = sorted(set(c for _, c in w.legacy_class_hits))
        findings.append(Finding(
            "ERROR", "E5 [§7]",
            f"legacy classes present (forbidden): {', '.join(f'`.{c}`' for c in seen)}",
        ))

    # E6 — no <p class="spacer">
    if w.spacer_count:
        findings.append(Finding(
            "ERROR", "E6 [§7]",
            f"{w.spacer_count} `<p class=\"spacer\">` element(s) — CSS margins already handle vertical spacing",
        ))

    # E7 — exactly one <h1> for the title
    h1_count = sum(1 for lv, _ in w.headings if lv == 1)
    if h1_count == 0:
        findings.append(Finding("ERROR", "E7 [§3,§6]", "missing `<h1>` title"))
    elif h1_count > 1:
        findings.append(Finding("ERROR", "E7 [§3,§6]", f"{h1_count} `<h1>` elements — should be exactly 1"))

    # W4 — h1 should start with an emoji (or embedded <img>)
    # Exemption: Claude Inspiration - Extra Section.html — section icon, title,
    # and color theme are Claude's pick per-guide (per Guide Structure.html). No
    # canonical emoji belongs in the rule file's h1 because the choice happens
    # at build time, not rule time.
    _W4_EXEMPT = {"Claude Inspiration - Extra Section.html"}
    if (w.has_h1
            and not w.h1_starts_with_visual
            and path.name not in _W4_EXEMPT):
        findings.append(Finding(
            "WARN", "W4 [§3,§6]",
            f"`<h1>` doesn't start with an emoji or `<img>` — got: {w.h1_text[:60]!r}",
        ))

    # W5 — RETIRED 2026-05-14. Dani's CORE RULES sweep removed § N. prefixes
    # from every h2 header across all 27 files. References are now file-name-only.
    # Check no longer applicable.

    # E8 — external <img src="..."> (non-data URI)
    if w.external_imgs:
        findings.append(Finding(
            "ERROR", "E8 [§7]",
            f"{len(w.external_imgs)} external `<img src=…>` (non-data URI) — embed as base64",
        ))

    # E11 — canonical elements must not be hidden with display:none
    # Catches two hiding attack vectors:
    #   A) display:none in an inline <style> block targeting canonical selectors
    #   B) style="display:none" attribute directly on canonical-class elements
    # Vector A — inline style block scan
    if w.style_blocks:
        actual_rules = parse_css("\n".join(w.style_blocks))
        CANONICAL_SELECTORS = {"p.banner", "h1", "h2", "h3", "h4", "p",
                               "ul", "ol", "li", ".banner", ".template"}
        hidden = [
            sel for sel, props in actual_rules.items()
            if props.get("display") == "none"
            and (sel in CANONICAL_SELECTORS
                 or any(c in sel for c in CANONICAL_SELECTORS))
        ]
        if hidden:
            findings.append(Finding(
                "ERROR", "E11a [§3,§6]",
                "canonical element(s) hidden with `display:none` in inline `<style>` — required structural "
                f"elements must be visible: {', '.join(f'`{s}`' for s in sorted(hidden))}",
            ))
    # Vector B — inline style attribute on elements with canonical classes
    _inline_hidden = re.findall(
        r'<(?:p|h[1-6]|div)\s[^>]*class="[^"]*(?:banner|meta|template)[^"]*"[^>]*'
        r'style="[^"]*display\s*:\s*none[^"]*"',
        raw, re.IGNORECASE
    )
    if _inline_hidden:
        findings.append(Finding(
            "ERROR", "E11b [§3,§6]",
            f"{len(_inline_hidden)} canonical element(s) hidden via inline `style=\"display:none\"` — "
            "structural elements must not be hidden",
        ))

    # W6 — RETIRED 2026-05-14. Was a stylistic check requiring blank source
    # lines to appear only immediately before <h2> headings. Pure source-code
    # aesthetics — no rendering, file-size, or functional impact. Today's § N
    # removal sweep naturally created blank lines in non-h2 positions; the
    # warning was noise.

    # W7 — version metadata pattern under the title (e.g. "v9 · 2026-04-30")
    version_meta = _scan_version_meta(raw)
    if version_meta:
        findings.append(Finding(
            "WARN", "W7 [§7]",
            f"version-metadata-looking text near top of `<body>`: {version_meta[:60]!r}",
        ))

    # W8 — RETIRED 2026-05-14. Was a stylistic check suggesting short
    # consecutive <p> tags be merged. Pure prose-style suggestion — some
    # sections (Getting Around's transit modes) legitimately need short
    # parallel paragraphs. Same noise category as W6.

    # E9 — ~ directly after a motion emoji (🚶 🚕 🚌) is a hard fail.
    # Rule docs use ~ in prose/examples legitimately; the broad ban lives
    # in validate_itinerary.py which checks shipped guide HTML.
    raw_no_comments = re.sub(r'<!--.*?-->', '', raw, flags=re.DOTALL)
    rendered = re.sub(r'<[^>]+>', ' ', raw_no_comments)
    tilde_hits = []
    for m in re.finditer(r'(?:🚶|🚕|🚌)\s*~\s*\d', rendered):
        snip = re.sub(r'\s+', ' ', rendered[max(0, m.start()-20):m.end()+30].strip())[:80]
        tilde_hits.append(snip)
    if tilde_hits:
        findings.append(Finding(
            "ERROR", "E9 [Motion §1]",
            f"~ after motion emoji — hard fail, actual minutes only: "
            f"{len(tilde_hits)} hit(s): "
            + "; ".join(f'"{s}"' for s in tilde_hits[:3]),
        ))

    # E10 — no currency/price figures in rule-doc HTMLs.
    # Rule-doc HTMLs document format rules — they must never show actual prices
    # ($, €, £, ¥, etc. adjacent to a digit). On Demand files live in a
    # subfolder and are not scanned by this validator (folder-level glob only).
    _rendered = re.sub(r'<[^>]+>', ' ', raw).replace('&nbsp;', ' ')
    currency_hits = []
    for m in re.finditer(r'([\$€£¥₩₹₽฿])\s*\d|\d+\s*([\$€£¥₩₹₽฿])', _rendered):
        snip = _rendered[max(0, m.start() - 20):m.end() + 20].strip()[:60]
        currency_hits.append(snip)
    if currency_hits:
        findings.append(Finding(
            "ERROR", "E10 [content]",
            f"currency/price figure in rule-doc HTML — prices belong in On Demand files only: "
            f"{len(currency_hits)} hit(s): "
            + "; ".join(f'"{s}"' for s in currency_hits[:3]),
        ))


    # E12 — no personal name references in rule-doc HTMLs
    # "Dani" is prohibited except in exempt patterns:
    #   - "Questions for Dani" (section label)
    #   - "My Tasks (Dani only)" (section label)
    #   - "BY REQUEST" in the read-only banner
    _rendered_text = re.sub(r'<[^>]+>', ' ', raw)
    _exempt = re.compile(
        r'Questions for Dani'    # section label
        r'|My Tasks[^.]*?Dani'   # section label (allow for parenthetical before name)
        r'|BY REQUEST',          # banner (already neutral)
        re.I | re.DOTALL
    )
    # scrub exempt spans, then look for bare "Dani"
    _scrubbed = _exempt.sub('___EXEMPT___', _rendered_text)
    _name_hits = re.findall(r'\bDani\b', _scrubbed)
    if _name_hits:
        # collect snippets for the message
        _snips = []
        for m in re.finditer(r'\bDani\b', _scrubbed):
            snip = _rendered_text[max(0, m.start()-30):m.end()+30].strip()
            snip = re.sub(r'\s+', ' ', snip)[:80]
            _snips.append(snip)
        findings.append(Finding(
            "ERROR", "E12 [content]",
            f"personal name reference(s) in rule doc ({len(_name_hits)} hit(s)) — "
            f"use neutral phrasing (e.g. 'the traveler'). First: {_snips[0]!r}",
        ))

    # E13 — no dated personal attributions (Per Dani YYYY-MM-DD or — Dani YYYY-MM-DD)
    _attr_hits = re.findall(
        r'(?:Per Dani|—\s*Dani)\s+\d{4}-\d{2}-\d{2}',
        raw, re.I
    )
    if _attr_hits:
        findings.append(Finding(
            "ERROR", "E13 [content]",
            f"{len(_attr_hits)} dated personal attribution(s) — remove 'Per Dani YYYY-MM-DD' "
            f"and '— Dani YYYY-MM-DD' patterns. First: {_attr_hits[0]!r}",
        ))


    # E15 — banned words must not appear as visible text in any rule doc.
    # Banned: "Map", "Maps", "Link", "Links" — the format shows what to do;
    # these words are never written out in guide text or rule docs.
    # Format-exception files (Links.html, Photos Rules.html, Rules for Claude.html)
    # are exempt — they are Claude reference files that may use these terms technically.
    # Per Icon Order and Format.html row 7 + Rules for Claude.html § 12.
    if path.name not in FORMAT_EXCEPTION_FILES:
        _e15_raw = re.sub(r'<script[^>]*>.*?</script>', '', raw, flags=re.DOTALL | re.IGNORECASE)
        _e15_raw = re.sub(r'<style[^>]*>.*?</style>', '', _e15_raw, flags=re.DOTALL | re.IGNORECASE)
        _e15_raw = re.sub(r'<!--.*?-->', '', _e15_raw, flags=re.DOTALL)
        # Exempt "Links.html" filename citations — proper noun reference, not the banned word.
        # Strip those before scanning so citations like "per Links.html §6" don't fire.
        _e15_raw = re.sub(r'\bLinks?\.html\b', '___FILENAME___', _e15_raw, flags=re.IGNORECASE)
        _e15_word_re = re.compile(r'>([^<]*\b(?:Maps?|Links?)\b[^<]*)<', re.IGNORECASE)
        _e15_hits: list[str] = []
        for _e15m in _e15_word_re.finditer(_e15_raw):
            _snippet = _e15m.group(1).strip()
            if _snippet:
                _e15_hits.append(_snippet[:60])
        if _e15_hits:
            findings.append(Finding(
                "ERROR", "E15 [content]",
                f'banned word(s) "Map/Maps/Link/Links" in visible text — '
                f'the format shows what to do; these words are never written out; '
                f'{len(_e15_hits)} hit(s): '
                + '; '.join(f'"{h}"' for h in _e15_hits[:3]),
            ))

    # E14 — no real domain names in rule docs (hard fail)
    # Rule docs are universal — baked-in domains (venue sites, booking URLs) create
    # city lock-in and drift. Domains belong only in files that are explicitly about
    # platforms or links (Links.html, Rules for Claude.html, Tours - Extra Section.html,
    # Michelin Restaurants, Photos Rules). 2026-05-13: `Tour Stop Rules.html` was
    # split into `Tours - Extra Section.html` + `Stops Structure.html`; the platform/domain
    # content stayed in Tours - Extra Section.html, so only that successor is exempt here.
    _DOMAIN_EXEMPT_FILES = {
        "links.html",
        "rules for claude.html",
        "tours - extra section.html",
        "michelin restaurants - extra section.html",
        "photos rules.html",
    }
    if path.name.lower() not in _DOMAIN_EXEMPT_FILES:
        _rendered_for_domains = re.sub(r'<[^>]+>', ' ', raw)
        # strip HTML entities that are part of template code blocks
        _rendered_for_domains = _rendered_for_domains.replace('&lt;', ' ').replace('&gt;', ' ').replace('&amp;', ' ')
        _domain_pat = re.compile(
            r'(?<![{/\w.-])([a-z0-9][a-z0-9\-]{1,60}'
            r'\.(?:com|org|net|fr|pt|es|it|de|uk|nl|be|ch|at|io|co|gov|edu))'
            r'(?![}\w-])',
            re.IGNORECASE
        )
        # exempt placeholder patterns, site: search operators, and common non-venue references
        _DOMAIN_PLACEHOLDER = re.compile(
            r'\{[^}]*\}'                   # {placeholder}
            r'|site:[a-z0-9.\-]+'          # site:viator.com search operators
            r'|show-or-venue-site\.com'
            r'|example\.com'
            r'|venue-site\.com'
            r'|venue-url',
            re.IGNORECASE
        )
        _rendered_no_placeholders = _DOMAIN_PLACEHOLDER.sub('___PLACEHOLDER___', _rendered_for_domains)
        _domain_hits = _domain_pat.findall(_rendered_no_placeholders)
        if _domain_hits:
            _domain_hits = sorted(set(_domain_hits))
            findings.append(Finding(
                "ERROR", "E14 [content]",
                f"real domain(s) in rule doc — use {{venue-site.com}} placeholder instead: "
                f"{', '.join(_domain_hits[:5])}",
            ))

    # W9 — redundant prose that restates what the entry template already shows visually.
    # Phrases like "each X ships as its own entry carrying…" duplicate the template row
    # and create drift when the format changes. The template is the spec — prose
    # descriptions of it are noise.
    # FORMAT_EXCEPTION_FILES are exempt: they are Claude-reference/behavioral docs that
    # legitimately use constructions like "without exception" in rule prose, not template narration.
    if path.name in FORMAT_EXCEPTION_FILES:
        return findings
    _REDUNDANT_PROSE_PATTERNS = [
        # Original catches
        r'ships as its own entry',
        r'each\s+\S+\s+ships\s+as',          # "each X ships as…" (any word, not just \w)
        r'each\s+entry\s+carries',
        r'the\s+entry\s+carries',
        r'appears\s+on\s+every\s+entry\s+without\s+exception',
        r'followed\s+by\s+the\s+(?:cuisine|description|map|address)',

        # Heading / row narration
        r'is\s+the\s+(?:heading|sub-?heading)',    # "X is the heading / sub-heading"
        r'is\s+the\s+first\s+row',                 # "X is the first row"
        r'immediately\s+below\s+the\s+(?:\w+\s+)?title',  # "immediately below the title"

        # Entry structure narration
        r'ships\s+as\s+one\s+(?:guided\s+)?stop',  # "ships as one guided stop"
        r'inside\s+the\s+same\s+colored\s+entry',
        r'outside\s+the\s+entry',
        r'one\s+heading\s+and\s+box\s+pair',

        # Link / element narration
        r'the\s+only\s+clickable\s+element',
        r'carries\s+the\s+same\s+visual\s+shape',

        # Row/box content narration
        r'the\s+row\s+(?:shows|contains|lists|carries|displays)',
        r'the\s+box\s+(?:shows|contains|lists|carries|displays)',
        r'is\s+followed\s+by\s+(?:its|the)\s+(?:closure|booking|description|rating|address)',

        # Generic "without exception" in format context
        r'without\s+exception',
    ]
    _rendered_for_prose = re.sub(r'<[^>]+>', ' ', raw)
    _prose_hits = []
    for pat in _REDUNDANT_PROSE_PATTERNS:
        for m in re.finditer(pat, _rendered_for_prose, re.I):
            snip = _rendered_for_prose[max(0, m.start()-20):m.end()+40].strip()
            snip = re.sub(r'\s+', ' ', snip)[:80]
            _prose_hits.append(snip)
    if _prose_hits:
        findings.append(Finding(
            "WARN", "W9 [content]",
            f"redundant prose restating the entry template ({len(_prose_hits)} hit(s)) — "
            f"the template row is the spec; remove the prose description. "
            f"First: {_prose_hits[0]!r}",
        ))

    return findings


def _scan_version_meta(raw: str) -> str | None:
    """Look for version-metadata text in the first ~20 lines after `<body>`.
    Catches things like 'v9 · 2026-04-30'."""
    lines = raw.splitlines()
    body_start = None
    for i, ln in enumerate(lines):
        if re.search(r"<body\b", ln, flags=re.I):
            body_start = i + 1
            break
    if body_start is None:
        return None
    head = "\n".join(lines[body_start:body_start + 25])
    # strip tags for the scan
    text = re.sub(r"<[^>]+>", " ", head)
    m = re.search(r"\bv\d+\s*·\s*\d{4}-\d{2}-\d{2}", text)
    return m.group(0) if m else None


# ──────────────────────────────────────────────────────────────────────────
# Reporting
# ──────────────────────────────────────────────────────────────────────────

def _hr(c: str = "─", n: int = 78) -> str:
    return c * n


def report(folder: Path, results: list[tuple[Path, list[Finding]]], quiet: bool) -> int:
    print(_hr("═"))
    print(f"  {folder.name} validator — {dt.datetime.now():%Y-%m-%d %H:%M}")
    print(_hr("═"))
    print(f"  Folder: {folder}")
    print(f"  Rules:  Brain/Reference/Core Rules Formatting.html")
    print(f"  Files:  {len(results)} HTML file(s) checked")
    print()

    clean_files: list[str] = []
    error_files: list[str] = []
    warn_files: list[str] = []

    for path, findings in results:
        errs = [f for f in findings if f.level == "ERROR"]
        warns = [f for f in findings if f.level == "WARN"]
        if errs:
            error_files.append(path.name)
        elif warns:
            warn_files.append(path.name)
        else:
            clean_files.append(path.name)

        if quiet and not findings:
            continue

        # File header
        if errs:
            tag = f"❌ {len(errs)} error(s)"
            if warns:
                tag += f", {len(warns)} warning(s)"
        elif warns:
            tag = f"⚠️  {len(warns)} warning(s)"
        else:
            tag = "✅ clean"
        print(f"  {path.name}  —  {tag}")
        for f in findings:
            print(f"     [{f.level:<5} {f.rule}] {f.message}")
        print()

    print(_hr())
    print(f"  Summary: {len(clean_files)} clean · {len(warn_files)} warn-only · {len(error_files)} with errors")
    print(_hr())
    if error_files:
        print(f"  Files with errors ({len(error_files)}):")
        for n in error_files:
            print(f"     · {n}")
    return 1 if error_files else 0


# ──────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("targets", nargs="*", help="Specific file(s) to check (default: every *.html in this folder)")
    ap.add_argument("--quiet", "-q", action="store_true", help="Only show files with violations")
    ap.add_argument("--warn-only", action="store_true", help="Downgrade ERRORs to warnings (always exit 0)")
    args = ap.parse_args()

    # Script lives in `Brain/scripts/`; HTMLs live at
    # `Brain/CORE RULES/`. Resolve up to Brain/ then into CORE RULES/ (moved 2026-05-13).
    folder = Path(__file__).resolve().parent.parent / "CORE RULES"
    if args.targets:
        files = [Path(t) if Path(t).is_absolute() else (folder / t) for t in args.targets]
        files = [p.resolve() for p in files]
        for p in files:
            if not p.exists():
                print(f"error: not found: {p}", file=sys.stderr)
                return 2
    else:
        files = sorted(folder.glob("*.html"))

    if not files:
        print(f"No .html files in {folder}")
        return 0

    results = [(p, check_file(p)) for p in files]

    if args.warn_only:
        for _, findings in results:
            for f in findings:
                if f.level == "ERROR":
                    f.level = "WARN"

    code = report(folder, results, quiet=args.quiet)
    return 0 if args.warn_only else code


if __name__ == "__main__":
    raise SystemExit(main())
