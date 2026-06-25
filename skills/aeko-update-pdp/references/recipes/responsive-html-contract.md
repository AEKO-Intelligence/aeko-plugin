---
recipe: responsive-html-contract
purpose: Hard rules for the generated PDP HTML — fail the run if violated
load_when: SKILL.md §5 generates HTML; Step 5 acceptance gates evaluate
---

# Responsive HTML contract (mandatory)

Fail the run if any rule below is violated. These are non-negotiable; brand-specific examples cannot relax them.

## Layout & semantics

- Mobile-first; no fixed-pixel container widths.
- `<img>` use `style="max-width:100%; height:auto; display:block; margin:0 auto;"` + non-empty `alt`.
- Semantic tags only: `<section>`, `<h2>`, `<h3>`, `<p>`, `<ul>`, `<ol>`, `<li>`.
- No executable JS (no `<script>` without `type` attr, no `on*` handlers, no `javascript:` URLs, no external CSS/`<link>`). Inline styles or single scoped `<style>` only.

## No action elements

This skill produces AEO citability content for the PDP description block — not a CTA layer. The host platform (Cafe24, Shopify) already provides the native "구매하기/장바구니" button and every other action UI in the product page.

- Do NOT emit `<a href>` or `<button>` elements anywhere in the rendered HTML, regardless of destination (same product page, size guide, brand story, separate landing page). This rule applies to every section, not just `aeko-cta`.
- Inline anchors that are clearly informational rather than action-driving (e.g. `<a href="mailto:...">` for a contact email, or a phone-number link wrapped in prose) are allowed only when prose explicitly requests them; in doubt, omit.
- CSS classes like `.aeko-cta-buttons` and any related styling must not be emitted.
- The `aeko-cta` section heading is "구매 안내" (KO) / "Purchase info" (EN), never "구매하기" / "Buy now".

## Citability baseline (apply even when prose is silent)

- 80–167 word passages per block.
- Name the subject explicitly in every paragraph (no pronoun opens).
- Each section opens with a 1–2 sentence direct answer.
- "X is a Y that Z" structures for core claims.
- Include specific numbers / dimensions / years where possible.

## Frontmatter must_include / forbidden / sections_required

- `must_include` — every string MUST appear in the rendered HTML.
- `forbidden` — none MAY appear.
- `sections_required` — every entry maps to a `<section>` heading (case-insensitive, trimmed). Missing → iterate or fail; do NOT call `aeko_complete_action_item`.

## Pending verifications

When a factual value is absent from OCR / content context / prose, do NOT emit `[VERIFY: <field>]` badges in the visible HTML and do NOT introduce a `.aeko-verify` style class. Production HTML must never carry visible VERIFY markers.

Instead, append an entry to an in-memory `pending_verifications` list (each entry: `{field, section, suggested_value_if_any, why_needed}`) and resolve it interactively with the user in Step 5b before finalizing. Never include unresolved values in JSON-LD (omit missing JSON-LD keys entirely).

The final artifact must contain ZERO `[VERIFY: <field>]` badges in visible HTML and ZERO `.aeko-verify`-style decorations. The only acceptable unresolved-state form is HTML comments produced by the explicit `두기` / `leave` reply.

Plan-level structural warnings (e.g. `prompts_to_rank_on_missing` from the FAQ thin-input exception) are different — they cannot be filled in by a user-supplied value, so they bypass Step 5b and are surfaced as plan warnings in Step 9 summary.
