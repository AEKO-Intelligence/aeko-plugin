# PDP Structural Status Rules

This is the testable contract for `aeko-pdp-audit`. It mirrors the dashboard's parser-derived
`aeo_checks` gating set and emits only `ready`, `needs_fixes`, or `analyzing`.

The backend also defines an older `ai_readiness_status` triad: `ready` when a crawled page's internal
`citability_score` is at least 70, `needs_fixes` when it is below 70, and `analyzing` before it is crawled.
This skill deliberately does not use that content-derived triad: product surfaces use the structural
`aeo_status` derived from `aeo_checks`, and the audit must not expose or recreate a numeric citability score.

Connected mode is deliberately deferred for G0. This skill computes the structural status from public or
local evidence and does not read a stored `aeo_status` through AEKO yet.

## Policy

`policy_version: 2`

Evaluate these gating checks in this exact order:

1. `crawlable`
2. `indexable`
3. `canonical_present`
4. `product_jsonld`

The checks mean:

| Check | `pass: true` | `pass: false` | Unknown |
|---|---|---|---|
| `crawlable` | A URL finishes with HTTP 200 and no fetch error. | The URL does not finish with HTTP 200, or fetching reports an error. | A local file has no live HTTP result, or no fetch result exists. |
| `indexable` | No applicable `noindex` or `none` directive appears in HTML robots metadata or the HTTP `X-Robots-Tag`. | An applicable `noindex` or `none` directive appears in either source. | The relevant HTML and response headers could not be inspected. |
| `canonical_present` | A non-empty canonical URL is present. | The page was inspected and has no non-empty canonical URL. | The page head could not be inspected. |
| `product_jsonld` | Parseable JSON-LD contains a `Product` with a non-empty `name` and an `Offer` with non-empty `price` or `lowPrice`. | JSON-LD was inspected and no such complete `Product` exists. | The page source could not be inspected. |

`Product` may be top-level, in an array, or inside `@graph`. `offers` may be one object or an array; at
least one offer must carry `price` or `lowPrice`.

## Derivation algorithm

Use the dashboard algorithm literally:

```text
if aeo_checks is not an object: analyzing
for check in [crawlable, indexable, canonical_present, product_jsonld]:
  if check is absent, is not an object, or check.pass is null: analyzing
  if check.pass is false: needs_fixes
ready
```

The ordered early return is intentional. Do not replace it with a weighted calculation or a count of
passing checks. Advisory checks never change this status.

## Advisory checks

Report these as findings without changing the triad:

- `faqpage_jsonld`
- `aggregate_rating`
- `title_ok`
- `meta_description_ok`
- `h1_single`
- `heading_hierarchy`
- `og_complete`
- `image_alt_ok`
- crawler policy for the target path
- live per-user-agent target and robots.txt access
- image-extracted product facts
- `image_dependency`
- `schema_body_product_copy_mismatch`

### Image dependency determination

This is advisory and never changes the structural status. Let `product_copy_character_count` be the Unicode
character count of the normalized `product_copy_text` segment printed in the text-only box, and let
`detail_image_count` be the number of positioned detail-image components. Never use
`total_character_count`, `merchandising_widget_character_count`, `platform_boilerplate_character_count`, or
`chrome_character_count` as the text basis for this determination.

Build `product_copy_text` by positively identifying text that describes the current item, using the page
title, product heading, Product JSON-LD `name`, module context, and product-specific facts as evidence. It is
not the remainder after exclusions. Tag every other included block as a named non-product segment, and
exclude in-root tab/navigation/review-summary chrome, merchandising widgets for other products, and
platform-appended commerce boilerplate from the count.

Detect a merchandising widget by three independent signals: an other-products offer heading; a dense run
of currency/price tokens with little prose; and repeated product names that differ from the current page's
title and Product JSON-LD `name`. One signal is weak, while any two are decisive for a coherent module. The
heading examples in `SKILL.md` are illustrative rather than a fixed string list. Detect boilerplate from
semantic section headings and their common variants—payment, shipping/delivery,
exchanges/returns/refunds, and customer service/support—not exact bytes, one platform name, or a CSS
selector. After the first recognized commerce heading, treat the remaining included detail-root blocks as
boilerplate unless positive product identity or unique product facts establish a clearly interleaved
product-content block. The full bot-view output still shows all non-product text in separately labeled
verbatim sections.

Evaluate in this exact order:

```text
if detail_image_count == 0 and product_copy_character_count == 0: no_content
else if detail_image_count > 0 and product_copy_character_count < 100: image_only
else if detail_image_count > 0 and product_copy_character_count < detail_image_count * 100: image_heavy
else: text_ok
```

Print the counts and this rule with the determination. Do not convert it to a percentage or readiness score.
For `no_content`, state: "No product-detail content was found at this URL — the detail root may be rendered
by JavaScript, or the selector did not match." Treat it as a serious evidence-backed finding while keeping
it advisory; it never changes the structural triad.

As a separate sanity check, when product copy is empty, detail images exist, and valid Product JSON-LD has
a non-empty `description`, emit `schema_body_product_copy_mismatch`. The schema description proves the
merchant has supplied product text, but that text is absent from the page-body product-copy stream. Keep
the finding advisory, classify the missing body signal `high`, and never let JSON-LD description satisfy
`image_dependency`.

## Live crawler evidence

For URL audits, raw browser evidence and live user-agent probes come from the bundled
`scripts/fetch_evidence.py --mode page`; markdown conversion is not evidence for head markup, JSON-LD, lazy-image attributes,
or crawler status. Report observed target and `/robots.txt` HTTP status separately for `GPTBot`,
`ClaudeBot`, `OAI-SearchBot`, `PerplexityBot`, `Google-Extended`, `CCBot`, and `Googlebot`.

Robots-file rules explain policy but never override an observed response. If the normal-browser request and
robots fetch succeed, a named crawler receives 403, and no controlling robots rule disallows it, classify
that as a platform-edge block and direct escalation to the host. It is not a robots.txt failure the merchant
can repair in the file. Classify an observed edge block `high`. These crawler findings remain advisory:
structural `crawlable` is still the normal document request's HTTP-200 check.

## Presentation of unknown checks

The derivation algorithm remains unchanged. When it returns `analyzing` because a check is unknown, list all
four gating checks as `true`, `false`, or `unknown`, name the evidence that could not be assessed, and name
the checks that were assessed successfully. For a local file, state that the file audit completed and a live
URL is required to resolve `crawlable`; do not present `analyzing` as a failed audit. If a later assessed
check is false, report that failure separately even though the ordered algorithm returned early on unknown.

## Golden cases

| Gating input | Expected status |
|---|---|
| all four checks are present and `pass: true` | `ready` |
| `crawlable`, `indexable`, `canonical_present` are true; `product_jsonld` is false | `needs_fixes` |
| all four checks are present; `indexable` is false | `needs_fixes` |
| no check object exists | `analyzing` |
| only `crawlable` is present and true | `analyzing` |
| local file: `crawlable` is unknown, later checks are available | `analyzing` |
| all gating checks pass and every advisory check fails | `ready` |

The `image_dependency` golden cases are:

| Product-copy character count | Detail-image count | Expected determination |
|---|---|---|
| 41 | 8 | `image_only` |
| 240 | 8 | `image_heavy` |
| 800 | 8 | `text_ok` |
| 0 | 0 | `no_content` |

### Real commerce-platform regression cases

| Live page | Total characters | Chrome | Merchandising widget | Platform boilerplate | Product-copy characters | Detail images | Naive answer | Correct answer |
|---|---:|---:|---:|---:|---:|---:|---|---|
| `https://grafen.co.kr/product/볼륨업-그루밍-휘핑-토닉/794/category/1/display/40/` | 2,685 | 0 | 426 | 2,258 | 0 | 40 | `image_heavy` from 426 widget characters | `image_only` |
| `https://collectmoments.kr/product/detail.html?product_no=924&cate_no=1&display_group=2` | 1,539 | 34 | 0 | 1,179 | 325 | 9 | `text_ok` from all 1,539 characters | `image_heavy` |

On Grafen, the 426-character `함께 구매하면 좋아요` module satisfies all three merchandising signals:
an other-products heading, 24 price tokens with almost no prose, and repeated product names that differ
from `볼륨업 그루밍 휘핑 토닉`. Counting the widget would return `image_heavy`; the positive-definition
rule finds 0 product-copy characters against 40 images and returns `image_only`. A non-empty Product JSON-LD
`description` does not change that result: it triggers the separate schema/body mismatch finding instead.

On Collect Moments, the naive rule compares 1,539 to `9 * 100` and passes. That is the documented wrong
answer: 1,179 characters come from the Cafe24 payment/shipping/returns/support module, not the product. The
corrected rule compares 325 product-copy characters to `9 * 100` and returns `image_heavy`. Segment counts
are direct counts of their independently normalized strings; an inter-segment DOM newline belongs to the
full stream rather than product copy.
