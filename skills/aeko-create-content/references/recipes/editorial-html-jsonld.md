---
channel: editorial-html-jsonld
purpose: HTML wrapper + JSON-LD schema for editorial channels (보도자료, magazine, partner_media)
load_when: SKILL.md §5.1 selects an editorial channel; load alongside the channel-specific recipe file
---

# Editorial channels — HTML + JSON-LD pair

Applies to `보도자료`, `magazine`, and `partner_media`. These channels write **two** artifacts: the existing `<slug>.md` (canonical, human/editor-facing) AND a `<slug>.html` (publish-ready, structured-data-bearing) at the same channel-segmented path. The `.md` remains the source of truth; the `.html` is generated from it.

## HTML structure

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

## JSON-LD schema per channel

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

`Review` is added when §3.5 locked the recipe to `Review` or detected `Review` as a top `@type`:

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

## JSON-LD validity rules

Mirror `aeko-update-pdp` and `aeko-refresh-jsonld`:

- Valid JSON: parses with `json.loads(block)`.
- No trailing commas.
- No comments (`//` or `/* */`) inside the block.
- The opening tag is exactly `<script type="application/ld+json">` — no additional attributes, no whitespace differences in `type=`.
- `@context` is `https://schema.org` (not `http://`, not omitted).
- For numeric fields like `ratingValue`, do not include them unless the body actually justifies a number.
- **`inLanguage` must be a valid ISO-639-1 / BCP 47 code** (e.g. `"ko"`, `"en"`, `"en-US"`) — the contract pins `frontmatter.target_language` to ISO-639-1 (action-item-contract.md §3.1), but defensively normalize: if the field is `"Korean"`/`"한국어"` map to `"ko"`; `"English"`/`"영어"` map to `"en"`; if the value is unrecognized, fall back to `"ko"` (AEKO's primary market) and surface a one-line warning above the artifact summary.

## HTML emission notes

- The `media_specs:` YAML block (SKILL.md §5.4), when present, is mirrored into the HTML as an HTML comment above `<footer>`. Sanitize: replace any `--` sequence inside user-supplied strings with `- -` before wrapping in `<!-- … -->` so the comment can never close prematurely.
- If `frontmatter.canonical_url` is absent, omit the `<link rel="canonical">` tag entirely — do not emit an empty `href`.
- HTML files are minified-optional; readable indentation is fine. The skill never injects CSS or external `<script>` tags beyond the JSON-LD block.

## Schema parity with cited sources

(Step 3.5 / 3.4): if `structural_template_by_channel[channel]` carries observed JSON-LD `@type`s from cited sources, the artifact's emitted `@type` SHOULD be in the same family. Mismatch is a soft warning at Step 6, not a hard fail — sometimes the editorial choice is to upgrade (cited sources are bare `Article` but you have data for `NewsArticle`).

## Acceptance gates (HTML pair)

Both `<slug>.md` AND `<slug>.html` must exist. The `.html` file:

- Parses as HTML (well-formed enough for `lxml` / `html.parser` to accept).
- Contains exactly one `<article>` root.
- Each `<script type="application/ld+json">` block parses with `json.loads` after stripping the script wrapper.
- Required JSON-LD fields are present per the schema above (e.g., `NewsArticle` requires `headline`, `datePublished`, `author`, `publisher`).
- **Schema parity** soft check: emitted top-level `@type` is in the same family as the cited sources' dominant `@type` (`Article` ⊇ `NewsArticle`/`BlogPosting`; `Review` ⊇ `Review`/`Recommendation`). Mismatch warns once.

Any HTML-side hard-gate failure → one fix iteration → leave `pending`.
