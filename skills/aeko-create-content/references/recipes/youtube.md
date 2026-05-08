---
channel: youtube
purpose: YouTube title, description, chapters, tags
load_when: SKILL.md §5.1 selects channel=youtube
---

# `youtube` — Description recipe

## Structure

- **Title** — ≤60 chars, includes the prompt keyword
- **Description**:
  - First 200 chars = hook (above the fold)
  - Then full description
  - Then chapter list: `00:00 Intro / …`
  - Then tags

## Acceptance gates

- Title ≤60 chars
- ≥3 chapters
- Hook in first 200 chars

## Media

Visual-first channel. Reference media in description (`Thumbnail: <url-or-path>`). If `media_by_channel[channel]` is null, emit a `media_specs:` YAML block (SKILL.md §5.4) with at minimum a `thumbnail` slot (16:9) and a `hero` slot if the description prose calls for one.

## File output

Filename is the literal `youtube.md`. Single artifact, markdown only — no HTML pair.
