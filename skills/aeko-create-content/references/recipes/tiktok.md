---
channel: tiktok
purpose: 30–60 second TikTok script with beats
load_when: SKILL.md §5.1 selects channel=tiktok
---

# `tiktok` — Script recipe

## Audience scope

Language-neutral channel. Output follows `frontmatter.target_language`:

- **Korean ecommerce brands** (`target_language=ko`): KO voiceover + KO on-screen text. Hashtags mix KO and EN (`#홈카페 #homecafe`) — TikTok KO discovery responds well to the bilingual pattern. Caption tone is closer to 해요체 spoken register, not 합니다체.
- **Global sellers** (`target_language=en` or other): single-language voiceover and on-screen text matching the target market. EN-market scripts use conversational US/UK register; locale-specific scripts use that locale's spoken norms. Don't mix languages on a single script — TikTok's algorithm narrows distribution when on-screen and audio languages diverge.
- TikTok cares more about hook strength than language; the `[0–3s] hook` beat is the highest-leverage line regardless of audience.

## Structure

30–60 second script, structured as numbered beats.

- **Beats** — `[0–3s] hook · [3–10s] context · …` format
- **On-screen text** per beat — language per Audience scope above
- **Voiceover line** per beat — language per Audience scope above
- **3–6 hashtags** at the bottom — language per Audience scope above

## Acceptance gates

- Total runtime in 30–60s window
- ≥1 hook beat ≤3s
- Every beat has BOTH on-screen and voiceover lines

## Media

Visual-first channel. Reference media inside the relevant beat (`[on-screen]: image at <path>`). If `media_by_channel[channel]` is null, emit a `media_specs:` YAML block (SKILL.md §5.4) with one entry per major beat (hero + per-beat insert frames as needed; aspect ratio 9:16).

## File output

Filename is the literal `tiktok.md`. Single artifact, markdown only — no HTML pair.
