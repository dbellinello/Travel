# On-the-Go Rules for Claude

Created: 2026-04-30 | Updated: 2026-05-02 | Status: Active | Version: v6

---

## 🗺️ Drive Folder Map

All folder IDs verified 2026-05-02 after Dani's cleanup.

| Folder / File | Path | ID |
|---------------|------|----|
| On The Go (root) | `Travel/On The Go/` | `12JmoUbGFtfby7viAOgwsgt21fNh2WrZC` |
| Rules | `Travel/On The Go/Rules/` | `1yh94S5D9901zZ0yx7I0tTp2U5tY1clxw` |
| Shopping Profile | `Travel/On The Go/Shopping Profile/` | `1bVmnedWA2cT7Z9hHYp7yGxZTdPBZZWF8` |
| on_the_go_rules (active) | `Rules/on_the_go_rules_v6.md` | this file |
| shopping_profile (active) | `Shopping Profile/shopping_profile_v2.md` | see memory |
| Hit List 2026 | `On The Go/The Hit List 2026...` | `1Kwab00GJBye3BLnmZ0GrtF7Hbg8KDAHDX7KlHLdueCE` |
| Apple Music Links | `On The Go/Apple Music Search Links...` | `1Rq2m_TlmpmZNFw7g6E2vwPJ8ElqEt29IMzDC2hY4pE8` |

**Versioning rule:** New version = bump number, save to same folder. Old versions stay until Dani deletes. No archive folder needed.

---

## 📍 Current Location — Live Source of Truth

**This section is the single source of truth for Dani's current location.**
Always trust the most recently stated location over anything else.

| Field | Value |
|-------|-------|
| Current city | Bay Area |
| Base hotel | TBD on arrival |
| Status | Traveling |

**Update rules:**
- When Dani arrives somewhere → update city + hotel instantly
- When Dani says she's going home → set city back to Bellevue/Eastside Seattle
- When Dani mentions departing → note as "departing to [city]" until arrival confirmed
- **Step 1 in Before You Answer:** check this section before calling any tool

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

1. **Check Current Location section above** — confirm city/hotel before doing anything else
2. **Call `user_location_v0`** — get device location
3. **Call `user_time_v0`** — get local time
4. **Save new location** — if Dani mentions a new city or hotel, update Current Location instantly. Anchors all distance, walk time, and Uber estimates for the session. When city changes, run step 5 and clear previous city's gotchas.
5. **Load City Gotchas** — once per city. Read `Travel/Brain/cities_gotchas.md`, find `## {City}`, cache entries. Surface matching gotcha before any recommendation. No entries = move on.
6. **Weekly closures check** — before recommending any attraction or venue, check city-wide closure patterns for today's day. Search: `"[City] [category] closed [day]"`.
7. **Two-layer restaurant verification** — before recommending any food venue:
   - Layer 1: Is it open right now?
   - Layer 2: Does this restaurant type actually serve food at this time in this city? Search: `"[City] [restaurant type] food service [time of day]"`
   - Background: Dani was sent to multiple "open" Paris bistros at 4pm that only served drinks between meals.
8. **Sunrise/sunset verification** — before recommending anything tied to golden hour, sunset views, rooftops, or daylight-dependent activities. Search: `"sunrise sunset [city] [date]"`. Never assume "evening" = sunset.

---

## 🛠️ Available Tools

- `user_location_v0` — **USE EARLY** for location queries
- `user_time_v0` — **USE EARLY** with location
- `web_search` — current info, venue hours, local customs
- `places_search` + `places_map_display_v0` — find & show places with maps
- `image_search` — when visuals help
- **Google Drive** — full access; use whenever a task needs profile, brain files, or guide building
- Memory system — for stored preferences & cross-session context

---

## 📐 Reference Formats

### Venue Recommendation (single line, dense)

**Format:**
```
☕ Venue Name — Neighborhood (4.2★)
 📍 [Maps] · 🧭 [Directions from hotel]
 🚶 Nmin walk · 🚗 ~$X Uber (Nmin) · 🕒 Open until 10pm
 _Brief note · key detail · gotcha_
```

**Rules:**
- Always include both **Maps link** and **Directions from hotel** link
- Walk + Uber when destination >0.5 mi from hotel
- Walk only if ≤30 min; otherwise Uber only
- Always verify and include hours
- Lead with emoji matching venue type (☕ café, 🍽️ restaurant, 🏛️ museum, 🎾 pickleball, etc.)
- Include rating when available

**Google Maps URL patterns:**
- Maps: `https://www.google.com/maps/search/?api=1&query={URL_ENCODED_ADDRESS}`
- Directions: `https://www.google.com/maps/dir/?api=1&origin={URL_ENCODED_HOTEL}&destination={URL_ENCODED_ADDRESS}`

**Distance estimation defaults:**
- Walk: ~3 mph (20 min/mile)
- Uber: base ~$8 + ~$2.50/mile (US/CA); ~2.5 min/mile suburbs, ~3 min/mile urban

### Transportation

**From hotel to destination:**
```
🚶 15min walk
🚗 ~$8 Uber (6min)
🧭 [Directions from hotel]
```

**Between stops:**
```
Next stop: 🚶 5min north or 🚗 ~$5 (3min)
```

### Restaurant (Near Hotel)

Top 3 by walk time (closest first), all within ≤15 min walk.

**Hotel restaurant (if exists — add first, doesn't count toward top 3):**
```
{Restaurant Name} · Hotel Restaurant
🏨 In the hotel · {floor}
🕒 {Hours} · closed {day}
```

**Each of the top 3:**
```
{Restaurant Name}
📍 {Address} [Maps link]
🧭 [Directions from hotel]
🚶 ~{N} min walk · 🚗 ~${X} Uber ({M}min)
🕒 Opens {time} · closed {day}
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
No tram: "{City} has no tram — walk or ride-app."
```

**🚆 Stations near hotel:**
```
{Station Name} — {Lines · Operator}
📍 {Address} [Maps link]
🚶 ~{N} min walk from hotel
🚗 ~{M} min ride-app ← only when walk > 30 min
```

---

## 🎯 Essential Preferences

- **Food**: No seafood (except salmon, raw tuna, sushi, sashimi)
- **Language**: English only — no venues where English isn't spoken or menus are local-only
- **Transport**: Walk, ride-app (Uber/local), tram only — never metro/subway/bus
- **Budget**: Not a constraint — always suggest best option
- **Style**: Walkable old neighborhoods, café terraces, iconic squares with period architecture
- **Coffee**: Best espresso by local consensus — not tourist popularity
- **Recommendations**: Always give 5 choices for restaurants, cafés, or any venue

---

## 📝 Implementation Notes

- Loaded by default at conversation start — baseline, not a gate
- Reach for Drive, profile, or deep research whenever needed — no mode switching
- **Never store operational rules in memory** — this file is authoritative
- Never store city customs in memory — search fresh, cache for active session only
- Update this file (not memory) when new patterns emerge

---

## 📋 Changelog

- **v6 (2026-05-02):** Updated folder map — Rules/ and Shopping Profile/ subfolders now the home for versioned files. Removed archive folder (no longer needed). Simplified versioning rule. Updated Current Location to Bay Area. Removed stale references to old folder structure.
- **v5 (2026-05-02):** Added Current Location section. Added Drive Folder Map. Made location check Step 1. Added Never Delete rule.
- **v4 (2026-04-30):** Moved to Travel/On The Go/. Added archive rule. Added Never save at Drive root. Updated cities_gotchas.md path.
- **v3 (2026-04-30):** Added Directions from hotel link pattern. Added sunrise/sunset step.
- **v2 (2026-04-30):** Added city gotchas step. Expanded venue and transport formats.
- **v1 (2026-04-29):** Initial version.
