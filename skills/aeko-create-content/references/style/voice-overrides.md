<!--
  Per-domain or per-channel voice overrides.

  This file is OPTIONAL. The skill reads it (when present) at SKILL.md §5.3 alongside the
  brand-kit voice and uses it to resolve conflicts between brand kit, recipe, and channel
  format requirements.

  When to use this file:
    - You run multiple brands from one AEKO install and they have different voices.
    - One channel needs a different register than the rest of your voice (e.g., 보도자료
      always 합니다체 even though brand voice is 요체 — though the skill already enforces
      this for 보도자료 specifically).
    - You want to lock down a glossary of preferred terms / forbidden words that the
      brand kit doesn't capture.

  Format:
    - Use H2 headings to scope each override block.
    - Domain scope: `## domain: <domain_id>` — applies whenever frontmatter.domain_id matches.
    - Channel scope: `## channel: <channel>` — applies whenever the channel is in selection.
    - Combined: `## domain: <id>, channel: <name>` — applies only when both match.
    - Free-form bullets inside each block.

  Example (delete this comment block + the example sections once you paste real overrides):
-->

## domain: example-domain-uuid, channel: instagram

- 항상 영어 hashtag만 사용 (한글 hashtag 금지)
- Hook은 항상 질문형으로 시작
- Forbidden: "출시", "런칭" — 우리는 "공개"라고 말함

## channel: 보도자료

- Boilerplate 마지막 줄에 항상 영문 사명을 병기 (예: "<브랜드명> (<English Name>)")
- Quote는 항상 직책+이름 순서 (이름+직책 X)

## glossary

| 선호 용어 | 피해야 할 용어 |
| --- | --- |
| (term) | (term) |
| (term) | (term) |
