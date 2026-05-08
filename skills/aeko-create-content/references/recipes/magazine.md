---
channel: magazine
purpose: Vogue-style editorial recipe (KO/EN per target_language)
load_when: SKILL.md §5.1 selects channel=magazine
---

# `magazine` — Editorial recipe

Vogue-style editorial. Target language follows `frontmatter.target_language` (KO default, EN if `target_language=en`).

## Structure

- **Hook quote** — italic, ≤25 words
- **Editor's note** — one paragraph
- **3–4 lifestyle scenes** weaving the product/topic in (NOT a listicle)
- Subject named per paragraph
- Sensory verbs throughout
- Minimal hashtags (this is a magazine, not social)

## Acceptance gates

- Hook quote present
- Narrative scenes ≥3
- No bullet lists

## Pairs with HTML/JSON-LD

`magazine` is an editorial channel: it writes BOTH `<slug>.md` AND `<slug>.html` with embedded `Article` JSON-LD. See `references/recipes/editorial-html-jsonld.md`.

## Media

Visual-first channel. If `media_by_channel[channel]` is null (user replied `skip`), emit a `media_specs:` YAML block at the top with one entry per slot the recipe expects (typically `hero` + 0–3 `inline`). See SKILL.md §5.4 for the exact YAML shape.
