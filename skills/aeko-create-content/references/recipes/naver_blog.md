---
channel: naver_blog
purpose: Naver Blog (블로그) recipe — brand-voice default on owned account, C-Rank / D.I.A.+ aware, KO-market-locked
load_when: SKILL.md §5.1 selects channel=naver_blog
---

# `naver_blog` — Naver 블로그 recipe

> Substance + quality/voice frameworks live in `../aeo-frameworks.md`. This recipe defines Naver-specific conventions only. Paste-into-platform: Naver renders the post; emit clean TEXT (markdown), no HTML/JSON-LD.

- **KO-only.** Naver ranks via C-Rank / D.I.A.+ (KO-only); EN gets near-zero discovery. `target_language` must be `ko` — warn at §5.3 if `en`. Global sellers not entering KO: skip this channel.
- **Brand voice on the owned account** (`blog.naver.com/<brand>`). Default 해요체 unless the brand kit says otherwise. Never fake a 1인칭 personal-reviewer voice — C-Rank penalizes it (opt-in only when prepping for a third-party influencer's blog). 저희 fine; 저 only with a named editor persona. Drop "한국 브랜드" framing (`[[feedback_aeko_brand_mark_and_scope]]`).
- **Concrete-scene open** — first paragraph names a specific time/place/product/measurement. No thesis opener ("이번 글에서는…"), no "안녕하세요" greeting — D.I.A.+ rewards auditable, scene-anchored claims and numeric specifics.
- **Body 1,500–3,000자 (target ≥2,000자)**, Hangul char count. `## H2` every 2–4 paragraphs.
- **Images 6–13장** interleaved, each with an alt line below in italic (`*alt: ...*`) — Naver search can't read text-in-image.
- **Tags 5–10개** at the bottom under `## 태그`, comma-separated, head + long-tail mix.
- No hard CTA — information-handoff close, not "지금 구매 / 구매하러 / Buy now" (`[[feedback_aeko_pdp_is_aeo_content_not_cta]]`).

## Acceptance gates

- Body 1,500–3,000자; out-of-band ≥50% → hard fail one fix iteration, else soft warn (§6.5).
- Concrete-scene hook present (specific time/place/product/measurement); generic thesis or greeting openers fail.
- ≥2 H2 sections. ≥6 image slots with alt text (real `![alt](url)` when `media_by_channel[naver_blog]` set, else `media_specs:` entries per §5.4). Tags 5–10.
- No hard-CTA substrings (`지금 구매`, `구매하러`, `Buy now`, `Click here`, `클릭하세요`). No `[Image]`/`[Photo]`/`[placeholder]` markers (§6.1).

## File output

- Single artifact, markdown only: `./aeko-artifacts/<domain_id>/<item_id>/naver_blog/<slug>.md` (`<slug>` per §5.5). No HTML pair.
