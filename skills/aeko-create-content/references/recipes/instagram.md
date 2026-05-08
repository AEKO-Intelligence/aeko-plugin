---
channel: instagram
purpose: Instagram caption + alt text + optional carousel
load_when: SKILL.md §5.1 selects channel=instagram
---

# `instagram` — Caption recipe

KO default, EN if `frontmatter.target_language=en`.

## Structure

- **Caption**
  - 1 hook line
  - 3–5 body lines
  - 5–12 hashtags (KO + EN mix)
- **Alt text** — ≤125 chars, accessibility-friendly
- **Optional 5-slide carousel outline** — only if forensics suggests a carousel beats a single-image listicle

## Acceptance gates

- Hook ≤2 lines
- Hashtags 5–12
- Alt text present

## Media

Visual-first channel. If `media_by_channel[channel]` is set, write `media:` field at top of file referencing the asset; alt text rendered in its own section. If null, emit a `media_specs:` YAML block (SKILL.md §5.4) with `hero` (1:1 typical) and any inline carousel slots the outline calls for.

## File output

Filename is the literal `instagram.md` (channel slug, not the title slug). Single artifact, markdown only — no HTML pair.
