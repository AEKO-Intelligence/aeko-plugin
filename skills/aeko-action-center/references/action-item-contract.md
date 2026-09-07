# AEKO action-item contract

Authoritative spec for the data shape that flows between the AEKO backend, Plan.md
artifacts on disk, and the aeko-plugin skills. Every skill in `aeko-plugin/skills/`
that references "action-item-contract.md" reads from this file.

This document is the **minimal stub** introduced in v1.4 to formalize the
`ProductRef` shape used by `/aeko-create-content` and `/aeko-publish-content`.
Other sections referenced from skill headers (§4 guide.md, §5 store-writes,
§6 completion, §7 shadow product) are TODO and will be added as they are
formalized; until then, the inline definitions inside each skill's SKILL.md
remain the source of truth for those areas.

## Versioning

Contract version is **v1.4** (current). Skills pin to a specific minor in their
own SKILL.md headers; bumping a pin requires the matching backend change to
have shipped first.

| Version | Change |
|---|---|
| v1.0..v1.3 | Pre-`ProductRef` formal definition; `products[]` was implicit. |
| v1.4 | This document. Adds formal `ProductRef` (§3.2.1) with required `source_id`. Backend's `build_plan_md()` must hydrate both `id` and `source_id` for v1.4 to be active. |

## §3 Plan.md format

(TODO — formalize the full Plan.md frontmatter schema in a later revision. For
now, see `aeko-plugin/skills/aeko-create-content/SKILL.md` Step 1 for the live
frontmatter parser's expectations.)

### §3.2 Action item shape

(TODO — see `aeko-plugin/skills/aeko-action-center/SKILL.md` for the live shape.)

### §3.2.1 `ProductRef`

Used by Plan.md's `products[]` array when the action item was generated from the
dashboard's `상품 선택` (product-select) mode. Each entry:

```yaml
products:
  - id: <uuid>                  # AEKO internal Product UUID. Required.
    source_id: <str(1..240)>    # External brand-registered identifier
                                #   (e.g., Shopify variant ID, Cafe24 SKU).
                                #   Required for v1.4 forward. The aeko.shop
                                #   backend joins on this field via
                                #   Product.source_id in
                                #   aeko-shop-backend/app/routes/internal.py
                                #   :352-356 _product_by_source(brand_id, source_id).
    name: <str(1..300)>         # Display name. Required.
    slug: <str(1..220)>         # URL-safe slug. Required.
    sku: <str(1..120)>          # Optional SKU.
    outbound_url: <str>         # Deep link. Usually
                                #   https://aeko.shop/brands/<brand>/products/<slug>
                                #   when product lives on aeko.shop, or the
                                #   client store's product URL when off-platform.
                                #   Required.
    image_url: <https://cdn.aeko.shop/...>  # CDN URL. Required for v1.4 — every
                                            # image must be on the AEKO CDN.
    short_description: <str(0..240)>        # Optional.
```

**Validation rule.** Each entry must have at minimum `id`, `source_id`, `name`,
`outbound_url`, `image_url`. Entries missing any of those → drop with a single
warning line listing the dropped IDs; keep going with the rest. The skill
remains operational on an empty `products[]`; downstream channels that depend
on it (currently only `aeko_shop`) draft articles-without-product-callouts.

**`id` vs `source_id`.** The two ID fields name different ID spaces:

- `id` is AEKO's internal Product UUID — used for cross-AEKO references and
  some MCP tool calls.
- `source_id` is the external identifier the brand registered the product with
  (e.g., the Shopify variant ID for Shopify-hosted catalogs). This is what
  `PostUpsert.featured_products[].product_source_id` joins on in the aeko.shop
  backend.

Both IDs must be populated by the backend's `build_plan_md()` hydration step
for v1.4 to be functional. Until then, every Plan.md will have `source_id`
absent or empty, and downstream channels that depend on `ProductRef` (`aeko_shop`
product callouts) operate in their "no products" fallback path.

**Backend wiring note.** As of the v1.4 contract revision, `build_plan_md()` is
still pending the hydration change. Skills should detect missing `source_id`
defensively (treat as v1.3 behavior — the product-callout path stays inert) and
not fabricate values.

## §4 guide.md (TODO)

## §5 Store-write semantics (TODO)

## §6 Action item completion (TODO)

## §7 Shadow product (TODO)
