# Separation Map

Which topic belongs in which core rules doc. Check this before adding anything to any file.

Each doc has ONE job. If a topic isn't listed under a file, it doesn't go there.

---

## Brain/Reference/Toolbar.html  *(moved out of CORE RULES 2026-05-30)*

- Required mount div markup for every HTML page (`<div id="toolbar-mount">` + script tag)
- `data-depth` rule (folder levels below `Travel/` — drives relative hrefs and script path)
- `data-maxwidth` values (760 Trip Essentials / 940 Guides)
- How to add a new page to the menu (edit `toolbar.js` ITEMS array only — never per-file)
- Auto-styling behavior (toolbar reads page background at runtime — no per-page override needed)
- Footer sharing link (§ 5 — cosmetic public URL, guide pages only)

---

## Brain/Reference/Navigation.html  *(moved out of CORE RULES 2026-05-29)*

- The shared footnote — the sharing link carried across to the guides (auto-injected by `toolbar.js` on Trip Essentials pages + guides index)
- `data-prev` / `data-next` attributes on the toolbar mount div (guide pages only)
- Chain integrity rule (bidirectional consistency — predecessor's next must match successor's prev)
- `guides_index.html` wiring (matching `data-guide-prev` / `data-guide-next` on index cards)
- Procedure for inserting a new guide into the chain (4 values + index card updated in one pass)
- Scroll progress bar and scroll button (passive aids on every page)

---

## Trip Essentials/Essentials Pages - Rules.md

- Which Trip Essentials pages carry a search box
- Search filtering and group-collapse behaviour
- No-results state: title + search box + message only; content, jump-nav, legends, index table, and shared footnote all hide

---

## Stops Structure

- Stop selection criteria (what qualifies, what doesn't ship — include/exclude lists, quality bar)
- 4-step research flow and trusted sources (Fodor's, Culture Trip, Rough Guides, Atlas Obscura, Rick Steves, NatGeo, official tourism boards)
- Travel style (meaningful over full, no FOMO, guided-tour-first, seasoned European traveler)
- Day-glance labels (🎒 Self-Guided / 🚆 Train Day)
- Stop type and shape template (Self-Guided Stop — the only active stop type)
- 🚆 Train Day pattern (day-level wrapper template)
- Stop naming rule (always the venue, never generic)
- Stop notes (🚫 closed / 🆓 free / 💵 cash-only / ⚠️ warning and their order)

## Tickets.html

- Booking-link source waterfall (US: Ticketmaster → StubHub → TodayTix · International: Viator / GetYourGuide / TripAdvisor flat pool · Klook fallback · Venue site last resort)
- Entry Format(s) — platform product (`🎟 {Title} · (N.N⭐) · {Platform}`) vs venue site (`🎟 {site.url}`)
- Skip-the-line link text format (product title, never bare host on bot-blocked platforms)

## Tours.html — ~~Retired 2026-05-20~~

Moved to `Travel/Retired Rules/Retired_Tours.html`. In-stop tour boxes and the Guided Tour Stop pattern are retired. All tour rules now live in `Tours - Extra Section.html`.

## Guide Structure

- Section order top-to-bottom (Title Page → Trip at a Glance → Day blocks → Extra sections → Claude Inspiration)
- Extra-section order (15 sections: Weekly Closures is #1; Tours is #2 — added 2026-05-20, after Weekly Closures; 12 universal + 2 conditional — Pickleball (CA/AZ/OR only), Cities Gotchas (entries gated) — plus Claude Inspiration optional / always last)
- Universal shipping rule (every guide ships the 12 universal Extra sections; Pickleball + Cities Gotchas are conditional)
- Build phases & required reads per phase (Phase 0–5 with mandatory file reads)
- Day numbering (Day 1 = first full touring day per Day Structure § 1)

## Day Structure

- Start time (~9:00 am default)
- Stop count (≥4 full day / ≥2 half day)
- Geographic clustering / no backtracking rule
- Transit banners (FROM HOTEL opener, between-stop lines, hotel closer)
- Bookends (FROM HOTEL + hotel closer — mandatory, every day)
- Stop numbering (resets to 1 every day)

## Motion Rule

- Walk vs. ride threshold (≤40 min walk / >40 min ride)
- Real times only — no estimates
- ` · ` separator between options
- Walk / Uber / tram only — no metro/subway/bus on transit lines

## Trip at a Glance

- Card format (Day N · type icon · type label · stop names)
- Train Day card suffix (Day N · 🚆 Train Day — {City})
- Day order (in-city days first, self-guided Train Days last)
- Jump anchor format

## Hotel Banner

- Title page layout (CITY / Hotel Name / Address)
- Hotel name appears exactly once (title page only)
- Every other reference = generic "hotel" / "HOTEL"

## Restaurants Near Hotel

- Minimum 5 · ≤25 min walk · ordered by walk time (closest first)
- Format: name (plain text, no link) + address + walk time + hours + closed day
- Hotel restaurant rule (add first if exists, doesn't count toward the minimum of 5)
- Seafood exclusion: venues whose primary identity is fish/shellfish/bacalhau are excluded (sushi permitted)

## Downtown Restaurants

- Minimum 5 in the historic downtown core, ordered by review consensus and editorial standout
- No walk-time row (district-scoped)
- No overlap with Restaurants Near Hotel — must be different picks
- Seafood exclusion (same as Restaurants Near Hotel)
- Negative finding when no historic downtown exists

## Michelin Restaurants

- Stars only (1⭐ 2⭐ 3⭐ — no Bib, no Plate)
- All tiers ship, no shortlist
- Order: stars descending, alphabetical within tier

## Cappuccino

- Minimum 5 cafés · ≤25 min walk · ordered by walk time (closest first)
- Best espresso by local consensus — independent cafés or non-American-chain specialty roasters only
- Café name links to the top review (Yelp / Google Reviews / Google Maps), not the café's own site
- No Tripadvisor links on café names (tourist-skewed)

## Shows, Performances & Concerts

- Truly exceptional only ("if it tours, it likely doesn't qualify")
- 🎟 → venue's own site only (never aggregators)

## Local Tastes

- Tied to a specific place's identity — not country-level clichés
- Negative finding when nothing genuinely distinctive exists

## Food Delivery

- Platform availability for the destination (DoorDash · Uber Eats → Grubhub → local platform)
- Delivery rows added to Cappuccino section (per-café; first qualifying platform wins)
- No-delivery exception: negative-finding line → explicit approval → `delivery-ok` comment → permanent pass
- Known locals: Deliveroo (UK), Wolt (Iceland), Glovo (Italy/Portugal), Uber Eats (Australia)

## Day Trips by Train - Extra Section

Train day-trips only (by-car/Uber retired 2026-05-03).

- Documentation-only list — train trip destinations
- Train trips: city + train time + Train: line + Why + Book via {operator}

## Getting Around

- Ride apps (Uber primary, fallbacks by city)
- Tram (simple above-ground streetcar only)

## Train Stations Near Hotel

- Two entries: closest station for local/regional trains + closest station for high-speed trains
- When the same station serves both, ship one entry with combined line names
- No walking-distance limit (always show closest, no matter how far)
- Header glyph rule: 🚄 only when every station listed serves HSR exclusively, otherwise 🚆
- Format: name + lines · operator (plain text) + 📍 address (Maps-linked) + 🚶 walk (+ 🚕 ride-app fallback when walk > 30 min)
- Row order locked: info → map → walk
- No-station fallback: ship "No train stations in {City}." when none exist

## Hotels & Rentals

- Listed brands only (US: Marriott/Hilton/Hyatt · Intl: NH Collection/Meliá/Novotel/Sofitel/Pullman/Radisson Blu/Intercontinental)
- No off-list brand ever ships as primary
- Ratings (9.0+ Booking.com / 4.5+ elsewhere)
- Rental fallback when no qualifying hotel

## Delta

- Delta + SkyTeam only — never search or compare others
- Origin SEA · round-trip · First Class preferred

## Car Rentals

- Hertz default
- Fallback ladder: Enterprise → Avis → Budget → Europcar → Sixt

## Links

- Every link live-verified, every edit
- 📖 → English Wikipedia only
- 📍 → Google Maps anchor on the address
- target="_blank" on every external link

## Photos

- Source: Wikimedia Commons (default)
- One photo per stop
- Licenses: Public Domain · CC0 · CC-BY · CC-BY-SA
- Storage: local in Guides/{City}/_build/assets/

## Weekly Closures

- City-wide patterns only
- Format: Category · Closed Day

## Cities Gotchas

- Per-trip "wish I'd known" intel — venue gotchas, timing tricks, booking quirks
- Format per entry: Venue/Topic + Gotcha + Workaround + Source (date learned)
- Surface upfront when a listed venue appears in a new guide

## Pickleball

- Optional Extra Section for pickleball-friendly destinations
- Any court within 25 min walk of the hotel qualifies (proximity is the only filter); no cap on entries
- Mix of outdoor parks and indoor facilities; ordered by walk time (closest first)
- Description line ≤80 chars; venue name is plain text (no hyperlink); no rating stars in name
- Negative-finding line when no court within 25 min
- Section icon: 🏓 Unicode emoji
- Section format and inclusion bar live in `Pickleball - Extra Section.html`

## Weather

- Weather.com · AccuWeather · Ventusky · Windy.com

## Claude Inspiration

- Optional, under 6 lines
- Always the last section — no exceptions

## Icon Order and Format

- Section header icons (which emoji leads which EoI section)
- Universal row order within every stop box (icon sequence rules)
- Exact format rule per icon glyph
- Train icons (🚄 vs 🚆 distinction)
- Description character limits per row type

---

## What goes where — quick decision

| I need to add... | Goes in... |
|---|---|
| A new stop type | Stops Structure.html |
| A new tour sourcing rule | Tours - Extra Section.html |
| A new EoI section | Guide Structure |
| A new stop flag | Stops Structure.html |
| A new ticket platform | Tickets.html (waterfall) |
| A new transport mode | Getting Around |
| A new station-near-hotel rule | Train Stations Near Hotel |
| A new hotel brand | Hotels & Rentals |
| A day structure rule | Day Structure |
| A walk-vs-ride threshold tweak | Motion Rule |
| A research source | Stops Structure.html |
| A new Cities Gotchas entry | Cities Gotchas |
| A new Pickleball-section rule | Pickleball |
| A new day-trip rule | Day Trips by Train - Extra Section |
| A new icon assignment or row-order rule | Icon Order and Format |
| A new guide added to the chain | Navigation.html (procedure) |
| A toolbar menu item added | Brain/Reference/Toolbar.html § 4 |
