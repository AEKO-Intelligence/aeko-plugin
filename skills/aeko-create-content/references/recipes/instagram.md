---
channel: instagram
purpose: Instagram caption + alt text + optional carousel
load_when: SKILL.md §5.1 selects channel=instagram
---

# `instagram` — Caption recipe

## Audience scope

Language-neutral channel. Output follows `frontmatter.target_language`:

- **Korean ecommerce brands** (`target_language=ko`): KO caption with KO+EN hashtag mix (`#홈인테리어 #homedecor`). Bilingual hashtags help discovery on both KO and EN-curious Korean audiences and reach Korean diaspora.
- **Global sellers** (`target_language=en` or other): single-language hashtags matching the brand's target market. EN-only for US/UK/global brands; locale-specific (FR, JA, ES …) when the brand kit names a non-EN market. Don't bolt KO hashtags onto EN-market content — it dilutes the targeting.
- Brand kit `target_audience` overrides the language default if it explicitly names a different market.

## Structure

- **Caption**
  - 1 hook line
  - 3–5 body lines
  - 5–12 hashtags — language mix per Audience scope above
- **Alt text** — ≤125 chars, accessibility-friendly. Language matches the caption.
- **Optional 5-slide carousel outline** — only if forensics suggests a carousel beats a single-image listicle

## Acceptance gates

- Hook ≤2 lines
- Hashtags 5–12
- Alt text present

## Media

Visual-first channel. If `media_by_channel[channel]` is set, write `media:` field at top of file referencing the asset; alt text rendered in its own section. If null, emit a `media_specs:` YAML block (SKILL.md §5.4) with `hero` (1:1 typical) and any inline carousel slots the outline calls for.

## File output

Filename is the literal `instagram.md` (channel slug, not the title slug). Single artifact, markdown only — no HTML pair.
