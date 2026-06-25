---
channel: youtube
purpose: YouTube title, description, chapters, tags
load_when: SKILL.md §5.1 selects channel=youtube
---

# `youtube` — Description recipe

> Substance + quality/voice frameworks live in `../aeo-frameworks.md`. This recipe defines YouTube-specific conventions only. Paste-into-platform: YouTube renders the listing; emit clean TEXT (markdown), no HTML/JSON-LD.

- **Language follows `target_language`.** KO brands: KO title + description, tags KO head terms + a few EN long-tails (`홈카페, 라떼아트, latte art`). Global sellers: single-language end-to-end (EN tags only for EN markets). Chapter labels and on-screen text in the chosen language.
- **Title** — ≤60 chars (EN) / ≤30자 (KO); YouTube truncates on byte count. Include the prompt keyword.
- **Description** — hook in the first 200 chars / 100자 (above the fold), then full body, then chapter list (`00:00 Intro / …`, labels in `target_language`), then tags.
- Reference thumbnail (`Thumbnail: <url-or-path>`, 16:9).
- No hard CTA — information-handoff voice, not "Buy now / 지금 구매" (`[[feedback_aeko_pdp_is_aeo_content_not_cta]]`). Don't fake a third-party-reviewer voice. Link only to real URLs from the brief; never invent URLs.

## Acceptance gates

- Title ≤60 chars (EN) / ≤30자 (KO). ≥3 chapters. Hook in first 200 chars / 100자.

## File output

- Single artifact, markdown only: `./aeko-artifacts/<domain_id>/<item_id>/youtube/<slug>__youtube.md`
  (path and `<slug>` per SKILL.md §A). No HTML pair.
