---
channel: instagram
purpose: Instagram caption + alt text + optional carousel
load_when: SKILL.md §5.1 selects channel=instagram
---

# `instagram` — Caption recipe

> Substance + quality/voice frameworks live in `../aeo-frameworks.md`. This recipe defines Instagram-specific conventions only. Paste-into-platform: Instagram renders the post; emit clean TEXT (markdown), no HTML/JSON-LD.

- **Language follows `target_language`.** KO brands: KO caption with KO+EN hashtag mix (`#홈인테리어 #homedecor`). Global sellers: single-language hashtags matching the target market — don't bolt KO hashtags onto EN content. Content context overrides if it names a different market.
- **Caption** — 1 hook line, then 3–5 body lines, then 5–12 hashtags (language per above).
- **Alt text** — ≤125 chars, language matches caption.
- **Optional 5-slide carousel outline** only when a multi-slide walkthrough genuinely beats a single image.
- No hard CTA — information-handoff voice, not "Buy now / 지금 구매" (`[[feedback_aeko_pdp_is_aeo_content_not_cta]]`). Don't fake a third-party-reviewer voice.

## Acceptance gates

- Hook ≤2 lines. Hashtags 5–12. Alt text present.

## File output

- Single artifact, markdown only: `./aeko-artifacts/<domain_id>/<item_id>/instagram/<slug>__instagram.md`
  (path and `<slug>` per SKILL.md §A). No HTML pair.
