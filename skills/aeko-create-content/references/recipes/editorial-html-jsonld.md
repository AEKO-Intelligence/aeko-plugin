---
channel: editorial-html-jsonld
purpose: HTML wrapper + JSON-LD schema for editorial channels (보도자료, magazine, partner_media, aeko_shop)
load_when: SKILL.md §5.1 selects an editorial channel; load alongside the channel-specific recipe file
---

# Editorial channels — HTML + JSON-LD

Two distinct artifact layouts live in this recipe:

| Channel | Artifacts | Where the `.html` lands |
|---|---|---|
| `보도자료` / `magazine` / `partner_media` | `<slug>.md` (source of truth) + `<slug>.html` (rendered from `.md`) | Editor-facing. The client distributes both files. Never round-trips through any sanitizer. |
| `aeko_shop` | `<slug>.html` (publish-ready body) + `<slug>.meta.json` (publish-ready metadata) + `<slug>.md` (debug mirror) | Shipped to aeko.shop's backend by `/aeko-publish-content`. The `.html` becomes `PostUpsert.body_html` **verbatim**; `.meta.json` populates the top-level publish fields. |

Because the `aeko_shop` `.html` round-trips through `aeko-shop-backend/app/sanitizer.py`, **its allowed-tag and allowed-attribute surface is strictly enforced**. Anything outside the allow-list returns HTTP 400 at publish time (no silent stripping). The editor-facing channels have no such constraint.

The sections below are explicit about which channels they apply to. Skim the "scope" line under each heading.

---

## HTML structure — `보도자료` / `magazine` / `partner_media`

**Scope:** editor-facing only. Not for `aeko_shop` (see next section).

Minimal semantic wrapper, no styling, no scripts beyond the JSON-LD block:

```html
<!doctype html>
<html lang="<frontmatter.target_language>">
<head>
  <meta charset="utf-8">
  <title><headline></title>
  <meta name="description" content="<lead-sentence-or-meta>">
  <link rel="canonical" href="<frontmatter.canonical_url-if-present>">
</head>
<body>
  <article>
    <header>
      <h1><headline></h1>
      <p class="lead"><lead></p>
      <p class="byline">
        <author> · <ISO datePublished>
      </p>
    </header>
    <section>
      <!-- markdown body rendered to HTML; preserve heading hierarchy -->
    </section>
    <!-- if media_specs: was used in lieu of real media, mirror it as an HTML comment block above <footer> -->
    <footer>
      <p class="boilerplate"><brand boilerplate from brand kit></p>
      <p class="contact"><문의처 line for 보도자료, otherwise omit></p>
    </footer>
    <script type="application/ld+json">
      <!-- channel-specific JSON-LD: see schemas below -->
    </script>
  </article>
</body>
</html>
```

If a real media URL exists (`media_by_channel[channel]` set), inject `<figure><img src=... alt=...></figure>` blocks at the natural insertion points (after the lead for hero, between sections for inline). Skip when only `media_specs:` was emitted — HTML preserves the YAML block as a leading comment so the publishing editor sees the spec without it polluting the rendered article.

---

## HTML structure — `aeko_shop`

**Scope:** `aeko_shop` only. The `.html` is the body that aeko.shop's backend stores as `PostUpsert.body_html` after running it through `sanitize_post_html`. No document wrapper, no `<head>`, no semantic chrome around the body — the rendered page (`aeko-shop-front/app/posts/[slug]/page.tsx`) supplies its own `<article>`, `<header>`, `<h1>`, breadcrumb, byline, hero image, breadcrumbs, JSON-LD, and "Featured products" cards from `PostUpsert` fields.

Emit a flat stream of allow-listed body tags only. No file-level wrapper:

```html
<p>Lead paragraph that opens the article.</p>

<h2>First section heading</h2>
<p>Section body.</p>
<ul>
  <li>Point one.</li>
  <li>Point two.</li>
</ul>

<figure role="callout" data-variant="product" data-product-source-id="BIO-CLS-001">
  <img src="https://cdn.aeko.shop/brands/bioelements/catalog/cool-sleep.jpg"
       alt="쿨링 슬립웨어" width="800" height="600" loading="lazy">
  <figcaption><strong>쿨링 슬립웨어</strong> — 체온 1.5°C 낮추는 메리노 울 슬립웨어.</figcaption>
</figure>

<h2>Second section heading</h2>
<p>Body continues.</p>

<table summary="Cooling sleepwear options compared">
  <thead><tr><th>Brand</th><th>Material</th><th>Cooling effect</th></tr></thead>
  <tr><td>Bioelements</td><td>Merino wool</td><td>−1.5°C</td></tr>
  <tr><td>…</td><td>…</td><td>…</td></tr>
</table>

<p>Closing paragraph with an <a href="https://example.com/study" rel="nofollow noopener" target="_blank">external citation</a>.</p>
```

What this file MUST NOT contain (each triggers HTTP 400 at publish):

`<!doctype>`, `<html>`, `<head>`, `<body>`, `<meta>`, `<title>`, `<link>`, `<article>`, `<header>`, `<section>`, `<footer>`, `<h1>`, `<script>` (including JSON-LD), `<style>`, any `<a data-aeko-product-ref>` / `<a data-product-sku>` attribute (these are NOT in the sanitizer's allow-list and there is no frontend upgrader for them — confirmed grep-zero in `aeko-shop-front/`).

Metadata that historically lived in `<head>` (title, og_description, canonical, locale, hero image) is carried by the sibling `<slug>.meta.json` (next section) — it is **never** embedded in the body HTML.

---

## Allow-list — `aeko_shop` body HTML

Verbatim from `aeko-shop-backend/app/sanitizer.py`. The sanitizer raises `HTTPException(400, "HTML contains disallowed tags or attributes: …")` on any deviation — it does **not** silently strip. Every tag and every attribute in the body must be in this list.

**Allowed tags (22 total):**

`a, blockquote, br, code, div, em, figcaption, figure, h2, h3, h4, hr, img, li, ol, p, pre, strong, table, td, th, thead, tr, ul`

Notes:

- `h1` is **not** allowed — `aeko-shop-front` renders `post.title` as the page `<h1>`.
- `div` is allowed; use sparingly when grouping is needed.
- `table / thead / tr / td / th` are allowed — comparison tables are a strong AEO signal.
- `info` / `warn` figure callouts (see below) are accepted by the sanitizer but currently have no specific frontend renderer; reserved for future non-product callouts.

**Allowed attributes:**

- `*` (any tag): `class`
- `a`: `href, title, rel, target, data-mention-type, data-mention-id`
- `figure`: `role, data-variant, data-product-source-id`
- `img`: `src, alt, title, width, height, loading`
- `table`: `summary`
- `td`: `colspan, rowspan`
- `th`: `colspan, rowspan, scope`

`data-variant` value enum: `info | warn | product` — sanitizer rejects any other value when `role="callout"`. Only `product` has a wired frontend consumer (the bottom "Featured products" section, populated from `featured_products[]` in `.meta.json`, not from body markup). `info` and `warn` are reserved; the recipe does not require them.

**Allowed `<a href>` protocols:** `http`, `https`, `mailto`.

**Allowed `<img src>` origins:** must match one of `settings.allowed_image_origins ∪ {settings.media_public_base_url}` — effectively `cdn.aeko.shop/...` in production. Non-CDN URLs (Unsplash, the brand's own non-CDN domain, anything else) return 400.

`data-mention-type` and `data-mention-id` on `<a>` are allow-listed but currently unused by any frontend consumer (grep confirms zero matches in `aeko-shop-front/`). Treat as reserved by backend; the recipe does not emit them.

---

## `<slug>.meta.json` — `aeko_shop` publish payload (sidecar)

**Scope:** `aeko_shop` only. The companion JSON that `/aeko-publish-content` reads as the single source of truth for top-level publish fields. Mirror of `PostUpsert` in `aeko-shop-backend/app/schemas.py`. `brand_id` is added by the courier from `frontmatter.domain_id`; everything else comes from this file.

```json
{
  "locale": "ko",
  "title": "…",
  "og_description": "≤500 chars; required (drives <meta description>, OG description, and the speakable JSON-LD on the rendered page).",
  "hero_image_url": "https://cdn.aeko.shop/…",
  "source_content_id": "<frontmatter.item_id>",
  "content_format_version": 1,
  "featured_products": [
    { "product_source_id": "<external Product.source_id>", "display_order": 0 }
  ],
  "mentioned_brand_ids": [],
  "external_publications": []
}
```

Field-by-field constraints (mirror `PostUpsert`):

| Field | Required | Type | Constraints |
|---|---|---|---|
| `locale` | yes | str | 2..12 chars. `ko`, `en`, `en-US`, `ko-KR` all valid. Normalize "Korean"/"한국어"→`ko`, "English"/"영어"→`en`; unrecognized → fall back to `ko` and emit a one-line warning. |
| `title` | yes | str | 1..300 chars. |
| `og_description` | **yes** (recipe requirement, even though `PostUpsert` allows null) | str | ≤500 chars. Absent → the rendered page's `speakable` JSON-LD block does not emit (`structured-data.ts:67-73`), so always include. |
| `hero_image_url` | recommended | str \| null | Must be a `cdn.aeko.shop/...` URL. The frontend renders this as the 16:9 hero `<Image>` above body HTML (page.tsx:125-136). |
| `source_content_id` | yes | str | 1..240 chars. Set to `frontmatter.item_id`. Backend idempotency keys on `(brand_id, source_content_id)` — re-publishes are safe. |
| `content_format_version` | yes | int | `1`. |
| `featured_products[]` | yes (may be `[]`) | array | ≤50 entries. Each: `{ product_source_id: str(1..240), display_order: int }`. **`product_source_id` is `ProductRef.source_id`, NOT `ProductRef.id` (UUID).** Backend joins on `Product.source_id` (the brand-registered external identifier). |
| `mentioned_brand_ids[]` | no | array | ≤50 entries of `{ brand_id: UUID, role?: str }`. Backend accepts and persists; frontend doesn't surface yet — populate only if a wired consumer exists. |
| `external_publications[]` | no | array | ≤10 entries of `{ platform: "tistory" \| "naver_blog", url: "https://…", published_at?: ISO }`. Backend persists; frontend currently hardcodes static stubs (page.tsx:214-229). Populate if the data is known. |

No other top-level fields are allowed by this version of the recipe. **Field-growth path:** `PostUpsert` is the canonical source of truth; when the aeko.shop backend adds a new top-level field (e.g., `tags[]`, `seo_canonical_url`, `published_at_override`), the path is — (1) backend ships the field in `aeko-shop-backend/app/schemas.py::PostUpsert`; (2) this recipe bumps `content_format_version` and adds the new field to the table above with its constraints; (3) `/aeko-create-content`'s §5.4 / §6.3 acceptance gates pick up the new field; (4) `/aeko-publish-content` Step 4 payload table adds a row sourcing the new field from `meta.<field>`. The publisher is intentionally strict (no `**kwargs` passthrough) so a backend-only addition cannot land silently — every new field flows through a recipe edit so drafters know it exists.

---

## Product callout pattern — `aeko_shop`

**Scope:** `aeko_shop` only. The canonical pattern for inline product references in body HTML. Sanitizer-validated at `aeko-shop-backend/app/sanitizer.py:134-141`.

```html
<figure role="callout" data-variant="product" data-product-source-id="BIO-CLS-001">
  <img src="https://cdn.aeko.shop/brands/bioelements/catalog/cool-sleep.jpg"
       alt="쿨링 슬립웨어" width="800" height="600" loading="lazy">
  <figcaption>
    <strong>쿨링 슬립웨어</strong> — 체온 1.5°C 낮추는 메리노 울 슬립웨어.
  </figcaption>
</figure>
```

Strict requirements (or 400):

- `role="callout"` is required for the variant check to fire.
- `data-variant="product"` is required for product callouts.
- `data-product-source-id` is required when `data-variant="product"` (and its value is `ProductRef.source_id` — NOT `ProductRef.id`).
- All `<img>` inside the callout carry `alt`, `width`, `height`, `loading="lazy"`.
- `<img src>` is `cdn.aeko.shop/...`.

Placement rules:

- **No hero product callout in body.** Top-level `hero_image_url` in `.meta.json` already renders above body_html on `aeko-shop-front`. Putting a hero `<figure>` at the top of body_html produces a duplicate hero.
- **Inline callouts** sit between H2 sections at natural breakpoints. Density: roughly one callout per 400 words. Do not cluster.
- **Below-the-body product cards** are rendered automatically by `aeko-shop-front` from `.meta.json` `featured_products[]` — no HTML callout is needed for the cards to appear.

Result: a given product can show up twice on the rendered page — once as an inline `<figure>` callout for mid-flow AEO reinforcement, once as a card in the "Featured products" section as the primary click target. This is intentional. The recipe **permits** but does not **require** an inline callout for every product in `featured_products[]`.

---

## ID-space resolution — `product_source_id`

Single most likely silent-failure mode. The rules:

1. **`featured_products[].product_source_id`** in `.meta.json` is sourced from `ProductRef.source_id` (the external brand-registered identifier; e.g., a Shopify variant ID). Backend joins on `Product.source_id` via `_product_by_source(brand_id, source_id)` in `aeko-shop-backend/app/routes/internal.py:352-356`.
2. **`data-product-source-id` on every `<figure data-variant="product">`** in `.html` carries the same `ProductRef.source_id`.
3. **Hard acceptance gate** (recipe §6.3): the set of `data-product-source-id` values in `.html` equals the set of `featured_products[].product_source_id` values in `.meta.json`. Count + set match.

`ProductRef.source_id` requires v1.4 contract minor (see `aeko-create-content/SKILL.md` Step 1 `products[]` definition). Until v1.4 lands and `build_plan_md()` hydrates `source_id` alongside `id`, the recipe's product-callout path stays inert: `aeko_shop` drafts produce articles-without-product-callouts cleanly — `.meta.json` has empty `featured_products[]`, no `<figure>` callouts appear in `.html`, and the frontend's "Featured products" section just doesn't render.

When `ProductRef.source_id` is missing (pre-v1.4), drop the product callout entirely with a single warning. Do not fabricate a value; do not use `ProductRef.id` (UUID).

---

## Image rules — `aeko_shop` body

- Every `<img src>` is a `cdn.aeko.shop/...` URL. Any other origin → 400 at publish.
- Every `<img>` carries `alt`, `width`, `height`, `loading` attrs. `loading="lazy"` is recommended for every image; the rendered page already eager-loads the top-level hero (frontend chrome handles that).
- User-supplied images uploaded via `aeko_request_media_upload` at SKILL.md §5.4 land at `cdn.aeko.shop/brands/<brand_id>/posts/<source_content_id>/<sha256>.<ext>` — reference that returned URL directly.
- `parsed_products[].image_url` is already a `cdn.aeko.shop/...` URL by construction — reference directly; do not re-upload.
- No `media_specs:` YAML for `aeko_shop`. The artifact is publish-ready or it isn't (SKILL.md §6.1 hard gate fails on `[image: …pending]` placeholders).
- **Do not** copy image URLs from `aeko-shop-front/lib/mock-data.ts`. The mock fixtures use Unsplash URLs that only work under `USE_MOCK_DATA=true`; they would return 400 from `sanitize_post_html` in production.

---

## JSON-LD schema per channel

**Scope:** `보도자료` / `magazine` / `partner_media` only. **`aeko_shop` does NOT emit JSON-LD inside body HTML** — the rendered page regenerates Article + Product JSON-LD from `PostUpsert` fields at render time (`aeko-shop-front/lib/structured-data.ts`); any in-body `<script>` block would be rejected by the sanitizer.

### `보도자료` → `NewsArticle`

```json
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "<headline (≤110 chars per Schema.org guidance)>",
  "datePublished": "<ISO 8601 date the press release is dated for>",
  "dateModified": "<same as datePublished unless re-issued>",
  "author": { "@type": "Person|Organization", "name": "<from brand kit or 'Press' if absent>" },
  "publisher": {
    "@type": "Organization",
    "name": "<brand_kit.brand_name>",
    "logo": { "@type": "ImageObject", "url": "<brand_kit.logo_url if present>" }
  },
  "articleBody": "<body text, with HTML stripped>",
  "inLanguage": "<frontmatter.target_language>"
}
```

### `magazine` → `Article`

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "<headline>",
  "datePublished": "<ISO date>",
  "author": { "@type": "Person|Organization", "name": "<from brand kit, or 'Editorial' if not specified>" },
  "publisher": { "@type": "Organization", "name": "<brand_kit.brand_name>" },
  "articleBody": "<body text>",
  "inLanguage": "<frontmatter.target_language>",
  "mentions": [
    { "@type": "Brand", "name": "<parent or related brand if brand kit names one>" }
  ]
}
```

Omit the `mentions` array entirely if the brand kit doesn't surface a relationship — don't fabricate.

### `partner_media` → `Article` (always) + `Review` (when forensics-detected as comparison-shaped)

`Review` is added when 3B.5 locked the recipe to `Review` or detected `Review` as a top `@type`:

```json
[
  {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "<headline>",
    "datePublished": "<ISO date>",
    "author": { "@type": "Person|Organization", "name": "<...>" },
    "publisher": { "@type": "Organization", "name": "<brand_kit.brand_name>" },
    "articleBody": "<body text>",
    "inLanguage": "<frontmatter.target_language>"
  },
  {
    "@context": "https://schema.org",
    "@type": "Review",
    "itemReviewed": {
      "@type": "Product",
      "name": "<the comparison subject named in the draft body — derive from the H1 / lead paragraph; do NOT invent>"
    },
    "reviewRating": {
      "@type": "Rating",
      "ratingValue": "<numeric score the body actually substantiates, or omit>",
      "bestRating": "5"
    },
    "author": { "@type": "Person|Organization", "name": "<...>" },
    "reviewBody": "<the comparison summary paragraph>"
  }
]
```

When emitting two blocks, use a JSON-LD array (top-level `[...]`) — schema.org and Google Rich Results both accept this.

### `aeko_shop` → no in-body JSON-LD

The rendered page emits its own Article + Product + BreadcrumbList JSON-LD from `PostUpsert` fields at render time via `articleSchema(post)` and `productSchema(product, brand)` in `aeko-shop-front/lib/structured-data.ts`. There is **nothing for the recipe to emit inside body HTML** — every `<script>` element is rejected by the sanitizer.

---

## JSON-LD validity rules

**Scope:** `보도자료` / `magazine` / `partner_media` only (the channels that embed JSON-LD inside body HTML). Mirrors `aeko-update-pdp` and `aeko-refresh-jsonld`:

- Valid JSON: parses with `json.loads(block)`.
- No trailing commas.
- No comments (`//` or `/* */`) inside the block.
- The opening tag is exactly `<script type="application/ld+json">` — no additional attributes, no whitespace differences in `type=`.
- `@context` is `https://schema.org` (not `http://`, not omitted).
- For numeric fields like `ratingValue`, do not include them unless the body actually justifies a number.
- **`inLanguage` must be a valid ISO-639-1 / BCP 47 code** (e.g. `"ko"`, `"en"`, `"en-US"`). Defensively normalize per the §"`<slug>.meta.json`" locale rule above.

---

## HTML emission notes

- (`보도자료` / `magazine` / `partner_media` only) The `media_specs:` YAML block (SKILL.md §5.4), when present, is mirrored into the HTML as an HTML comment above `<footer>`. Sanitize: replace any `--` sequence inside user-supplied strings with `- -` before wrapping in `<!-- … -->` so the comment can never close prematurely. **Not applicable to `aeko_shop`** — `aeko_shop` has no `media_specs:` (its §5.4 branch requires concrete CDN URLs) and no `<footer>` survives the sanitizer.
- (`보도자료` / `magazine` / `partner_media` only) If `frontmatter.canonical_url` is absent, omit the `<link rel="canonical">` tag entirely — do not emit an empty `href`.
- HTML files are minified-optional; readable indentation is fine.
- The skill never injects CSS or external `<script>` tags. For `aeko_shop`, no `<script>` at all.

---

## Schema parity

**Scope:** `보도자료` / `magazine` / `partner_media` only.

If `structural_template_by_channel[channel]` carries observed JSON-LD `@type`s from cited sources (Step 3B.5 / 3B.3), the artifact's emitted `@type` SHOULD be in the same family. Mismatch is a soft warning at Step 6, not a hard fail.

`aeko_shop` has no in-body JSON-LD and the rendered page always emits `Article` regardless. There is no parity check to perform for `aeko_shop`.

---

## Acceptance gates

### Common to all four editorial channels

Both `<slug>.md` AND `<slug>.html` must exist. The `.html` parses with `lxml` / `html.parser`. Every required JSON-LD field is present per the schemas above (for the three channels that embed JSON-LD).

### `보도자료` / `magazine` / `partner_media`-only gates

- The `.html` contains exactly one `<article>` root.
- Each `<script type="application/ld+json">` block parses with `json.loads` after stripping the script wrapper.
- **Schema parity** soft check: emitted top-level `@type` is in the same family as the cited sources' dominant `@type` from 3B.5.

### `aeko_shop`-only gates

- `<slug>.meta.json` exists and parses with `json.loads`.
- `<slug>.meta.json` validates against the `PostUpsert` shape table in §"`<slug>.meta.json`" above: required fields present, every field within its constraint (length, count caps, `cdn.aeko.shop` origin for `hero_image_url`, valid `locale`, valid `product_source_id` length, etc.).
- `<slug>.html` is sanitizer-safe: zero matches for `<(script|article|header|footer|section|h1|meta|title|link|html|body|head)\b` in the file. **Hard gate.**
- Every `<a>` tag's attributes are a subset of `{href, title, rel, target, class, data-mention-type, data-mention-id}`. No `data-aeko-product-ref` or `data-product-sku`. **Hard gate.**
- Every `<img src>` is a `cdn.aeko.shop/...` URL — no other origins. **Hard gate.** (Confirms the §5.4 upload step ran and no external URL leaked in.)
- Every `<img>` carries `alt`, `width`, `height`, `loading` attributes. **Hard gate.**
- Zero `[image: …pending]` placeholder markers remain in `.md` or `.html`. **Hard gate.** (No unresolved `aeko_request_media_upload` failures.)
- **ID-match gate.** The set of `data-product-source-id` values across all `<figure data-variant="product">` in `.html` equals the set of `featured_products[].product_source_id` values in `.meta.json`. Count + set match. **Hard gate.**
- Body contains zero `<figure>` callouts with `data-variant="product"` when `featured_products[]` is empty (no orphans). **Hard gate.**
- (Soft warning) When `featured_products[]` has > 3 entries: at least one inline `<figure>` callout exists for at least one product — not required to cover every product (body may be too short).

Any HTML-side hard-gate failure → one fix iteration → leave `pending`.

---

## Notes on the migration from the pre-v1.4 recipe

Before this rewrite the recipe described an `aeko_shop` `.html` as a full HTML document with embedded JSON-LD, inline `<a data-aeko-product-ref>` product links, and an in-body hero `<figure>`. Every one of those constructs returns HTTP 400 from `sanitize_post_html` (`aeko-shop-backend/app/sanitizer.py`). If a drafter produces an artifact in the old shape, `/aeko-publish-content` will fail at the POST step with the sanitizer's tag/attr-enumeration error. Re-draft against this recipe.
