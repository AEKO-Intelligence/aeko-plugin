<!--
  Per-domain technical voice overrides for /aeko-fix-technical.
  OPTIONAL. Mostly used for:
    - Custom Korean phrasing in llms.txt section headings ("제품 안내" vs "Products" vs "상품 카탈로그")
    - Brand-specific terms in JSON-LD `description` fields
    - Domain-specific deploy gotchas (e.g., "this domain is on Vercel, not Cafe24")

  Format: H2 blocks scope each rule.
    `## domain: <domain_id>` applies whenever frontmatter.domain_id matches.

  Example (delete the example sections once you paste real overrides):
-->

## domain: example-domain-uuid

- llms.txt section headings in Korean only (no English fallback)
- JSON-LD `Organization.description` always 80-120 chars (longer drops citation rate)
- This domain hosts on Vercel, not Cafe24 — DEPLOY.md should reference `vercel deploy --prod`

## glossary

| Preferred term | Avoid |
| --- | --- |
| (term) | (term) |
| (term) | (term) |
