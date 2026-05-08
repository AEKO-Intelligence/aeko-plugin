<!--
  Per-domain voice overrides for /aeko-update-pdp.

  This file is OPTIONAL. The skill reads it (when present) at Step 5 alongside the
  brand-kit voice and uses it to resolve conflicts between brand-kit register and
  PDP-specific conventions.

  Format: H2 headings scope each override block to a domain.
    `## domain: <domain_id>` applies whenever frontmatter.domain_id matches.
    Free-form bullets inside.

  Example (delete the example sections once you paste real overrides):
-->

## domain: example-domain-uuid

- Hero section subject must always include the model number in parentheses (e.g., "에코 베딩 (BD-200)")
- Benefits section must use 4-item bullet lists exactly (not 3, not 5) — brand convention
- Forbidden in any section: "베스트셀러", "1위", "최고급" — superlatives banned per legal review
- "Purchase info" section heading: use "구매 안내 및 배송" (longer than recipe default)

## glossary

| Preferred term | Avoid |
| --- | --- |
| (term) | (term) |
| (term) | (term) |
