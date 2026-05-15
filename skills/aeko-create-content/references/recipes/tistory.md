---
channel: tistory
purpose: Tistory long-form blog recipe — Google + Daum/Kakao surface, AEO-first structure
load_when: SKILL.md §5.1 selects channel=tistory (auto-detected from forensics or user-added)
---

# `tistory` — Tistory recipe

## Audience scope

This channel is primarily **KO-market-oriented** but more permissive than Naver Blog because Tistory surfaces through Google (which indexes all languages) in addition to Daum/Kakao.

- **Korean ecommerce brands**: primary audience — publishing brand-owned long-form content on Tistory for KO + Google discovery.
- **Global sellers entering the Korean market**: same usage — KO output is the recommended default.
- **Global sellers not entering KO market**: EN content on Tistory *can* rank in Google but loses the Daum/Kakao referral path — usually a generic blog platform (the brand's own site, Medium, Substack) outperforms Tistory for EN-only. If the user still wants Tistory EN output, the recipe's structural rules below apply with EN substituted; expect lower KO referral traffic.

`frontmatter.target_language` defaults to `ko`. `en` is allowed but surface a one-line note at §5.3 that EN Tistory loses the Daum/Kakao path.

## Platform mechanics

Tistory posts surface across **Google**, **Daum/Kakao**, and (via referral) Naver — the recipe optimizes for the union: clear semantic structure (Google), AEO answer-first openings (AI engines), and topical authority (search engines generally).

This recipe layers on top of the forensics-derived structural template (3B.5). When the live recrawl of a top-cited Tistory post returns measured numeric targets, those override the defaults below. The recipe's *register*, *AEO discipline*, and *platform conventions* always apply.

## Register

This recipe drafts for the **user's brand on their owned Tistory** (`<brand>.tistory.com` — for AEKO that's `aeko.tistory.com`; for other domains, the brand's own subdomain). Brand voice, not personal-blogger voice — Tistory rewards documents that read as *expertise*, and impersonating a personal blogger from a brand account looks inauthentic.

- **Default: brand voice** from `brand_kit.tone_of_voice`. 합니다체 reads as the most natural fit for Tistory's expertise register, with 해요체 acceptable when the brand kit specifies a warmer voice.
- **First-person plural** ("저희") is fine when the brand kit allows it; first-person singular ("저") is acceptable only when the brand kit names an editor/author persona. Default toward 3인칭 brand-objective voice with occasional 저희 callouts.
- **Tistory's register sits between a magazine and a Naver Blog** — more disciplined than 1인칭 Naver review, less formal than 보도자료. Personal anecdote belongs in service of an explanatory point, not as the whole arc.
- **Format-vs-voice conflict** (same rule as `naver_blog`): forensics may surface 1인칭 cited posts. Mimic format (paragraph length, list density, AEO answer-first cadence) but never the voice — brand kit wins.
- Numeric specifics over vague claims. Auditable claims win.
- No "한국 브랜드" framing; brand voice stays neutral.

## Structure

- **Title (H1)** — single `# ` H1, keyword in the first 25자, ≤45자 total. Numbered or "방법/가이드/완벽정리" forms perform well; avoid "?" titles unless the body genuinely answers.
- **메타 한 줄** — single italic paragraph directly under H1 summarizing the article in ≤120자. Doubles as the `<meta name="description">` candidate when the user downstream renders to HTML.
- **본문** — 3–6 `## H2` sections. **Each H2 opens with a 2–3 sentence direct answer to the implied question** (AEO discipline). Bulk explanation follows the answer; never bury the answer past the third sentence.
- `### H3` subsections allowed inside any H2, max depth `###` (don't reach for `####`).
- Paragraphs **≤167 words** (≤300자 KO) — matches the §6.2 prose-channel structural target.
- **표/리스트** — use when comparing items or enumerating steps; lists fail flat prose 2–3× on engagement in Tistory data. Mix prose-heavy and list-heavy sections by topic, not formula.
- **이미지 3–8장** interleaved at section boundaries. Each gets alt text on the line below (`*alt: ...*`).
- **내부 링크 ≥2** — link to category-sibling posts on the same Tistory domain. When `in_store_topic_index[]` exposes related URLs, use them; otherwise emit `<!-- internal link slot: link to a related post on this Tistory -->` markers (markdown comment, not body text — distinct from banned `[Image]` placeholders).
- **외부 출처 ≥1** — link to a top-cited forensics source where the draft genuinely benefits. Never invent URLs (§6.1).
- **마무리** — short "정리" or "참고" section, 2–3 sentences. Information-handoff close, no hard CTA.
- **태그 5–10개** at the bottom under `## 태그`. Comma-separated, mix of head + long-tail.

## AEO discipline (answer-first)

For every `## H2` section, the first 2–3 sentences MUST directly answer the question implied by the heading. This is the rule that makes Tistory drafts citable by AI engines — engines prefer documents where the answer is *adjacent to the heading*, not buried.

Worked example:

```markdown
## 여름 침구로 어떤 소재가 좋을까요?

여름 침구는 통기성과 흡습성이 핵심이며, 모달과 텐셀이 가장 안정적인 선택입니다. 면 100%는 흡수력은 좋지만 건조 속도가 느려 장마철엔 불리합니다. 가격대와 세탁 빈도에 따라 둘을 조합해 쓰는 경우도 많습니다.

[그 뒤로 본격 본문 — 소재별 비교, 가격대, 관리 팁 …]
```

Acceptance gate §6.2 checks that each H2's opening paragraph contains a recognizable answer pattern (a declarative sentence stating "X is Y" or "X means Y"); H2 sections that open with a question, anecdote, or table-of-contents pointer count as misses.

## Acceptance gates

- Single `# ` H1 (exactly one). Multiple H1s → hard fail.
- ≥3 `## H2` sections, each with answer-first opening (per AEO discipline above). <3 H2s with answer-first openings → hard fail one fix iteration.
- Body length 1,500–3,000자 (Hangul char count). Out-of-band ≥50% → hard fail; otherwise soft warn (§6.5).
- ≥1 list or table block in the body (not in the closing 태그 section).
- ≥2 internal-link slots (real link or comment-marker TODO).
- ≥1 external citation from `cited_url_allowlist[]`.
- ≥3 image slots — real markdown images when `media_by_channel[tistory]` is set, otherwise `media_specs:` entries (§5.4).
- Alt text present on every image slot.
- Tags 5–10 at the bottom.
- No hard CTA in body (banned substrings: `지금 구매`, `구매하러`, `Buy now`, `Click here`, `클릭하세요`).
- No `[Image]` / `[Photo]` / `[placeholder]` bracket markers in body (§6.1 universal gate).

## Media

Visual-first channel. If `media_by_channel[tistory]` is null, emit a fenced `media_specs:` YAML block at the top of the file per SKILL.md §5.4. Slot guidance:

- `hero` (16:9 or 4:3; reference_image seeded from 3B.3 `og.image` when available).
- 2–6 `inline` slots at section boundaries. 4:3 default.
- Tistory does not have a Naver-style `moment` equivalent — skip the video slot unless the draft body explicitly calls for an embed.

The skill never copies or uploads media — references only.

## File output

- Filename: `<slug>` derived per SKILL.md §5.5; extension `.md`. Single artifact — no HTML pair at the channel level. (The downstream `/aeko-publish-content` step may render to HTML on its own.)
- Path: `./aeko-artifacts/<domain_id>/<item_id>/tistory/<slug>.md`.

## Forensics interaction

When 3B.5 produced a `structural_template_by_channel[tistory]` with measured numeric targets (paragraph length, heading count, list density, image count), those override the defaults above. The recipe's register, AEO discipline, and platform-conventions sections (single H1, answer-first openings, internal links, tags, no-CTA) always apply on top.
