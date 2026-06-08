---
channel: press_release
purpose: Press release recipe — language-aware (Korean 합니다체 OR English AP-style), for both KO- and EN-market brands
load_when: SKILL.md selects channel=press_release
---

# `press_release` — press release recipe (KO + EN)

> Substance + quality/voice frameworks live in `../aeo-frameworks.md`. This recipe defines press-release
> format conventions only. Republished by a third-party outlet that controls final markup — emit clean
> TEXT (markdown) only; no HTML, no structured data.

**Language-aware.** Write in the brief's `target_language`. Both Korean and English markets are
first-class — do not assume KO. Pick the register block below by language; the *structure* (lead with
5W1H, one quote, boilerplate, contact) is shared.

- **Korean (`ko`):** **합니다체** (formal) throughout — required even if brand voice elsewhere is 요체; the
  format wins. Headline ≤40자; 부제 한 줄; 리드는 첫 2문장에 5W1H; 본문 3–4단락; 문의처 line at the bottom.
- **English (`en`):** formal **AP-style**. Headline in title case (≤ ~12 words); optional dateline
  (`CITY, Country — Mon DD, YYYY —`); lead paragraph carries the 5W1H; 3–4 body paragraphs; "Media
  Contact" block at the bottom.

Shared across both languages:
- **One quote** from a named spokesperson (CEO or product lead).
- **Boilerplate** — one "About <Brand>" paragraph derived from `brand_kit.brand_voice_summary`. Never
  hard-code "AEKO"; this drafts for the user's domain/brand.
- **Embargo line** at the top if the user supplies one (KO: `엠바고:` / EN: `EMBARGO until …`).
- Link only to real URLs from the brief; never invent URLs. No hard-CTA / "Buy now" voice
  (`[[feedback_aeko_pdp_is_aeo_content_not_cta]]`). Keep the brand mark in Latin script and drop
  "한국 브랜드"-style framing (`[[feedback_aeko_brand_mark_and_scope]]`).

## Acceptance gates

- 5W1H present in the lead; register matches `target_language` (합니다체 for KO / AP-style for EN);
  ≥1 named quote; "About <Brand>" boilerplate present; contact/문의처 line present.

## Media

Prose-only channel — no `media_specs:` block in the body. May add a media attachment list at the bottom
(KO: `## 첨부 참고` / EN: `## Media assets`) only if the frontmatter prose explicitly requests it.

## File output

- Single artifact, markdown only: `./aeko-artifacts/<domain_id>/<item_id>/press_release/<slug>__press_release.md`
  (`<slug>` per SKILL.md §A.3).
