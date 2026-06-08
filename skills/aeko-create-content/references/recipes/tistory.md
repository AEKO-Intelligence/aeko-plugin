---
channel: tistory
purpose: Tistory long-form blog recipe — Google + Daum/Kakao surface, AEO-first structure
load_when: SKILL.md §5.1 selects channel=tistory
---

# `tistory` — Tistory recipe

> Substance + quality/voice frameworks live in `../aeo-frameworks.md`. This recipe defines Tistory-specific conventions only. Paste-into-platform: Tistory renders the post; emit clean TEXT (markdown), no HTML/JSON-LD.

- **KO default; EN allowed.** Tistory surfaces via Google (all languages) + Daum/Kakao (KO only). `target_language` defaults to `ko`; if `en`, note at §5.3 that EN loses the Daum/Kakao referral path (a generic blog usually beats Tistory for EN-only).
- **Brand voice on the owned subdomain** (`<brand>.tistory.com`). Default 합니다체 (expertise register), 해요체 if the brand kit specifies warmer. Tistory sits between magazine and Naver Blog — anecdote serves an explanatory point, never the whole arc. Do not fake 1인칭 or third-party-reviewer voice. No "한국 브랜드" framing.
- **Single `# ` H1** — keyword in first 25자, ≤45자. **메타 한 줄** italic paragraph under H1, ≤120자.
- **Answer-first H2s (AEO core).** Each `## H2` opens with a 2–3 sentence declarative answer ("X is Y") to the question its heading implies — never bury the answer past sentence 3, and don't open with a question/anecdote/TOC pointer. Body 3–6 H2 sections.
- **Body 1,500–3,000자**, Hangul char count. Paragraphs ≤300자 (§6.2). ≥1 list or table block. Images 3–8장 at section boundaries, each with `*alt: ...*` below.
- **Tags 5–10개** at the bottom under `## 태그`, head + long-tail mix.
- No hard CTA — information-handoff close (`[[feedback_aeko_pdp_is_aeo_content_not_cta]]`).

## Acceptance gates

- Exactly one `# ` H1 (multiple → hard fail).
- ≥3 `## H2` sections, each answer-first (§6.2 checks for a declarative "X is Y" opener; question/anecdote/TOC openers count as misses); <3 → hard fail one fix iteration.
- Body 1,500–3,000자; out-of-band ≥50% → hard fail, else soft warn (§6.5). ≥1 list/table block (not in 태그 section).
- ≥3 image slots with alt (real images when `media_by_channel[tistory]` set, else `media_specs:` per §5.4). Tags 5–10.
- No hard-CTA substrings (`지금 구매`, `구매하러`, `Buy now`, `Click here`, `클릭하세요`). No `[Image]`/`[Photo]`/`[placeholder]` markers (§6.1).

## File output

- Single artifact, markdown only: `./aeko-artifacts/<domain_id>/<item_id>/tistory/<slug>.md` (`<slug>` per §5.5). No HTML pair.
