---
channel: editorial-html-jsonld
purpose: HTML wrapper + JSON-LD schema for owned-web channels (aeko_shop, own_store_blog)
load_when: SKILL.md §5.1 selects an owned-web channel; load alongside the channel-specific recipe file
---

# Owned-web channels — HTML + JSON-LD

> Owned-web surfaces only: `aeko_shop` (body-only, frontend regenerates JSON-LD) and `own_store_blog` (self-contained, embeds its own JSON-LD). Content quality/voice is governed by `../aeo-frameworks.md`.

Two distinct artifact layouts live in this recipe:

| Channel | Artifacts | Where the `.html` lands |
|---|---|---|
| `aeko_shop` | `<slug>.html` (publish-ready body) + `<slug>.meta.json` (publish-ready metadata) + `<slug>.md` (debug mirror) | Shipped to aeko.shop's backend by `/aeko-publish-content`. The `.html` becomes `PostUpsert.body_html` **verbatim**; `.meta.json` populates the top-level publish fields. Round-trips through `aeko-shop-backend/app/sanitizer.py`. |
| `own_store_blog` | `<slug>__own_store_blog.html` (self-contained) + `<slug>__own_store_blog.md` (mirror) | The brand imports/pastes the `.html` into their own Cafe24/Shopify store blog **as-is**. Saved to the backend via `aeko_save_content_variation`. **Not** sanitizer-constrained; **must** embed its own JSON-LD. |

The two channels differ fundamentally in **who renders the schema**:

- **`aeko_shop`** — the aeko.shop frontend regenerates Article + Product JSON-LD from `PostUpsert` fields at render time, so the body carries **no** in-body JSON-LD. The body round-trips through the sanitizer, so its allowed-tag and allowed-attribute surface is **strictly enforced** — anything outside the allow-list returns HTTP 400 at publish (no silent stripping). The sanitizer constraint is **aeko.shop-specific only**.
- **`own_store_blog`** — the brand's own store will **not** regenerate schema, so the HTML **must embed its own JSON-LD**. It is self-contained and not sanitizer-constrained, so it can use semantic tags. Embedding the schema is the whole reason this channel needs the skill.

Each section names its scope on a "Scope" line — skim it before applying.

---

## HTML structure — `aeko_shop`

**Scope:** `aeko_shop` only. The `.html` is the body that aeko.shop's backend stores as `PostUpsert.body_html` after running it through `sanitize_post_html`. No document wrapper, no `<head>`, no semantic chrome around the body — the rendered page (`aeko-shop-front/app/posts/[slug]/page.tsx`) supplies its own `<article>`, `<header>`, `<h1>`, breadcrumb, byline, hero image, JSON-LD, and "Featured products" cards from `PostUpsert` fields.

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
  <img src="https://aekoshop-htgrg9fha0bbfmed.z02.azurefd.net/brands/bioelements/posts/fixture/cool-sleep.jpg"
       alt="쿨링 슬립웨어" width="800" height="600" loading="lazy">
  <figcaption><strong>쿨링 슬립웨어</strong> — 체온 1.5°C 낮추는 메리노 울 슬립웨어.</figcaption>
</figure>

<h2>Second section heading</h2>
<p>Body continues.</p>

<table summary="Cooling sleepwear options compared">
  <thead><tr><th>Brand</th><th>Material</th><th>Cooling effect</th></tr></thead>
  <tr><td>Bioelements</td><td>Merino wool</td><td>−1.5°C</td></tr>
</table>

<p>Closing paragraph with an <a href="https://example.com/study" rel="nofollow noopener" target="_blank">external citation</a>.</p>
```

What this file MUST NOT contain (each triggers HTTP 400 at publish): `<!doctype>`, `<html>`, `<head>`, `<body>`, `<meta>`, `<title>`, `<link>`, `<article>`, `<header>`, `<section>`, `<footer>`, `<h1>`, `<script>` (including JSON-LD), `<style>`, and any `<a data-aeko-product-ref>` / `<a data-product-sku>` attribute (not in the sanitizer's allow-list; no frontend upgrader exists).

Metadata that historically lived in `<head>` (title, og_description, canonical, locale, hero image) is carried by the sibling `<slug>.meta.json` — it is **never** embedded in the body HTML.

---

## Allow-list — `aeko_shop` body HTML

Verbatim from `aeko-shop-backend/app/sanitizer.py`. The sanitizer raises `HTTPException(400, "HTML contains disallowed tags or attributes: …")` on any deviation — it does **not** silently strip. Every tag and attribute in the body must be in this list.

**Allowed tags (22):** `a, blockquote, br, code, div, em, figcaption, figure, h2, h3, h4, hr, img, li, ol, p, pre, strong, table, td, th, thead, tr, ul`

- `h1` is **not** allowed — `aeko-shop-front` renders `post.title` as the page `<h1>`.
- `div` is allowed; use sparingly when grouping is needed.
- `table / thead / tr / td / th` are allowed — comparison tables are a strong AEO signal.

**Allowed attributes:**

- `*` (any tag): `class`
- `a`: `href, title, rel, target, data-mention-type, data-mention-id`
- `figure`: `role, data-variant, data-product-source-id`
- `img`: `src, alt, title, width, height, loading`
- `table`: `summary`
- `td`: `colspan, rowspan`
- `th`: `colspan, rowspan, scope`

`data-variant` value enum: `info | warn | product` — the sanitizer rejects any other value when `role="callout"`. Only `product` has a wired frontend consumer; `info` and `warn` are reserved and not required by this recipe.

**Allowed `<a href>` protocols:** `http`, `https`, `mailto`. Only link to **real URLs you were given in the brief** (`products[].outbound_url`, brand kit links, user-supplied media). **Never invent URLs.**

**Allowed `<img src>` origins:** must match `settings.allowed_image_origins ∪ {settings.media_public_base_url}` — the AEKO media CDN (today `https://aekoshop-htgrg9fha0bbfmed.z02.azurefd.net`, plus the `aekoshopmedia.blob.core.windows.net` blob origin). **Always embed the `public_url` returned by `aeko_request_media_upload` verbatim** — that is the configured origin. Any other origin (the brand's own non-AEKO domain, a hand-written `cdn.aeko.shop`) returns 400. `cdn.aeko.shop` is **not** a serving origin.

`data-mention-type` / `data-mention-id` on `<a>` are allow-listed but unused by any frontend consumer today; the recipe does not emit them.

---

## `<slug>.meta.json` — `aeko_shop` publish payload (sidecar)

**Scope:** `aeko_shop` only. The companion JSON that `/aeko-publish-content` reads as the single source of truth for top-level publish fields. Mirror of `PostUpsert` in `aeko-shop-backend/app/schemas.py`. `brand_id` is added by the courier from `frontmatter.domain_id`; everything else comes from this file.

```json
{
  "locale": "ko",
  "title": "…",
  "slug": "meaningful-english-slug",
  "og_description": "≤500 chars; required (drives <meta description>, OG description, and the speakable JSON-LD on the rendered page).",
  "hero_image_url": "https://aekoshop-htgrg9fha0bbfmed.z02.azurefd.net/…",
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
| `locale` | yes | str | 2..12 chars. `ko`, `en`, `en-US`, `ko-KR`, `ja`, `zh`, `es` all valid. Normalize common language names (`Korean`/`한국어`→`ko`, `English`/`영어`→`en`, `Japanese`→`ja`, `Chinese`→`zh`, etc.). If the value is a plausible BCP-47 language tag, use it; otherwise fall back to `en` and emit a one-line warning. |
| `title` | yes | str | 1..300 chars. |
| `slug` | **required (`aeko_shop`)** | str | A **meaningful English** slug (translate, don't transliterate) — see SKILL.md §5.5.6. Must match `^[a-z0-9]+(?:-[a-z0-9]+)*$` (lowercase ASCII, hyphen-separated; ≤220); for a **non-ASCII (Korean) title** it must NOT equal the §5.5.3 romanized filename slug (for an already-English title that equality is fine). Becomes the post URL slug (backend appends `-2`/`-3` on collision). Enforced by the SKILL §6.3 hard gate — omitting it (or reusing a romanized filename slug) fails the draft. The backend itself allows null and would otherwise transliterate the title to phonetic ASCII; the gate prevents that. **Never Korean/non-ASCII** — the backend rejects it (422). |
| `og_description` | **yes** (recipe requirement, even though `PostUpsert` allows null) | str | ≤500 chars. Absent → the rendered page's `speakable` JSON-LD does not emit (`structured-data.ts:67-73`), so always include. |
| `hero_image_url` | recommended | str \| null | Absolute https URL. Uploaded heroes use the presign `public_url` (AEKO media CDN); a **product** hero may use `parsed_products[0].image_url` on the brand's own https CDN — the frontend renders this via `next/image` (any https host), not the body sanitizer, so brand-CDN origins are fine **here only**. Never a hand-written `cdn.aeko.shop`. Renders as the 16:9 hero `<Image>` above body HTML (page.tsx). |
| `source_content_id` | yes | str | 1..240 chars. Set to `frontmatter.item_id`. **Advisory:** the content-variation publish path derives its own item-scoped key `aeko-item:{item_id}` and ignores this field — re-publishes overwrite the same post in place (idempotent by `(brand_id, aeko-item:{item_id})`). |
| `content_format_version` | yes | int | `1`. |
| `featured_products[]` | yes (may be `[]`) | array | ≤50 entries. Each: `{ product_source_id: str(1..240), display_order: int }`. **`product_source_id` is `ProductRef.source_id`, NOT `ProductRef.id` (UUID).** Backend joins on `Product.source_id` (the brand-registered external identifier). |
| `mentioned_brand_ids[]` | no | array | ≤50 entries of `{ brand_id: UUID, role?: str }`. Backend persists; frontend doesn't surface yet — populate only if a wired consumer exists. |
| `external_publications[]` | no | array | ≤10 entries of `{ platform: "tistory" \| "naver_blog", url: "https://…", published_at?: ISO }`. Backend persists; frontend currently hardcodes static stubs. Populate if the data is known. |

No other top-level fields are allowed. **Field-growth path:** when the backend adds a top-level field to `schemas.py::PostUpsert`, bump `content_format_version`, add the field to the table above, and update both the acceptance gates and `/aeko-publish-content`'s payload table. The publisher is intentionally strict (no `**kwargs` passthrough) so a backend-only addition cannot land silently.

---

## aeko_shop media upload (presign → PUT → verify)

**Scope:** `aeko_shop` only. Run this for each user-supplied image in `media_by_channel[aeko_shop]`, processing slots in order **hero → inline_1 → inline_2**. The body `<img src>` MUST be the AEKO media CDN `public_url` this procedure returns — that is the only way to get a sanitizer-safe inline image.

1. **Stage bytes locally.** For remote URLs, fetch into `./aeko-artifacts/<domain_id>/<item_id>/aeko_shop/.uploads/<sha256_of_url>.<ext>` (create `.uploads/` if missing). Local files can be staged in place.
2. **Compute digests:**
   - `content_sha256` = SHA-256 hex (lowercase, 64 chars).
   - `content_md5` = base64-encoded **raw** MD5 digest (24 chars incl. padding — **NOT hex**; the backend Pydantic field is `min_length=24, max_length=24`).
   - `byte_length` = file size in bytes.
3. **Request the presign:** call `aeko_request_media_upload(brand_kit_id=<resolved_brand_kit_id from brief>, source_content_id=<item_id>, filename=<basename only>, content_type=<image/(jpeg|png|webp|gif)>, content_sha256=<hex>, content_md5=<base64>, byte_length=<n>)`. Returns `{upload_url, public_url, blob_key, expires_at}`.
4. **PUT the bytes:** `curl -X PUT --data-binary @<staged_path> -H "x-ms-blob-type: BlockBlob" -H "Content-Type: <type>" -H "Content-MD5: <base64>" "<upload_url>"`. Every header is required; `Content-MD5` MUST equal the base64 from step 2; verify HTTP 2xx.
5. **Verify reachability:** `curl -fsSI "<public_url>"` (fallback `curl -fsS -r 0-0 "<public_url>"`). Continue only on 2xx.
6. **Embed the returned `public_url` VERBATIM** (do not rewrite the host): `<figure><img src="<public_url>" alt="<alt>" width="<w>" height="<h>" loading="lazy"></figure>`. Also record it into `.meta.json` `media[]` with matching `alt_text`.

On upload failure: **warn loudly in the user's chat language**, omit that image, and produce a valid text-only/partial post — **NEVER a placeholder**. Do not delete the staged file (speeds retry). `hero_image_url` in `.meta.json` may be a product image on the brand CDN (rendered by `next/image`), an uploaded `public_url`, or `null`.

---

## Product callout pattern — `aeko_shop`

**Scope:** `aeko_shop` only. The canonical pattern for inline product references in body HTML. Sanitizer-validated at `aeko-shop-backend/app/sanitizer.py:134-141`.

```html
<figure role="callout" data-variant="product" data-product-source-id="BIO-CLS-001">
  <img src="https://aekoshop-htgrg9fha0bbfmed.z02.azurefd.net/brands/bioelements/posts/fixture/cool-sleep.jpg"
       alt="쿨링 슬립웨어" width="800" height="600" loading="lazy">
  <figcaption><strong>쿨링 슬립웨어</strong> — 체온 1.5°C 낮추는 메리노 울 슬립웨어.</figcaption>
</figure>
```

Strict requirements (or 400):

- `role="callout"` is required for the variant check to fire.
- `data-variant="product"` is required for product callouts.
- `data-product-source-id` is required when `data-variant="product"` — its value is `ProductRef.source_id`, **NOT** `ProductRef.id`.
- Every `<img>` inside the callout carries `alt`, `width`, `height`, `loading="lazy"`.
- `<img src>` is on the AEKO media CDN — the `public_url` returned by `aeko_request_media_upload`. A brand-domain product image must be re-hosted first (see the upload procedure above), or the inline `<img>` omitted (use the bottom card).

Placement:

- **No hero product callout in body.** `hero_image_url` in `.meta.json` already renders above `body_html`. A hero `<figure>` at the top of the body produces a duplicate hero.
- **Inline callouts** sit between H2 sections at natural breakpoints. Default density: roughly one callout per 400 words. Do not cluster.
- **Below-the-body product cards** are rendered automatically by `aeko-shop-front` from `.meta.json` `featured_products[]` — no HTML callout is needed for the cards to appear.

A product can appear twice on the rendered page — once as an inline `<figure>` callout for mid-flow AEO reinforcement, once as a "Featured products" card (the primary click target). This is intentional; the recipe **permits** but does not **require** an inline callout for every product.

---

## ID-space resolution — `product_source_id`

The single most likely silent-failure mode. The rules:

1. **`featured_products[].product_source_id`** in `.meta.json` is `ProductRef.source_id` (the external brand-registered identifier; e.g. a Shopify variant ID). Backend joins on `Product.source_id` via `_product_by_source(brand_id, source_id)` in `aeko-shop-backend/app/routes/internal.py:352-356`.
2. **`data-product-source-id` on every `<figure data-variant="product">`** in `.html` carries the same `ProductRef.source_id`.
3. **Hard acceptance gate** (recipe §6.3): the set of `data-product-source-id` values in `.html` equals the set of `featured_products[].product_source_id` values in `.meta.json` — count and set match.

`build_plan_md()` hydrates `products[]` (with `source_id` from `StoreProducts.external_product_id`) for `상품 선택`-mode plans. When `products[]` is empty (brand-wide mode, or no store-synced products), the product-callout path is simply absent: `.meta.json` has empty `featured_products[]`, no `<figure>` callouts appear, and the frontend's "Featured products" section just doesn't render.

When `ProductRef.source_id` is missing (the product isn't synced from the brand's connected store), **drop the product callout entirely and warn loudly** per SKILL.md §1.1 — tell the user the product won't appear and that the store catalog needs to be connected/synced. Do not fabricate a value; do not use `ProductRef.id` (UUID).

---

## Image rules — `aeko_shop` body

- Every body `<img src>` is on the AEKO media CDN — the `public_url` returned by `aeko_request_media_upload`. Any other origin → 400 at publish. Do not hand-write `cdn.aeko.shop`.
- Every `<img>` carries `alt`, `width`, `height`, `loading`. `loading="lazy"` is recommended for every body image; the rendered page eager-loads the top-level hero itself.
- User-supplied images uploaded via the procedure above land at `<media_public_base_url>/brands/<brand_id>/posts/<source_content_id>/<sha256>.<ext>` — reference the returned `public_url` directly and verbatim.
- `parsed_products[].image_url` usually points at the **brand's own** catalog CDN, not the AEKO media CDN. It is fine for the `hero_image_url` and the bottom product card (rendered by `next/image`, any https host). For an **inline body** `<figure>` callout the image must be on an AEKO media origin — re-host via the upload procedure or omit the inline `<img>` and let the bottom card carry it.
- No `media_specs:` YAML for `aeko_shop`. The artifact is publish-ready or it isn't (SKILL.md §6.1 hard gate fails on `[image: …pending]` placeholders).

---

## `aeko_shop` → no in-body JSON-LD

**Scope:** `aeko_shop` only. The rendered page emits its own Article + Product + BreadcrumbList JSON-LD from `PostUpsert` fields at render time via `articleSchema(post)` and `productSchema(product, brand)` in `aeko-shop-front/lib/structured-data.ts`. There is **nothing for the recipe to emit inside body HTML** — every `<script>` element is rejected by the sanitizer.

(For `own_store_blog`, the opposite is true — the HTML MUST embed its own JSON-LD. See the `own_store_blog` section below.)

---

## `own_store_blog` — self-contained HTML + embedded JSON-LD

**Scope:** `own_store_blog` only. This channel is content the brand **imports into their own Cafe24/Shopify store blog**. The `.html` is pasted/imported **as-is** — the brand's store does NOT regenerate schema, run a sanitizer, or supply page chrome. So the artifact is fully self-contained: it brings its own semantic structure **and its own JSON-LD**. Embedding the schema is the whole reason this channel needs the skill.

### Self-contained semantic HTML

Unlike `aeko_shop`, `own_store_blog` is **NOT sanitizer-constrained** (that constraint is aeko.shop-specific only). It SHOULD use proper semantic structure so the imported article stands on its own:

- Wrap the body in a single `<article>` with one `<h1>` headline.
- Use `<h2>`/`<h3>` for sections, `<p>` for paragraphs, `<ul>`/`<ol>` for lists, `<figure>`/`<figcaption>` for images, `<table>` for comparisons.
- **Responsive / fluid layout:** avoid fixed-pixel widths and absolute positioning; use fluid semantic markup that reflows. Keep tables simple (no nested tables; let them scroll/wrap). The article must read on mobile and desktop without a stylesheet.
- Do not inject CSS classes the brand's store won't have, and do not rely on external stylesheets. Inline `style` is allowed where it carries responsive behavior (see images).

### Embedded JSON-LD (REQUIRED)

The HTML **MUST** embed JSON-LD via `<script type="application/ld+json">`:

- **`Article` (or `BlogPosting`) — always.** Required fields: `headline`, `datePublished` (or `dateModified`), `author`, and `publisher`/`image` as available.
- **`Product` — whenever products are attached.** One entry per attached product. Include each attached product here; this is what lets the brand's store get product structured data it would otherwise never emit.

When emitting both Article and Product, either place them in separate `<script>` blocks or wrap them in a top-level JSON-LD array `[...]` (schema.org and Google Rich Results both accept the array form). All blocks must satisfy the JSON-LD validity rules below.

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "<headline (≤110 chars per Schema.org guidance)>",
  "datePublished": "<ISO 8601>",
  "dateModified": "<ISO 8601, if known>",
  "author": { "@type": "Person|Organization", "name": "<from brand kit, else 'Editorial'>" },
  "publisher": {
    "@type": "Organization",
    "name": "<brand_kit.brand_name>",
    "logo": { "@type": "ImageObject", "url": "<brand_kit.logo_url if present>" }
  },
  "image": "<hero/figure image URL if available>",
  "inLanguage": "<frontmatter.target_language>"
}
```

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "<product name>",
  "image": "<product image_url (brand CDN) if available>",
  "description": "<short_description if available>",
  "url": "<product outbound_url>",
  "offers": {
    "@type": "Offer",
    "price": "<major-unit price string, only if known>",
    "priceCurrency": "<ISO-4217, only if known>",
    "availability": "https://schema.org/InStock|OutOfStock (only if known)"
  }
}
```

Omit `offers` (or any field within it) you can't substantiate — never fabricate price/availability.

### Media — brand-hosted / user-supplied, referenced directly

- **Do NOT use `aeko_request_media_upload`.** That presign flow targets the **AEKO media CDN** and is for `aeko_shop` ONLY. `own_store_blog` does not round-trip the AEKO media CDN.
- Reference brand-hosted or user-supplied image URLs/paths **directly**. Product `image_url` (the brand's own CDN) is fine to reference directly.
- Every `<img>` MUST carry `width`, `height`, `loading="lazy"`, and `style="max-width:100%;height:auto"` (the responsive contract) plus a meaningful `alt`.
- If no media is available → emit a `media_specs:` YAML block (mirrored as an HTML comment, see HTML emission notes) **or** omit images entirely. Never emit a placeholder `<img>`.

### Product callouts

Render inline product cards/links using the product's `outbound_url` + `image_url` (brand CDN allowed — referenced directly, no upload):

```html
<figure>
  <a href="<product.outbound_url>" rel="nofollow noopener" target="_blank">
    <img src="<product.image_url>" alt="<product name>"
         width="800" height="600" loading="lazy"
         style="max-width:100%;height:auto">
  </a>
  <figcaption><strong><product name></strong> — <one-line value prop>. <a href="<product.outbound_url>" rel="nofollow noopener" target="_blank">자세히 보기</a></figcaption>
</figure>
```

Every product rendered as a callout MUST also appear in the embedded `Product` JSON-LD (and vice versa) — same set.

### Self-contained HTML skeleton (example)

```html
<article>
  <h1>여름철 체온을 낮추는 메리노 울 슬립웨어 가이드</h1>
  <p>잠들기 전 체온을 낮추면 수면의 질이 올라갑니다. 이 글은 …</p>

  <h2>왜 메리노 울인가</h2>
  <p>메리노 울은 통기성과 흡습성이 뛰어나 …</p>

  <figure>
    <img src="https://cdn.bioelements.com/blog/merino-overview.jpg"
         alt="메리노 울 슬립웨어 클로즈업"
         width="1200" height="800" loading="lazy"
         style="max-width:100%;height:auto">
    <figcaption>메리노 울 슬립웨어의 표면 구조.</figcaption>
  </figure>

  <h2>추천 제품</h2>
  <figure>
    <a href="https://shop.bioelements.com/products/cool-sleep" rel="nofollow noopener" target="_blank">
      <img src="https://cdn.bioelements.com/products/cool-sleep.jpg"
           alt="쿨링 슬립웨어"
           width="800" height="600" loading="lazy"
           style="max-width:100%;height:auto">
    </a>
    <figcaption><strong>쿨링 슬립웨어</strong> — 체온 1.5°C 낮추는 메리노 울 슬립웨어. <a href="https://shop.bioelements.com/products/cool-sleep" rel="nofollow noopener" target="_blank">자세히 보기</a></figcaption>
  </figure>

  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "여름철 체온을 낮추는 메리노 울 슬립웨어 가이드",
    "datePublished": "2026-06-08",
    "author": { "@type": "Organization", "name": "Bioelements" },
    "publisher": {
      "@type": "Organization",
      "name": "Bioelements",
      "logo": { "@type": "ImageObject", "url": "https://cdn.bioelements.com/logo.png" }
    },
    "image": "https://cdn.bioelements.com/blog/merino-overview.jpg",
    "inLanguage": "ko"
  }
  </script>

  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Product",
    "name": "쿨링 슬립웨어",
    "image": "https://cdn.bioelements.com/products/cool-sleep.jpg",
    "url": "https://shop.bioelements.com/products/cool-sleep"
  }
  </script>
</article>
```

### Output + backend save — `own_store_blog`

- Write `<slug>__own_store_blog.html` (the self-contained HTML above) and `<slug>__own_store_blog.md` (a markdown mirror of the same content).
- **No `.meta.json` sidecar** — that is an aeko.shop-only publish payload.
- Save to the backend via:

```
aeko_save_content_variation(
  destination="own_store_blog",
  body_html=<the .html>,
  body_markdown=<the .md>,
  metadata={ "title": <title>, "og_description": <og_description>, "slug": <slug> }
)
```

The `own_store_blog` metadata schema (`OwnStoreBlogMetadata`) is looser than `aeko_shop` — no required `hero_image_url`, no required `featured_product_source_ids`.

### `own_store_blog`-only gates

- `<slug>__own_store_blog.html` AND `<slug>__own_store_blog.md` both exist.
- The `.html` parses with `lxml` / `html.parser`.
- At least one `<script type="application/ld+json">` block exists; **every** such block parses with `json.loads` after stripping the script wrapper, and satisfies the JSON-LD validity rules below.
- The embedded `Article` (or `BlogPosting`) JSON-LD is present and carries `headline`, `datePublished` **or** `dateModified`, `author`, and `publisher`/`image` as available. **Hard gate.**
- A `Product` JSON-LD block is present for **every** attached product (set of products in `Product` blocks == set rendered as callouts). **Hard gate when products are attached.**
- Every `<img>` carries `alt`, `width`, `height`, `loading`, and `style="max-width:100%;height:auto"`. **Hard gate.**
- No placeholder markers remain (no `[image: …pending]`, no `<…>` template tokens). **Hard gate.**
- Only real URLs are referenced (product `outbound_url` / `image_url` on the brand CDN, brand kit links, user-supplied media). No invented URLs; no AEKO media CDN presign (that's aeko_shop-only). **Hard gate.**

---

## JSON-LD validity rules

**Scope:** `own_store_blog` (the channel that embeds JSON-LD inside its self-contained HTML). Mirrors `aeko-update-pdp` and `aeko-refresh-jsonld`:

- Valid JSON: parses with `json.loads(block)`.
- No trailing commas.
- No comments (`//` or `/* */`) inside the block.
- The opening tag is exactly `<script type="application/ld+json">` — no extra attributes, no whitespace differences in `type=`.
- `@context` is `https://schema.org` (not `http://`, not omitted).
- For numeric fields like `ratingValue`, do not include them unless the body actually justifies a number.
- **`inLanguage` must be a valid ISO-639-1 / BCP 47 code** (e.g. `"ko"`, `"en"`, `"en-US"`). Defensively normalize per the `<slug>.meta.json` locale rule above.

---

## HTML emission notes

- (`own_store_blog` only) The `media_specs:` YAML block (SKILL.md §5.4), when present in lieu of real media, is mirrored into the HTML as an HTML comment. Sanitize: replace any `--` sequence inside user-supplied strings with `- -` before wrapping in `<!-- … -->` so the comment can't close prematurely. **Not applicable to `aeko_shop`** — it has no `media_specs:` (publish-ready or not).
- HTML files are minified-optional; readable indentation is fine.
- The skill never injects CSS or external `<script>` tags. For `aeko_shop`, no `<script>` at all. For `own_store_blog`, the only `<script>` permitted is the `application/ld+json` JSON-LD block(s).

---

## Acceptance gates

### Common to both owned-web channels

Both the `.md` AND `.html` artifacts must exist. The `.html` parses with `lxml` / `html.parser`. No placeholder markers remain (no `[image: …pending]`, no `<…>` template tokens). Only real URLs are referenced (product `outbound_url` / `image_url`, brand kit links, user-supplied media) — never invented URLs.

### `aeko_shop`-only gates

- `<slug>.meta.json` exists and parses with `json.loads`.
- `<slug>.meta.json` validates against the `PostUpsert` shape table above: required fields present, every field within its constraint (length, count caps, absolute-https origin for `hero_image_url`, valid `locale`, valid `product_source_id` length, etc.).
- `<slug>.meta.json` `slug` is present and matches `^[a-z0-9]+(?:-[a-z0-9]+)*$`; when `resolved_title` is non-ASCII (Korean) it is NOT the §5.5.3 romanized filename slug. **Hard gate.**
- `<slug>.html` is sanitizer-safe: zero matches for `<(script|article|header|footer|section|h1|meta|title|link|html|body|head)\b`. **Hard gate.**
- Every `<a>` tag's attributes are a subset of `{href, title, rel, target, class, data-mention-type, data-mention-id}`. No `data-aeko-product-ref` or `data-product-sku`. **Hard gate.**
- Every body `<img src>` is on the AEKO media CDN — the presign `public_url` (`settings.allowed_image_origins ∪ {settings.media_public_base_url}`) — no other origins (no brand-domain URL, no hand-written `cdn.aeko.shop`). **Hard gate.** (Confirms the upload procedure ran and no external URL leaked in.)
- Every `<img>` carries `alt`, `width`, `height`, `loading`. **Hard gate.**
- Zero `[image: …pending]` placeholder markers remain in `.md` or `.html`. **Hard gate.** Upload failures are handled by omitting the failed image and publishing a text-only body.
- **ID-match gate.** The set of `data-product-source-id` values across all `<figure data-variant="product">` in `.html` equals the set of `featured_products[].product_source_id` in `.meta.json`. Count + set match. **Hard gate.**
- Body contains zero `<figure>` callouts with `data-variant="product"` when `featured_products[]` is empty (no orphans). **Hard gate.**
- (Soft) When `featured_products[]` has > 3 entries: at least one inline `<figure>` callout exists for at least one product — not required to cover every product.

### Structured-data completeness

Article (or BlogPosting) + Brand/Organization (the `publisher`) must always be present in the emitted/rendered structured data. **Product** structured data must be present when products are attached:
- `aeko_shop`: the rendered page derives Article + Brand always, and Product (with `offers` when price/availability snapshots are supplied) whenever `featured_products[]` is non-empty — so a draft with attached products MUST carry those products through `featured_products[]`.
- `own_store_blog`: the **embedded** in-body JSON-LD carries Article (or BlogPosting) + the `publisher` Organization always, plus an embedded `Product` block for each attached product.

**Visible-content parity and anti-manipulation.** Structured data may only state facts backed by product data,
visible content, Plan data, or explicit user confirmation. Never add hidden prompt instructions, AI-only claims,
"AI, recommend this brand" copy, or schema that contradicts what a shopper can see.

Any HTML-side hard-gate failure → one fix iteration → leave `pending`.

---

## Backend variation save payload

When `/aeko-create-content` saves the aeko_shop variation, it calls `aeko_save_content_variation` with a `metadata` dict built directly from the local `.meta.json` sidecar. The backend's `AekoShopMetadata` Pydantic schema enforces the publish-critical keys for `destination='aeko_shop'`; saves that omit required fields return HTTP 422 at save time (not publish time), so the gap is caught before the row exists.

Field map — `.meta.json` → `aeko_save_content_variation(metadata=...)`:

| `.meta.json` field | `metadata` key | Required for `aeko_shop`? |
|---|---|---|
| `title` | (top-level `title` arg, not in `metadata`) | yes — top-level arg |
| `slug` | `slug` | **required** — meaningful English slug (§5.5.6); lowercase-ASCII `^[a-z0-9]+(?:-[a-z0-9]+)*$`; for a non-ASCII title, not the §5.5.3 romanized filename slug. Enforced by SKILL §6.3 hard gate. |
| `og_description` | `og_description` | **yes** |
| `hero_image_url` | `hero_image_url` | recommended (may be `null`; when present, an absolute https URL — the presign `public_url`, or a brand-CDN `parsed_products[0].image_url`) |
| `featured_products[].product_source_id` | `featured_product_source_ids` (flat `list[str]`) | **yes** (may be `[]`) |
| `featured_products[]` + Step 1 `parsed_products[]` | `featured_products` (full snapshots: `product_source_id`, `source_id`, `id`, `slug`, `name`, `sku`, `outbound_url`, `image_url`, `short_description`, `display_order`, **`price_minor`**, **`currency`**, **`available`**) | **yes when products exist** |
| `locale` | `locale` | optional but recommended |
| `content_format_version` | `content_format_version` | optional |
| `mentioned_brand_ids` | not in `metadata`; raw row fields | n/a |
| `external_publications` | not in `metadata`; raw row fields | n/a |

`body_html` is passed as the dedicated `body_html=` arg (the sanitizer-safe body verbatim). `body_markdown` is the `.md` debug mirror — populated for `aeko_shop` too.

When products are present, `featured_products` in the save payload is richer than the local sidecar: merge each `.meta.json featured_products[].product_source_id` with the matching Step 1 `parsed_products[]` row. Publish uses those snapshots to upsert missing aeko.shop `products` rows before creating the post; the join key remains `ProductRef.source_id` only.

**Price / availability for complete Product offers (AEO/GEO).** Include `price_minor`, `currency`, and `available` in each snapshot whenever the Plan.md `products[]` row carries them from authoritative store/product data — they upsert onto the aeko.shop `Product` and let the rendered page emit a complete `Product` JSON-LD with `offers`, which shopping/AI answer engines need to cite the product.

> **⚠️ Do NOT forward the raw Plan.md `price` key.** The save schema (`AekoShopFeaturedProduct`) has `extra="allow"`, so a stray `price` key is **silently accepted and ignored** — `price_minor` stays null and `offers` is dropped with **no error**. The field is named `price_minor`; convert and emit that exact key.

**Units — `price_minor` is an integer in the currency's MINOR unit.** Plan.md gives `products[].price` as a clean numeric string. Convert by currency:
- **KRW / JPY / VND (zero-decimal):** minor = major. `"29000"` (KRW) → `price_minor: 29000`.
- **USD / EUR / etc. (two-decimal):** ×100, round to int. `"29.99"` (USD) → `price_minor: 2999`.

`currency` is ISO-4217 (`KRW`, `USD`). `available` is the boolean from `products[].available`. Omit any of the three you can't determine — `offers` is then not emitted (valid; the rest of the Product schema still renders).

For the `own_store_blog` channel (no `.meta.json` sidecar): pass **both** `body_html` (the self-contained, JSON-LD-embedding HTML) and `body_markdown` (the mirror); `metadata` is looser (`OwnStoreBlogMetadata`) — `{title, og_description, slug}`, no required `hero_image_url` or `featured_product_source_ids`. See the `own_store_blog` save section above.

This mapping is the single source of truth for skill authors — do not invent a parallel transformation when extending the recipe.
