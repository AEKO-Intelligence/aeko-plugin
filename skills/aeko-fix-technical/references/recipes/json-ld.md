---
recipe: json-ld
purpose: schema.org JSON-LD generation rules for site-level / brand-level schemas
load_when: SKILL.md §3 dispatches artifact_type=json_ld or technical_bundle includes it
---

# `json_ld` recipe

This recipe covers **site-level / brand-level** JSON-LD (Organization, WebSite, BreadcrumbList, Article, BlogPosting). Product-level JSON-LD lives in `/aeko-update-pdp` (see that skill's `references/recipes/json-ld-schemas.md`).

## Spec rules (schema.org + AEO)

- `@context: "https://schema.org"` on every block.
- Common types: `Organization`, `WebSite`, `BreadcrumbList`, `Article`, `BlogPosting`, `Review`, `AggregateRating`.
- Include `sameAs` on Organization when Wikipedia / Wikidata entity exists (use WebSearch to verify; don't fabricate).
- No trailing commas, no comments — valid JSON only.
- Script tag for embedding: `<script type="application/ld+json">...</script>`. `type` attribute exactly that string.
- For Korean brands, include Korean and English forms via `alternateName` or `@graph` split.

## Generation

1. Derive `schema_type` from prose + `frontmatter.validation_hints` (contract field for JSON-LD items).
2. For `Organization` / `Brand` schemas: run a targeted `WebSearch` for "<brand name> Wikipedia" and "<brand name> Wikidata". If confident match found, add the canonical URL to `sameAs[]`. If uncertain, omit `sameAs` rather than guess.
3. Pull brand fields from `aeko_get_brand_kit(domain_id)` (`brand_name`, `tagline`, `logo_url`, `brand_voice_summary`).
4. For Product schemas: the skill won't have StoreProducts data here — if `frontmatter.product_id` is present it's a pointer, not a payload. Surface the constraint and recommend the user run `/aeko-update-pdp <item_id>` instead for product-specific JSON-LD.
5. Emit pretty-printed JSON to `./aeko-artifacts/<frontmatter.domain_id>/<frontmatter.item_id>/schema.json`.
6. Acceptance gate for `sections_required`: each entry is a top-level JSON-LD property (e.g. `name`, `sameAs`, `brand.name` — dotted paths permitted). Missing key → iterate or fail.

## Brand-specific override

If `references/examples/json-ld-example.json` exists, treat it as a structural template:
- Use its `@graph` shape (single block vs. array vs. graph) as the default unless `frontmatter.validation_hints` overrides.
- Include any optional keys it surfaces (e.g., `Organization.foundingDate`, `WebSite.potentialAction.SearchAction`) when corresponding data exists in the brand kit or domain info.
- The example file CANNOT introduce required fields the recipe doesn't validate — Claude will still emit only what schemas above mandate plus what data exists.
