---
name: drafter-instructions
purpose: The contract for a single per-channel drafter. The coordinator (SKILL.md) spawns one drafter subagent per selected channel in parallel; each one reads this file plus aeo-frameworks.md plus its channel recipe, drafts the artifact, and returns a structured self-check.
load_when: Read by each drafter subagent at the start of its task (the coordinator points it here).
---

# Per-channel drafter contract

You are drafting **one channel** of an AEKO content item. You run in parallel with sibling drafters
for the other channels; you share nothing with them except the files on disk, so stay within your
own channel directory. Your job: turn the substance you were handed into one citable artifact, then
report honestly on whether it passed its gates.

## 1. Inputs (the brief)

The coordinator hands you a JSON brief:

```
{
  "channel": "naver_blog",                 // your channel slug
  "domain_id": "...", "item_id": "...",    // for artifact paths
  "resolved_title": "...",                  // drives the slug (§5.5)
  "target_language": "ko",                  // BCP-47-ish content language, e.g. ko | en | ja | zh | es
  "target_cohort": "...",                    // sharpen per aeo-frameworks §3b
  "must_include": [...], "forbidden": [...], // hard content constraints
  "contrarian_hint": "..." | null,           // deep mode only — the gap in current AI answers
  "products": [ {id, source_id, name, sku, slug, outbound_url, image_url,
                 short_description, full_description, ocr_text} ],   // substance backbone
                 // ocr_text: Claude-vision text extracted from image-only/image-heavy PDPs
                 // (clinical/test results, %s, ingredient amounts, certifications). null if none.
  "context_reviews": [ {context, persona, quote, detail} ],  // lived experience — originality source
  "media": { "<slot>": {src, alt, type} | null },  // from the media form
  "recipe_path": "references/recipes/naver_blog.md" | null
}
```

`products[]` and `context_reviews[]` are your substance. If both are empty (no-product run), draft
from the prompt + a neutral, product-led voice + your own expertise, and follow the anti-fabrication rule strictly.

## 2. Process

1. **Read `references/aeo-frameworks.md`** — this is your quality bar. Then read your `recipe_path`
   (channel format conventions) if one was given. For the **owned-web channels** (`aeko_shop`,
   `own_store_blog`) your `recipe_path` IS `references/recipes/editorial-html-jsonld.md` — follow §3 below.
   Paste-tier channels only need their thin recipe (or none) + the frameworks.
   Also read brand example files when present:
   - Always read `references/examples/in-store-content-example.md` if it exists; it is the global owned-content voice signal.
   - `naver_blog` and `tistory`: read `references/examples/blog-example.md` plus any `references/examples/<channel>-*example*.md`.
   - `press_release`: read `references/examples/press-release-example.md` plus any `references/examples/press_release-*example*.md`. The Korean UI label is `보도자료`, but the channel slug is `press_release`.
   - Other paste-tier channels: read any `references/examples/<channel>-*example*.md`.
   - If an example file is missing, skip it silently. Examples shape tone and structure; they do not supply facts, URLs, or claims.
2. **Plan the substance, then the shape.** Decide the BLUF answer, the 2–4 PREP blocks, which
   context-review supplies the originality detail for each, the cohort, the contrarian angle, and
   **2–3 honest trade-offs/limitations (a "best for / not for" beat, grounded in specs/reviews —
   never invented)** per `aeo-frameworks.md` §4.5. *Then* fit it to the channel's format from the recipe.
3. **Draft** in the neutral product-led voice (voice precedence below). Pull real specifics from product
   `full_description`, **`ocr_text`** (image-extracted clinical/test results, percentages, ingredient
   amounts, certifications — treat these as **primary**, high-citability evidence; quote figures exactly
   in PREP examples and E-E-A-T FAQ answers), and `context_reviews`. Honor `must_include` (each string
   appears at least once) and `forbidden` (never appears). No hard CTAs ("지금 구매" / "Buy now" /
   "Click here") — AEKO content earns the click through authority, not commands.
4. **Media** — embed only what's in `media`. Use real `![alt](src)` / `<img alt>`; never emit
   `[Image]`/`[photo]`/`[placeholder]`/`TODO` markers. If a visual-first channel has no media, emit
   the fenced `media_specs:` YAML block (see recipe). Every image carries non-empty alt text.
5. **Write the file(s)** to the §5.5 path: `./aeko-artifacts/<domain_id>/<item_id>/<filename_token>/<slug>__<filename_token>.<ext>`.
   Derive `<slug>` and `<filename_token>` exactly per SKILL.md §5.5 (the coordinator passes those rules).
6. **Self-check** (below) and return the result JSON.

### Voice precedence (highest first)
1. Brand example file (`references/examples/<channel>-*example*.md`, when present) →
2. channel recipe conventions (format/register norms) → 3. target-cohort vocabulary.
Absent an example file, write in a **neutral, product-led voice** grounded in the product facts, OCR
substance, and context-reviews. When format and that voice conflict (e.g. `press_release` requires a
formal register — 합니다체 for KO, AP-style for EN), the format wins for that channel — note it in your self-check.

## 3. Owned-web channels (`aeko_shop` and `own_store_blog`) — the HTML + JSON-LD path

These two channels publish as real web pages, so they produce HTML with extra mechanics. They differ in
**who renders the structured data**, which changes the HTML shape. Read
`references/recipes/editorial-html-jsonld.md` and follow the matching section exactly.

### `aeko_shop` — body-only (the aeko.shop frontend regenerates JSON-LD)
- Produce the **triple**: `<slug>__aeko_shop.html` (sanitizer-safe **body-only** HTML — no
  `<html>/<head>/<script>/<h1>/<article>`), `<slug>__aeko_shop.meta.json` (publish payload), and
  `<slug>__aeko_shop.md` (debug mirror). **No in-body JSON-LD** — the frontend regenerates it.
- **Media upload:** every inline body `<img>` must be an AEKO-media-CDN `public_url` from
  `aeko_request_media_upload` (presign → curl PUT with the Azure headers → verify reachable). Brand-CDN
  product images are allowed only in the hero (`.meta.json hero_image_url`) and bottom product cards
  (`next/image`), never in body HTML. The recipe carries the exact steps and digests.
- **Slug:** `.meta.json slug` must be a *meaningful English* slug (translate, don't transliterate),
  matching `^[a-z0-9]+(?:-[a-z0-9]+)*$`; for a Korean title it must NOT equal the romanized filename slug.
- **Products:** render as `<figure role="callout" data-variant="product" data-product-source-id="<source_id>">`;
  the set of source-ids in HTML must equal `featured_products[].product_source_id` in `.meta.json`.
- If a media upload fails, omit that image and produce a valid text-only post — warn loudly, never
  leave a placeholder.

### `own_store_blog` — self-contained (the brand's store renders it as-is)
- Produce `<slug>__own_store_blog.html` (self-contained) + `<slug>__own_store_blog.md` (mirror). No
  `.meta.json` (that's an aeko.shop-only payload).
- **Embed JSON-LD yourself:** the store does NOT regenerate schema, so the `.html` MUST contain
  `<script type="application/ld+json">` with `Article`/`BlogPosting` (always) and `Product` (when products
  attached). This is the whole reason this channel needs the skill.
- **Not sanitizer-constrained:** semantic tags (`<article>`, `<h1>`, `<figure>`, `<table>`, `<script>`
  JSON-LD) are expected. Make it **responsive**: every `<img>` carries `alt`/`width`/`height`/`loading`
  and `style="max-width:100%;height:auto"`; fluid layout.
- **Media:** reference brand-hosted or user-supplied URLs/paths directly — do **NOT** call
  `aeko_request_media_upload` (that's aeko.shop-only). Product `image_url` (brand CDN) is fine to reference.
- **Products:** render inline cards/links from `outbound_url` + `image_url`, and include each in the
  embedded `Product` JSON-LD.

## 4. Return value (self-check JSON)

Return ONLY this object — it's data for the coordinator, not a message to a human:

```
{
  "channel": "naver_blog",
  "artifact_paths": ["<absolute path>", ...],
  "references_loaded": ["references/recipes/naver_blog.md", "references/examples/blog-example.md"],
  "framework_check": {
    "bluf": true, "prep": true, "specific_cohort": true, "contrarian": true,
    "originality_source": "context_review" | "expertise_only",  // expertise_only = no reviews; flag it
    "eeat_faq": true | "n/a"
  },
  "hard_gates": {
    "no_placeholders": true, "alt_text_present": true, "no_invented_urls": true,
    "forbidden_clean": true, "must_include_satisfied": true,
    "aeko_shop_sanitizer_safe": true | "n/a", "slug_valid": true | "n/a",
    "img_origins_valid": true | "n/a", "product_id_match": true | "n/a"
  },
  "notes": "any conflicts resolved, media dropped, or substance gaps flagged"
}
```

Be truthful in the self-check — the coordinator re-verifies the publish-blocking aeko_shop hard
gates before saving, so an inflated self-report just wastes a round-trip. If a hard gate fails after
one fix iteration, report it `false` with a note rather than papering over it.
