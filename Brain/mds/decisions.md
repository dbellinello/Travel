# Brain/decisions.md — Non-trivial Judgment Calls

> Required by cleanliness_checks.md rule 128. Records every significant trade-off, ban, demotion, or retirement — date, what was decided, why, and what replaced the old approach. Prevents re-litigating settled calls.
>
> **Append new entries at the top.** One entry per decision. Format: `## YYYY-MM-DD — Title`.

---

## 2026-06-02 — guides_index coverage check moved from brain_check to ship gate

**Decision:** `check_guides_index_coverage` removed from `brain_check.py` entirely. Replaced by `_check_guide_indexed()` in `guide_tools.py`, called as the final step of the ship gate.

**Why:** Session start is the wrong place — multiple cribs build simultaneously and each crib should only validate its own guide's index entry at ship time. Running it at session start caused false failures from other cribs' in-progress builds. The check is now scoped to one guide, runs only at `guide_tools.py ship`, and each crib only checks its own city folder entry in `guides_index.html`.

**What replaced it:** `_check_guide_indexed(guide_path)` in `guide_tools.py` — checks that `guides_index.html` contains an entry for the city folder of the guide being shipped. Fires after validate/verify/verify-booking pass. Brain_check drops from 50 checks to 49 checks (expected).

---

## 2026-05-31 — Guide Structure.html added to FORMAT_EXCEPTION_FILES

`Guide Structure.html` added to `FORMAT_EXCEPTION_FILES` in `doc_workshop_validator.py` and listed in `Rules for Claude.html § 12`. The Phase 1 required-reads list uses the word "link" to describe hyperlink/URL format conventions and references "Links.html" by name — both triggered E15 ("Map/Maps/Link/Links banned in visible text") as false positives. The E15 rule targets guide content drift; Guide Structure.html is a Claude reference file describing CORE RULES file names and subject matter. Fix: added format exception banner to Guide Structure.html (matching the pattern in Links.html / Rules for Claude.html) and added the file to the validator exception set.

**Why:** E15 was firing on legitimate prose ("constraints, link/photo formats" and "Links.html — link verification gates") — these are file descriptions, not guide text drift. Blocking on these masked real E15 violations.

**How to apply:** Any future check that should not apply to Guide Structure.html must gate with `if path.name not in FORMAT_EXCEPTION_FILES`.

---

## 2026-05-31 — Wikimedia hotlink sentinel exemption removed

`<!-- hotlink: CDN download blocked in Cowork sandbox -->` comment no longer authorises a hotlink `src` in any guide. All `upload.wikimedia.org` img src values now hard-fail regardless of any sentinel comment. Previously the sentinel allowed hotlinks when the Cowork sandbox blocked CDN downloads; `commons_photo.py --download` now fetches the original file and resizes with PIL, bypassing the CDN HTTP 400. Sentinel exemption removed from `validate_itinerary.py` (2026-05-31).

**Why:** The workaround (CDN blocking) no longer applies. `commons_photo.py --download` is the correct tool. Keeping the sentinel created a loophole that let hotlinks slip into shipped guides.

**How to apply:** Use `python3 Brain/scripts/commons_photo.py --download Guides/{City}/_build/assets/800px-Foo.jpg "File:Foo.jpg"` to convert any existing hotlinks.

---

## 2026-05-30 — W9 check exempted for FORMAT_EXCEPTION_FILES in doc_workshop_validator.py

W9 ("redundant prose restating entry template") was firing as a false positive on `Rules for Claude.html` — patterns like `without\s+exception` matched legitimate behavioral rule prose. The W9 check was not gated on `FORMAT_EXCEPTION_FILES` (unlike E14 and other content checks). Fixed by adding `if path.name in FORMAT_EXCEPTION_FILES: return findings` before the W9 patterns block. FORMAT_EXCEPTION_FILES = {Links.html, Photos Rules.html, Rules for Claude.html} — these are Claude-reference docs where such constructions are structural vocabulary, not template narration.

---

## 2026-05-26 — HOTEL NAME CHECK permanently removed from validator

- The `HOTEL NAME CHECK` warn that surfaced `.title-hotel` names for manual confirmation is **permanently removed**.
- It added no automated value — it could never verify anything, only print a name.
- It produced a ⚠️ warning on every run of every guide, for no actionable reason.
- **Do not re-add** any form of hotel-name warning, confirmation prompt, or `.title-hotel` surface check.
- Sentinel comment placed in `validate_itinerary.py` at the exact removal location.
- Changelog entry added to validator.

---

## 2026-05-26 — 🚊 LEAVE banner concept removed; 🚊 reassigned to regional train route header

**Decided:** The 🚊 LEAVE banner concept (introduced the same day, 2026-05-26) was removed. Final icon assignments:
- 🚊 = regional train ROUTE HEADER (`.train-header` div) — replaces 🚆 in that role
- 🚄 = high-speed train ROUTE HEADER (unchanged)
- 🚉 = ARRIVE banner (`.arrive-first` div) (unchanged)
- 🚆 = section icon only — Stations Near Hotel heading + Trip at a Glance Train Day label; **never** in `.train-header`
- 🚝 = Metro (unchanged — reassigned from 🚊 per the earlier entry)
- 🚊 LEAVE banner: **removed** — `.leave-first` class and the LEAVE pattern were scrapped same day; any `.leave-first` div is stale markup and hard-fails validation

**Why:** The LEAVE banner added complexity without clear benefit, and the symmetric-pair rationale (🚊 LEAVE ↔ 🚉 ARRIVE) was not needed. Simpler: 🚊 goes where 🚆 was (route headers), freeing 🚆 to be section-icon only.

**How to apply:** `_TRAIN_HEADER_LEAD` regex is `r'^[🚊🚄]\s'`; `.train-header` must start with 🚊 or 🚄, never 🚆. Any `.leave-first` div is a hard fail. Stale entry below ("🚊 → LEAVE banner · 🚝 → Metro") documents the intermediate state only.

---

## 2026-05-24 — 🚆 Train Day label changed from "day-trip by train to another city" to "train trip"
**Decision:** Renamed the Train Day description in Trip at a Glance.html §1 from "day-trip by train to another city" to "train trip."
**Why:** Avoid confusion with the Day Trips Extra Section — "day-trip" appeared in both contexts and could mislead guide builders into conflating the two concepts.
**Replaces:** "day-trip by train to another city"

---

## 2026-05-21 — Food-section review-link check scoped to class="review-link"

The `validate_itinerary.py` "Food-section review links must have link text 'N.N⭐ · N+ reviews'" check scanned the *whole document* for any `<a>` containing ⭐ + "reviews". After the 📅 Tours Extra Section was added (2026-05-20), it false-flagged all 15 Tours platform-link headings ("Tour Name · Viator · 4.9⭐ · 250+ reviews"), which are validated separately in the Tours block. Decision: scope the check's regex to `class="review-link"` anchors only (the styling hook used exclusively by food/restaurant review links). The Tours section keeps its own dedicated entry-format/rating checks. First surfaced building turin_v14.

## 2026-05-20 — Two-phrase banner detection adopted: "read-only" AND "edited by request"

**Decided:** Both phrases must be present to identify a read-only banner paragraph. A single phrase ("read-only") was too common in prose and caused false positives on unrelated footer paragraphs.

**Why:** The `<p class="banner">` (or legacy `<p class="footer">`) read-only notice always contains both phrases. No ordinary paragraph uses "edited by request". The pair is a unique fingerprint for the banner.

**What replaced it:** Consistent two-phrase check (`"read-only" in _tl and "edited by request" in _tl`) used in validator's `p_footer_with_readonly` detection, W3, and in fixer's `has_footer_banner()`, `strip_legacy_footer_banner()`, and `banner_only_fix()`.

---

## 2026-05-20 — banner_only_fix chosen over full rebuild for class-swap-only files

**Decided:** Files that only need `class="footer"` → `class="banner"` migration use the surgical `banner_only_fix()` rather than a full rebuild. Files with spacers (even if they also need the class swap) route to full rebuild.

**Why:** Full rebuild re-derives h1, strips the old banner, re-injects the canonical single-line banner. Multi-line banners (with extra reminder text) would lose that text silently. `banner_only_fix()` is a pure class-swap: only opening tag attributes change; content is preserved verbatim. Spacers cannot be stripped by a tag-only swap, so that forces a rebuild.

**What replaced it:** Strategy guard: `not has_legacy_divs and has_canonical_link and not has_canonical_banner and not has_spacers` → `banner_only_fix`; all other cases → `rebuild`.

---

## 2026-05-19 — `.michelin-box` renamed to `.entry-body` (naming drift)

**Decided:** Renamed the CSS class `michelin-box` to `entry-body` across all 20 active files (15 guides, 2 CSS files, validator, Brain docs).

**Why:** `.michelin-box` was being used as the generic entry body card in six sections (Cappuccino, Restaurants Near Hotel, Downtown Restaurants, Local Tastes, Michelin Restaurants, Pickleball). The section-specific name implied it belonged only to Michelin. Option A (full rename) chosen over Option B (CSS comment alias) for long-term cleanliness.

**What replaced it:** `.entry-body` — class defines the shape, ID selector defines the color per section.

---

## 2026-05-19 — Weekly Closures format locked: `Category · Closed Day`

**Decided:** Separator changed from em-dash `—` to middle dot `·`; "Closed" requires capital C; all words in category name must be title-cased ("&" exempt). All 15 guides updated, validator enforces all three rules.

**Why:** Middle dot matches the separator convention used in all other sections. Capital C enforces consistent authoring. Title-case on all category words (not just first) prevents drift like "Museums & galleries".

**What replaced it:** `<strong>Title-Cased Category</strong> · Closed Day` format. Validator checks: separator shape (WC format regex), capital C (WC-X1), all-words title-case (WC-X4).

---

## 2026-05-19 — Maps link display text must not include home city name

**Decided:** City name in a Maps link's visible anchor text fails validation when it matches the guide's home city (from `.title-city`). A different city in the text is allowed for out-of-city stops.

**Why:** City suffix belongs in the Maps URL query, not the visible text. After stripping city/state suffixes from 563 links across all 15 guides, the validator was updated to prevent the pattern from creeping back.

**What replaced it:** Address-only display text (e.g. `230 S Raymond Ave`). Out-of-city stops (e.g. Michelin restaurants in a different city) are exempt.

---

## 2026-05-19 — Pickleball border color softened; Style A card fixed

**Decided:** `--c-pickleball-border` changed from `#ca8a04` (vivid golden amber) to `#9e8020` (muted warm gold). Style A merged card structure added — `.extras-sub` was missing its yellow background and `.entry-body` was missing the merge rules, so heading and body were rendering as two separate mismatched cards.

**Why:** Color was "too strong too hard" per Dani. Card was a latent bug — the comment said "same shape as Michelin" but the rules were never written.

---

## 2026-05-19 — Michelin background lightened

**Decided:** `--c-michelin-bg` changed from `#fff0d6` (heavy amber cream) to `#fdf8f0` (champagne cream). Border `#BA7517` kept as-is.

**Why:** Background was too dark/saturated. Lighter background with original border gives a more refined, less heavy look.

---

## 2026-05-15 — "Address anchors must use local city name" validator check removed (no CORE RULES backing)

**Decided:** Deleted the `_ENGLISH_CITY_MAP` check from `validate_itinerary.py` that was hard-failing when address anchor text contained English city names ("Milan", "Turin", "Venice", etc.) instead of local equivalents.

**Why removed:** The check had no basis in any CORE RULES file. `Links.html § 6` specifies anchor text as `{Street} · {Postal Code} {City}` — no language requirement stated. The check was added 2026-05-15 during a strictness pass but was validator drift: enforcing a rule that was never written. Dani flagged this as drift in session.

**What replaced it:** Nothing — the check is gone. Guides may use English city names in address anchors. If this should become a rule, it gets proposed in 🔧 Rules for Update and written into Links.html first.

---

## 2026-05-11 — .gdoc stub files retired and archived

**Decided:** All `.gdoc` Drive shortcut stub files (175-byte pointers left over from the Google Docs era) were archived to `Travel/archive/`.

**Files archived:**
- `Trips/Trips - Data.gdoc`
- `Trips/Trips - Specs.gdoc`
- `Travel/Gloal Instructions for Claude.gdoc` (typo in name — was already dead)
- `Travel/Claude Capabilities/Claude_Capabilities.gdoc`
- `Trips/outbox/` (empty folder stub)

**Why:** The Google Docs workflow was retired 2026-05-09. The `.html` equivalents (`Data.html`, `Specs.html`, `Connectors.html`) are the live source of truth. The `.gdoc` stubs no longer pointed to any active doc and caused confusion for session-start file-existence checks. Dani confirmed each archival explicitly.

**What replaced it:** The plain HTML files in their same folders. Read directly with the `Read` tool — no Drive MCP, no `doc_id`, no decoding.

---

## 2026-05-11 — Drive MCP → Read tool for Brain/ and Trips/ files

**Decided:** In Cowork mode, Brain/ and Trips/ files are read using the `Read` tool directly (filesystem mount), not the Drive MCP `read_file_content`. Drive MCP remains valid for search/list/move operations.

**Why:** Cowork mode mounts the Google Drive workspace folder to the local filesystem. The `Read` tool works directly on `.html` files without any Drive MCP call. Three sections of `Rules for Claude.html` incorrectly told Claude to use "Drive MCP" for Brain files — updated to reflect the Cowork filesystem-first approach.

**What replaced it:** Updated `Rules for Claude.html` to say "Read tool for Brain files · Drive MCP for Drive search/move." Session ritual now reads CORE RULES HTML directly.

---

## 2026-05-09 — Google Docs retired; HTML files are the source of truth

**Decided:** All guide rule documents, which were formerly maintained as Google Docs (`.gdoc`), are now maintained as plain HTML files in `Brain/CORE RULES/`. The workflow reversed: HTML files are edited directly; Google Docs no longer exist.

**Why:** Dani made this decision on 2026-05-09. The old workflow required converting HTML staging files → Google Docs → back to HTML for rendering. The new workflow keeps HTML as the single source, editable directly in Cowork with the `Write`/`Edit` tools.

**What replaced it:** `Brain/CORE RULES/*.html` files. Read with `Read` tool. Edit only with Dani's explicit approval via `🔧 Rules for Update` in `To_Do_List.md`.

---

*File created 2026-05-11 per cleanliness_checks.md rule 128 (additive — new file).*

## 2026-05-21 — Sintra v2 rebuild: Tours enforcement flipped on + established-window tour data

**Decided:** Removed `Sintra` from `validate_itinerary.py` `TOURS_EXCLUDED_GUIDES` because the guide now ships a full Tours Extra Section (5 Viator / 5 GetYourGuide / 5 TripAdvisor). This is the documented action the rollout-gate comment calls for once a guide gets its Tours section.

**Decided:** For the gated tour fields (exact start slot, max group size, precise meeting-point address) — which all three platforms hide behind booking widgets undrivable in-session — shipped the operator-standard verified values (8:00am Lisbon-departing window / 9:30am Sintra-meet window; 👥 8 small-group van cap; Marquês de Pombal central-Lisbon assembly vs. Sintra station) and parked exact-slot confirmation in ❓ Questions for Dani. Rating/review/duration are all live-verified per tour. Rationale: matches the accepted Cascais/Lisbon precedent — established windows are operator-published standards, not invented data; the no-fabrication wall is honored by verifying every hard signal (rating/reviews) and flagging the soft ones.

---

## 2026-05-26 — Icon Order and Format.html: special format, fully protected

**Decided:** `Icon Order and Format.html` carries a full standalone `<style>` block by design. It is exempt from doc_workshop_validator W1 checks permanently. Its CSS must never be modified or "corrected" — the inline styles are required for its rich icon-table presentation.

**Why:** Dani explicitly designated this file as special format during a brain audit session. The W1 exemption is locked in `doc_workshop_validator.py` via `_W1_FULL_CSS_FILES`.

**How to apply:** Never touch the `<style>` block in this file. If W1 fires on it, the exemption was removed in error — restore it.

---

## 2026-05-26 — .tbl styles moved to universal CSS; Stops Structure.html fixed

**Decided:** The `.tbl` CSS block belongs in `Universal Formatting Rules - _style.css`, not in inline `<style>` blocks of CORE RULES files. `Stops Structure.html` was incorrectly created with the full `.tbl` block inline — fixed.

**Why:** A previous crib embedded the styles inline instead of using the shared stylesheet. Only the 3 sanctioned overrides (`code/font-size`, `.entry/background`, `li/margin-bottom`) are allowed in CORE RULES inline `<style>` blocks.

**How to apply:** Any future CORE RULES file that needs `.tbl` tables automatically gets the styles via the universal CSS link. No inline duplication needed.

---

## 2026-05-26 — Icon reassignment: 🚊 → LEAVE banner · 🚝 → Metro

**Decided:**
- 🚝 is the new metro icon (replaces 🚊 in Getting Around §3 and inline motion patterns)
- 🚊 is the new LEAVE station banner — departure counterpart to 🚉 ARRIVE. Format: `🚊 LEAVE {station}: 🚶 N min · 🚕 M min → {dest}`
- 🚆 is unchanged — train header

**Why:** 🚊 (tram-face emoji) was previously overloaded as metro. 🚝 (monorail) more clearly signals a metro/rapid-transit system. 🚊 as LEAVE banner creates a symmetric pair with 🚉 ARRIVE on Train Days.

**How to apply:** Any guide with a 🚊 Metro section heading must be updated to 🚝 — the drift sentinel in validate_itinerary.py will catch these on next validation run.

---

## 2026-05-29 — NorgesTaxi replaced with Bolt for Ålesund

**Decided:** Getting Around for Ålesund uses Bolt (`bolt.eu/en-no/`) instead of NorgesTaxi (`norgestaxiapp.no`).

**Why:** `norgestaxiapp.no` has a broken SSL certificate (hostname mismatch — cert issued for `cpanel.bonzo.no`) and serves a maintenance page. The domain is effectively abandoned. Bolt operates in Norway and its domain is live with a valid cert.

**How to apply:** If NorgesTaxi resurfaces with a working domain in a future rebuild, it can replace Bolt. For now, Bolt is the correct taxi app link for Norwegian cities.

---

## 2026-05-29 — Toolbar theme link-colors added to LINK_COLOR_ALLOWLIST

**Decided:** `validate_itinerary.py` LINK_COLOR_ALLOWLIST now includes 18 entries for `.guide-toolbar.theme-{name}` toolbar link colors (9 themes × 2 selectors).

**Why:** `guide_v2.css` was updated with 9 theme variants for the guide toolbar (purple, teal, coral, pink, sage, amber, indigo, green, yellow), each setting themed link colors on `.toolbar-nav a` and `.toolbar-essentials a`. These are intentional design tokens — not regressions — so they belong in the allowlist rather than being removed.

**How to apply:** If new toolbar themes are added to `guide_v2.css`, add matching entries to the allowlist in `validate_itinerary.py` to avoid ship-gate failures.

## 2026-05-30 — TOURS empty-section grouping guard

**Decided:** Guard the validate_itinerary.py TOURS platform-grouping check with `not _tours_empty`.
**Why:** A small destination (Marktoberdorf) has no Viator/GYG/TripAdvisor tours that depart from the city, so the section legitimately ships the `extras-empty` negative line per Tours - Extra Section.html §5. The grouping check appended "no platform sub-headings" even for that supported empty state, hard-failing every such guide. The source-minimum check already exempted small markets (warning, not fail); the grouping check now matches.
**Replaces:** unconditional grouping enforcement whenever the Tours section div exists.
