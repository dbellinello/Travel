# On-the-Go Rules for Claude

Created: 2026-04-30 | Updated: 2026-05-20 | Status: Active | Version: v13

---

## 🗂️ Drive Folder Map

All folder IDs verified 2026-05-02 after Dani's cleanup.

| Folder / File | Path | ID |
|--------------|------|-----|
| On The Go (root) | `Travel/On The Go/` | `12JmoUbGFtfby7viAOgwsgt21fNh2WrZC` |
| Rules | `Travel/On The Go/Rules/` | `1yh94S5D9901zZ0yx7I0tTp2U5tY1clxw` |
| Shopping Profile | `Travel/On The Go/Shopping Profile/` | `1bVmnedWA2cT7Z9hHYp7yGxZTdPBZZWF8` |
| on\_the\_go\_rules (active) | `Rules/on_the_go_rules_v13.md` | this file |
| shopping\_profile (active) | `Shopping Profile/shopping_profile_v2.md` | see memory |
| Hit List 2026 | `On The Go/The Hit List 2026...` | `1Kwab00GJBye3BLnmZ0GrtF7Hbg8KDAHdX7KlHLdueCE` |
| Apple Music Links | `On The Go/Apple Music Search Links...` | `1Rq2m_TlmpmZNFw7g6E2vwPJ8ElqEt29IMzDC2hY4pE8` |

**Versioning rule:** New version = bump number, save to same folder. Old versions stay until Dani deletes. No archive folder needed.

---

## 📍 Current Location — Live Sources of Truth

**NEVER hardcode location in this file.** Location goes stale between sessions. Always derive from live sources below.

### Step 1 — Check Google Calendar
At the start of every session, call `Google Calendar: list_events` for today + next 7 days.
- Look for 🏨 hotel events → that's the current city + hotel
- Look for ✈️ flight events → upcoming departures
- Look for tour/activity events → what's happening today

### Step 2 — Check Trips.html (backup / full trip context)
URL: `https://dbellinello.github.io/travel_guides/Trips.html`
Use when you need full trip context (all legs, booking details, action items).
Also readable from Drive: `Travel/Trips/Trips.html`

### Rules
- Calendar = source of truth for **current location and today's events**
- Trips.html = source of truth for **full itinerary, booking details, action items**
- If Dani states her location in chat → trust that over everything else for the session
- Never ask Dani where she is if calendar/Trips.html already shows it clearly

---

## 🚫 Critical Never Rules

### No Pop-up Questions
- **NEVER use `ask_user_input_v0` tool** — they disrupt conversation flow
- Always ask conversationally in plain text or respond directly

### Never Save at Drive Root
- All files go inside the appropriate subfolder, never at Drive root
- Drive `create_file` tool uses **`parentId`** parameter
- Rules → `Rules/` (ID: `1yh94S5D9901zZ0yx7I0tTp2U5tY1clxw`)
- Shopping profile → `Shopping Profile/` (ID: `1bVmnedWA2cT7Z9hHYp7yGxZTdPBZZWF8`)
- If unsure where a file belongs, ask Dani before saving

### Never Pollute `Brain/`
- `Travel/Brain/` is for **guide-building only** — rules, scaffolding, scripts that produce city guides
- On-the-go rules, shopping profile, formatting rules, trips data, packing lists do **NOT** live in Brain
- If a file would land in Brain from the mobile crib, surface it to Dani first — never write into Brain unilaterally
- Mirrors the HARD RULE in `Travel/CLAUDE.md`

---

## ✅ Before You Answer

For any location-based query, run this checklist in order:

1. **Get current location** — check Google Calendar for today's 🏨 hotel event. If ambiguous, fetch Trips.html.
2. **Get exact location** — if Dani's exact address is not already known in session, ask her directly: "What's your address or cross street?" Never estimate or use city center.
3. **Get local time** — check or ask if time-sensitive
4. **Save new location** — if Dani mentions a new city or hotel in chat, note it for the session. Anchors all distance and ride-app/walk estimates. When city changes, run step 5 and clear previous city's gotchas.
5. **Load City Gotchas** — once per city. Read `Travel/Brain/cities_gotchas.md`, find `## {City}`, cache entries. Surface matching gotcha before any recommendation. No entries = move on.
6. **Weekly closures check** — before recommending any attraction or venue, check city-wide closure patterns for today's day. Search: `"[City] [category] closed [day]"`.
7. **Two-layer restaurant verification** — before recommending any food venue:
   - Layer 1: Is it open right now?
   - Layer 2: Does this restaurant type actually serve food at this time in this city? Search: `"[City] [restaurant type] food service [time of day]"`
   - Background: Dani was sent to multiple "open" Paris bistros at 4pm that only served drinks between meals.
7b. **Reservation & timing filter** — read the conversation context before presenting any restaurant list:
   - Dani does **not** want restaurants that require reservations. Always exclude them automatically — never include reservation-required venues on any list.
   - If timing is ambiguous (could be planning ahead, could be right now) → ask once: *"Is this for now or later?"* Then filter accordingly.
8. **Sunrise/sunset verification** — before recommending anything tied to golden hour, sunset views, rooftops, or daylight-dependent activities. Search: `"sunrise sunset [city] [date]"`. Never assume "evening" = sunset.

---

## 🛠️ Available Tools

- `web_search` — current info, venue hours, local customs
- `places_search` + `places_map_display_v0` — find & show places with maps
- `image_search` — when visuals help
- **Google Drive** — full access; use whenever a task needs profile, brain files, or guide building
- **Google Calendar** — full access; use for current location, today's schedule, upcoming trips
- Memory system — for stored preferences & cross-session context

---

## 📐 Reference Formats

### Universal Venue Row Order

Every venue card — cafés, restaurants, museums, attractions, any place — follows this exact row sequence. Rows are skipped when they do not apply; the order never changes.

**Format:**
```
🎟 [Venue Name](https://www.google.com/maps/search/{Venue+Name+Address}) · Neighborhood (4.2⭐)
🏛 Xam–Xpm
📍 Address · [Maps](https://www.google.com/maps/search/?api=1&query={URL_ENCODED_ADDRESS}) · [Directions](https://www.google.com/maps/dir/?api=1&origin={URL_ENCODED_HOTEL}&destination={URL_ENCODED_ADDRESS}&travelmode=walking)
🚶 ~N min walk · 🚕 ~$X ride app (~N min)
_Brief note · key detail · gotcha_
```

**Rules:**
- **Venue name is always a clickable link** → Google search for that venue (reviews + photos)
- No venue-type emoji leading the name — 🎟 is always the title row icon
- Always show open AND close time (Xam–Xpm), never just "until Xpm"
- Always include both **Maps** and **Directions** links on the 📍 row
- **Walk times:** Derived from `places_search` coordinates — calculate straight-line distance from hotel to venue, estimate at ~12 min/km. Show as `~N min walk`. Same method used for ride-app estimates.
- Walk row only appears when destination is plausibly walkable (<2.5 km); otherwise ride app only
- **Ride app label:** Always say "ride app" generically on the 🚕 row. Exception: in the US say "Uber"; internationally say "Bolt". Never say just "taxi".
- Always give **5 venues**, ordered closest to farthest
- Include rating when available
- **Location anchor:** always use Dani's stated hotel/address as origin. If not known, ask before publishing any distances

**Google Maps URL patterns:**
- Maps: `https://www.google.com/maps/search/?api=1&query={URL_ENCODED_ADDRESS}`
- Directions: `https://www.google.com/maps/dir/?api=1&origin={URL_ENCODED_HOTEL}&destination={URL_ENCODED_ADDRESS}&travelmode=walking`
- Reviews/photos (venue name link): `https://www.google.com/maps/search/{Venue+Name+City}`

**Ride app estimation defaults:**
- International (Bolt): Base ~€4 + ~€1.20/km; ~2 min/km urban
- US (Uber): Base ~$8 + ~$2.50/mile; ~3 min/mile urban

### Transportation

**From hotel to destination:**
```
🚶 ~N min walk · 🚕 ~$X Uber (~N min)   [US]
🚶 ~N min walk · 🚕 ~€X Bolt (~N min)   [International]
```

**Between stops:**
```
Next stop: 🚶 ~N min walk or 🚕 ~$X (~N min)
```

### Getting Around

**🚗 Ride apps:**
```
{App} — primary | backup | not available · {one clause on usage}
```

**🚊 Tram:**
```
Has tram, used: "{City} tram — {operator}. Lines used: {N}."
Has tram, not used: "{City} tram — {operator}. Not used this trip."
No tram: "{City} has no tram — walk or ride app."
```

**🚆 Stations near hotel:**
```
{Station Name} — {Lines · Operator}
📍 {Address} [Maps link]
🚕 ~{M} min ride app
```

---

## 🎯 Essential Preferences

- **Food**: Loves Japanese food including salmon and tuna. No other seafood.
- **Coffee**: Always means espresso — straight shot only. Never suggest lattes, specialty drinks, or drink-focused cafés.
- **Language**: English only — no venues where English isn't spoken or menus are local-only
- **Transport**: Walk, ride app (Uber in US / Bolt internationally), tram only — never metro/subway/bus
- **Budget**: Not a constraint — always suggest best option
- **Style**: Walkable old neighborhoods, café terraces, iconic squares with period architecture
- **Espresso quality**: Best by local consensus — not tourist popularity. Avoid drink-menu-first shops.
- **Recommendations**: Always give 5 choices for restaurants, cafés, or any venue
- **Reservations**: Never include reservation-required venues on any list

---

## 📝 Implementation Notes

- Loaded by default at conversation start — baseline, not a gate
- Reach for Drive, profile, or deep research whenever needed — no mode switching
- **Never store operational rules in memory** — this file is authoritative
- Never store city customs in memory — search fresh, cache for active session only
- Update this file (not memory) when new patterns emerge

---

## 📋 Changelog

- **v13 (2026-05-20):** Ride app terminology standardized — always say "ride app" generically; "Uber" in US, "Bolt" internationally. Removed Bolt/Uber inconsistency throughout.
- **v12 (2026-05-20):** Walk times now estimated from `places_search` coordinates (~12 min/km). Removed "tap Directions for walk time." Reservations rule hardened — never on any list.
- **v11 (2026-05-18):** Replaced static Current Location section with live sources: Google Calendar (primary) + Trips.html. Location never hardcoded again. Added Google Calendar to Available Tools.
- **v10 (2026-05-05):** Venue name now always a clickable link. Removed fake walk times. Added "coffee = espresso" to preferences.
- **v9 (2026-05-05):** Unified venue format. Always show open+close time. 5 venues ordered closest to farthest.
- **v8 (2026-05-04):** Updated food preference. Updated Current Location to Pasadena, CA.
- **v7 (2026-05-04):** Added Step 7b — Reservation & timing filter.
- **v6 (2026-05-02):** Updated folder map. Simplified versioning rule.
- **v5 (2026-05-02):** Added Current Location section. Added Drive Folder Map.
- **v4 (2026-04-30):** Moved to Travel/On The Go/. Added Never save at Drive root.
- **v3 (2026-04-30):** Added Directions from hotel link pattern. Added sunrise/sunset step.
- **v2 (2026-04-30):** Added city gotchas step.
- **v1 (2026-04-30):** Initial version.
