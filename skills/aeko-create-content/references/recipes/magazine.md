---
channel: magazine
purpose: Vogue-style editorial recipe — follows target_language with KO/EN guidance and native-register fallback
load_when: SKILL.md §5.1 selects channel=magazine
---

# `magazine` — Editorial recipe

> Substance + quality/voice frameworks live in `../aeo-frameworks.md`. This recipe defines magazine format conventions only. Republished by a third-party editor/outlet that controls final markup — emit clean TEXT (markdown) only; no HTML, no structured data.

- **Language follows `target_language`.** KO brands: Vogue-Korea register — 감각적 sensory verbs, 해요체 or 합니다체 per brand kit, KO-market cultural cues (계절감, 라이프스타일 scenes). Global sellers: Vogue-US / Harper's Bazaar editorial English; don't fabricate cultural specificity — stay neutral if the brand kit names no market. Other languages: that market's native magazine register.
- **Hook + thesis** — italic hook quote ≤25 words, then a 2–3문장 editor's note framing the piece.
- **3–5 sections**, each with a subhead + body — lifestyle scenes weaving the product/topic in, NOT a listicle. Subject named per paragraph; sensory verbs throughout.
- **Optional callout** — one short pull-quote / aside where it earns the space.
- **Conclusion** — a closing scene or reflection, not a hard CTA.
- Minimal hashtags (this is a magazine, not social). Information-handoff voice, not "Buy now / 지금 구매" (`[[feedback_aeko_pdp_is_aeo_content_not_cta]]`). Don't fake a third-party-reviewer voice. Link only to real URLs from the brief; never invent URLs.

## Acceptance gates

- Hook quote present. ≥3 narrative scenes/sections. No bullet lists.

## File output

- Single artifact, markdown only: `./aeko-artifacts/<domain_id>/<item_id>/magazine/<slug>.md` (`<slug>` per §5.5).
