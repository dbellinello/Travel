# Universal Formatting Rules

> **Source of truth for how the CORE RULES docs look in a browser.**
>
> Not for guides. Guides have their own formatting that lives in `Brain/`.
> Browser-first as of 2026-05-09 — Google Docs import constraints no longer apply.

All files in this folder start with `Universal Formatting Rules - ` so if any of them wander out, you (or future Claude) can tell at a glance where they belong.

---

## Scope — what lives in this folder

This folder is the single home for **all HTML and CSS formatting rules across the workspace**, per the canonical pointer in `Brain/CORE RULES/Rules for Claude.html` § 2 ("Where things go") and § 6 DriftyCat: *"Any CSS rule, HTML formatting convention, or visual style instruction belongs in `Travel/Universal Formatting Rules/Universal Formatting Rules - Rules.html`."*

That covers two layers, both governed by this folder:

| Layer | What it formats | Where the rule lives |
|---|---|---|
| **Rule-doc formatting** | The look of the meta rule documents themselves — i.e., the `.html` files in `Brain/CORE RULES/`. Heading sizes, banner color, paragraph spacing, the `<style>` block inlined into every rule doc. | §§ 1–5 of `Universal Formatting Rules - Rules.html` |
| **Guide formatting** | The HTML structure and CSS for the rendered city guides — element wrappers (which tag holds which content), entry HTML shape per extras section, the stylesheet link, font stack. | §§ 6+ of `Universal Formatting Rules - Rules.html` |

**Stylesheet split — where the CSS files live, which is different from where the rules live:**
- `Universal Formatting Rules - _style.css` — the CSS that's inlined into every rule doc (rule-doc formatting). Lives in this folder.
- `Brain/guide_v2.css` — the CSS that styles the shipped guides (guide formatting). Lives in `Brain/` so the GitHub Pages copy path stays clean (`Guides/guide_v2.css` is the deployed copy).

The **rules** about both stylesheets — naming conventions, wrappers, structural HTML, what the validator enforces — live in `Universal Formatting Rules - Rules.html` regardless of where the CSS files themselves sit.

**Content vs. structure split.** CORE RULES (`Brain/CORE RULES/`) own the **content** of every guide section (what qualifies, how many entries, length caps, which platforms). This folder owns the **HTML structure that carries that content** (which tag wraps the description, which class names matter, what shape an entry takes). The two never overlap: a CORE RULES file never specifies a tag name, and this folder never specifies a content cap — but the validator reads both.

---

## Files in this folder

| File | What it is |
|------|------------|
| **`Universal Formatting Rules - Rules.html`** | Complete reference — canonical CSS, HTML shell, building blocks, whitespace rules, new-doc checklist. Open in a browser. |
| **`Universal Formatting Rules - _style.css`** | Canonical CSS. Copy into every rule-doc HTML's `<style>` block. |
| **`Universal Formatting Rules - README.md`** | This file. |

---

## The rule in one sentence

**Inline the canonical CSS into every rule-doc HTML's `<head>` as a `<style>` block.**

---

## Reference HTML (gold standards)

When building or fixing a rule-doc HTML, copy from these — confirmed-working examples in `Brain/CORE RULES/`:

- `Stops Structure.html` — biggest fully-working example
- `Day Structure.html` — medium length with templates and lists
- `Pickleball - Extra Section.html` — proven extra section with embedded base64 icon

---

## History

Created 2026-05-02 (originally named `Universal Rules`, renamed `Universal Formatting Rules` same day). All files prefixed with the folder name 2026-05-02 for cross-folder traceability.

Files originally moved here from:
- `_style.css` — was in `Travel/HTML Rules Before Conversion/`. Old copy archived at `Travel/archive/_style.css.from_Doc_Workshop_2026-05-02`.
- `Formatting Rules.md` — written from scratch 2026-05-02 as the comprehensive reference.

Files later archived (legacy / redundant):
- `HTML Snippets.md` (was `Travel/Brain/mds/`) → `Travel/archive/HTML Snippets.md_legacy_from_UniversalFormattingRules_2026-05-02.md`. Older CSS shell + guide-content structural templates that may belong in Brain if/when needed.
- `Formatting Rules For Any Doc.md.gdoc` (was Travel root) → `Travel/archive/Formatting Rules For Any Doc.md_legacy_2026-05-02.gdoc`. Older Drive doc, mostly redundant with `Brain/mds/Separation Map.md` content.

Brain retains all guide-formatting (`guide_v2.css`, photo rules, hotel banner rules, etc.) — those are how guides are made, and they belong in Brain.
