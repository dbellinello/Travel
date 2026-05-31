# on_the_go_rules_v11.md
# Single source of truth for operational rules

---

## 🚀 Startup

- Fetch https://dbellinello.github.io/travel_guides/Trips.html at the start of every session — single source of truth for current location, active hotel, upcoming trip context.
- Check Google Calendar for additional context.
- Do NOT load this rules file on every startup — only when Dani says "reload rules" or it's a complex planning session.
- 🏃 or "street mode" = skip ALL startup checks. Answer immediately from memory.

---

## 📍 Location

- Memory entry #6 holds current location. Update it when Dani says she's moved.
- Never rely on memory alone for location — always verify with Trips.html at session start (unless street mode).

---

## 🗂 Drive File Placement

- Travel-related files → Travel/
  - Utility files → Travel/On The Go/ (ID: 12JmoUbGFtfby7viAOgwsgt21fNh2WrZC)
  - Guide building → Travel/Brain/
  - Generated guides → Travel/Guides/
- Non-travel files → root-level On The Go/ folder
- Rules → Travel/On The Go/ (this folder)
- Shopping profile → Travel/On The Go/Shopping Profile/
- To-dos → Travel/On The Go/ (this folder)
- NEVER save at Drive root
- Drive create_file tool uses `parentId` parameter (not `parentFolderId`)

---

## 🗑 Archive, Never Delete

- We never delete anything — always archive.
- Claude mistakes → Travel/archive/
- Any file created in wrong place by Claude → move to Travel/archive/
- Never use rm. Never leave stale files in place.

---

## 📝 To-Do List Rules

- To_Do_List.md is the single source of truth for ALL tasks.
- Read before adding — no duplicates.
- When task is done → remove from file (no strikethrough).
- Memory never holds to-dos — they live in the file only.
- Drive can't edit files, only create new ones. Workflow: read → rewrite → create new → Dani archives old.

---

## 🛒 Shopping Rules

- Amazon only
- ⭐ 4+ reviews on every card
- Clickable links
- No price filtering
- Consistent card format
- Load shopping_profile_v2.md for any product search

---

## ✈️ Travel Rules

### Transport
- International: walking or Uber/Bolt only. No metro, bus, ferry, or shuttle.
- US: Uber or rental car only. No trains.

### Day Trips (US guides)
- Max 1.5hr drive from base city → full planning
- Over 1.5hrs → "Extras" section, listed only, no detailed itinerary
- Tours exempt from time limit

### Pickleball
- Include pickleball section in US guides if destination has a good scene
- No pickleball section for international guides