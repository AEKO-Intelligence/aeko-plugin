---
name: aeko-publish-content
description: >
  Single-destination publisher for the `aeko_shop` artifact produced by
  `/aeko-create-content`. Reads the local `aeko_shop/<slug>.{html,meta.json,md}`
  triple, optionally re-fetches Plan.md for a drift check, and sends a
  single rich call to aeko.shop with `body_html` (the .html verbatim) and
  the top-level fields from `.meta.json`. aeko.shop is the only
  publishing destination this skill routes to. Other channels' drafts
  (tistory, naver_blog, social, editorial) remain on disk as
  generation-only outputs — clients post them themselves.
argument-hint: "<item-id>"
allowed-tools: aeko_get_action_plan, aeko_get_brand_kit, aeko_publish_content, aeko_get_publish_status, Read, Bash
---

# AEKO Publish Content

Runs after `/aeko-create-content`. Picks up the `aeko_shop` artifact triple for one item, builds a publish payload from the artifact's `.html` (body) + `.meta.json` (top-level fields), and POSTs it to aeko.shop's `aeko_publish_content` MCP. aeko.shop is the source of truth — and currently the only AEKO-routed destination.

This skill does **not** route Tistory, Naver Blog, Instagram, TikTok, YouTube, 보도자료, magazine, or partner_media drafts anywhere. Those artifacts are produced by `/aeko-create-content` for the client to consume however they want (paste into their own Tistory account, hand to a PR distribution service, schedule via their social tooling, etc.). No Notion work-queue, no cross-post handoff.

> **Backend prerequisite — `aeko_publish_content` MCP handler not yet implemented.** As of writing, `aeko-mcp/aeko_mcp/tools/` does not contain a `aeko_publish_content` (or `aeko_get_publish_status`) handler. The aeko.shop backend has `POST /internal/posts` (per `aeko-shop-backend/app/routes/internal.py`) but the MCP tool that fronts it hasn't shipped. Running this skill today will fail at Step 6 with a tool-not-found error. The skill is shipped ahead of the backend so the executor + payload shape is reviewable; the backend handler is tracked as a separate ticket.

## Input

- `item-id` (required) — `$1`. If missing, stop and point the user to `/aeko-action-center <domain_id> content` to discover the item, or to `/aeko-create-content <item_id>` if drafts don't exist yet.

## Step 0 — Backend availability preflight (cheap; runs first)

The `aeko_publish_content` MCP handler is shipped ahead of the backend tool implementation (see the Backend prerequisite callout above). This step detects the case where the handler is missing and surfaces a friendly message **before** any artifact reads, brand-kit calls, or user-facing confirms — so a user who just ran `/aeko-create-content` and clicks the "Publish:" suggestion doesn't see a generic tool-not-found stack trace at Step 6.

Probe by introspecting the tool registry:

1. Check whether `aeko_publish_content` is a registered MCP tool name in the current session. This is a registry lookup, not a call — no network traffic, no side effects.
2. If **present** → proceed to Step 1 silently.
3. If **absent** → stop and print (bilingual; pick by `target_language` if available, else default to the user's locale):
   - EN:
     ```
     aeko.shop publish backend is rolling out
     
     Your draft is saved and verified:
       ./aeko-artifacts/<domain_id>/<item_id>/aeko_shop/
         ├─ <slug>.html         ← sanitizer-safe body, ready for PostUpsert
         ├─ <slug>.meta.json    ← publish-payload sidecar (mirrors PostUpsert)
         └─ <slug>.md           ← debug mirror
     
     The MCP tool that POSTs to aeko.shop's backend (aeko_publish_content) is the last
     piece still shipping. Your artifact is already complete — you'll be able to publish
     by re-running /aeko-publish-content <item_id> once the tool lands. No re-drafting
     needed.
     
     Status: track AEKO release notes or run /aeko-action-center to check.
     ```
   - KO:
     ```
     aeko.shop 게시 백엔드가 곧 출시됩니다
     
     초안은 저장되어 있고 검증되었습니다:
       ./aeko-artifacts/<domain_id>/<item_id>/aeko_shop/
         ├─ <slug>.html         ← 검증된 본문 (PostUpsert 준비 완료)
         ├─ <slug>.meta.json    ← 게시 페이로드 사이드카 (PostUpsert와 1:1)
         └─ <slug>.md           ← 디버그용 미러
     
     aeko.shop 백엔드에 POST하는 MCP 도구(aeko_publish_content)가 마지막으로 출시 대기 중입니다.
     초안 자체는 이미 완성돼 있으므로, 도구가 출시되면 /aeko-publish-content <item_id>를 다시
     실행하기만 하면 게시됩니다. 다시 작성할 필요는 없습니다.
     
     상태 확인: AEKO 릴리즈 노트를 확인하거나 /aeko-action-center를 실행하세요.
     ```

Exit with status code 0 — this is a "your work is preserved, come back later" message, not an error.

The probe is deterministic: it does not consume tokens for a backend call, and it does not produce false negatives because tool registration is a local property of the MCP session.

## Step 1 — Locate the aeko_shop artifact triple

The on-disk layout from `/aeko-create-content` is:

```
./aeko-artifacts/<domain_id>/<item_id>/aeko_shop/<slug>.html
./aeko-artifacts/<domain_id>/<item_id>/aeko_shop/<slug>.meta.json
./aeko-artifacts/<domain_id>/<item_id>/aeko_shop/<slug>.md
```

- `<slug>.html` — sanitizer-safe body HTML; shipped verbatim as `PostUpsert.body_html`.
- `<slug>.meta.json` — publish-payload sidecar mirroring `PostUpsert` top-level fields. The source of truth for `title`, `og_description`, `hero_image_url`, `locale`, `featured_products[]`, `source_content_id`, `mentioned_brand_ids[]`, `external_publications[]`.
- `<slug>.md` — debug mirror of the body; not consumed by this skill, but its presence is the §6.3 gate's parity check with the other channels.

If `<domain_id>` is not in the argument, scan `./aeko-artifacts/*/<item_id>/aeko_shop/` for the one match. **Derive `<domain_id>` from the matched artifact path** (the path component immediately under `./aeko-artifacts/`) — this is the publish skill's source of truth for `brand_id`. Plan.md is **not** required for `brand_id`; the artifact is self-locating. Stop with an actionable error if:

- No `aeko_shop/` subdirectory under `<item_id>` → "No aeko_shop draft found for `<item_id>`. Either the brand doesn't have an aeko.shop tenant (channel never appeared in Step 4 of `/aeko-create-content`), or it was deselected at §4b. Re-run `/aeko-create-content <item_id>` with `aeko_shop` kept in the channel set."
- Multiple `<item_id>` matches across domains → ask the user to pass `<domain_id>/<item_id>`.
- aeko_shop dir exists but is missing any of `.html` / `.meta.json` / `.md` → "Editorial triple incomplete. Re-run `/aeko-create-content <item_id>` so the §6.3 acceptance gates run again."

All three files must exist. Read `.html` and `.meta.json` (the `.md` is debug-only). The `.html` carries the body; the `.meta.json` carries every top-level publish field.

## Step 2 — Read .meta.json + optional Plan.md drift check

**`.meta.json` is the publish source of truth.** Read it once at the start of this step and use its fields verbatim for the publish payload (Step 4). The previous version of this skill extracted `productID` values from in-body JSON-LD `<script>` blocks; that path is removed — the sanitizer at `aeko-shop-backend/app/sanitizer.py` rejects every `<script>` element, so the body `.html` never contains JSON-LD anymore. Product IDs come from `.meta.json` `featured_products[].product_source_id`.

**Language selection for user-facing messages.** Use `meta.locale` (the source of truth for this artifact) to pick the language for every warning/error string in Steps 2-5. `locale` starting with `ko` → Korean variant; anything else → English variant. Both variants are listed below.

Steps:

1. Read `aeko_shop/<slug>.meta.json`. Parse with `json.loads`. Validate it has the required top-level keys (`locale`, `title`, `og_description`, `source_content_id`, `content_format_version`, `featured_products`). Missing required keys → stop with:
   - EN: `meta.json missing required key \`<name>\`. Re-run /aeko-create-content <item_id>.`
   - KO: `meta.json에 필수 키 \`<name>\`이(가) 없습니다. /aeko-create-content <item_id>를 다시 실행해 주세요.`
2. Extract `meta_product_source_ids = [fp.product_source_id for fp in meta.featured_products]`. Preserve order; this becomes the publish payload's `featured_products` (Step 4).
3. **Integrity check (hard gate).** Read `aeko_shop/<slug>.html` and scan for every `<figure data-variant="product" data-product-source-id="X">`. Collect the `X` values as `figure_source_ids`. Assert set equality with `meta_product_source_ids` (the §6.3 ID-match gate from `/aeko-create-content` should already have enforced this, but a publish-time re-check catches local hand-edits). Mismatch → stop with an actionable explanation (not just a set-diff dump). Let `extra_in_html` = `figure_source_ids - meta_product_source_ids` and `extra_in_meta` = `meta_product_source_ids - figure_source_ids`:
   - EN:
     ```
     ⚠ Your <slug>.html and <slug>.meta.json disagree about which products this post links to.
        In <slug>.html only:       <extra_in_html or "(none)">
        In <slug>.meta.json only:  <extra_in_meta or "(none)">

     This usually means you hand-edited one of the files. Either:
       • Remove the orphan callouts from <slug>.html (the ones listed under "In .html only"), OR
       • Re-run /aeko-create-content <item_id> to rebuild a consistent triple — the dashboard's
         상품 선택 list is the source of truth.
     Publishing as-is is blocked because the linked products on the rendered page would not match
     what the body HTML actually references.
     ```
   - KO:
     ```
     ⚠ <slug>.html과 <slug>.meta.json의 연결 상품이 일치하지 않습니다.
        <slug>.html에만 있음:       <extra_in_html or "(없음)">
        <slug>.meta.json에만 있음:  <extra_in_meta or "(없음)">

     보통 한쪽 파일을 직접 편집했을 때 발생합니다. 다음 중 하나를 선택해 주세요:
       • <slug>.html에서 "html에만 있음"으로 표시된 callout을 제거하거나,
       • /aeko-create-content <item_id>를 다시 실행해 일관된 결과물을 다시 만드세요 — 대시보드의
         상품 선택이 진실 공급원입니다.
     렌더링된 페이지의 연결 상품과 본문 HTML이 일치하지 않게 되므로 그대로 게시할 수 없습니다.
     ```
4. **Plan.md drift check — fully advisory; never blocks publish.** Call `aeko_get_action_plan(item_id)` opportunistically. The skill does **not** require Plan.md to publish — `brand_id` comes from the artifact path (Step 1), and every payload field comes from `.meta.json`. Plan.md is consulted only to surface whether the brand's product selection has drifted since draft time. Split the drift signal by direction:
   - Let `additions` = `plan_md_source_ids - meta_product_source_ids` (products newly selected after draft time) and `removals` = `meta_product_source_ids - plan_md_source_ids` (products that were in the draft but are no longer in the brand's catalog / Plan).
   - Call succeeds → parse YAML frontmatter for `products[]` and compute the two sets:
     - **Exact match** → proceed silently.
     - **Additions only** (`removals == ∅` and `additions != ∅`) → emit a one-line info note (not a blocker; users will normalize to this signal so keep it muted):
       - EN: `ℹ Plan.md added <N> new product(s) since draft time. The published post will not include them. Re-run /aeko-create-content if you want them in the body.`
       - KO: `ℹ 초안 시점 이후 Plan.md에 상품 <N>개가 추가되었습니다. 이번 게시에는 포함되지 않습니다. 본문에 반영하려면 /aeko-create-content를 다시 실행해 주세요.`
     - **Removals present** (`removals != ∅`) → this is the dangerous case (the artifact links to products that may 404 on click). Emit a **confirm prompt**, not just a warning:
       - EN: `⚠ <M> product(s) referenced by this draft are no longer in your Plan.md: <comma-joined removals>. Those product links may 404 on click. Continue publishing? [y/N]`
       - KO: `⚠ 본 초안이 참조하는 상품 <M>개가 Plan.md에 더 이상 없습니다: <comma-joined removals>. 게시 후 해당 상품 링크는 404가 될 수 있습니다. 그대로 게시하시겠습니까? [y/N]`
       - User declines (default) → stop without publishing. User confirms → continue with `meta_product_source_ids` as-is.
     - **Returned `item_id` differs from artifact directory** → emit a single warning ("Plan.md item-id mismatch — skipping drift check; verify the artifact directory" / "Plan.md item-id 불일치 — drift 체크를 건너뜁니다; artifact 디렉터리를 확인하세요") and **do not** stop; the artifact is still the source of truth.
   - Call fails (network, 4xx, 5xx, item not found) → emit a single warning ("Plan.md unavailable — skipping drift check" / "Plan.md을(를) 가져올 수 없어 drift 체크를 건너뜁니다") and continue. Plan.md unavailability is not a publish blocker.

**No HTML JSON-LD parsing anywhere in this skill.** The body `.html` is a courier payload; it is read for the ID-match integrity check only, never to extract structured-data fields.

## Step 3 — Brand-kit recheck (soft, optional)

Call `aeko_get_brand_kit(domain_id)` opportunistically — `domain_id` comes from Step 1's artifact path. Compare brand-kit `updated_at` against the newest artifact mtime under `<item_id>/aeko_shop/`. All messages bilingual; pick by `meta.locale`:

- Brand kit newer than artifacts by >24h → warn:
  - EN: `⚠ Brand kit was updated after this draft was generated. Re-run /aeko-create-content <item_id> to capture the latest voice, or proceed with the older draft.`
  - KO: `⚠ 이 초안이 생성된 이후 브랜드 키트가 업데이트되었습니다. 최신 보이스로 다시 작성하려면 /aeko-create-content <item_id>를 실행하거나, 기존 초안으로 진행하세요.`
- Brand kit missing or call fails → warn and continue:
  - EN: `ℹ Brand kit unavailable — voice recheck skipped. The publish call does not consume brand-kit fields directly.`
  - KO: `ℹ 브랜드 키트를 가져올 수 없어 보이스 검수를 건너뜁니다. 게시 호출 자체는 브랜드 키트 필드를 사용하지 않습니다.`
- Otherwise → proceed silently.

Never blocks; soft warning + confirm-to-continue.

## Step 4 — Build the publish payload

Construct the `aeko_publish_content` payload. Every top-level field except `body_html` and `brand_id` comes from `<slug>.meta.json` directly:

| Field | Source |
|---|---|
| `brand_id` | `<domain_id>` derived from the artifact path at Step 1 (`./aeko-artifacts/<domain_id>/<item_id>/aeko_shop/...`). Independent of Plan.md so the skill remains publishable when Plan.md is unavailable. |
| `source_content_id` | `meta.source_content_id` (must equal `frontmatter.item_id`). |
| `title` | `meta.title`. |
| `body_html` | raw contents of `aeko_shop/<slug>.html` — no transformation, no parsing, no extraction. The body file is shipped verbatim. |
| `hero_image_url` | `meta.hero_image_url` (may be null). |
| `og_description` | `meta.og_description`. |
| `featured_products` | `meta.featured_products` — array of `{product_source_id, display_order}`. Backend joins on `Product.source_id` and hydrates name/sku/price/etc. from its own Product table. |
| `mentioned_brand_ids` | `meta.mentioned_brand_ids` (default `[]`). |
| `external_publications` | `meta.external_publications` (default `[]`). |
| `locale` | `meta.locale` (e.g., `ko`, `en`, `ko-KR`). |
| `content_format_version` | `meta.content_format_version` (currently `1`). |

The skill is a courier — it does **not** transform `body_html` and does **not** mutate `.meta.json`. Whatever `editorial-html-jsonld.md` produced is what aeko.shop receives.

## Step 5 — Confirm

Print a one-block summary before sending. Every value comes from a non-blocking source — `<domain_id>` from the artifact path, `<title>` / `<hero_image_url>` / `<locale>` / featured-products IDs from `.meta.json`. Plan.md and brand kit are advisory; when either is missing, fall back to the artifact-derived values without blocking.

**Human-readable product names — resolution order** (Step 5 is a human confirmation; SKU strings like `BIO-CLS-001` are unreadable, so do this work to give brand owners something they can verify):

1. **Plan.md fetched successfully** (Step 2 step 4) → use `plan_md.products[].name` joined by source_id. Best signal.
2. **`.html` callout figcaptions** → scan body `.html` for each `<figure data-product-source-id="X">` block, extract the `<figcaption><strong>...</strong>` text. The recipe (`references/recipes/editorial-html-jsonld.md` §"Product callout pattern") authors this from `parsed_products[].name` at draft time, so this is the same name the user saw when drafting. Use when Plan.md is unavailable.
3. **Source-ID fallback** → if neither 1 nor 2 yields a name for a given source_id (no Plan.md AND no inline figcaption for that product — only happens when Plan.md is missing AND the product appears only in `.meta.json` `featured_products[]` but has no inline callout), render the bare `product_source_id`.

```
Publish plan
  brand:             <brand_label if brand-kit fetched, else <domain_id>>
  item:              <item_id>
  destination:       aeko.shop
  body source:       ./aeko-artifacts/<domain_id>/<item_id>/aeko_shop/<slug>.html
  title:             <meta.title>
  hero image:        <meta.hero_image_url or "none">
  featured products: <N> (<comma-joined names via resolution order above>)
  locale:            <meta.locale>
```

Ask for confirmation (bilingual prompt per `meta.locale`): EN `Proceed with publish? [y/N]` / KO `게시할까요? [y/N]`. If the user declines → stop without sending anything. Skip the prompt only when an explicit `non_interactive` flag is passed by a caller (forward-compat; no such caller exists today).

## Step 6 — Publish

Single MCP call:

```
aeko_publish_content(
  brand_id              = ...,
  source_content_id     = item_id,
  title                 = meta.title,
  body_html             = <.html file contents>,
  hero_image_url        = meta.hero_image_url,
  og_description        = meta.og_description,
  featured_products     = meta.featured_products,
  mentioned_brand_ids   = meta.mentioned_brand_ids,
  external_publications = meta.external_publications,
  locale                = meta.locale,
  content_format_version = meta.content_format_version,
)
```

The call is the single side-effecting moment in this skill. If it fails:

- 4xx → surface the backend message verbatim. Common cases: brand_id ownership (403), pro-tier gate (403), body_html sanitizer rejection (`aeko-shop-backend/app/sanitizer.py` raises 400 with the enumerated disallowed tag/attribute set, e.g. `"HTML contains disallowed tags or attributes: script, h1, img[srcset]"`), `<img>` origin rejection (400, non-`cdn.aeko.shop` URLs), `PostUpsert` schema validation (422 — e.g. `og_description > 500 chars`, `content_md5` length, missing required field). The sanitizer NEVER silently strips; every rejection is a 400 with the exact rule violated. Don't retry — re-run `/aeko-create-content <item_id>` if the artifact is the problem.
- 5xx / network → surface error + tell the user the publish was not recorded. They can re-run; idempotency is keyed on `(brand_id, source_content_id)` so re-runs are safe.

## Step 7 — Report

On success, print (bilingual per `meta.locale`):

EN:
```
Published to aeko.shop:  <aeko_shop_url>
Post ID:                 <post_id>
Status:                  published
Featured products:       <N> linked to your live catalog (<comma-joined names>)
Structured data:         Article + Product schemas regenerated at render time —
                         ChatGPT / Claude / Perplexity / Gemini can cite the post
                         and the linked products directly from the rendered page.
```

KO:
```
aeko.shop에 게시 완료:    <aeko_shop_url>
포스트 ID:                <post_id>
상태:                     published
연결된 상품:              실시간 카탈로그 <N>개 연결 (<comma-joined names>)
구조화 데이터:            Article + Product 스키마가 렌더링 시점에 재생성되어
                          ChatGPT / Claude / Perplexity / Gemini가 본 포스트와
                          연결된 상품을 직접 인용할 수 있습니다.
```

If aeko.shop publish failed → hard stop with the backend error. No partial state to report; nothing else to do in this skill.

If the original action item is still `pending` and the user wants to mark it done, suggest `/aeko-action-center <domain_id>` to close it manually. This skill does **not** auto-complete the action item — completion is a Plan.md decision, not a publish decision.

## Step 8 — Status follow-up (optional)

If the user later asks "is the post live?", call `aeko_get_publish_status(post_id)` and pretty-print the current state plus the aeko.shop URL.

## Error paths

- aeko_shop artifact dir missing → stop with "Run `/aeko-create-content <item_id>` first, ensuring `aeko_shop` is in the selected channels."
- aeko_shop triple incomplete (any of `.html` / `.meta.json` / `.md` missing) → stop; instruct re-run.
- `.meta.json` fails to parse, missing required keys, or set-disagrees with `.html`'s `data-product-source-id` values → stop; instruct re-run (re-drafting will rebuild a consistent triple).
- Plan.md re-fetch fails → **warn and continue** (drift check is advisory; the artifact is the publish source of truth and `brand_id` is derived from the artifact path).
- Brand kit missing → warn ("Brand kit not configured for `<domain_id>` — voice recheck skipped; proceeding with the existing artifact. Run `/aeko-brand-kit <domain_id> edit` if voice drift is a concern."); do not block publish. The publish call only needs `brand_id` (from path) and the `.meta.json` fields; brand-kit lookup is for the soft staleness warning at Step 3 only.
- `aeko_publish_content` 4xx → surface message; no retry.
- `aeko_publish_content` 5xx / network → surface; instruct re-run; rely on idempotency.

## Hard rules

- **aeko.shop is the only destination.** This skill does not route Tistory, Naver Blog, Instagram, TikTok, YouTube, 보도자료, magazine, or partner_media drafts anywhere. Those are generation-only outputs from `/aeko-create-content`; the client posts them themselves.
- **Never auto-post anywhere else.** No Notion queue, no Chrome-bridge, no API integration for non-aeko.shop channels lives in this skill.
- **Never widen `allowed-tools`** to include browser-bridge tools, Tistory APIs, Naver APIs, or Notion tools. If a future skill needs those, it lives in its own SKILL.md with its own permission boundary.
- **Never re-render or transform** the artifact `body_html`. The skill is a courier from disk → backend; the backend owns rendering.
- **Idempotent.** Re-running on the same `<item_id>` is safe; backend de-dupes on `(brand_id, source_content_id)`. Already-published posts return the existing post + URL without re-publishing.
- **Never read prose to extract machine values** — `post_id`, `aeko_shop_url`, status come only from the structured MCP response.

## What this skill never does

- Never writes to Tistory, Naver Blog, Instagram, TikTok, YouTube, or any external channel directly.
- Never queues those drafts in Notion or anywhere else.
- Never modifies artifact files on disk.
- Never marks the originating action item complete (that's a Plan-side decision via `/aeko-action-center`).
- Never publishes content that wasn't drafted by `/aeko-create-content` — the artifact pair is the source.
- Never invents an aeko.shop URL or post_id — those come from the MCP response, or the call failed.
