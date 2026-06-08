---
channel: tiktok
purpose: 30–60 second TikTok script with beats
load_when: SKILL.md §5.1 selects channel=tiktok
---

# `tiktok` — Script recipe

> Substance + quality/voice frameworks live in `../aeo-frameworks.md`. This recipe defines TikTok-specific conventions only. Paste-into-platform: TikTok renders the post; emit clean TEXT (markdown), no HTML/JSON-LD.

- **Language follows `target_language`.** KO brands: KO voiceover + KO on-screen text, 해요체 spoken register, KO+EN hashtag mix (`#홈카페 #homecafe`). Global sellers: single-language throughout. Never mix languages across audio + on-screen text on one script — TikTok narrows distribution when they diverge.
- **30–60s script as numbered beats** — `[0–3s] hook · [3–10s] context · …`. The `[0–3s]` hook is the highest-leverage line regardless of audience (≤15s hook window; lead beat ≤3s).
- **Every beat** carries BOTH an on-screen text line AND a voiceover line (language per above).
- **Audio/visual spec** — reference media per beat (`[on-screen]: image at <path>`), aspect 9:16.
- **3–6 hashtags** at the bottom (language per above).
- Soft CTA only — information-handoff voice, not "Buy now / 지금 구매" (`[[feedback_aeko_pdp_is_aeo_content_not_cta]]`). Don't fake a third-party-reviewer voice.

## Acceptance gates

- Total runtime 30–60s. ≥1 hook beat ≤3s. Every beat has both on-screen and voiceover lines.

## File output

- Literal filename `tiktok.md`. Single artifact, markdown only — no HTML pair.
