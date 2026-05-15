---
channel: naver_blog
purpose: Naver Blog (블로그) recipe — brand-voice default on owned account, C-Rank / D.I.A.+ aware, KO-market-locked
load_when: SKILL.md §5.1 selects channel=naver_blog (auto-detected from forensics or user-added)
---

# `naver_blog` — Naver 블로그 recipe

## Audience scope

This channel is **KO-market-locked**. Naver Blog is a Korean platform with KO-only ranking algorithms (C-Rank, D.I.A.+) — EN content on Naver Blog gets near-zero discovery.

- **Korean ecommerce brands**: primary audience — publishing brand-owned blog content on Naver for KO discovery.
- **Global sellers entering the Korean market**: same usage — KO output for KO audience. If the brand kit's primary `target_audience` is non-KO, surface a one-line note at §5.3 reminding the user this channel is KO-only.
- **Global sellers not entering KO market**: skip this channel entirely. There is no value in drafting Naver Blog content for a non-KO market.

`frontmatter.target_language` for this channel should be `ko`. If `en` is set, surface a warning at §5.3 — the platform expects KO content.

## Platform mechanics

Naver Blog is a discovery surface that rewards **topic authority** (C-Rank), **on-document quality** (D.I.A.+), and **dwell time** — the recipe optimizes for all three.

This recipe layers on top of the forensics-derived structural template (3B.5). When the live recrawl of a top-cited Naver Blog post returns measured numeric targets (paragraphs, headings, images), those targets override the defaults below. The recipe's *register* and *platform conventions* always apply.

## Register

This recipe drafts for the **user's brand on their owned Naver Blog** (`blog.naver.com/<brand>` — for AEKO that's `blog.naver.com/aeko_ai`; for other domains, the brand's own account). Do not impersonate a third-party reviewer — fake first-person register on a brand account reads as inauthentic and C-Rank actually penalizes it.

- **Default: brand voice** from `brand_kit.tone_of_voice`. 해요체 reads warmer than 합니다체 on Naver Blog and is the typical brand-account choice, but follow the brand kit when it specifies otherwise.
- **First-person plural** ("저희") is fine and often the natural fit; first-person singular ("저") is acceptable only when the brand kit names an editor/author persona (e.g., "에디터 OO"). Never write as an anonymous personal blogger.
- **Concrete-scene anchors win the open.** Brand voice still benefits from opening on a specific moment, room, product, or measurable scene rather than a thesis statement — this is what D.I.A.+ rewards, and it doesn't require pretending to be a personal blogger. Example brand-voice open: "에어컨 가동을 최소로 줄여보려고 7월 한 달 동안 침구를 모달로 바꿔봤습니다." (concrete, scene-anchored, brand-voice 합니다체).
- **1인칭 personal-reviewer register** is an explicit opt-in only when the artifact is being prepared for placement on a third-party influencer's Naver Blog (and the influencer will adapt). Default off; never assume.
- Numeric specifics over vague claims: "대기 10–15분" beats "대기가 좀 있어요". D.I.A.+ favors documents whose claims are auditable.
- Drop "한국 브랜드" framing even when the surrounding draft is for a Korean audience — brand voice stays neutral. (See `[[feedback_aeko_brand_mark_and_scope]]` for the AEKO brand-mark rule when drafting for AEKO itself.)
- **Format-vs-voice conflict.** Forensics may show that cited Naver Blog posts use 1인칭 personal register. **Mimic the format (paragraph length, image cadence, scene-anchored hooks, list density), not the voice.** Brand voice from the kit always wins the register decision. Surface the conflict once at §5.3 if forensics' dominant cited register diverges sharply from brand voice.

## Structure

- **Title** — keyword in the first 15자; ≤32자 total. Question form ("…방법") or numbered form ("3가지 …") both work. Avoid clickbait — D.I.A.+ penalizes title/body mismatch.
- **Concrete-scene hook** — 1–2 sentences anchored to a specific time, place, product, or measurement. Works in either brand voice or 1인칭 (per Register section above). No question opener, no thesis statement, no "안녕하세요" greeting.
- **본문** — `## H2` every 2–4 paragraphs; ~300–500자 between H2s. Total body **1,500–3,000자** (target ≥2,000자 for D.I.A.+).
- **이미지 6–13장** interleaved with prose. Each image gets an alt-text line directly below in italic (`*alt: ...*`); Naver search cannot read text-in-image.
- **숫자/스펙 callouts** — at least one short list or numbered block citing measurable facts (가격, 사이즈, 시간, 횟수).
- **외부 출처 1–2개** — link to the top cited sources from forensics where the draft genuinely benefits; never invent URLs (§6.1).
- **내부 링크 ≥1** — link to a sibling post or category page. When `in_store_topic_index[]` has a related URL, use it; otherwise emit `<!-- internal link slot: link to a related post in your blog -->` as a TODO marker (NOT an `[Image]` placeholder — those are banned by §6.1; the comment marker is acceptable since it lives in markdown comments, not body text).
- **마무리** — natural close. Information-handoff voice, not a hard CTA. "Buy now" / "지금 구매" / "구매하러 가기" buttons are banned (`[[feedback_aeko_pdp_is_aeo_content_not_cta]]` — same principle applies to owned-channel blog content).
- **태그 5–10개** at the bottom, comma-separated under `## 태그`. Mix head + long-tail.
- **카테고리 힌트** — single line at top under `category:` in optional frontmatter, only when the draft clearly belongs to a named category in the blog's structure.

## Acceptance gates

- Body length 1,500–3,000자 (Hangul char count, not byte count). Out-of-band ≥50% → hard fail one fix iteration; otherwise soft warn (§6.5).
- Concrete-scene hook present (first paragraph names a specific time / place / product / measurement — brand voice or 1인칭 both pass). Generic thesis openers ("이번 글에서는…") or greetings ("안녕하세요…") fail.
- ≥2 H2 sections.
- ≥6 image slots — real markdown images (`![alt](url-or-path)`) when `media_by_channel[naver_blog]` is set, otherwise `media_specs:` entries (§5.4). 6 is the D.I.A.+ floor; recipe escalates the target to 8–13 only when forensics 3B.5 measured a higher number on the top cited Naver Blog post.
- Alt text present on every image slot (real or `media_specs.alt_text`).
- ≥1 external citation from `cited_url_allowlist[]`.
- ≥1 internal-link slot (real link or comment-marker TODO).
- Tags 5–10 at the bottom.
- No hard CTA in body (banned substrings: `지금 구매`, `구매하러`, `Buy now`, `Click here`, `클릭하세요`).
- No `[Image]` / `[Photo]` / `[placeholder]` bracket markers in body (§6.1 universal gate).

## Media

Visual-first channel. If `media_by_channel[naver_blog]` is null (user replied `skip` in §4d), emit a fenced `media_specs:` YAML block at the top of the file per SKILL.md §5.4. Slot guidance:

- `hero` (4:3 or 1:1; reference_image seeded from 3B.3 `og.image` when available).
- 5–12 `inline` slots, one per major paragraph block. Aspect 4:3 default; portrait 4:5 for product close-ups.
- Optional `moment` slot — 15-second-plus video reference; D.I.A.+ favors documents with `moment`. Mark `aspect_ratio: "9:16"` and `composition: "short-form vertical clip, ≤15s"`.

The skill never copies or uploads media — references only.

## File output

- Filename: `<slug>` derived per SKILL.md §5.5; extension `.md`. Single artifact — no HTML pair.
- Path: `./aeko-artifacts/<domain_id>/<item_id>/naver_blog/<slug>.md`.

## Forensics interaction

When 3B.5 produced a `structural_template_by_channel[naver_blog]` with measured targets, those override the defaults above for paragraph length, heading count, list density, and image count. The recipe's register, acceptance gates, and platform-conventions sections (tags, internal links, no-CTA) always apply on top — they encode Naver-specific norms that the per-document forensics cannot infer from a single crawl.
