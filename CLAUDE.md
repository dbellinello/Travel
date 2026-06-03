# Travel — entry point for Claude

---

## ⚡ READ THIS FIRST — NO ASKING, EVER

**All tool use is pre-authorized for the entire session.**
Web searches, URL fetches on any domain, Wikipedia, Wikimedia Commons, Chrome MCP, any connector (Viator, TripAdvisor, Booking, Resy, StubHub, Expedia, any), file reads, script runs — execute immediately. Never ask, never confirm, never announce intent and wait for a reply. No URL requires per-site authorization. The only exception: a destructive irreversible action on a non-build file gets a one-line confirm.

**Guide builds require zero clarification.**
When asked to build a guide, all requirements are fully specified in the Brain files. Begin immediately. Run the full build — ritual → reads → research → build → validate → ship — without stopping. Never wait for confirmation.

**Guide builds — HARD GATE: zero HTML before reads.**
Before writing a single line of guide HTML, read in order:
1. `Brain/CORE RULES/Rules for Claude.html`
2. `Brain/CORE RULES/Guide Structure.html`
3. All Phase 1+2 files listed in the Guide build phases section below

The format lives in `Brain/CORE RULES/` — never in memory, never in past guides. Writing HTML before these reads = wrong format. Self-diagnostic: HTML exists and Phase 1+2 boxes are unchecked in `_build/build_state.md` → stop, delete the HTML, do the reads, restart from scratch.

**These phrases are banned. Any of these in a draft = stop, delete, act instead:**
- "Want me to…" / "Should I…" / "Shall I…"
- "Would you like me to…" / "Do you want me to…"
- "Let me know if you want me to…"
- "Happy to… if you'd like" / "I can… if that helps"
- "Just say the word and I'll…" / "Ready when you are"
- "Want me to fetch the rules doc?" / "Should I read the brain first?"

**Three moves replace permission-asking:**
1. Do it and announce briefly — "Reading Platforms.md…" then do it.
2. Surface a real fork — "Two paths: A keeps X, B drops it. Which?" (expects a choice, not "yes")
3. Confirm destructive/irreversible only — "About to publish X — confirm?"

**Self-diagnostic:** banned phrase in draft = violation. Delete it. Take the action.

---

## Source of truth

`Brain/CORE RULES/Rules for Claude.html` — governs everything. When this file and Rules for Claude.html disagree, Rules for Claude.html wins. Read it at every session start with the `Read` tool directly — no Drive MCP, no doc_id.

---

## Session ritual

Runs before the first response, every session. Auto-authorized — no asking.

1. `python3 Brain/scripts/guide_tools.py start`
2. Read `Brain/mds/travel_map.md`
3. Read `Brain/CORE RULES/Rules for Claude.html`
4. Check `Brain/Reference/Platforms.md` — note any ❌ or ⏳ in opening message, do not block
5. Read `Brain/Reference/Connectors.html` — know what's available, do not announce or prompt
6. Check `Brain/mds/audit_log.md` — if last entry > 7 days ago, add one line: "Last audit: {date} ({N} days ago)." Continue immediately.

---

## Routing

| Task | Go to |
|------|-------|
| Trip data update | `Travel/Trip Essentials/Trips.html` — read `Trips - Rules.md` first |
| Flights / hotels / rentals / weather | Read matching file in `Travel/On Demand/` first |
| Shopping request | Read `Travel/shopping_profile_v2.md` first |
| URL failure in a build | `Brain/CORE RULES/Links.html` |
| PDF rendering | `Brain/Reference/PDF Render Notes.md` |
| Connector capabilities | `Brain/Reference/Connectors.html` |
| Validator work | Read `Rules for Claude.html § 4` before touching anything |

**File location:** all Cowork files stay inside `Travel/`. Mobile surface files in `Travel/On The Go/`.
**Archive:** never `rm`. Move to `Travel/archive/`. Always. Pre-authorized — no asking.
**CORE RULES:** never edit `Brain/CORE RULES/` without explicit per-session approval.
**Guides/:** frozen. Never read, grep, or reference any file there unless explicitly named.
**Connectors:** already configured. Do not prompt to connect, suggest connectors, or search the registry.
**Vocabulary:** when the user says "the HTML," "fix the {name} HTML" → means `Brain/CORE RULES/{name}.html`.

---

## Guide build phases

Full spec in `Brain/CORE RULES/Guide Structure.html`. **Do not write a single line of HTML before Phase 1 + 2 reads are done.**

**First action of any build — create the build-state tracker:**
`Guides/{City}/_build/build_state.md` with a checkbox `[ ]` for every Phase 1–6 file. Flip each to `[x]` when read or completed. The validator and ship gate read this file — an unchecked Phase 5/6 = not done.

- **Phase 1** — `Links.html` · `Photos Rules.html` · `Brain/Reference/Connectors.html` · `Brain/Reference/Platforms.md`
- **Phase 2** — `Guide Structure.html` · `Stops Structure.html` · `Hotel Banner.html` · `Trip at a Glance.html` · `Brain/Reference/Toolbar.html` · `Brain/Reference/Navigation.html`
- **Phase 3** — `Day Structure.html` (before locking any day)
- **Phase 4** — `Tickets.html` · `Motion Rule.html` · `Icon Order and Format.html` (per stop)
- **Phase 5** — matching `*Extra Section*.html` for each section (re-read at start of each)
- **Phase 6** — `Ship Checklist.html` · validator 0 failures · ship gate

**City name only** → look in `Trips.html`, use hotel + dates there.
**City + day count** → skip Trips.html, run hotel research, build for stated day count.
Dates never ship in a guide. Always Day 1 / Day 2 / Day N. Never ask for dates.

---

## Research workflow — follow this order, every build

**Before researching anything** — Phase 1 reads must be done: `Links.html` · `Photos Rules.html` · `Brain/Reference/Connectors.html` · `Brain/Reference/Platforms.md`. These define the tools and rules. Skipping them = building without a method.

**Tours (always MCP first — never start with web search):**
1. Viator MCP: `search_experiences` → `get_experience_details`. This is always step 1.
2. GetYourGuide: `site:getyourguide.com {city} {attraction} tour` (no MCP connector exists)
3. TripAdvisor MCP: `search_experiences`
- Bar: 4.5+★ · ≥6 reviews. Full rules in `Tours - Extra Section.html`.

**Photos (Wikimedia Commons only — one source, one method):**
1. Find the filename: WebSearch `site:commons.wikimedia.org {stop name} {city}`
2. Resolve the URL: `python3 Brain/scripts/commons_photo.py "File:{filename}"`
3. Never direct-fetch commons.wikimedia.org — it's blocked. Never use Google Images or Unsplash.

**Links and verification:**
- Every URL live-verified before it ships — including every edit inside a session.
- Platforms marked ⚡ or ❌ in `Platforms.md`: skip web_fetch entirely → `site:{domain}` WebSearch.
- When web_fetch fails on anything else → Chrome MCP (`navigate` + `get_page_text`) immediately.
- Never ask "may I access {domain}?" — pre-authorized, execute.

**Stop research (trusted sources only):**
- Wikipedia (`en.wikipedia.org`) · Fodor's · Rick Steves · National Geographic Travel · Rough Guides · Atlas Obscura · official tourism boards
- No random blogs, no affiliate lists, no AI-generated SEO content, no content farms — regardless of Google ranking.
- Check `Brain/mds/Cities Skip List.md` for the city before picking any stop.

---

## Behavioral rules

Full detail in `Brain/CORE RULES/Rules for Claude.html` § 3. The short version is at the top of this file. Key points:

- No preamble, no option menus, no pop-up questions. Pick what the rules point to and move.
- Decisive over hesitant. When the task scope is clear, run end-to-end.
- No permission-asking on already-authorized actions. Do it and announce briefly.
- Connector usage stays authorized across the session — no re-asking on every action.
- "Delete" / "remove" / "clean up" = ARCHIVE. Move to `Travel/archive/`. Never `rm`.

---

## ⚠️ DriftyCat — things that keep breaking

One-line tripwires. Full rule for each in its CORE RULES HTML file.

- ⚠️ **Working-surface drift = fix immediately, no approval.** Any file outside `Brain/CORE RULES/` that drifts from a CORE RULES rule — fix it in the same pass. CORE RULES is always the authority; working-surface files follow. No questions, no parking. Full rule: `Rules for Claude.html § 3`.
- ⚠️ **After any CORE RULES approval — work the cascade before announcing done.** Read `Brain/Reference/Change Cascade.html`, work every ✅ step for that change type, regenerate checksums, run doc_workshop_validator. A CORE RULES change without its cascade is half-done. Full rule: `Rules for Claude.html § 3 + § 5`.
- ⚠️ **No AskUserQuestion — ever.** The Cowork popup is never invoked for any Travel task. Start immediately. Full rule: `Rules for Claude.html § 4`.
- ⚠️ **Tour-first always.** Viator MCP → GYG → TripAdvisor before venue site. Bar: 4.5+★ · ≥6 reviews.
- ⚠️ **Zero money in shipped guides.** No `$` `€` `£` `¥` `~` or ISO codes — ever.
- ⚠️ **No fabrication.** Every fact live-verified this build. Memory from past builds is not a source.
- ⚠️ **No placeholders.** `{TBD}` / `{TODO}` / "fill in later" = fabrication.
- ⚠️ **Every link live-verified — every time.** Including every edit inside a session.
- ⚠️ **Photos in same pass as stop research.** Never deferred.
- ⚠️ **Wide wins over detail (stop photos).** Facade > interior. Wide > close-up.
- ⚠️ **Icon format — read the canonical file.** `Icon Order and Format.html` before any stop box.
- ⚠️ **Validator before "done" — every scope.** Any session touching guide HTML runs validator to 0 failures. Scope of change is not an exemption.
- ⚠️ **Validator check before any guide fix.** Write the check first; fix the guide after.
- ⚠️ **Don't read past guides.** `Guides/` is output, not reference or format template.
- ⚠️ **No hedging in factual rows.** "typically open" / "usually takes" / "approximately" = banned. Look it up or omit.
- ⚠️ **🚕 ride time = Google Maps Driving mode.** No ride-share APIs, no estimators.
- ⚠️ **One archive — `Travel/archive/` only.** Never create a subfolder archive anywhere else.
- ⚠️ **guides_index.html — update on every ship, same pass.** Five steps: new card + predecessor/successor data-guide-next/prev + counts + toolbar data-prev/data-next + map pin (see next rule).
- ⚠️ **Map pins — add on every ship, same pass.** European guides → add pin to `Trip Essentials/Europe Map.html`; US guides → add pin to `Trip Essentials/US Map.html`. Entry format: `['CityName', lon, lat, '../Guides/City/file.html']` in the `PINS` array. Ship gate blocks if pin is missing.
- ⚠️ **Punt-detection.** "I can't access Viator" / "ratings need manual lookup" = wrong. Run the tool. Chrome MCP bypasses bot-blocks.
- ⚠️ **No full EoI cards in Trip at a Glance day-card area.** Days-only grid. Compact nav pills permitted.
- ⚠️ **Day count in prompt = trip not in Trips.html.** "Amsterdam" → look in Trips.html. "Amsterdam, 4 days" → skip lookup, run hotel research.
- ⚠️ **Calendar hotel blocks — end = checkout + 1 day.** Google Calendar all-day events use exclusive end dates.
- ⚠️ **Resuming a build — read `build_state.md` first.** If Phase 5 unchecked, the guide is not done.
- ⚠️ **No new files in `Brain/mds/` without explicit permission.** Fixed set of 5 files.
- ⚠️ **Absence of rule = don't ship.** No rule authorizes it → it doesn't ship.
- ⚠️ **Agent prompts are mini-rules.** Every rule the agent's output must respect goes in the prompt.

---

## On-demand documents

Run only when explicitly asked. Output goes to `Travel/Trip Essentials/Trips.html` — never auto-ships in a guide.

- `On Demand/Weather - On Demand.html`
- `On Demand/Delta - On Demand.html`
- `On Demand/Hotels & Rentals - On Demand.html`
- `On Demand/Car Rentals - On Demand.html`

---

## Shopping

When asked to find, buy, or research any product — read `Travel/shopping_profile_v2.md` before responding.

---

## Two-crib architecture

Two environments, same Drive workspace:

| | Cowork (desktop) | On The Go (mobile) |
|---|---|---|
| **Root folder** | `Travel/` | `Travel/On The Go/` |
| **Capabilities** | Full read/write/edit/delete | Read + add files only |
| **Entry point** | `Travel/CLAUDE.md` | `Travel/On The Go/Rules/on_the_go_rules_v27.md` |

---

## Quick Reference

### CORE RULES HTML file index

| File | Purpose |
|------|---------|
| `Rules for Claude.html` | Master behavior doc — session ritual, authority, task execution, build discipline, parking, DriftyCat, audit, close-out, calendar |
| `Guide Structure.html` | Section order, EoI shipping, cross-link anchors, build discipline, guide directory layout |
| `Day Structure.html` | Day-block shape, stop count, geographic clustering, bookends |
| `Trip at a Glance.html` | Navigation card spec, day-order rule |
| `Hotel Banner.html` | Title page anatomy, single-name rule |
| `Stops Structure.html` | Stop selection criteria, stop types, train day pattern, ticket waterfall, discovery/curation rules |
| `Motion Rule.html` | Walk-vs-ride threshold |
| `Tickets.html` | Ticket waterfall format, ticket box format, rating bar |
| `Photos Rules.html` | Wikimedia Commons sourcing, licenses, harvest workflow |
| `Links.html` | Link verification, Wikipedia spec, Google Maps spec |
| `Icon Order and Format.html` | Canonical icon reference — row order, format per icon, section header icons, train icons |
| `Skip List.html` | Footnote for already-visited venues — ships only when city has a skip list |
| `Tours - Extra Section.html` | Tours section — source pool, rating bar, per-source minimums, entry format |
| `Getting Around - Extra Section.html` | Getting around section — tram subsection templates, transit operators |
| `Weekly Closures - Extra Section.html` | Weekly closures — recurring patterns only |
| `Local Tastes - Extra Section.html` | Local tastes — city-specific only |
| `Food Delivery - Extra Section.html` | Food delivery — platform availability, preference order |
| `Michelin Restaurants - Extra Section.html` | Michelin section — format, booking rules |
| `Restaurants Near Hotel - Extra Section.html` | Restaurants near hotel section |
| `Cappuccino - Extra Section.html` | Cappuccino / coffee culture section |
| `Day Trips by Train - Extra Section.html` | Day trips by train — Train/Why/Book format |
| `Shows, Performances & Concerts - Extra Section.html` | Shows section — venue own-site links only |
| `Train Stations Near Hotel - Extra Section.html` | Train stations — walk times, negative-finding line |
| `Pickleball - Extra Section.html` | Pickleball section |
| `Downtown Restaurants - Extra Section.html` | Historic downtown restaurants section |
| `Claude Inspiration - Extra Section.html` | Claude's inspiration note section |
| `Heads Up - Extra Section.html` | City-specific gotchas — construction, closures, quirks |

### Validators

| Script | Job |
|--------|-----|
| `guide_tools.py ship` | Single entry point — chains validate + verify + verify-booking |
| `brain_check.py` | Brain integrity — required sections, required files, ghost references |
| `validate_itinerary.py` | Guide structure — stop blocks, box shapes, motion rule, currency |
| `verify_urls.py` | Link health — every URL returns 200 + editorial prose |
| `verify_booking_links.py` | Subject drift — booking link h1 matches stop subject |
| `commons_photo.py` | Photo resolution — Commons URLs to 800px thumbs |
| `autofix_itinerary.py` | Guide auto-repair — rewrites mis-filed booking boxes |
| `sweep_stray_travel.py` | Stray-file enforcement |
| `render_pdf.py` | PDF render — headless Chromium (on-demand only) |
| `validate_pdf.py` | PDF integrity (on-demand only) |
