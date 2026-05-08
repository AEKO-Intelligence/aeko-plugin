---
channel: tiktok
purpose: 30–60 second TikTok script with beats
load_when: SKILL.md §5.1 selects channel=tiktok
---

# `tiktok` — Script recipe

30–60 second script, structured as numbered beats.

## Structure

- **Beats** — `[0–3s] hook · [3–10s] context · …` format
- **On-screen text** per beat
- **Voiceover line** per beat
- **3–6 hashtags** at the bottom

## Acceptance gates

- Total runtime in 30–60s window
- ≥1 hook beat ≤3s
- Every beat has BOTH on-screen and voiceover lines

## Media

Visual-first channel. Reference media inside the relevant beat (`[on-screen]: image at <path>`). If `media_by_channel[channel]` is null, emit a `media_specs:` YAML block (SKILL.md §5.4) with one entry per major beat (hero + per-beat insert frames as needed; aspect ratio 9:16).

## File output

Filename is the literal `tiktok.md`. Single artifact, markdown only — no HTML pair.
