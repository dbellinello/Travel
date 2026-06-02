# Essentials Pages — Rules

How the Trip Essentials pages behave. Covers the in-page search and the no-results state. The shared toolbar and the shared footnote are documented in `Brain/Reference/Navigation.html` and `Brain/Reference/Toolbar.html`; this file covers only what is specific to these pages.

*Trip data lives in `Trips.html` (rules in `Trips - Rules.md`). This file is about page behaviour, not trip content.*

## Pages with a search box

Six pages carry an in-page search box:

| Page | Searches over | Section/grouping it collapses |
|------|---------------|-------------------------------|
| `Trips.html` | trip cards | month dividers |
| `Plug Adapter/Plug Adapter Guide.html` | index rows + country blocks | region sections + the index table |
| `Lounges US.html` | airport cards | group headers |
| `Lounges Europe.html` | airport cards inside country blocks | country blocks |
| `Delta Routes SEA.html` | destination cards | sections (also has tier-pill filters) |
| `Delta Routes Full.html` | destination cards | hub sections + the cross-hub table |

`Travel Packing.html` has no search box.

## Search behaviour

As the reader types, matching items stay visible and non-matching items hide. Grouping containers (month dividers, region sections, country blocks, hub sections, group headers) hide when none of their items match, so no empty headers are left behind. Clearing the field restores everything.

## No-results state

When a query matches nothing, the page collapses to a clean empty state. Only three things remain visible:

1. the page title,
2. the search box, and
3. the no-match message.

Everything else hides:

- all result content,
- the page's own section jump-nav (the row of section/airport/hub links),
- any colour-key legend or tier legend,
- the index table (Plug page), and
- the **shared footnote** (the sharing link the toolbar script adds at the foot of the page).

The shared top toolbar always stays in place. As soon as the query matches again or the field is cleared, every hidden element returns.

## Why the footnote hides too

The shared footnote is appended at runtime by `toolbar.js`, after the page's own scripts cache their elements. Each page therefore looks the footnote up live, at the moment it decides the no-results state, rather than caching a reference that might not exist yet. This keeps the empty state clean regardless of when the footnote was injected.

---
*Added 2026-05-29.*
