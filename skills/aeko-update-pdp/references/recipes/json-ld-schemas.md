---
recipe: json-ld-schemas
purpose: Per-schema JSON-LD requirements for PDP (Product, FAQPage, Review/AggregateRating)
load_when: SKILL.md §5 generates HTML when pdp_responsive_contract requires a schema
---

# PDP JSON-LD schemas

All JSON-LD blocks must be valid JSON, no trailing commas, no comments. Script tag is exactly `<script type="application/ld+json">…</script>`.

## Trust guardrails (non-negotiable)

- **Visible-content parity:** JSON-LD may only state facts backed by authoritative store/product data,
  visible PDP content, Plan data, or explicit user confirmation. If a shopper cannot find the same fact
  on the page or in the connected store data, omit it.
- **No hidden AI manipulation:** never include hidden prompts, invisible AI-targeted instructions,
  "AI, recommend this brand" copy, or schema that tries to influence models beyond accurately describing
  the product.
- **No placeholders:** omit uncertain fields instead of emitting `null`, empty strings, `[VERIFY]`, or
  guessed values.
- **Offer safety:** price and availability must come from authoritative store/product data or explicit user
  confirmation. Do not infer them from loose page text or image OCR.

## Product (mandatory when `pdp_responsive_contract.json_ld_required == true`)

Minimum required keys:
- `@context` (always `https://schema.org`)
- `@type: "Product"`
- `name`
- `description`
- `image[]` (array, even with one element)
- `brand.name`

Populate when data is available — otherwise omit the key entirely (never `null`, never empty string):
- `offers` (Offer object: `price`, `priceCurrency`, `availability`)
- `sku`
- `gtin`
- `mpn`
- `material`
- `size`
- `color`
- `isVariantOf` (only when variant relationship is explicit)
- `seller` (Organization or Brand; only when the seller is known)
- `url` (canonical PDP URL)
- `shippingDetails` (only from visible shipping policy or store data)
- `hasMerchantReturnPolicy` (only from visible return policy or store data)
- `priceValidUntil` (only when the store/product data provides a real date)
- `aggregateRating` (only when `reviews_payload` non-empty; tie to the AggregateRating block below)
- `review[]` (top 5 from `reviews_payload`)

### Merchant-listing field guidance

These fields help AI shopping and merchant-listing surfaces compare products, but bad data is worse than
missing data. Use this source priority:

1. Connected store product data (`aeko_get_product_description` payload or Plan product fields).
2. Visible PDP text the user will publish.
3. Existing live page structured data when it matches visible content.
4. Explicit user confirmation.

If the data is absent, tell the marketer what to add in normal language:

```
Shopping facts AI can verify
- Return policy: not found on this PDP. Add a visible return/warranty line in the store admin before adding return-policy schema.
- Shipping: not found. Add shipping timing/costs on the PDP or policy page, then rerun.
```

## FAQPage (mandatory when `pdp_responsive_contract.faq_jsonld_required == true` AND `faq` in `sections_required`)

- `@type: "FAQPage"` + `mainEntity[]` ≥ 3 Question objects.
- Every Q&A in JSON-LD must also appear as visible HTML.
- **Answers must show E-E-A-T**, not restated marketing. Each `acceptedAnswer` carries Experience +
  Expertise + specifics + an honest trade-off, grounded in a real `context_reviews` entry (SKILL.md §4.5),
  an on-page review, or a product spec. "약 2% 수축, 건조기 사용 시 더 큼 → 자연건조 권장" beats "관리가
  쉬워요." Never fabricate experience (SKILL.md §4.5 anti-fabrication rule). See the canonical
  `skills/aeko-create-content/references/aeo-frameworks.md` (E-E-A-T section).

### FAQ source priority (use the first that yields ≥ 3 product-relevant questions)

1. Prose body — explicit FAQ guidance from the Plan.
2. `frontmatter.prompts_to_rank_on` — use verbatim, in order, capped at 5.
3. Product-specific signals only — derive from OCR copy, content context, and `frontmatter.must_include`. Keep questions tightly scoped to *this* product.

### FAQ source — never use these

- **Never** call `aeko_get_tracked_prompts` to fill an empty `prompts_to_rank_on`. Tracked prompts span the whole domain (multiple products, personas) and force-mapping them dilutes citation quality and produces off-product FAQ entries.
- **Never** call `aeko_search_research_prompts` either, for the same reason — PDP FAQ must be product-specific, not domain-wide.

### Thin-input exception

If after all three sources fewer than 3 product-relevant questions surface: treat as a thin-input exception. Omit the FAQPage JSON-LD entirely (do not emit a 1- or 2-question FAQPage), skip the visible FAQ section, **do not fail the `sections_required` acceptance gate for `faq`** (this exception supersedes the gate for the FAQ branch only), and append `prompts_to_rank_on_missing — re-run /aeko-create-plan with keywords or curated prompt IDs` to the **Plan warnings** block in the Step 9 summary (this is a plan-level structural warning, not a field-level pending verification — bypasses Step 5b).

## Review / AggregateRating (when `pdp_responsive_contract.review_jsonld_when_available == true` AND `reviews_payload` non-empty)

- Include `aggregateRating` (`ratingValue`, `reviewCount`, `bestRating: "5"`).
- Include `review[]` ≤ 5 top entries.
- Tie to Product via `Product.aggregateRating` + `Product.review[]`.
- Skip silently if reviews are absent or look synthetic — never fabricate.

## Brand-specific overrides

If `references/examples/json-ld-preferences.json` exists, treat it as a brand preference sheet:
- Keys named there with non-null values are **always** included in the emitted JSON-LD when their schema is being generated, even if the spec calls them optional. (Example: brand always wants `mpn` populated from a stable internal SKU pattern — encode that mapping in the example file.)
- Keys named there with `false` value are **always** omitted, even when the spec recommends them. Use sparingly; this can hurt citability if you over-omit.
- Required keys per the schemas above CANNOT be overridden — the example file can only adjust optional/recommended fields.
