---
channel: youtube
purpose: YouTube title, description, chapters, tags
load_when: SKILL.md §5.1 selects channel=youtube
---

# `youtube` — Description recipe

## Audience scope

Language-neutral channel. Output follows `frontmatter.target_language`:

- **Korean ecommerce brands** (`target_language=ko`): KO title and description. Tags include KO head terms + a few EN long-tails when relevant (`홈카페, 라떼아트, latte art`). Korean YouTube viewers commonly search bilingually for product categories.
- **Global sellers** (`target_language=en` or other): single-language title and description matching the target market. EN tags only for EN markets — mixing KO tags hurts EN discovery.
- Chapter labels and on-screen text in the description follow the chosen language end-to-end.

## Structure

- **Title** — ≤60 chars (Latin / EN) or ≤30자 (Hangul). YouTube uses byte count under the hood; 60 EN chars ≈ 30 Hangul chars before mobile truncation. Include the prompt keyword.
- **Description**:
  - First 200 chars / 100자 = hook (above the fold)
  - Then full description
  - Then chapter list: `00:00 Intro / …` — chapter labels in `target_language`
  - Then tags — language mix per Audience scope above

## Acceptance gates

- Title ≤60 chars (EN) / ≤30자 (KO)
- ≥3 chapters
- Hook in first 200 chars (EN) / 100자 (KO)

## Media

Visual-first channel. Reference media in description (`Thumbnail: <url-or-path>`). If `media_by_channel[channel]` is null, emit a `media_specs:` YAML block (SKILL.md §5.4) with at minimum a `thumbnail` slot (16:9) and a `hero` slot if the description prose calls for one.

## File output

Filename is the literal `youtube.md`. Single artifact, markdown only — no HTML pair.
