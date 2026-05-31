# Travel Folder Map — Claude's Resource Briefing

> **Read this at every session start.** It is your complete map of what exists, where it lives, and what it's for. If you don't know where something is — it's in here.
>
> **Last updated: 2026-05-28**

---

## What you are working with

You are Claude, working inside the owner's Travel folder on Google Drive. You build city guides, manage trip logistics, and maintain the infrastructure that makes guide-building clean and consistent. Everything you need is in this folder tree. This file tells you where.

---

## Travel/ — root folder

| File / Folder | What it is | Who owns it |
|---|---|---|
| `CLAUDE.md` | **Your session entry point.** Lean quick-reference pointer file: points to Rules for Claude.html as the source of truth, key reminders (connectors, file location, archive rule, trip updates), and workspace layout overview. The full session ritual, DriftyCat, and behavioral rules live in `Brain/CORE RULES/Rules for Claude.html` — CLAUDE.md points there, not duplicates. Read at every session start. | Claude maintains |
| `Brain/mds/travel_map.md` | **This file.** Read at session start alongside CLAUDE.md. | Claude maintains |
| `Brain/` | Everything that powers guide-building: rules, validators, scripts, CSS, reference files. Details below. | Claude maintains |
| `Guides/` | **FROZEN.** Shipped city guides (HTML + PDF + assets). Never read, grep, touch, or reference unless explicitly asks in chat. Contains `guides_index.html` — master index of all published guides with live GitHub Pages URLs; update on every ship per the delivery procedure in `Rules for Claude.html` § 4. Also contains `Guide Style.css` — a copy of `Brain/Reference/Guide Style.css` kept in sync whenever the Brain CSS changes (GitHub Pages can't reach Brain/). | owner-managed |
| `Brain/Reference/` | Operational reference files: `Core Rules Style.css` (styles CORE RULES docs) · `Guide Style.css` (styles shipped guides; copy kept in `Guides/guide_v2.css` for GitHub Pages) · `Core Rules Formatting.html` (canonical formatting rules for CORE RULES docs) · plus Platforms, Separation Map, PDF Render Notes, Rule Dependencies, Validator Index, Guide Entry Counts, Ship Checklist, Change Cascade, Connectors, Emoji Library, and more. | Claude maintains |
| `Brain/Reference/Connectors.html` | Briefing doc listing every connected tool and connector (TripAdvisor, Drive, Viator, Canva, Spotify, Chrome, Calendar, etc.). Read at session startup. Moved from `Travel/Claude Capabilities/` 2026-05-26. | Claude maintains |
| `Retired Rules/` | Retired CORE RULES files — removed from `Brain/CORE RULES/` when a rule is superseded. Current contents: `Retired_Tours.html` (in-stop guided tour format retired 2026-05-20; Tours Extra Section now governed by `Tours - Extra Section.html` only). Sealed — never reference these files in builds. | owner-managed |
| `Hotel Research/` | the owner's hotel research files. Not under Brain — hotel research is on-demand, not guide-building infrastructure. Contains `Amsterdam Hotels - Research.md`, `Hotel Research Index.md`, `Bend_Rentals.docx` (Bend rental research). | owner-managed |
| `Icons Library/` | Icon assets for guides. Key utility files: `icon_resources.md` (source links + notes), `_PREVIEW_all_icons.html` (browse all icons), `icon_picker_transport.html` (transport icon picker). `for_guides/` contains the icons actually used in shipped guides (organised by section: cappuccino, pickleball, shows, etc.). Source packs in `Favorite iconscout_3d/`, `iconscout_2d/`, `3dicons_co/`, `magnific/`, `transport_icons/`. | owner-managed, Claude references |
| `Brain/Reference/Emoji Library.html` | Locked-out emoji list and glyph registry. Moved from `Travel/Emojis Library/` 2026-05-26. | Claude maintains |
| `Trip Essentials/` | Combined essentials + trip-tracker folder (formerly separate `Trips/` folder merged here). Trip tracker: `Trips.html` (live tracker — source of truth for trip data; Claude edits this), `Trips v2.html`, `Trips - Rules.md` (read before editing Trips.html). Packing: `Travel Packing List.md`, `Travel Packing.html`, `Travel Packing v2.html`, `Plug Adapter/` (folder). Lounges: `Lounges Europe.html`, `Lounges Europe v2.html`, `Lounges US.html`, `Lounges US v2.html`. Delta routes: `Delta Routes Full.html`, `Delta Routes Full v2.html`, `Delta Routes SEA.html`, `Delta Routes SEA v2.html`. Also `README.md`. | owner-managed, Claude edits Trips.html when asked |
| `shopping_profile_v2.md` | the owner's shopping profile — preferences and style. **Moved here from `On The Go/Shopping Profile/` on 2026-05-18** so it sits with everything else Cowork-edited. Read before any shopping / product / buying request. | owner-managed, Claude reads |
| `To Do List/` | `To_Do_List.md` = cross-session task list (owner tasks + Rules for Update + Questions for the owner). `README.md` = index and routing rules for the folder. Claude reads and edits `To_Do_List.md` per the README. | owner-managed |
| `On Demand/` | On-demand research docs — read only when explicitly asked. None ship with the guide. Files: `Weather - On Demand.html`, `Delta - On Demand.html`, `Hotels & Rentals - On Demand.html`, `Car Rentals - On Demand.html`, `_style.css`. Moved from `Brain/CORE RULES/On Demand - Don't Ship in Guide/` 2026-05-28. | Claude reads, owner-managed |
| `Universal Formatting Rules/` | Currently empty. Referenced in `Trip Essentials/README.md` as part of the "core rules" system. | owner-managed |
| `archive/` | **Sealed vault.** Everything "deleted" goes here — never `rm`. Archive rule: move to `Travel/archive/`, no subfolders inside Guides. Flat folder — no brain/ subfolder. | the owner controls |

---

## Brain/ — guide-building infrastructure

### Brain/CORE RULES/ — source of truth for every guide rule

Every rule that shapes a guide lives here as a plain **HTML file**. **CORE RULES always beats CLAUDE.md.** When they conflict, the HTML file wins.

To read any CORE RULES file: use the `Read` tool directly on the `.html` file path. No Drive MCP, no doc_id, no decoding needed.

| File | What it governs |
|---|---|
| `Rules for Claude.html` | **Master rules doc.** Session ritual, build discipline, parking surfaces, archive walls, all behavioral rules. Read at session start. |
| `Guide Structure.html` | Overall guide shape, section IDs, section order, the canonical 14-id list (Tours first, added 2026-05-20). Guide directory layout. |
| ~~`Ship Checklist.html`~~ | Moved to `Brain/Reference/` 2026-05-24 — no longer a CORE RULES file |
| `Stops Structure.html` | Stop selection criteria (what to include/exclude), stop block format (§§2–5), Train Day entry pattern |
| `Day Structure.html` | Day shape rules: geographic clustering, stop count, route discipline |
| `Tours.html` | ~~Retired 2026-05-20.~~ In-stop tour box and Guided Tour Stop pattern retired. File moved to `Travel/Retired Rules/Retired_Tours.html`. Tours now live entirely in `Tours - Extra Section.html`. |
| `Tickets.html` | 🎟 ticket-box format: Skip-the-Line link text, venue-site fallback, Attraction Tickets waterfall (US / International / venue-site). |
| `Hotel Banner.html` | Title page: city + hotel + address only. Naming rules. FROM HOTEL banner. |
| `Trip at a Glance.html` | Glance section: day card format, train day suffix rule, card content |
| `Photos Rules.html` | One photo per stop, licensing rules, photo sourcing |
| `Links.html` | URL rules, Maps anchor format, booking link format |
| `Motion Rule.html` | Transit banners between stops: walk/tram/ride-app format |
| `Icon Order and Format.html` | **Canonical authority** for icon ordering (positions 1–11), per-icon format spec, section-header icon list, char limits per row. Read before using any icon — never guess from memory. |
| `Tours - Extra Section.html` | Tours Extras section (second section, after Weekly Closures): source pool (Viator/GetYourGuide/TripAdvisor + local fallback), 4.5⭐/6-review bar, per-source minimums (4 Viator / 4 GYG / 2 TripAdvisor), entry format (📅 name-link · operator · rating · reviews / 🕐⏳👥 / 📍 / 🚶🚕). NOT the same as `Tours.html` (that's the in-stop tour-box format). |
| `Getting Around - Extra Section.html` | Getting around section: tram subsection locked templates, transit operators |
| `Weekly Closures - Extra Section.html` | Weekly closures section: recurring patterns only, no national holidays |
| `Local Tastes - Extra Section.html` | Local tastes: city-specific only, no country-level clichés |
| `Food Delivery - Extra Section.html` | Food delivery section: platform availability, preference order, delivery rows in Cappuccino, exception approval |
| `Michelin Restaurants - Extra Section.html` | Michelin section: format, booking via own site only |
| `Restaurants Near Hotel - Extra Section.html` | Restaurants near hotel section |
| `Cappuccino - Extra Section.html` | Cappuccino / coffee culture section |
| `Day Trips by Train - Extra Section.html` | Day trips by train: Train/Why/Book via format, negative-finding line |
| `Shows, Performances & Concerts - Extra Section.html` | Shows section: venue own-site links only, no aggregators |
| `Train Stations Near Hotel - Extra Section.html` | Train stations section: walk times, negative-finding line |
| `Pickleball - Extra Section.html` | Pickleball section (the owner plays) |
| `Downtown Restaurants - Extra Section.html` | Historic downtown restaurants section |
| `Claude Inspiration - Extra Section.html` | Claude's inspiration note section |
| `Cities Gotchas - Extra Section.html` | City-specific gotchas section: construction, closures, quirks per city |
| `Guide Entry Counts.html` | Canonical min/max/exact count reference for every enforced count in the guide system — enforcement type and negative-finding line status. Lives at `Brain/Reference/Guide Entry Counts.html` (moved out of CORE RULES 2026-05-24 → Brain root → `Reference/` folder 2026-05-24). |
| `Skip List.html` | Skip List footnote section — appears last in guide; names venues skipped because already visited; small italic grey, no banner; ships only when the city has a skip list. |
| `Toolbar.html` | Shared navigation bar — required on every HTML page. Covers: mount div markup, data-depth (folder levels from Travel/), data-maxwidth (760 Trip Essentials / 940 Guides), how to add pages to the menu (edit toolbar.js ITEMS only). *(added 2026-05-29)* |
| `Brain/Reference/Navigation.html` | Moved out of CORE RULES → `Brain/Reference/` 2026-05-29; banner removed. Covers: the **shared footnote** (the sharing link carried across to the guides), prev/next arrow navigation for guide sequences (data-prev / data-next, chain integrity, guides_index wiring, inserting a new guide), the scroll progress bar, and the scroll button. *(added 2026-05-29)* |
| `Trip Essentials/Essentials Pages - Rules.md` | Behaviour of the Trip Essentials pages: which pages carry a search box, how search filters and collapses groups, and the no-results state (title + search box + message only; content, jump-nav, legends, index table, and shared footnote all hide). *(added 2026-05-29)* |

---

### Brain/Reference/Rule Dependencies.html — crib navigation aid (moved 2026-05-14 from CORE RULES → Reference/ 2026-05-24)

Helper file for cribs. When a rule is changed, the crib consults this map to find every other place that references the same icon, threshold, or concept — and updates each referenced location to match. **Direction is one-way: rule changes flow into this map; the map never flows back.** The CORE RULES HTML files are the source of truth. A rule is never modified to match what this map says. Not a rule. Not authoritative. Editable freely as long as it tracks the rules.

---

### Brain/Reference/ — files maintained by Claude after every session

| File | What it is |
|---|---|
| `Brain/Reference/Guide Entry Counts.html` | Canonical count reference — moved from `Brain/CORE RULES/` → `Brain/` root → `Reference/` 2026-05-24 (not a rule, a reference table; read-only banner removed). |
| `Brain/Reference/Rule Dependencies.html` | Crib navigation aid — moved from CORE RULES 2026-05-14, to `Reference/` 2026-05-24. Maps every icon/threshold/concept to every file that references it. |
| `Brain/Reference/Validator Index.html` | Living index of every check in `validate_itinerary.py` and `brain_check.py`, with ✅/❌/⚠️ status. Updated whenever a new check ships, per Rules for Claude.html § 10 item 5. |
| `Brain/Reference/Ship Checklist.html` | Pre-ship gate checklist — every guide build ends with this. Any "no" blocks ship. Moved out of CORE RULES 2026-05-24 (not a rule, a working checklist). Update §8 when sections are added/removed, §10 when new validator scripts are added. |
| `Brain/Reference/Cleanliness Checks.md` | 276 cross-cutting cleanliness rules (Categories A–U; highest number is 281 — rules 149–153 deleted). Moved from `Brain/mds/` 2026-05-27. Brain-check runs Category A at session start; validators use the rest. |
| `Brain/Reference/PDF Render Notes.md` | **Critical.** Full WeasyPrint PDF render guide: install commands, CSS override block, emoji font setup, staging directory, all 5 gotchas. Moved from `Brain/mds/` 2026-05-27. Read before every in-Cowork PDF render. |
| `Brain/Reference/Platforms.md` | Booking platform rules: which platforms are allowed, which are banned, direct-link requirements. Moved from `Brain/mds/` 2026-05-27. |
| `Brain/Reference/Separation Map.md` | Locator table: which CORE RULES file owns which rule. Use this to know where to look when a rule question comes up. Moved from `Brain/mds/` 2026-05-27. |
| `Brain/Reference/Change Cascade.html` | Reference map of what to update when a rule, format, or structure changes — which files cascade from which decisions. |
| ~~`Brain/Section Snippets.html`~~ | **Archived 2026-05-24** to `Travel/archive/`. Permanently banned — snippet files cause format drift when rules change. Read CORE RULES directly. `brain_check.py` hard-fails if any snippet/scaffold/template file is recreated under Brain/. |

---

### Brain/mds/ — Claude's reference files (5 files, fixed set)

No new files without the owner's explicit permission. These 5 are the complete set. (`PDF Render Notes.md`, `Cleanliness Checks.md`, `Platforms.md`, `Separation Map.md` moved to `Brain/Reference/` 2026-05-27.)

| File | What it is |
|---|---|
| `travel_map.md` | **This file.** Folder map + resource briefing. Read at session start. |
| `audit_log.md` | Rolling audit log. Updated after every guide build and audit pass. brain_check gates on staleness. |
| `Cities Gotchas.md` | Per-city known issues (construction, closures, quirks). Claude writes and maintains this as cities are researched. Feeds T6 ship gate. |
| `Cities Skip List.md` | Venues to skip per city (bad experience, permanently closed, not the owner's style). Claude writes and maintains. Used at research phase. |
| `decisions.md` | Non-trivial judgment call log — bans, demotions, retirements, significant trade-offs. Required by cleanliness_checks.md rule 128. Append new entries at the top. |

---

### Brain/scripts/doc_workshop_*.py — CORE RULES formatting validators (moved 2026-05-13 from Brain/CORE RULES/script/)

Two scripts that validate and repair the CORE RULES HTML files themselves. Run directly with `python3` — not through `guide_tools.py`.

| Script | What it does | When to run |
|---|---|---|
| `doc_workshop_validator.py` | Validates all CORE RULES HTML files against the canonical formatting rules (banner, h1, § headings, CSS, legacy class detection). Reports E-errors and W-warnings. | After any CORE RULES edit or formatting audit |
| `doc_workshop_fixer.py` | Rewrites non-conforming CORE RULES HTML files to the canonical shell: injects canonical CSS, fixes banner text, preserves body content. Run only on files the validator flags. **Never run blind.** | After validator identifies drift; confirm which files before running |

Source of truth for what "canonical" means: `Brain/Reference/Core Rules Formatting.html` § 1.

---

### Brain/scripts/ — validators and tools

All validators are accessed through `guide_tools.py` (single entry point). Run from the Travel root.

| Script | What it does | When to run |
|---|---|---|
| `guide_tools.py` | **Single entry point** for all validators. Commands: `start`, `brain-check`, `sweep-stray`, `validate`, `verify`, `verify-booking`, `photo`, `ship`, `pdf`, `validate-pdf`, `audit` | Always use this instead of calling scripts directly |
| `brain_check.py` | Session-start integrity check: required files exist, CLAUDE.md has required sections, no ghost references, audit log not stale. Run at every session start. | Session start + after any Brain edit |
| `validate_itinerary.py` | Full guide validator: 691-check cleanliness sweep, tour-first evidence, all ship gates | Before every ship |
| `autofix_itinerary.py` | Mechanically rewrites mis-filed booking boxes and common format drift | Before validate, when drift is detected |
| `verify_urls.py` | Checks all URLs in a guide are live and not redirecting | Before ship |
| `verify_booking_links.py` | Ship gate: booking link coverage + h1-match | Before ship |
| `audit_all_guides.py` | Sweep-all-guides audit helper — runs validators across every shipped guide and summarizes. | On demand during audit |
| `core_rules_checksums.json` | SHA-256 hashes for every CORE RULES file — feeds the CORE RULES integrity check in `validate_itinerary.py`. Regenerated by `update_core_rules_checksums.py`. | Never edited by hand |
| `update_core_rules_checksums.py` | Regenerates `core_rules_checksums.json` after an approved CORE RULES edit. | After approved a CORE RULES change |
| `render_pdf.py` | PDF render using headless Chromium (500px mobile viewport). **Does not run inside Cowork** — use from a normal terminal. For in-Cowork rendering, use WeasyPrint (see `Brain/Reference/PDF Render Notes.md`). | On demand |
| `validate_pdf.py` | PDF integrity check: page breaks, image loads, layout | After render |
| `sweep_stray_travel.py` | Enforces file location rule: Cowork files live in `Travel/`, mobile surface files in `Travel/On The Go/`. Catches stray files outside their designated root. | Session start + after file moves |
| `commons_photo.py` | Wikimedia Commons photo sourcing helper | During guide build |

### Brain/Reference/Guide Style.css

Shared stylesheet for all guides. **Source of truth.** Referenced by every guide HTML file as `../guide_v2.css` (one level up — never `../../Brain/Reference/Guide Style.css`, which breaks on GitHub Pages). A copy lives at `Guides/guide_v2.css` for GitHub Pages — whenever Brain/Reference/Guide Style.css is updated, copy it to Guides/ as well. Contains the full mobile-first layout, color system, section styling, and `@media print` rules. **Never edit without understanding the WeasyPrint override implications** (see `Brain/Reference/PDF Render Notes.md`).

### Brain/tests/ — retired

Folder no longer exists on disk (last documented empty 2026-05-11; gone by 2026-05-14). Was never referenced by any script or CORE RULES file. No action needed unless a real test suite gets added in the future, at which point a new folder can be created.

---

## Travel/On The Go/

Moved under `Travel/` on 2026-05-19. Only `Rules/` remains — Shopping Profile and To do list were removed on 2026-05-18.

- **Travel/On The Go/Rules/** — Active file: `on_the_go_rules_v27.md`. Archive subfolder holds v5–v26. Claude reads v27 at mobile session start; never edits without being asked.

When the user asks for the to-do list, read `Travel/To Do List/To_Do_List.md` — no second source to merge.

---

## What Claude owns vs what owner-managed

**Claude writes and maintains:**
- `CLAUDE.md`, `Brain/mds/*`, `Brain/scripts/*`, `Brain/Reference/Guide Style.css`
- `Brain/Reference/*`
- Individual guide files inside `Guides/{City}/` (during active builds only)

**owner-managed — Claude reads, edits only when explicitly asked:**
- `Guides/` (frozen after ship), `Trip Essentials/`, `Hotel Research/`, `To Do List/To_Do_List.md`
- `Icons Library/`
- Everything in `archive/` (sealed vault — never move anything in without explicit per-file permission)
- `Brain/CORE RULES/*.html` (apply rule changes only when approved a 🔧 Rules for Update proposal)

---

## Key rules to remember

- **CORE RULES always wins.** If CLAUDE.md and a CORE RULES file disagree, the HTML file wins. No exception.
- **Guides/ is frozen.** Never read, grep, or reference guide files unless when asked.
- **archive/ is a vault.** Never rm anything — archive to `Travel/archive/` and move on. No archive subfolders inside Guides/.
- **brain_check must pass 0 failures** before starting any guide build. Run it. Fix it. Then build.
- **WeasyPrint notes are critical.** Before any in-Cowork PDF render, read `Brain/Reference/PDF Render Notes.md` in full.
- **Cities Gotchas and Cities Skip List are yours.** You write and maintain them as you research cities.

---

*Updated by Claude: 2026-05-18 (deep audit pass) — (1) Bumped "Last updated" to 2026-05-18. (2) Added new "Brain/ root — other helper HTML files" section documenting `Guide Entry Counts.html` (CORE RULES is canonical; Brain root duplicate archived 2026-05-18), `Section Snippets.html` (copy-paste-ready HTML for error-prone sections), and `Validator Index.html` (living index of validator checks — was previously undocumented in the map). (3) Added three previously-undocumented scripts to the validators/tools table: `audit_all_guides.py`, `core_rules_checksums.json`, `update_core_rules_checksums.py`. (4) Archived 5 stale `validate_itinerary.py.*_bak` files + `.DS_Store` + `__pycache__/` from `Brain/scripts/` to `Travel/archive/`. (5) Stale references to `_DO_NOT_ARCHIVE.md` and `On Demand/_README.md` in the audit-history block below are noted but preserved — those files were retired and the references reflect the state at the time of the entry.*

*Updated by Claude: 2026-05-15 (deep audit pass) — (1) Named `shopping_profile_v2.md` in Shopping Profile entry (was vague). (2) Added two flight playlist gdocs to On The Go/ root (were completely undocumented). (3) Expanded Icons Library entry to name utility files (`icon_resources.md`, `_PREVIEW_all_icons.html`, `icon_picker_transport.html`) and source pack folders. (4) Corrected CLAUDE.md description — was overstated (claimed to contain DriftyCat, session ritual, rendering notes); corrected to reflect its actual role as a lean pointer/quick-reference file.*

*Updated by Claude: 2026-05-15 (audit pass) — (1) Added `On Demand/_style.css` to On Demand folder entry (exists on disk, was undocumented). (2) Added `README.md` to `To Do List/` entry (exists on disk, was undocumented). (3) Expanded `Trip Essentials/` to list actual files on disk — `Bend_Rentals.docx` surfaced as possibly misfiled (flag for the owner). (4) On The Go/ contents unverifiable from Cowork bash environment this session.*

*Updated by Claude: 2026-05-15 — (1) Added `Icon Order and Format.html` to CORE RULES table (was missing — it's the canonical authority for every icon, but wasn't listed). (2) Added `Tickets.html` to CORE RULES table (existed on disk, referenced in Rules Dependency Map, not documented here). (3) Added `Ship Checklist.html` to CORE RULES table (referenced in DriftyCat, not documented here). (4) Fixed `Trips/` entry: live tracker filename was `Data.html` in the map — actual file on disk is `Trips.html`, consistent with Core Rules § 4. (5) Fixed stale footer inside `Rule Dependencies.html` — still said `Brain/CORE RULES/`; corrected to `Brain/` (moved 2026-05-14).*

*Updated by Claude: 2026-05-12 — (1) Updated `Guides/` entry to document `guides_index.html` (master guide index, update on every ship) and `Guide Style.css` (copy of Brain CSS for GitHub Pages). (2) Updated `Brain/Reference/Guide Style.css` section to note correct per-guide CSS path (`../guide_v2.css`), the wrong path that breaks GitHub Pages (`../../Brain/Reference/Guide Style.css`), and the sync requirement. (3) Fixed `lisbon_v3.html` CSS path from broken `../../Brain/Reference/Guide Style.css` to `../guide_v2.css`. (4) Synced `Guides/guide_v2.css` from updated `Brain/Reference/Guide Style.css`.*

*Updated by Claude: 2026-05-24 (MD audit) — Updated `On The Go/Rules/` entry: active file is now `on_the_go_rules_v27.md`; archive holds v5–v26 (v11–v26 were in active folder, archived today). Marrakech guide uses `index.html` filename (inconsistent with other guides — logged as ❓ for the owner).*

*Updated by Claude: 2026-05-11 — (1) Added `Brain/CORE RULES/script/` section. (2) Added `Cities Gotchas - Extra Section.html` to CORE RULES table (was in folder but missing from map). (3) Added `Brain/mds/decisions.md` section (new file, rule 128 additive). (4) Added `_DO_NOT_ARCHIVE.md` and `On Demand/_README.md` to CORE RULES table (both existed on disk, neither was documented). (5) Updated `On The Go/Rules/` description — active file is `on_the_go_rules_v11.md` (created 2026-05-11); v5–v10 in archive/.*
