# Travel — entry point for Claude

**Source of truth: `Brain/CORE RULES/Rules for Claude.html`** — read it at every session start using the `Read` tool. It defines everything and points to every other authoritative file in `Brain/CORE RULES/`. When this file and Rules for Claude.html disagree, Rules for Claude.html governs.

**CORE RULES files are plain HTML** — use the `Read` tool directly on the file path. No Drive MCP, no doc_id needed.

---

**📖 Before building any guide:** Read the planning and formatting instructions in `Brain/CORE RULES/` first — every time. Follow what's in the rules; never invent structure or format. When anything is unclear mid-build, park the question in `Travel/To Do List/To_Do_List.md` (❓ Questions for Dani) and keep building. Never block.

**🎨 HTML formatting:** All HTML files follow the formatting rules in `Travel/Universal Formatting Rules/Universal Formatting Rules - Rules.html`. Read it before creating or editing any HTML.

**🧪 Validator work:** Read the procedure in `Brain/CORE RULES/Rules for Claude.html` § 4 before any validator task. Validator check comes before any guide fix — always.

**🚫 File location — two-crib rule:** Two environments, two root folders. Every file belongs to one:
- **Cowork surface** → `Travel/` (guides, brain, scripts, specs, trip data, formatting rules, essentials). All Cowork file creation stays here.
- **Mobile surface** → `Travel/On The Go/` (on-the-go rules). Mobile can only ADD files — Cowork tidies periodically.

**🗺 Trip updates:** Any request to update or edit trip data goes to `Travel/Trips/Trips.html` — read `README.md` there before making any changes.

**🗂 Mistakes go to archive:** Any file or folder created in the wrong place by Claude gets moved to `Travel/archive/`. Never `rm`, never left in place.

**🔌 Connectors:** Viator and TripAdvisor are always MCP connectors — never web search for these. Browser tasks use Claude in Chrome MCP.

**📚 Key references — read before using:**
- **URL failures during a guide build** → `Brain/CORE RULES/Links.html`
- **Building a PDF** → `Brain/mds/render_pdf_weasyprint_notes.md`
- **What Claude can do** → `Brain/Claude to keep updated/Claude_Capabilities.html`

**✈️ Travel planning:** Before any task involving flights, hotels, house rentals, or car rentals — read the on-demand files in `Brain/CORE RULES/On Demand - Don't Ship in Guide/` first. For hotels, also check `Travel/Hotel Research/` for previous research before starting anything new.

---

## How this workspace is organized

This folder is the Cowork workspace. Two subfolders:

- **`Brain/`** — contains the brain. `Brain/CORE RULES/` holds the authoritative `.html` files. Everything else under `Brain/` (markdown files in `Brain/mds/`, CSS, scripts, logs) is operational scaffolding — Claude-maintained, not authoritative for rules.

- **`Guides/`** — shipped output only. Frozen until Dani asks. Never read, grep, audit, or reference any file under `Guides/` unless Dani explicitly names it. Old guides are finished artifacts, not references or templates.

**Vocabulary:** when Dani says *"the HTML," "the HTML files," "fix the {name} HTML,"* she means `Brain/CORE RULES/{name}.html`. That's the live file.

---

## Session ritual

Runs before the first response, every Cowork session. Auto-authorized — no asking permission. Full detail in `Brain/CORE RULES/Rules for Claude.html` § 1.

1. Run `python3 Brain/scripts/guide_tools.py start`
2. Read `Travel/CLAUDE.md`
3. Read `Brain/mds/travel_map.md`
4. Read `Brain/CORE RULES/Rules for Claude.html`
5. Open `Brain/mds/PLATFORMS.md` — surface any ❌ failed or ⏳ retry platforms
6. Read `Brain/Claude to keep updated/Claude_Capabilities.html` — announce relevant connectors

**Self-diagnostic:** when a draft contains *"Want me to fetch the rules doc?", "Should I read the brain first?"* — the ritual was skipped. Stop. Run it. Re-draft.

---

## Guide-build phases — required reads

A guide build moves through six phases. Each has a mandatory read list. Full phase definitions live in `Brain/CORE RULES/Guide Structure.html` § 1. Reading these files in order is non-optional — skipping is how guides drift and get rebuilt.

**Phase 0 — Session start.** Done by the Session ritual above.

**Build-state tracker.** At the start of every guide build, create `Guides/{City}/_build/build_state.md` with a checkbox for each Phase 1-5 required file. Flip each `[ ]` to `[x]` as the build progresses. Format is in `Brain/CORE RULES/Guide Structure.html § 1`.

**Phase 1 — Pre-build orientation** (before researching any city):
- `Brain/CORE RULES/Guide Structure.html`
- `Brain/CORE RULES/Stops Structure.html`
- `Brain/CORE RULES/Hotel Banner.html`
- `Brain/CORE RULES/Trip at a Glance.html`

**Phase 2 — Day shape** (before locking any day):
- `Brain/CORE RULES/Day Structure.html`

**Phase 3 — Per-stop build** (every stop in the itinerary):
- `Brain/CORE RULES/Tickets.html` — for any ticketed stop (🎟)
- `Brain/CORE RULES/Motion Rule.html`
- `Brain/CORE RULES/Icon Order and Format.html`
- `Brain/CORE RULES/Photos Rules.html`
- `Brain/CORE RULES/Links.html`

**Phase 4 — Per-section build** (each extra section that ships):
- The matching `*Extra Section*.html` file
- Plus `Motion Rule.html`, `Icon Order and Format.html`, `Links.html` as needed

**Phase 5 — Ship gate** (before output):
- Run the Pre-Ship Checklist end-to-end (`Brain/Claude to keep updated/Pre-Ship Checklist.html`). Any "no" blocks ship.
- Validator passes (`Brain/scripts/validate_itinerary.py`)
- Every extra section is populated or carries its negative-finding line

**Self-diagnostic:** when a guide build starts and Phase 1-4 reads haven't happened — the build is already drifting. Stop, do the reads, start the build over.

---

## Parking surface

One file. Three sections. Everything lives in `Travel/To Do List/To_Do_List.md`. Full rules in § 5 of Rules for Claude.html.

- **✈️ My Tasks** — Dani's private tasks. Read only — never append.
- **🔧 Rules for Update** — rule proposals. Propose → approval in same session → apply to matching `Brain/CORE RULES/*.html` → delete item.
- **❓ Questions for Dani** — mid-build questions. Park and keep building.

**Single to-do list (2026-05-18):** the mobile `On The Go/To do list/` was removed. `Travel/To Do List/To_Do_List.md` is now the only place — no second source to merge.

---

## Archive rules

Full rules in `Brain/CORE RULES/Rules for Claude.html` § 3. Two walls:

- **Wall 1 — Auto-archive before every new version.** Pre-authorized. Before creating a new version of any file, move the current one to `Travel/archive/` first. Archive destination is always `Travel/archive/` — never per-folder subfolders.
- **Wall 2 — Archive is read-locked.** Never read archive files without explicit per-file permission. Archives preserve history, not inform builds.

**The word is ARCHIVE.** Never `rm`. When something needs to go away: `mv` to `Travel/archive/`, done.

---

## Rendering guide PDFs in Cowork

The canonical renderer is `Brain/scripts/render_pdf.py` (Playwright + headless Chromium). It does not run inside Cowork. Run it from a normal terminal.

When asked to render a PDF from inside a Cowork session, use WeasyPrint. Read `Brain/mds/render_pdf_weasyprint_notes.md` before every WeasyPrint render — it has the full recipe, CSS override block, and all gotchas.

---

## Behavioral rules

Full detail in `Brain/CORE RULES/Rules for Claude.html` § 3. Key points:

- No preamble, no option menus, no pop-up questions. Pick what the rules point to and move.
- Decisive over hesitant. When the task scope is clear, run end-to-end.
- No permission-asking on already-authorized actions. Do it and announce briefly.
- Connector usage stays authorized across the session — no re-asking on every action.

---

## ⚠️ DriftyCat — things that keep breaking

One-line tripwires. Full rule for each lives in its CORE RULES HTML file.

- ⚠️ **Icon format and row order — read the canonical file.** `Brain/CORE RULES/Icon Order and Format.html` — § 1 = 🏨 day boundary · § 2 = universal row order (positions + exact format per icon) · § 3 = section header icons + per-section sub-rows · § 4 = train icons (🚄 vs 🚆). Read before writing any stop box.
- ⚠️ **Tour-first ALWAYS.** Viator / GetYourGuide / TripAdvisor before skip-the-line, before venue site. Bar: 4.5+★ · ≥6 reviews. Full rule: `Tours - Extra Section.html`.
- ⚠️ **Zero money in shipped guides.** No `$`, `€`, `£`, `¥`, `~`, no ISO codes — ever.
- ⚠️ **No placeholders.** `{TBD}` / `{TODO}` / "fill in later" = fabrication.
- ⚠️ **No fabrication.** Every fact live-verified this build. Memory from past builds is not a source.
- ⚠️ **Every link live-verified — every time.** Including every edit inside a session. Bot-blocked platforms verify via `site:` search-result inspection, not direct fetch.
- ⚠️ **Photos in same pass as stop research.** Never deferred.
- ⚠️ **Wide wins over detail (stop photos).** Facade > interior. Wide > close-up.
- ⚠️ **No full EoI cards in Trip at a Glance day-card area.** Day-card grid is days-only. Compact extras navigation pills are permitted — navigation infrastructure, not EoI cards.
- ⚠️ **Don't read past guides.** `Guides/` is output, not reference. Only open a guide file when Dani explicitly names it.
- ⚠️ **CORE RULES folder is Dani-only.** No `mv` / `cp` / `rm` / rename / archive / create. Never touch the folder.
- ⚠️ **No new files in `Brain/mds/` without explicit permission.** 10 files — that is the complete set.
- ⚠️ **"List fixes" ≠ audit.** Audit fires only on the word "audit." A "list fixes" ask surfaces what is already known broken.
- ⚠️ **Absence of rule = don't ship.** When no rule authorizes the format about to ship, that format does not ship.
- ⚠️ **Agent prompts are mini-rules.** Every rule the agent's output must respect must be written into the prompt.
- ⚠️ **🚕 Uber time = Google Maps Driving mode. Full stop.** Maps driving time is the number. No ride-share APIs or estimators.
- ⚠️ **No hedging language in factual rows.** Every 🏛/🚶/🚕/⏰/📍/🎟 row comes from a confirmed source. Full banned list in Rules for Claude.html § 6.
- ⚠️ **Rule docs state what IS — the validator enforces it.** Positive rules only, no prohibition banners, no bad examples.
- ⚠️ **Punt-detection — run the tool first.** *"I can't access Viator," "ratings need manual lookup"* — all wrong. Run the tool first.
- ⚠️ **Validator check before any guide fix.** Write the check in `validate_itinerary.py` first; fix the guide after. Full rule: § 4 of Rules for Claude.html.
- ⚠️ **Calendar hotel blocks — end = checkout + 1 day.** Google Calendar all-day events use exclusive end dates — the block displays through end_date − 1. Always set end date to the day after checkout, or it appears to end one day early.

---

## On-demand documents

Run only when explicitly asked. Output goes to `Travel/Trips/Trips.html` — never auto-ships in a guide. Full rules in each CORE RULES HTML file.

- `Brain/CORE RULES/On Demand - Don't Ship in Guide/Weather - On Demand.html`
- `Brain/CORE RULES/On Demand - Don't Ship in Guide/Delta - On Demand.html`
- `Brain/CORE RULES/On Demand - Don't Ship in Guide/Hotels & Rentals - On Demand.html`
- `Brain/CORE RULES/On Demand - Don't Ship in Guide/Car Rentals - On Demand.html`

---

## Shopping

When Dani asks to find, buy, or research any product — read the shopping profile at **`Travel/shopping_profile_v2.md`** before responding. (Moved from `On The Go/Shopping Profile/` to the Travel root on 2026-05-18 — single file at Travel root, no subfolder.)

---

## Two-crib architecture

Dani uses Claude across two environments sharing the same Drive workspace:

| | Cowork (desktop) | On The Go (mobile) |
|---|---|---|
| **Root folder** | `Travel/` | `Travel/On The Go/` |
| **Capabilities** | Full read/write/edit/delete | Read + add files only — cannot edit or delete |
| **Entry point** | `Travel/CLAUDE.md` | `Travel/On The Go/Rules/on_the_go_rules_v11.md` |
| **Where heavy work happens** | ✅ Guides, audits, cleanup, scripts | ❌ Fast lookups while moving |

**Why folders (not single files) for shared resources** like Shopping Profile and on-the-go rules: the mobile crib can only ADD versions, so files accumulate over time. Cowork periodically tidies up. Both cribs read from the same folder — update one place, both pick it up.

---

## Quick Reference

### CORE RULES HTML file index

| File | Purpose |
|---|---|
| `Rules for Claude.html` | Claude behavior — §1 Session start · §2 Authority · §3 Task execution · §4 Building a guide · §5 Parking surface · §6 DriftyCat · §7 On-demand · §8 Audit · §9 Close-out |
| `Guide Structure.html` | Section order + EoI shipping (§1) · day numbering (§2) · cross-link anchors (§3) · build discipline (§4) · what never ships (§5) · Cities Gotchas data file (§6) · transit banners (§7) · free self-visit box (§8) · guide directory layout (§9) |
| `Day Structure.html` | Day-block shape, stop count, geographic clustering, bookends |
| `Trip at a Glance.html` | Navigation card spec, day-order rule |
| `Hotel Banner.html` | Title page anatomy, single-name rule |
| `Stops Structure.html` | Stop selection criteria, day-glance labels, stop types, train day pattern, stop flags, ticket waterfall |
| `Motion Rule.html` | Walk-vs-ride threshold |
| Tours.html | ~~Retired 2026-05-20~~ — moved to Travel/Retired Rules/. Tours now governed by Tours - Extra Section.html only. |
| `Tours - Extra Section.html` | Tours section detail — what ships, rating bar, min count per source (Viator/GYG/TripAdvisor), entry format |
| `Tickets.html` | Ticket waterfall — official site → Viator → GetYourGuide → Tiqets; ticket box format and rating bar |
| `Photos Rules.html` | Wikimedia Commons sourcing, licenses, harvest workflow |
| `Links.html` | Link verification, 📖 Wikipedia spec, 📍 Google Maps spec |
| `Icon Order and Format.html` | **Icon canonical reference** — § 1: 🏨 day boundary marker · § 2: universal row order (positions + exact format per icon, in one table) · § 3: section header icons (in guide order, with per-section description char limits in the sub-rows) · § 4: train icons (🚄 vs 🚆) |
| `Stops Structure.html` | Discovery/curation rules: 4-step research flow, quality bar, trusted sources, stop selection |
| `Brain/Claude to keep updated/Emoji Library.html` | Locked-out emoji list |
| `Food Delivery - Extra Section.html` | Food delivery section: platform availability, preference order, delivery rows in Cappuccino, exception approval |
| `Restaurants Near Hotel - Extra Section.html` | — |
| `Downtown Restaurants - Extra Section.html` | — |
| `Michelin Restaurants - Extra Section.html` | — |
| `Cappuccino - Extra Section.html` | — |
| `Local Tastes - Extra Section.html` | — |
| `Shows, Performances & Concerts - Extra Section.html` | — |
| `Day Trips by Train - Extra Section.html` | Train day-trips only |
| `Getting Around - Extra Section.html` | — |
| `Train Stations Near Hotel - Extra Section.html` | Closest station per mode; 🚄 vs 🚆 glyph rule |
| `Weekly Closures - Extra Section.html` | — |
| `Cities Gotchas - Extra Section.html` | — |
| `Pickleball - Extra Section.html` | — |
| `Claude Inspiration - Extra Section.html` | — |
| `Skip List.html` | Footnote (last in guide) naming venues skipped because already visited — small italic grey, no banner; ships only when the city has a skip list |
| `Brain/CORE RULES/On Demand - Don't Ship in Guide/Hotels & Rentals - On Demand.html` | On demand only |
| `Brain/CORE RULES/On Demand - Don't Ship in Guide/Delta - On Demand.html` | On demand only |
| `Brain/CORE RULES/On Demand - Don't Ship in Guide/Car Rentals - On Demand.html` | On demand only |
| `Brain/CORE RULES/On Demand - Don't Ship in Guide/Weather - On Demand.html` | On demand only |

### Brain root helper files — maintained by Claude after every session

Three files that must stay current. Update before the session ends whenever relevant changes were made — no asking permission. Full rule in `Brain/CORE RULES/Rules for Claude.html` § 10 item 5.

| File | What to update |
|---|---|
| `Brain/Claude to keep updated/Count Reference.html` | Any count, minimum, or threshold that changed this session (section minimums, char caps, walk caps, etc.) |
| `Brain/Claude to keep updated/Validator Coverage.html` | Every new check added to `validate_itinerary.py` or `brain_check.py` |
| `Brain/Claude to keep updated/Rules Dependency Map.html` | Any icon, threshold, or shared concept that moved, was renamed, or changed scope |
| `Brain/Claude to keep updated/Pre-Ship Checklist.html` | §8 when sections are added or removed; §10 when new validator scripts are added |
| ~~`Brain/Section Snippets.html`~~ | **Archived 2026-05-24.** Permanently banned — causes drift when rules change. `brain_check.py` hard-fails on recreation. |

### Validators

| Script | Job |
|---|---|
| `guide_tools.py ship` | Single entry point — chains validate + verify + verify-booking |
| `brain_check.py` | Brain integrity — required sections, required files, ghost references |
| `validate_itinerary.py` | Guide structure — stop blocks, box shapes, motion rule, currency |
| `verify_urls.py` | Link health — every URL returns 200 + ≥100 words editorial prose |
| `verify_booking_links.py` | Subject drift — booking link `<h1>` matches stop subject |
| `commons_photo.py` | Photo resolution — Commons URLs to 800px thumbs |
| `autofix_itinerary.py` | Guide auto-repair — rewrites mis-filed booking boxes. Run directly: `python3 Brain/scripts/autofix_itinerary.py {guide}` |
| `sweep_stray_travel.py` | Stray-file enforcement — scans Downloads/Desktop/Documents/Drive root |
| `render_pdf.py` | PDF render — headless Chromium 500px (on-demand only) |
| `validate_pdf.py` | PDF integrity — page-break, image-load, layout (on-demand only) |

### Glossary

| Symbol | Meaning |
|---|---|
| 🏨 | Day boundary marker — `🏨 FROM HOTEL` opener / hotel return at day close |
| 📒 | Stop summary / show description (outside the blue box) |
| 📅 | Tour box (guided tour booking row) |
| 🎟️ | Ticket / show booking link |
| 🚐 | Hotel pickup / drop-off (tour-coach transit) |
| 📍 | Address — always a clickable Google Maps link |
| 🚩 | Guided Tour Stop title icon (CSS-rendered) |
| 🎒 | Self-Guided Stop title icon (CSS-rendered) |
| 🚆 | Regular / regional / commuter train |
| 🚄 | High-speed train ONLY |
| 📖 | Wikipedia link (English Wikipedia only) |
| 🍽️ | Cuisine type (Michelin) · also Downtown Restaurants section header |
| ⭐ | Michelin star tier · also Michelin section header |
| 🎭 | Shows section header |
| 🍮 | Local Tastes section header |
| ☕ | Cappuccino section header |
| 🫕 | Restaurants Near Hotel section header |
| 🚌 | Getting Around section header |
| 🚕 | Ride apps glyph |
| 🚎 | Tram glyph |
| 🚊 | Metro glyph (only planned by request) |
| ⛲️ | Day Trips section header |
| 🗞️ | Day Trip destination intro |
| 🎫 | Day Trip booking link |
| 🗓️ | Weekly Closures section header |
| 🏓 | Pickleball section header (CA+AZ only) |
| ❗ | Cities Gotchas section header |
| ✈️ | Delta / flights — research only, never in itinerary |
| 🚗 | Car Rentals — on-demand research only, never in itinerary |
| 🚶 | Walking time on a transit line |
| 🏛️ | Opening hours |
| ⏰ | Typical visit time |
| ⏳ | Tour duration |
| 🕐 | Tour start time |
| 👥 | Max group size for a tour |
| ⚠️ | Stop flag — warning callout (inline inside stop boxes; distinct from the ❗ Cities Gotchas section header) |
| Extra Section | Any guide section NOT inside a day block. Lives in EoI. |
| One parking surface | `To_Do_List.md` — three sections: ✈️ My Tasks · 🔧 Rules for Update · ❓ Questions for Dani |
