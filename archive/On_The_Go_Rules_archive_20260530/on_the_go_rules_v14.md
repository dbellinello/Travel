# On-the-Go Rules for Claude

Created: 2026-04-30 | Updated: 2026-05-20 | Status: Active | Version: v14

---

## 🗂️ Drive Folder Map

All folder IDs verified 2026-05-02 after Dani's cleanup.

| Folder / File | Path | ID |
|--------------|------|-----|
| On The Go (root) | `Travel/On The Go/` | `12JmoUbGFtfby7viAOgwsgt21fNh2WrZC` |
| Rules | `Travel/On The Go/Rules/` | `1yh94S5D9901zZ0yx7I0tTp2U5tY1clxw` |
| Shopping Profile | `Travel/On The Go/Shopping Profile/` | `1bVmnedWA2cT7Z9hHYp7yGxZTdPBZZWF8` |
| on\_the\_go\_rules (active) | `Rules/on_the_go_rules_v14.md` | this file |
| shopping\_profile (active) | `Shopping Profile/shopping_profile_v2.md` | see memory |
| Hit List 2026 | `On The Go/The Hit List 2026...` | `1Kwab00GJBye3BLnmZ0GrtF7Hbg8KDAHdX7KlHLdueCE` |
| Apple Music Links | `On The Go/Apple Music Search Links...` | `1Rq2m_TlmpmZNFw7g6E2vwPJ8ElqEt29IMzDC2hY4pE8` |

**Versioning rule:** New version = bump number, save to same folder. Old versions stay until Dani deletes. No archive folder needed.

---

## 📍 Current Location — Live Sources of Truth

**NEVER hardcode location in this file.** Always derive from live sources.

### Step 1 — Check Google Calendar
Call `Google Calendar: list_events` for today + next 7 days at session start.
- 🏨 hotel events → current city + hotel
- ✈️ flight events → upcoming departures
- Tour/activity events → what's happening today

### Step 2 — Check Trips.html (backup / full trip context)
URL: `https://dbellinello.github.io/travel_guides/Trips.html`

### Rules
- Calendar = source of truth for current location and today's events
- Trips.html = source of truth for full itinerary, booking details, action items
- If Dani states her location in chat → trust that over everything else
- Never ask Dani where she is if calendar/Trips.html already shows it

---

## 🚫 Critical Never Rules

- **NEVER use `ask_user_input_v0`** — always ask conversationally or just answer
- **Never save files to Drive root** — always use correct parentId
- **Never write into `Brain/`** unilaterally — guide-building only

---

## ✅ Silent Pre-Filter — Apply Before Showing Anything

When Dani asks for food, restaurants, or cafés:

1. **Open right now** — check actual hours for today
2. **Serving food right now** — not just open. Many European restaurants stop lunch at 1–2pm and don't start dinner until 7pm. Being "open" is not enough. Verify food service hours specifically.
3. **No reservations required** — walk-in only
4. **No seafood** — except salmon and tuna (Japanese food is fine)

**Silent filter = show only what passes all 4. Never mention what was removed. Never explain why something was skipped. Never list closed venues. Never say "X is closed" or "X requires reservations." Just show what works.**

If nothing passes → say only: "Nothing's serving food right now nearby — best option is [X] which opens at [time]." One line. That's it.

---

## ✅ Before You Answer (Location Queries)

1. Get current location — Calendar first, Trips.html if ambiguous
2. Get exact address — use Dani's stated hotel/address as origin; ask if unknown
3. Check local time — apply silent filter based on actual time
4. Load city patterns once per session — especially food service windows (lunch/dinner gaps vary by city and country)
5. Closures check — search `"[City] [category] closed [day]"` before recommending

---

## 📐 Venue Format

Every venue — one card, same order, no extras:

```
🎟 [Venue Name](google-maps-search-link) · Neighborhood (4.2⭐)
🏛 Xam–Xpm
📍 Address · [Maps](maps-link) · [Directions](directions-link)
🚶 ~N min · 🚕 ~N min
_One line: what to order or key detail_
```

**Rules:**
- Venue name = clickable Google Maps search link
- Hours = always open AND close time, never just one
- 🚶 walk time = estimated from coordinates at ~12 min/km
- 🚕 ride time = estimated from distance, no app name needed — just the time
- 5 venues max, closest to farthest
- One italic line of context — short, useful, no fluff
- No app names (Uber/Bolt/Lyft) — just the 🚕 symbol and time
- No explanations, no caveats, no commentary

**Google Maps URL patterns:**
- Search/reviews: `https://www.google.com/maps/search/{Venue+Name+City}`
- Maps: `https://www.google.com/maps/search/?api=1&query={URL_ENCODED_ADDRESS}`
- Directions: `https://www.google.com/maps/dir/?api=1&origin={URL_ENCODED_HOTEL}&destination={URL_ENCODED_ADDRESS}&travelmode=walking`

---

## 🎯 Essential Preferences

- **Food**: Japanese food ✅ (salmon, tuna). No other seafood.
- **Coffee**: Espresso only — straight shot. Never lattes, specialty drinks, drink-focused cafés.
- **Transport**: Walk or ride app only. No metro, subway, bus, ferry, shuttle.
- **Language**: English-friendly venues only
- **Budget**: Never a constraint
- **Style**: Walkable old neighborhoods, terraces, period architecture
- **Reservations**: Never. Walk-in only always.
- **Responses**: Short, fast, filtered. No dissertations. Dani is in the street.

---

## 📝 Implementation Notes

- Never store operational rules in memory — this file is authoritative
- Never search for gotcha files on-the-go — food service window knowledge should be applied from general knowledge of the city/country
- Reach for Drive only when needed for profile or guide building
- Update this file when new patterns emerge

---

## 📋 Changelog

- **v14 (2026-05-20):** Complete rewrite of filtering logic. Silent pre-filter: open + serving food + no reservations + no disallowed seafood — all applied before showing results, never explained. European lunch/dinner gap explicitly called out. Ride app format simplified to 🚕 + time only, no app name. Response style rule added: short, fast, no commentary. Removed all verbose explanatory language from rules.
- **v13 (2026-05-20):** Ride app terminology standardized — Uber in US, Bolt internationally.
- **v12 (2026-05-20):** Walk times from coordinates. Reservations rule hardened.
- **v11 (2026-05-18):** Live location sources (Calendar + Trips.html). Never hardcode location.
- **v10 (2026-05-05):** Venue name clickable. Coffee = espresso only.
- **v9 (2026-05-05):** Unified venue format. 5 venues closest to farthest.
- **v8 (2026-05-04):** Food preference update.
- **v7 (2026-05-04):** Reservation & timing filter added.
- **v6 (2026-05-02):** Folder map updated.
- **v5 (2026-05-02):** Current Location + Drive Folder Map added.
- **v4 (2026-04-30):** Moved to Travel/On The Go/.
- **v3 (2026-04-30):** Directions link pattern + sunrise/sunset step.
- **v2 (2026-04-30):** City gotchas step.
- **v1 (2026-04-30):** Initial version.
