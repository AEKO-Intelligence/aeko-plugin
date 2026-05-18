---
name: aeko-create-content
description: >
  Multi-channel content executor for Action-tab items with
  `execution_class=local_content_artifact`. Fetches a Plan.md, runs
  tracked-prompt citation forensics to identify the source structures
  AI engines actually cite (Reddit threads, Naver blogs, partner media,
  etc.), then fans out into per-channel drafts: auto-detected channels
  from forensics PLUS user-added formats (보도자료 / magazine /
  Instagram / TikTok / YouTube / free-form). Optional image/video
  reference per channel. Saves locally; never writes to a store and
  never auto-publishes. Splits the content branch out of the retired
  `/aeko-run-action`.
argument-hint: "<item-id>"
allowed-tools: aeko_get_action_plan, aeko_get_brand_kit, aeko_resolve_prompts_by_text, aeko_get_tracked_prompts, aeko_get_tracked_prompt, aeko_crawl_url, aeko_list_own_content, aeko_request_media_upload, aeko_complete_action_item, Read, Write, Bash, WebFetch, WebSearch
---

# AEKO Create Content

Executes one Action-tab content item end-to-end: fetch Plan.md → pull citation-forensics on tracked prompts → identify winning source structures + auto-detect channels → confirm channels with user + collect optional add-on formats and per-channel media → draft N channel-fitted artifacts in the brand voice → save local artifacts → mark complete.

Contract reference: `docs/contracts/action-item-contract.md` §3 (Plan.md), §3.2.1 (ProductRef), §6 (completion). Pinned to contract minor `v1.4` (introduces formal `ProductRef.source_id` required for `aeko_shop` product-callout publishing; backend `build_plan_md()` hydration still pending — see Step 1's "Backend wiring note").

## Input

- `item-id` (required) — `$1`. If missing, stop and point user to `/aeko-action-center <domain_id> content`.

## Step 1 — Fetch and parse the Plan.md

Call `aeko_get_action_plan(item_id)`. Parse YAML frontmatter + prose.

**Validate:**
- `contract_version` starts with `2026-04-17.action.v1.` — else stop.
- Pin this skill to contract minor `v1.4` (matches the skill header). Greater minor → print advisory + proceed.
- `tab == "action"` — else stop.
- `execution_class == "local_content_artifact"` — else redirect to the right executor.
- `artifact_type ∈ {own_store_markdown, external_media_markdown, own_store_content, external_media_content}` (accept both v1 and v2 names for forward-compat). In v2 this is **advisory** — actual channel set is decided in Step 4 — but it must be present.
- `status ∈ {pending, ready}` — else stop.
- `write_target == "local"` — content artifacts never write to store; mismatch → stop.
- `tier_required` gate via brand kit metadata.

**Parse `products[]` (optional; contract minor v1.4 — see `docs/contracts/action-item-contract.md §3.2.1`).** When the v1.4 backend wiring ships, Plan.md generated from the dashboard's `상품 선택` mode will carry a `products[]` array; brand-wide mode omits it. Today (pre-v1.4) the field is absent from all live Plan.md — the parse logic below is forward-compat. Each entry shape:

```yaml
products:
  - id: <uuid>                  # AEKO internal Product UUID. Required.
    source_id: <str(1..240)>    # External brand-registered identifier
                                #   (e.g., Shopify variant ID). Required for v1.4
                                #   forward. aeko.shop backend joins on this via
                                #   Product.source_id.
    name: <display name>        # Required.
    slug: <url-safe slug>       # Required.
    sku: <optional sku>
    outbound_url: <deep link, e.g. https://aeko.shop/brands/<brand>/products/<slug> or the client store's product URL>  # Required.
    image_url: <https://cdn.aeko.shop/... URL>  # Required.
    short_description: <≤240 chars, optional>
```

**`id` vs `source_id`.** Different ID spaces — `id` is AEKO's internal UUID for cross-AEKO references; `source_id` is the brand-registered external identifier and is what `PostUpsert.featured_products[].product_source_id` joins on at publish time. Both must be present for v1.4. See `docs/contracts/action-item-contract.md §3.2.1` for the authoritative definition.

If `products[]` is present:
- Validate each entry has at minimum `id`, `source_id`, `name`, `outbound_url`, `image_url`. Entries missing any of those → drop with a single warning line listing the dropped IDs; keep going with the rest.
- For pre-v1.4 Plan.md (where `source_id` may be absent because `build_plan_md()` hasn't been updated): drop the entry with the same warning. Do **not** fabricate `source_id`; do **not** fall back to `id` for the `product_source_id` slot. Without `source_id` the publish-time backend join fails and downstream product callouts are inert.
- Carry the validated list into Step 4 and Step 5 as `parsed_products[]`.
- The list is only consumed by the `aeko_shop` channel's draft (§5.3 + the editorial recipe's "Product callout pattern" section). Other channels render product names as plain text in the body when relevant; they do not generate product reference links.

If `products[]` is empty or absent (including the "pre-v1.4 backend, every entry dropped for missing `source_id`" case):
- `aeko_shop` (if selected) still drafts a rich article without product callouts. `.meta.json` has empty `featured_products[]` and no `<figure data-variant="product">` blocks appear in `.html`. Non-fatal.
- **Surface a pre-v1.4 distinguishing notice when applicable.** If `frontmatter.content_scope == "products"` (v1.4 dashboard flag — `상품 선택` mode was used) AND `products[]` is absent or empty AND `aeko_shop` is in the selected channel set, the user picked specific products on the dashboard but the backend hasn't shipped the hydration yet. Emit a one-line info note in §4a to distinguish "pending backend" from "your selection didn't save":
  - EN: `ℹ Product-specific content generation (상품 선택 mode) is waiting on a backend release — this draft will be written in your brand's general voice without inline product callouts. Your selection is preserved on the dashboard; re-run this skill after the release to see product callouts in the body.`
  - KO: `ℹ 상품 선택 기반 콘텐츠 생성은 백엔드 배포 대기 중입니다 — 이번 초안은 브랜드 전체 톤으로 작성되며 본문에 인라인 상품 callout이 포함되지 않습니다. 대시보드의 상품 선택은 그대로 유지되며, 배포 후 다시 실행하면 본문에서 상품 callout을 확인할 수 있습니다.`
  - If `frontmatter.content_scope` is absent (older Plan.md without the flag) or is `"brand"`, do NOT surface this note — an empty `products[]` in brand-wide mode is the expected shape.

The §4a.5 warning ("Plan carries N products but aeko_shop not active") fires only if `parsed_products[]` is non-empty AND `aeko_shop` is not in the final selected channel set after §4e.

**Backend wiring note** — as of the v1.4 contract revision, `build_plan_md()` does NOT yet hydrate `products[]` (or `source_id` on those entries) from the dashboard's product-selection payload. Until the backend wires this, every Plan.md will have `products[]` empty regardless of which content-scope mode the user picked. The skill remains pinned to v1.4; the contract is in place ahead of the backend so skills can validate against the final shape before the wiring ships.

Print header in `target_language`:
1. Action label — KO (own): "자사 콘텐츠 생성: `<artifact_type>`" / KO (external): "외부 매체 콘텐츠 생성: `<artifact_type>`" / EN: "Generating {own-site|external-media} content: `<artifact_type>`"
2. Context: domain, channels suggested by Plan (comma-joined).
3. Persona: `persona_label` if present.
4. Note: "Final channel set decided after forensics in Step 4."

Print prose verbatim. Never echo frontmatter.

## Step 2 — Stale brand-kit check

If `frontmatter.requires_brand_kit == true`:
- `aeko_get_brand_kit(frontmatter.domain_id)`. Missing / empty → stop with Brand-Kit-missing message.
- Verify voice minimum: `tone_of_voice` present + at least one of `{brand_voice_summary, target_audience}`. Thin kit → warn + offer to abort (`/aeko-brand-kit <domain_id> edit`).
- Snapshot-version drift: ask user.

## Step 3 — Citation forensics (two phases)

This is what makes AEKO-grounded content beat vanilla Claude. Build a structural model of what AI engines currently cite for this topic, then mimic — across one OR many channels.

The work splits in two:

- **Phase 3A — Selection forensics** (runs before Step 4). Cheap signal only: prompt resolution, compact tracked-prompt snapshot, cited-domain ranking, channel auto-detection, in-store dedupe index, selection-confidence score. No live recrawls; no full-body harvesting. Feeds Step 4's channel-selection UX.
- **Phase 3B — Post-selection enrichment** (runs during §4e, after channel/media selection and before the proceed-to-draft confirmation). Live recrawls and the full structural template — but only for channels the user actually kept. Feeds Step 5's drafting.

The phase boundary means deselected channels never pay an enrichment cost. Net effect vs. the single-phase predecessor: roughly half the tokens on 3A.1 (no bodies, `latest` window), all live crawls deferred and scoped to the kept channels, all tool fan-outs issued as parallel batches.

### Phase 3A — Selection forensics (pre-Step-4)

#### 3A.0 Resolve `prompts_to_rank_on` to UUIDs

`frontmatter.prompts_to_rank_on` may carry either UUIDs (preferred — newer Plan-builders write these directly) or raw prompt text (older Plan-builders + manually authored Plans). `aeko_get_tracked_prompt` only accepts UUIDs, so resolve text → UUID before 3A.1.

Pass the whole list through `aeko_resolve_prompts_by_text(prompts_to_rank_on)` in one call. The tool short-circuits entries that already look like UUIDs and matches the rest against `prompt_en` / `prompt_ko` / `raw_prompt` server-side (NFC + lowercase + strip-punctuation + collapse-whitespace), returning one deterministic line per input:

```
- "웨딩 촬영 전 피부 톤업 앰플 추천" → `7a3f8b2c-…` (matched_via: prompt_ko)
- "에스테틱샵에서 쓰는 비타민C 앰플" → UNRESOLVED
- `92c4e6a1-…` → already a UUID
```

Carry `(text → uuid, matched_via)` for §4a transparency. **Do not** fall back to grep-parsing `aeko_get_tracked_prompts` markdown — that table renders `prompt_ko` on a separate row from the ID column, which is why text→UUID resolution used to silently fail on Korean Plan.md inputs.

Collect any `UNRESOLVED` entries and surface them in §4a as "unresolved prompts" (don't silently drop) — the user needs to know which prompts were skipped.

**Hard precondition.** If zero entries resolve to UUIDs (every input came back UNRESOLVED), stop here:

```
Forensics requires tracked prompts. None of `prompts_to_rank_on` resolved to a tracked UUID.

Either:
  • track these prompts first: /aeko-find-prompts-to-track <domain_id>
  • or rewrite the Plan with UUIDs from `aeko_get_tracked_prompts`.

Re-run /aeko-create-content <item_id> after.
```

Do not proceed to 3A.1 with zero resolved UUIDs and do not fall back to research-prompt search — see 3A.8.

Cap `prompts_to_rank_on` to the top 5 resolved UUIDs (by Plan ordering) before 3A.1.

#### 3A.1 Compact snapshot pull

For each resolved UUID from 3A.0, call `aeko_get_tracked_prompt(prompt_id, window="latest")`. Issue **all** of these calls as a single parallel batch — they have no inter-dependencies; sequencing them is wasted wall-clock. Issue them in the same batch as 3A.4's `aeko_list_own_content` call (also independent).

Per citation, harvest only:
- `domain`
- `source_url`
- `source_type`
- `position_in_response`
- `context_snippet`
- JSON-LD `@type`s (from the `JSON-LD: …@types` line)
- `Citability: …` score
- `Extracted: …` body slice (server-side 600-char capped)

Per response, retain only the platform and any per-response counters needed for ranking — **not** the response body. Body text is not consumed downstream; Step 5 mimics cited-source format, not AI-response prose. Harvesting the body inflates context for no signal.

If the snapshot carries an embedded `crawl` payload per cited URL (the prompt-collection-time crawl alongside the citation), preserve it under `cached_crawl_by_url{}` for 3A.5 and 3B.2 — those payloads are older but free, and the 3B.2 stale-gate can reuse them when fresh enough.

#### 3A.2 Rank cited sources

Rank the aggregated sources by **citation frequency × inverse average position × citability score** (when the score is present). Surface the top 5–10 source domains and their canonical URLs.

#### 3A.3 Auto-detect candidate channels

Classify each top source domain into a channel slug per the table in `references/forensics/channel-detection.md`. Read that file lazily on first need (once per skill run). Deduplicate while preserving rank order. Carry `auto_detected_channels[]` into Step 4.

#### 3A.4 List in-store content

Single call: `aeko_list_own_content(domain_id, type="all", limit=15)`. Issue this in the same parallel batch as 3A.1's tracked-prompt fan-out — independent.

Split the result client-side by `content_type`:
- Build `in_store_topic_index[]` from the (title, url) pairs across blog and PDP rows. Used in §4a duplicate detection: if the working draft title is ≥80% token-overlap with an existing page, surface the conflict and offer a pivot at Step 4e.

**Do not crawl in-store posts in 3A.** Tone-signature crawling is conditional and moves to 3B.4.

New domain with no in-store content → call returns empty; skip silently and note "no in-store signature — drafting from cited-source signal only" in §4a output. Non-fatal.

#### 3A.5 Build light structural template stubs

For each `auto_detected_channels` entry, build a *stub* of `structural_template_by_channel[channel]` from snapshot-only signals:

- Citability score across the channel's top cited URLs.
- JSON-LD `@type`s aggregated across the channel's cited sources (from snapshot citation data).
- `Extracted: …` body slices joined for tone calibration.
- If `cached_crawl_by_url{}` (from 3A.1) carries data for any of this channel's top sources, derive approximate numeric targets (paragraph word counts, heading depth, list density) from the cached crawl. Mark these stubs with `freshness: cached` for §4a transparency. If no cached crawl is available for a channel, omit the numeric-targets line at §4a for that channel and report `freshness: pending`.

These stubs power §4a's "Structural targets" hint so the user can pick channels intelligently. 3B.5 upgrades them with live-crawl data for the channels the user keeps; deselected channels' stubs are discarded.

#### 3A.6 Initialize `cited_url_allowlist[]`

Seed `cited_url_allowlist[]` with every `source_url` harvested in 3A.1. 3B.6 and Step 4d append to it; Step 6.1 reads it as the source of truth for "no invented URLs."

#### 3A.7 Compute selection confidence

Purely pre-crawl, no recrawl dependency:

- `high` — ≥3 prompts resolved × ≥3 distinct cited domains × JSON-LD `@type` present on ≥50% of citations.
- `medium` — ≥1 prompt × ≥2 cited domains.
- `low` — anything weaker (single prompt resolved, no citations, every prompt empty for the latest window, etc.).

Reported in §4a as `Selection confidence: high|medium|low`. Drives 3B.1's recrawl escalation: `low` selection confidence triggers the 3-URL escalation in 3B even on non-editorial channels.

#### 3A.8 No-tracked-prompts handling

3A.0 already hard-stops when zero entries resolve to UUIDs. The skill does **not** fall back to `aeko_search_research_prompts` — research prompts are unrelated to the user's tracked-prompt set, so their forensics carry the wrong structural signal (different cited sources, different `@type`s, different audience). Substituting them produces drafts that look forensics-grounded but optimize for the wrong queries.

If 3A.0 succeeded but every `aeko_get_tracked_prompt` call in 3A.1 returns no responses for the latest window (tracked but never re-queried), surface this in 3A.7 as `low selection confidence` with the note "tracked prompts exist but no response history yet — re-run after the next response cycle, or proceed with brand-kit-only drafting." The user decides at §4e whether to abort.

### Phase 3B — Post-selection enrichment (runs during §4e, after channel/media selection)

3B runs after Step 4d completes (≥1 selected channel) and before the §4e proceed-to-draft confirmation. Enrichment is scoped to the selected channels — deselected auto-detected channels pay nothing. The §4e summary reports freshness so the user can see what 3B produced before committing to drafting; if they cancel or edit at §4e, the 3B output is discarded.

#### 3B.1 Recrawl budget per selected channel

- Default budget: top **1–2** cited URLs per selected channel (rank order from 3A.2).
- Escalate to **3** when either:
  - Selection confidence (3A.7) is `low`, **or**
  - The channel is editorial — `보도자료`, `magazine`, or `partner_media` — because §5.6.6 emits JSON-LD that should parity-match the cited-source dominant `@type`, and 1–2 URLs may not be enough to identify the dominant type.

#### 3B.2 Stale-gate the recrawls

For each URL in the channel's recrawl budget:

1. Compute `snapshot_age_days` from the most-recent response timestamp on the tracked prompt that surfaced this URL.
2. If `snapshot_age_days ≤ 7` AND `cached_crawl_by_url[url]` (from 3A.1) carries `title` + `meta_description` + `og.image` + `json_ld[]`, **reuse the cached payload** and skip the recrawl for this URL.
3. Otherwise call `aeko_crawl_url(url, force_refresh=true)`.

Record per-URL outcome — `cached_fresh` (stale-gate suppressed), `recrawled_success`, `recrawled_failure` — for 3B.7's freshness confidence.

#### 3B.3 Parallel-batch recrawl

Issue every URL eligible for recrawl in 3B.2 (i.e., the ones not suppressed by the stale-gate) across all selected channels as a single parallel batch — not sequential per channel.

On any recrawl failure (4xx/5xx, connect error), log a single warning line and keep going on the snapshot signal alone. Recrawl is enriching, not gating.

Per recrawled URL, merge into the channel's structural template (in 3B.5):

- **Numeric targets** (override snapshot when fresher): `paragraphs.avg_word_count`, `paragraphs.median_word_count`, heading count + max depth, `lists.ul_count`/`ol_count`/`total_items`, `images.count`, `images.with_alt`.
- **Schema signal**: collect `json_ld[]` raw blocks across the top sources; aggregate `@type`s. Drives the editorial-channel HTML JSON-LD recipe in Step 5.
- **Title / meta seeds**: `title` and `meta_description` seed the draft's own title and meta when the channel has metadata slots.
- **Visual seeds**: `og.image` and `images.alt_examples` feed the Step 5.4 `media_specs:` block when the user skipped media.
- **Tone signal**: combined with the snapshot's `Extracted: …` text from 3A.1, the live crawl's title + meta + first heading establish the cited source's diction; carry into Step 5.3.

#### 3B.4 Conditional in-store crawl

Fetch the top **1** in-store blog post via `aeko_crawl_url(url)` (cached default — in-store pages are slower-changing; the 24h cache is fine here) **only when**:

- Any selected channel is an own-store channel (artifact_type starts with `own_store_`), **or**
- The cited-source structural template is thin (the top selected channel has fewer than 3 cited sources) AND no brand-specific exemplar matched in §5.0.

Otherwise skip — cited-source structural template + brand kit + exemplars carry the voice.

If the crawl runs, build `in_store_tone_signature{}` (title length, paragraph length, heading style, list density) for §5.3's voice precedence.

#### 3B.5 Build `structural_template_by_channel{}` for selected channels

Upgrade the 3A.5 stubs (selected channels only) by merging:

1. Snapshot signals from 3A.1 (citability score, JSON-LD `@type`s, extracted-text tone).
2. Live crawl signals from 3B.2 / 3B.3 (numeric targets, raw JSON-LD blocks, OG fields, title/meta seeds) — or the cached-fresh payload when the stale-gate suppressed the recrawl.
3. **JSON-LD `@type` lock** — when an `@type` dominates the channel's top sources, lock the recipe to it:
   - `QAPage` / `DiscussionForumPosting` → reddit recipe locked to Q&A
   - `Article` / `NewsArticle` → tistory / partner_media / editorial recipes calibrated to measured paragraph + heading stats
   - `Recipe` / `HowTo` → step-list scaffold
   - `Review` → comparison / scoring scaffold

**You are not copying text** — you are matching format: if Reddit threads win, the draft reads like a Q&A with lived-experience tone; if Naver 블로그 wins, it reads like a first-person informal review with in-line images; if partner-media wins, it reads like a comparison article with product callouts. Carry `structural_template_by_channel{}` (selected-channels only) into Step 5.

Deselected auto-detected channels: their stubs from 3A.5 are discarded — do not build full templates for channels the user did not keep.

#### 3B.6 Append crawled URLs to `cited_url_allowlist[]`

Every URL passed to `aeko_crawl_url` in 3B.2 or 3B.4 — success or failure both count — appends to `cited_url_allowlist[]`. Failure URLs may still be referenced via §4d media so they remain allowlist-eligible.

#### 3B.7 Compute freshness confidence

Post-crawl:

- `high` — ≥50% of attempted recrawls succeeded, **or** all selected channels' templates derived from snapshots ≤7 days old (stale-gate fully suppressed the recrawls because cached data was fresh).
- `medium` — at least one selected channel has fresh signal (`cached_fresh` or `recrawled_success`); others may be stale or failed.
- `low` — all recrawls failed and no snapshot is ≤7 days old.

Reported in §4e as `Freshness confidence: high|medium|low` alongside the recrawl tally. Distinct label from selection confidence — never collapse them.

## Step 4 — Channel & media selection (interactive)

This step is the v2 fanout. Always run; respect `skip` / `none` for empty selections.

### 4.0. Auto-add `aeko_shop` for tenant brands (runs before §4a prints)

This substep mutates `auto_detected_channels[]` so the §4a summary below reflects the final pre-selection set. Run it before any §4a output.

aeko.shop publishing is enabled for a brand when (a) the brand is on the Pro tier or higher (content-generation is gated Pro+ per contract §3.2 — `aeko-mcp/docs/contracts/action-item-contract.md`'s 2026-04-27 tier-restructure entry), AND (b) the backend `Brand` row's `aeko_shop_disabled` field is `false` (the default — see `aeko-shop-backend/app/models.py:32`). Read the brand-kit response from Step 2:

**Tier gate (runs first, hard):** Read `brand_kit.metadata.account_tier`. Allowed values per contract §3.2: `starter`, `pro`, `enterprise`.

- `account_tier ∈ {pro, enterprise}` → proceed to the destination-flag check below.
- `account_tier == starter` → **do not** prepend `aeko_shop`. Emit a one-line user-facing message (bilingual when `frontmatter.target_language` starts with `ko`):
  - EN: `ℹ aeko.shop publishing is a Pro feature — your draft will skip aeko_shop. Upgrade at <brand_kit.metadata.billing_url or https://aeko-intelligence.com/billing>.`
  - KO: `ℹ aeko.shop 게시는 Pro 플랜 이상에서 사용할 수 있어요. 이번 초안에서는 aeko_shop을 건너뜁니다. 업그레이드: <brand_kit.metadata.billing_url 또는 https://aeko-intelligence.com/billing>`
  - Continue with the rest of the channel set; the user can still pick the non-aeko_shop channels.
- `account_tier` missing / unrecognized → emit a one-line warning ("ℹ Account tier not surfaced by brand kit — skipping aeko_shop preselection. Re-run /aeko-brand-kit to refresh.") and **do not** prepend `aeko_shop`. Safer to omit than to draft a publish-ready triple the user can't actually publish.

**Destination-flag check (runs second, only when tier passes):** Read `brand_kit.aeko_shop_disabled`:

- `false` (or absent — backend default) → prepend `aeko_shop` to `auto_detected_channels[]`. The channel appears in §4a's "Auto-detected channels" line and is preselected at §4b — the user can still deselect it. When the field is absent, emit a one-line warning in §4a: "ℹ aeko.shop status not surfaced by brand-kit response — assuming enabled. Verify in the dashboard if aeko_shop draft is unexpected."
- `true` → no-op; `aeko_shop` never appears in the channel set.

**Backend wiring note** — as of the current MCP minor version, `aeko_get_brand_kit` may not surface `aeko_shop_disabled` or `metadata.account_tier` in its response. When `account_tier` is missing the tier gate is conservative (omits aeko_shop); when `aeko_shop_disabled` is missing the destination gate assumes enabled. Both fields need to land in the brand-kit MCP route response for the gate to fire correctly; track as a backend prerequisite (same workstream as the `products[]` hydration in `build_plan_md`).

`aeko_shop` is **not** forensics-detected; it's a brand destination flag. Its §4a "Structural targets" line reads `freshness: pending` until 3B runs (3B will recrawl 1–2 representative pages from the brand's existing aeko.shop content via the same `aeko_list_own_content` → `aeko_crawl_url` flow used for any other selected channel, then derive numeric structural targets).

When `aeko_shop` lands in the final selected set, drafting for it uses `references/recipes/editorial-html-jsonld.md` (the same recipe `보도자료`/`magazine`/`partner_media` use; aeko_shop has its own section in that file with the sanitizer-safe body-only HTML shape, the `<slug>.meta.json` sidecar, and the product callout pattern — see §5.6 and §5.6.6). aeko.shop is the **only** channel that consumes `parsed_products[]` (from Step 1) — rendered as `<figure role="callout" data-variant="product" data-product-source-id="<source_id>">` callouts in body HTML and `featured_products[]` entries in `.meta.json`. **No in-body JSON-LD** — the aeko.shop frontend regenerates Article + Product structured data from `PostUpsert` fields at render time. If `parsed_products[]` is non-empty but `aeko_shop` is **not** in the final selected channel set after §4e, surface a warning before drafting: "Plan carries `<N>` products but `aeko_shop` channel is not active — products won't be linked. Re-select `aeko_shop` at §4b to use them, or accept that other channels render product names as plain text only."

**User-facing channel label.** When printing the channel in §4a/§4b/§4e, render it as `aeko_shop (브랜드 스토어 · aeko.shop)` on first appearance and `aeko_shop` thereafter — this gives Korean-speaking users immediate context for what aeko.shop is. Other channels keep their bare slug since their slugs are platform names.

### 4a. Print selection summary

Print the Phase 3A signal so the user can tell at a glance whether forensics is grounded **before** committing to channels. This is pre-crawl — the live recrawl runs in Phase 3B during §4e (after channel/media selection completes, before the proceed-to-draft confirmation), so the recrawl line is "deferred" here and reported separately at §4e.

The `Selection confidence` line is computed in 3A.7:

- `high` — ≥3 prompts × ≥3 distinct cited domains × JSON-LD `@type` on ≥50% of citations
- `medium` — ≥1 prompt × ≥2 cited domains
- `low` — anything weaker

```
Prompt resolution (3A.0):
  resolved:    3/4 prompts (1 by UUID, 2 matched by text)
  unresolved:  "아토피 알레르기 이불 추천" — not in tracked set; track it via /aeko-find-prompts-to-track

Top cited source domains (top 5):
  1. reddit.com/r/sleeptips    · cited 5× · pos 2.1 · citability 0.81 · @types: [QAPage]      · "여름철 침구 추천..."
  2. blog.naver.com/<author>   · cited 3× · pos 3.4 · citability 0.74 · @types: []            · "1인칭 후기..."
  3. <partner-media>.com       · cited 2× · pos 4.0 · citability 0.69 · @types: [NewsArticle] · "비교 리뷰..."

Structural targets (approximate; from cached snapshot crawls when available):
  reddit:        ~340 words · 0 headings · Q&A pairs ~3                · freshness: cached
  naver_blog:    ~1500자 · 5 images · 2 H2 sections                    · freshness: cached
  partner_media: structural targets pending live recrawl                · freshness: pending

Auto-detected channels:  reddit, naver_blog, partner_media
In-store signature:      indexed 12 existing posts (titles only — no crawl yet)
Live re-crawl:           deferred (runs after channel confirmation)
Selection confidence:    high (5 prompts × 12 cited sources, 4 distinct domains, JSON-LD on 8/12)
```

If `Selection confidence: low`, warn before Step 4b: "the structural template will be thin — consider tracking more prompts first via `/aeko-find-prompts-to-track` for higher-quality output. Phase 3B will escalate to a 3-URL recrawl per channel to compensate." User may still proceed.

If 3A.4 surfaced a likely duplicate (≥80% title token-overlap with an in-store page from `in_store_topic_index[]`), append a single-line warning above the question in 4b: "⚠ This draft topic looks ≥80% similar to <existing-url> — consider pivoting the angle or canonicalizing in Step 4e."

### 4b. Confirm auto-detected channels

Ask: "Generate drafts for all auto-detected channels above? Reply with the channels to keep, or `all`, or `none`."

Parse user reply into `selected_detected_channels[]` (subset of `auto_detected_channels`).

### 4c. Add additional formats

Ask: "Add any of these formats?
- `보도자료` (Korean press release, 합니다체)
- `magazine` (Vogue-style editorial)
- `instagram` (caption + hashtags + alt text)
- `tiktok` (30–60s script with beats)
- `youtube` (title, description, chapters)
- `other:<name>` (free-form — describe the format briefly, or paste 1-2 reference URLs)

Reply with comma list, or `none`."

Parse into `selected_addon_channels[]`. For each `other:<name>`, ask one follow-up: "Reference URL(s) or short description for `<name>` format?"

### 4d. Per-channel media

For each channel in `selected_detected_channels + selected_addon_channels`, ask once:
"Image/video for `<channel>`? Reply with URL, local path, or `skip`."

Validate:
- URL → light `WebFetch` probe; warn if 4xx/5xx but allow continue.
- Local path → `Read` to confirm exists; warn + allow if missing.
- `skip` → record null.

Record into `media_by_channel{}`. For every URL captured here (and every URL pasted into `other:<name>` references in §4c), append to `cited_url_allowlist[]` so Step 6.1's "no invented URLs" gate accepts the user-supplied media link.

### 4e. Confirm before generating

Print a selection table:

```
| Channel       | Source template       | Media          |
| reddit        | forensics: r/<sub>    | skip           |
| naver_blog    | forensics: 1인칭 review | https://...   |
| 보도자료       | recipe: press_release | skip           |
| instagram     | recipe: instagram     | /Users/.../a.jpg |
```

If the **total selected channels is 0**, stop with "no channels selected" and do NOT call `aeko_complete_action_item`. Do not run Phase 3B; do not ask the proceed-to-draft question.

Otherwise, **run Phase 3B now** (`§3` → Phase 3B). 3B scopes its recrawl budget to the selected channels only, so the cost is bounded. When 3B completes, print the enrichment summary:

```
Enrichment summary (Phase 3B, selected channels only):
  Recrawls attempted:    4   (1-2 / channel, escalated to 3 on `보도자료`)
  Recrawls succeeded:    3   (1 stale-gated via snapshot ≤7d, 0 failed)
  In-store crawl:        ran (top blog post — own_store_blog selected)
  Freshness confidence:  high
```

Render `Freshness confidence` as a distinct label from `Selection confidence` (§4a) — never collapse them. The two answer different questions: selection confidence is "is the channel auto-detect grounded?"; freshness confidence is "is the structural template fresh enough to draft against?"

Ask: "Proceed to draft? (`yes` / `cancel` / `edit`)". On `edit`, loop back to 4b (the 3B work is discarded — re-run 3B if the new selection differs). On `cancel`, stop without writing or completing. On `yes`, proceed to Step 5 with `structural_template_by_channel{}` populated for selected channels only.

## Step 5 — Per-channel draft loop

Loop over the final selected channel list. For each channel:

### 5.0 Load references (per-channel, on-demand)

Reference content lives under `skills/aeko-create-content/references/` and is loaded **only when needed** per channel — Anthropic's progressive-disclosure model. SKILL.md stays small; recipes and brand-specific exemplars load when their channel runs.

For each channel `C` in the selection, before drafting:

1. **Load the recipe** (always, when a recipe file exists for the channel): `Read references/recipes/<C>.md`. Channel-to-file map:
    - `보도자료` → `references/recipes/보도자료.md` (also load `references/recipes/editorial-html-jsonld.md`)
    - `magazine` → `references/recipes/magazine.md` (also load `references/recipes/editorial-html-jsonld.md`)
    - `partner_media` → forensics-derived; load `references/recipes/editorial-html-jsonld.md` for the HTML/JSON-LD pair
    - `aeko_shop` → load `references/recipes/editorial-html-jsonld.md` (the aeko_shop section + product reference rendering + cdn.aeko.shop image rules). No channel-specific recipe file; the editorial recipe is the single source. Forensics template from 3B.5 supplies numeric targets for the aeko.shop body (paragraph / heading / image-density stats sampled from the brand's existing aeko.shop content).
    - `instagram` → `references/recipes/instagram.md`
    - `tiktok` → `references/recipes/tiktok.md`
    - `youtube` → `references/recipes/youtube.md`
    - `naver_blog` → `references/recipes/naver_blog.md` (layered on top of the forensics template from 3B.5 — recipe provides platform conventions, forensics provides measured numeric targets)
    - `tistory` → `references/recipes/tistory.md` (same layering pattern as `naver_blog`)
    - `reddit` — no recipe file; structural template comes from 3B.5 alone (Q&A locked when forensics 3B.5 detects `QAPage` / `DiscussionForumPosting`).
    - `other:<name>` — no recipe file; structural template comes from §5.1's mini-forensics.

2. **Load the brand-specific exemplar** (if it exists, conditional). Filename pattern: `references/examples/<C>-*example*.md` or the explicit names in the table below. Use a `Read` with `Glob`/check-exists semantics — silently skip if absent. Treat each match as style guidance:

    | channel | example file the skill scans for |
    | --- | --- |
    | `naver_blog`, `tistory` | `references/examples/blog-example.md` |
    | `instagram` | `references/examples/instagram-post-example.md` |
    | `보도자료` | `references/examples/press-release-example.md` |
    | `tiktok` | `references/examples/tiktok-script-example.md` (optional) |
    | `youtube` | `references/examples/youtube-description-example.md` (optional) |
    | `magazine` | `references/examples/magazine-feature-example.md` (optional) |
    | (any) | `references/examples/in-store-content-example.md` — voice signal across all channels |

3. **Load voice overrides** (if it exists): `Read references/style/voice-overrides.md`. Filter to blocks scoped to `domain: <frontmatter.domain_id>` and/or `channel: <C>`. Skip silently if the file doesn't exist or no scoped block matches.

**Example-file rules** (mirror §6.1 hard-gate intent):

- Example files are loaded as **style reference**, not as cited content. Any URL inside an example file MUST NOT be carried into the artifact — the §6.1 "no invented URLs" gate still applies, scoped to `cited_url_allowlist[]`.
- Example files may legitimately contain `[Image]` placeholders as part of demonstrating a brand's pattern. The §6.1 placeholder gate scans the *generated artifact*, not the example file.
- Mimic structure (paragraph length, hook style, hashtag density, heading cadence) and tone (sensory verbs, register, glossary). Do not copy phrases verbatim — even your brand's own exemplar.

The user-facing summary at Step 8 must list which reference files were loaded per channel so the user can verify their exemplars are picked up (e.g., `Mimicked: examples/instagram-post-example.md + recipes/instagram.md`).

### 5.1 Pick the structural source

- **Auto-detected channel without recipe** (`reddit`): use `structural_template_by_channel[channel]` from Step 3 alone (snapshot + live crawl already merged in 3B.3 / 3B.5).
- **Auto-detected channel with recipe** (`naver_blog`, `tistory`): use BOTH the forensics template (3B.5 numeric targets) AND the recipe loaded in §5.0 from `references/recipes/<channel>.md` (platform conventions, register, acceptance gates). When the two disagree on a numeric target, forensics wins; when they disagree on register or platform conventions, the recipe wins. Recipe acceptance gates apply *alongside* §6.2 structural-target deltas.
- **Brand-destination editorial** (`aeko_shop`): use BOTH the forensics template (3B.5 numeric targets sampled from the brand's existing aeko.shop content via in-store recrawl) AND `references/recipes/editorial-html-jsonld.md`'s aeko_shop section (sanitizer-safe body HTML, product callout pattern, `<slug>.meta.json` field constraints, cdn.aeko.shop image rules — **no in-body JSON-LD**, the frontend regenerates it from `PostUpsert` fields). Recipe wins for product-callout rules, body HTML structure, and `.meta.json` shape; forensics wins for measured paragraph / heading / list / image-density numeric targets.
- **Built-in addon** (`보도자료`, `magazine`, `instagram`, `tiktok`, `youtube`): use the recipe loaded in §5.0 from `references/recipes/<channel>.md` (and `references/recipes/editorial-html-jsonld.md` for editorial channels' HTML pair).
- **`other:<name>`**: if reference URLs were provided, fetch them via `aeko_crawl_url(url)` and derive an ad-hoc template (mini-forensics: title, meta, paragraph length, heading depth, list usage, JSON-LD `@type`s). Fall back to `WebFetch` if the crawl tool returns 4xx/5xx — for `other:<name>` channels, JSON-LD signal is nice-to-have, not required. If only a description was given, use the description plus brand-voice defaults.

### 5.2 Optional research

If frontmatter prose requests external research OR an `other:<name>` channel needs reference fetching:
- `WebSearch` for related context (competitor brand names, recent news, review themes).
- `WebFetch` on specific URLs called out in prose or supplied by user. Do NOT invent URLs.
- Append a research-log to the channel's artifact directory.

### 5.3 Draft the artifact

**Output format per channel** (overridden by `frontmatter.output_artifact_format` when present):

| channel | default format(s) |
| `reddit`, `naver_blog`, `tistory`, `instagram`, `tiktok`, `youtube` | `markdown` |
| `보도자료`, `magazine`, `partner_media` | `markdown` + `html` (both files written; HTML carries embedded JSON-LD per `references/recipes/editorial-html-jsonld.md`). |
| `aeko_shop` | `html` + `meta.json` + `markdown` (three files; `.html` is the sanitizer-safe body, `.meta.json` is the publish-payload sidecar mirroring `PostUpsert`, `.md` is a debug mirror). No in-body JSON-LD (the rendered page regenerates it from publish fields). Product references render as `<figure role="callout" data-variant="product" data-product-source-id="…">` callouts. See `references/recipes/editorial-html-jsonld.md`. |

Enforce:
- `frontmatter.must_include` — every string MUST appear in **at least one** generated artifact (not necessarily every channel — a brand name belongs in 보도자료 boilerplate but may not fit a TikTok beat).
- `frontmatter.forbidden` — no string MAY appear in any artifact.
- `frontmatter.sections_required` — applies to prose channels (forensics-detected, `보도자료`, `magazine`). Each entry MUST map to a heading or named section. Social channels (`instagram`, `tiktok`, `youtube`) use the recipe's required parts in place of `sections_required`.

**Voice discipline** (priority order, highest first):

1. **Voice overrides** (`references/style/voice-overrides.md`, if present) — domain- or channel-scoped exception sheet. Wins over everything below for the scopes it names.
2. **Brand-specific exemplar** (`references/examples/<channel>-*example*.md`, if present, loaded in §5.0) — drives structural mimicry (paragraph length, hook style, hashtag density, heading cadence) and channel-specific glossary. Recipe acceptance gates still apply on top.
3. **Brand kit** `tone_of_voice` drives sentence-level register; brand kit `must_include` and `forbidden` override frontmatter if conflicting (surface the conflict to the user before resolving).
4. **Cited-source structural template** (3B.5) drives format when no exemplar is present: paragraph length, heading depth, list density, list-vs-prose split, Q&A patterning when locked.
5. **In-store tone signature** (3B.4) — fills gaps when the brand kit's `tone_of_voice` is thin or absent. May be absent when 3B.4 didn't trigger (no own-store channel selected and template not thin); in that case treat as null. When brand kit and in-store conflict, brand kit wins; surface the conflict once at Step 4e.

Plus the always-on rules:
- Target audience from brand kit shapes word choice (beginner vs expert vocabulary).
- For `보도자료` specifically: 합니다체 is required even if brand voice elsewhere is 요체 — the format wins; surface the conflict before resolving.
- **No hard CTAs** ("Buy now" / "Click here" / promotional commands) in the body. Citability content earns the click via authority, not commands. Same principle as `/aeko-update-pdp`: AEKO injects citability content; the host channel owns the action UI.

**Structural discipline** (from Step 3 template or `references/recipes/<channel>.md`):
- Match the winning-source format the forensics identified.
- Be honest about what this is: Reddit-style Q&A is fine, but do NOT fake Reddit thread formatting or pretend the content is crowd-sourced.
- Link out to the top cited sources where the draft genuinely benefits from them (prevents the "generic AEO mush" failure mode).

### 5.4 Embed media reference

**Hard rule:** never emit `[Image #N]`, `[image placeholder]`, `[Image]`, `[photo]`, `[Video:` (without a real URL inside), `[Photo:`, `[graphic]`, or any unfilled `[…]` media marker in body text. Markdown image syntax (`![alt](url-or-path)`) is only permitted with a real URL or local path. If you find yourself wanting to write a placeholder, stop and use the `media_specs:` block below instead (except for `aeko_shop` — see below). The §6.1 hard gate scans for any `[Image`/`[image`/`[Video`/`[video`/`[Photo`/`[photo`/`[Graphic`/`[graphic`/`[placeholder` token followed by a non-URL — fail the artifact if any match.

**For the `aeko_shop` channel specifically** (publish-ready path; the artifact lands on aeko.shop without further transformation):

- **No `media_specs:` YAML for aeko_shop.** The channel needs concrete `cdn.aeko.shop/...` URLs in the body. If the user replied `skip` for aeko_shop's media at §4d AND `parsed_products[]` is empty, the recipe still produces a text-only article (no hero, no inline images) — the §6.3 acceptance gates accept image-count = 0 for this case.
- **For each user-supplied image** (URL or local path from §4d's `media_by_channel[aeko_shop]`): upload to `cdn.aeko.shop` before embedding. The contract is enforced by `aeko-shop-backend/app/schemas.py::MediaPresignRequest` (which uses base64 MD5, not hex) and Azure Blob's signed-URL PUT requirements (which need `x-ms-blob-type` and `Content-MD5` headers). Mismatch returns HTTP 400 or 403. Steps:
  1. **Stage the bytes locally.** For local-path inputs the file already exists; for remote URLs, fetch first into a temp file at `./aeko-artifacts/<domain_id>/<item_id>/aeko_shop/.uploads/<sha256_of_url>.<ext>` (deterministic temp path; safe under parallel runs; auto-cleaned at Step 7 success). Create the `.uploads/` subdir if missing.
  2. **Compute digests.** `content_sha256` = **SHA-256 hex** (lowercase, 64 chars, no separators). `content_md5` = **base64-encoded raw MD5 digest** (exactly 24 chars including padding; do **NOT** use hex — the backend's Pydantic field is `min_length=24, max_length=24`). `byte_length` = file size. Reference implementation: `aeko-mcp/aeko_mcp/tools/store_write.py:84-85` (`base64.b64encode(hashlib.md5(data).digest()).decode()`).
  3. **Call `aeko_request_media_upload`** per `aeko-mcp/aeko_mcp/tools/media_upload.py` — args: `brand_id=frontmatter.domain_id` (required — the backend's `MediaPresignRequest` validates this; the MCP tool must forward it), `source_content_id=frontmatter.item_id`, `filename=<basename only — no path separators>`, `content_type=<MIME, must match `^image/(jpeg|jpg|png|webp|gif)$`>`, `content_sha256=<hex>`, `content_md5=<base64>`, `byte_length=<n>`. Response: `{upload_url, public_url, blob_key, expires_at}`.
  4. **PUT the bytes** via `Bash` with the Azure-required headers — every header is required (Azure rejects with 403 otherwise): `curl -X PUT --data-binary @<staged_path> -H "x-ms-blob-type: BlockBlob" -H "Content-Type: <type>" -H "Content-MD5: <base64>" "<upload_url>"`. The `Content-MD5` value MUST equal the `content_md5` passed at step 3 — Azure verifies the body against this header. Verify HTTP 2xx before proceeding; treat 4xx/5xx as upload failure per the rule below.
  5. **Embed `public_url`** (the `cdn.aeko.shop/...` URL) in the artifact body — Markdown `![<alt>](<cdn_url>)` and HTML `<figure><img src="<cdn_url>" alt="<alt>" width="<w>" height="<h>" loading="lazy"></figure>` (per the recipe's image-attribute hard gate at §6.3).
- **For `parsed_products[]` image references**: `product.image_url` is already a `cdn.aeko.shop/...` URL by construction (aeko.shop catalog images live on the same CDN). Do **not** re-upload; reference directly.
- **Hero image**: written to `<slug>.meta.json` `hero_image_url` (top-level publish field) — NOT embedded as an in-body `<figure>` (the rendered page emits its own hero `<Image>` from the publish payload; embedding it in body HTML produces a duplicate hero). First entry of `parsed_products[]` (if any) wins — its `image_url` populates `hero_image_url`. If `parsed_products[]` is empty, fall back to the first user-supplied image. If neither, leave `hero_image_url` as `null` in `.meta.json` and omit the hero entirely.
- On upload failure (network error, presign 4xx/5xx, PUT non-2xx): surface a single-line warning and write a placeholder body marker `[image: <filename> — upload pending]` in the draft. §6.1's hard gate **fails** the aeko_shop artifact when any such placeholder remains — this is intentional, since aeko_shop is publish-ready or it isn't. The user re-runs once the upload path recovers. Do not delete the staged file on failure — it speeds up retry.

**If `media_by_channel[channel]` is set** (real URL or local path supplied) for **non-aeko_shop channels**:

- Markdown channels → standard image / video markdown:
  - Image: `![<alt>](<url-or-path>)`
  - Video: `[Video](<url-or-path>)` link with caption on the next line. Bracket form `[Video: <url>]` (with a colon and inlined URL) is **not** allowed because the §6.1 scanner would flag it; use the link form so the URL parses cleanly.
- Instagram → `media:` field at the top of the file referencing the asset; alt text rendered in its own section.
- TikTok → reference inside the relevant beat (`[on-screen]: image at <path>`).
- YouTube → reference in description (`Thumbnail: <url-or-path>`).

For non-aeko_shop channels, the skill **does not copy or upload** the media — references only.

**If `media_by_channel[channel]` is null** (user replied `skip` in Step 4d) — excludes `aeko_shop` (its skip behavior is handled above):

- **Visual-first channels** (`instagram`, `tiktok`, `youtube`, `magazine`, `naver_blog`, `tistory`, `partner_media`): write a fenced `yaml` code block at the top of the file (immediately after the `# <title>` heading) containing the `media_specs:` array — one entry per slot the recipe expects (typically `hero` + 0-3 `inline` slots; YouTube also `thumbnail`; TikTok one entry per major beat). Fenced so downstream consumers (designer tools, image-gen pipelines) can reliably extract it; an unfenced `- ` prefixed list breaks markdown rendering AND parsing.

  Emit it exactly like this — opening and closing fences included:

  ````markdown
  ```yaml
  media_specs:
    - slot: hero
      composition: "<one-line composition direction>"
      subject: "<who/what is in the shot>"
      copy_overlay: "<on-image text, or 'none'>"
      alt_text: "<≤125 char alt text>"
      aspect_ratio: "<e.g., 1:1, 9:16, 16:9>"
      reference_image: "<og.image URL from 3B.3 if available, else 'none'>"
  ```
  ````

  Body references slots by name (`see media_specs.hero`) — never by `[Image #N]` or any other bracket marker. Seed the `reference_image` field from 3B.3's `og.image` and `images.alt_examples` when they exist for a top cited source on this channel; otherwise emit `'none'`.
- **Prose-only channels** (`reddit`, `보도자료`): no image references in body at all. Do not emit a `media_specs:` block — these channels are text-first and inserting visual specs creates noise. (`보도자료` may include media as a separate distribution attachment list at the bottom under `## 보도자료 첨부 참고`, but only if frontmatter prose explicitly requests it.)

### 5.5 Artifact path

**Always use channel-segmented paths.** Do not flatten artifacts into one folder — recent runs produced flat outputs because the slug rule was under-specified; fix is below.

Path template:

`./aeko-artifacts/<domain_id>/<item_id>/<channel_slug>/<filename>.<ext>`

**Slug derivation** (for prose channels and editorial HTML):

1. Source: `frontmatter.title` (not Plan prose, not response text).
2. Lowercase, ASCII-fold non-ASCII characters (Hangul → romanization via standard fold; if no fold available, drop the character).
3. Replace any run of non-alphanumeric characters with a single hyphen.
4. Truncate to **60 characters at the nearest word boundary** (don't truncate mid-word).
5. Strip leading and trailing hyphens.
6. On filename collision within the same channel directory, append `-2`, `-3`, … until unique.
7. **Empty-slug fallback.** If steps 1–5 produce an empty string (most common cause: 100% Hangul title with no romanization fold available), use `<frontmatter.item_id>` as the slug. Never write to a hidden filename like `.md`. Example: title `여름철 침구 가이드` with no fold → `<slug>` becomes `<item_id>` (a UUID), so the file lands at `.../naver_blog/3f2c1a04-….md` rather than `.../naver_blog/.md`.

**Filename rules per channel:**

| channel | filename pattern | extension(s) |
| `reddit`, `naver_blog`, `tistory`, `partner_media` | `<slug>` | `.md` |
| `보도자료`, `magazine` | `<slug>` | `.md` AND `.html` (see `references/recipes/editorial-html-jsonld.md`) |
| `aeko_shop` | `<slug>` | `.html` AND `.meta.json` AND `.md` — three files (the publish-ready triple; see `references/recipes/editorial-html-jsonld.md` for the per-file shape and §6.3 for the acceptance gates) |
| `instagram`, `tiktok`, `youtube` | the channel slug (literal `instagram` / `tiktok` / `youtube`) | `.md` |

**Worked-example directory tree** the skill MUST produce when 10 channels are selected (the 9 below plus `aeko_shop`) for a draft titled "Summer Cooling Bedding — 2026 Guide":

```
aeko-artifacts/
  <domain_id>/
    <item_id>/
      reddit/summer-cooling-bedding-2026-guide.md
      naver_blog/summer-cooling-bedding-2026-guide.md
      tistory/summer-cooling-bedding-2026-guide.md
      partner_media/summer-cooling-bedding-2026-guide.md
      보도자료/summer-cooling-bedding-2026-guide.md
      보도자료/summer-cooling-bedding-2026-guide.html
      magazine/summer-cooling-bedding-2026-guide.md
      magazine/summer-cooling-bedding-2026-guide.html
      aeko_shop/summer-cooling-bedding-2026-guide.html
      aeko_shop/summer-cooling-bedding-2026-guide.meta.json
      aeko_shop/summer-cooling-bedding-2026-guide.md
      instagram/instagram.md
      tiktok/tiktok.md
      youtube/youtube.md
```

The `aeko_shop/` channel is the only one that produces a **triple** (`.html` + `.meta.json` + `.md`). All other editorial channels produce a pair (`.md` + `.html`) or a single `.md`.

If frontmatter prose requests sibling files (JSON-LD, meta, social teaser), write them next to the channel's main file using the same `<slug>` stem (e.g., `<slug>.jsonld.json`, `<slug>.meta.json`).

### 5.6 Channel recipes (loaded from `references/recipes/`)

Built-in addon channels each have a recipe file under `references/recipes/`. They were loaded in §5.0; apply them now. Acceptance bullets in each recipe file ARE the §6.4 social-channel gates and the §6.2 prose-channel structural-target source.

| channel | recipe file | output |
| --- | --- | --- |
| `보도자료` | `references/recipes/보도자료.md` + `references/recipes/editorial-html-jsonld.md` | `.md` + `.html` |
| `magazine` | `references/recipes/magazine.md` + `references/recipes/editorial-html-jsonld.md` | `.md` + `.html` |
| `partner_media` | forensics template (3B.5) + `references/recipes/editorial-html-jsonld.md` | `.md` + `.html` |
| `aeko_shop` | `references/recipes/editorial-html-jsonld.md` (aeko_shop section — sanitizer-safe body HTML + product callout pattern + cdn.aeko.shop image rules; **no in-body JSON-LD** — the frontend regenerates Article + Product schemas from `PostUpsert` fields at render time) + 3B.5 forensics template for paragraph/heading targets | `.html` + `.meta.json` + `.md` (publish-ready triple) |
| `naver_blog` | `references/recipes/naver_blog.md` + forensics template (3B.5) | `.md` |
| `tistory` | `references/recipes/tistory.md` + forensics template (3B.5) | `.md` |
| `instagram` | `references/recipes/instagram.md` | `.md` |
| `tiktok` | `references/recipes/tiktok.md` | `.md` |
| `youtube` | `references/recipes/youtube.md` | `.md` |

If a brand-specific exemplar was loaded in §5.0, mimic its structure on top of the recipe — recipe gates still apply. See §5.3 voice-discipline precedence for conflict resolution.

### 5.6.6 Editorial channels' HTML + structured data

Editorial channels (`보도자료`, `magazine`, `partner_media`, `aeko_shop`) ship structured-data-bearing HTML alongside their markdown. **The full recipe lives in `references/recipes/editorial-html-jsonld.md` and MUST be loaded before drafting any of these channels.** Do not author the HTML from this section — the recipe is the single source of truth, and it covers two distinct layouts that this skill must not flatten:

| Channels | HTML shape | Structured data |
|---|---|---|
| `보도자료`, `magazine`, `partner_media` | Full document — `<!doctype>`/`<html>`/`<head>`/`<article>`/`<header>`/`<h1>`/`<section>`/`<footer>` allowed; editor-facing. | Embedded `<script type="application/ld+json">` block per the channel's schema (`NewsArticle` / `Article` / `Article + Review`). |
| `aeko_shop` | **Inner body only** — no document wrapper, no `<head>`, no `<article>`, no `<h1>`, no `<script>`. Round-trips through `aeko-shop-backend/app/sanitizer.py` which raises HTTP 400 on every disallowed tag/attribute (no silent stripping). | **No in-body JSON-LD.** The aeko.shop frontend regenerates Article + Product schemas from the `PostUpsert` fields carried in `<slug>.meta.json`. |

The recipe enumerates the allow-list, the `<slug>.meta.json` field constraints, the product-callout pattern (`<figure role="callout" data-variant="product" data-product-source-id="…">`), the ID-space rules (`ProductRef.source_id`, not `id`), the image origin rule (`cdn.aeko.shop/...` only), and the per-channel acceptance gates this skill enforces at §6.3.

Common content rules that apply to all four editorial channels (the recipe folds these in too; restating only what the executor needs to keep in mind at draft time):

- `inLanguage` / `locale` is a valid ISO-639-1 / BCP 47 code (`ko`, `en`, `en-US`). Defensively normalize: `"Korean"`/`"한국어"` → `ko`, `"English"`/`"영어"` → `en`; unrecognized → fall back to `ko` with a one-line warning.
- For the three editor-facing channels: if `frontmatter.canonical_url` is absent, omit the `<link rel="canonical">` tag — do not emit an empty `href`.
- For `aeko_shop`: every `<img src>` is a `cdn.aeko.shop/...` URL and every `<img>` carries `alt`/`width`/`height`/`loading`. §6.3 rejects the artifact otherwise.
- **Schema parity** (editor-facing channels only): if `structural_template_by_channel[channel]` carries observed JSON-LD `@type`s from cited sources, the artifact's emitted `@type` SHOULD be in the same family. Soft warning at §6, not a hard fail. `aeko_shop` has no in-body JSON-LD, so no parity check applies.

Authoring against this section without loading the recipe will produce sanitizer-invalid `aeko_shop` artifacts (full-document HTML, embedded JSON-LD, and `<h1>`/`<script>` all return HTTP 400). Load the recipe first.

## Step 6 — Citability self-check (per artifact)

Run per artifact before completion.

### 6.1 Universal hard gates (every channel)

These fail the artifact immediately — one fix iteration, then leave the item `pending`:

- **No image placeholders.** Zero occurrences of `[Image`, `[image`, `[Photo`, `[photo`, `[placeholder`, `[Placeholder`, or `TODO` in body text. Real markdown image syntax with a URL or path is allowed; `media_specs:` YAML is allowed (it's a distinct format).
- **No invented URLs.** Every external URL in the artifact must appear in `cited_url_allowlist[]` — the union of: every cited `source_url` from 3A.1 (seeded into the allowlist at 3A.6), every URL passed to `aeko_crawl_url` in 3B.2 or 3B.4 (appended at 3B.6), every URL returned by `aeko_list_own_content` in 3A.4 (when surfaced as a draft reference), every URL in `media_by_channel{}` from Step 4d, plus any URL the user pasted into an `other:<name>` reference in Step 4c. Step 6's URL extractor scans the artifact for `https?://…` tokens and fails the artifact if any URL is not in the allowlist. Brand-internal anchor links (`#section`) and `mailto:` are exempt.
- **Frontmatter `forbidden` list:** zero matches.

### 6.2 Prose channels (forensics-detected, `보도자료`, `magazine`, `partner_media`)

Apply the 5 citability dimensions:
1. **Answer-block quality** — opening 1-2 sentences of each section directly answer a natural question.
2. **Self-containment** — subject named in every paragraph; no pronoun opens.
3. **Structural readability** — headings, lists, short paragraphs (≤167 words).
4. **Statistical density** — specific numbers / dimensions / years where appropriate.
5. **Uniqueness signals** — at least one claim or angle not obviously derivable from a generic search.

Plus the **structural-target deltas** from 3B.5 / 3B.3:

- Median paragraph word count within ±25% of the channel's target.
- Heading max-depth within ±1 of the target (e.g., target h3 → h2/h3/h4 OK, h5 not).
- List density (lists per 1000 words) within ±25% of target.
- Image count within ±1 of target (only when target > 0; not enforced if no media specs and target == 0).

Out-of-band targets are **soft warnings** unless the deviation is ≥50%, which becomes a hard gate (one fix iteration).

### 6.3 Editorial channels' HTML pair (`보도자료`, `magazine`, `partner_media`, `aeko_shop`)

Both `<slug>.md` AND `<slug>.html` must exist. The `.html` file parses with `lxml` / `html.parser`.

**Channels `보도자료` / `magazine` / `partner_media`:**

- Contains exactly one `<article>` root.
- Each `<script type="application/ld+json">` block parses with `json.loads` after stripping the script wrapper.
- Required JSON-LD fields are present per the schema in `references/recipes/editorial-html-jsonld.md` (e.g., `NewsArticle` requires `headline`, `datePublished`, `author`, `publisher`).
- **Schema parity** soft check: emitted top-level `@type` is in the same family as the **cited sources'** dominant `@type` from 3B.5 (`Article` ⊇ `NewsArticle`/`BlogPosting`; `Review` ⊇ `Review`/`Recommendation`).

**Channel `aeko_shop`:**

The publish-ready artifact is a triple: `<slug>.html` (sanitizer-safe body) + `<slug>.meta.json` (publish-payload sidecar) + `<slug>.md` (debug mirror). The `.html` is shipped verbatim as `PostUpsert.body_html`; the `.meta.json` populates top-level publish fields. See `references/recipes/editorial-html-jsonld.md` for the full shape.

- `<slug>.meta.json` exists and parses with `json.loads`. Required fields present; all values within their `PostUpsert` constraints (recipe's "`<slug>.meta.json`" §). Hard gate.
- Sanitizer-safety pre-flight on `<slug>.html`: zero matches for `<(script|article|header|footer|section|h1|meta|title|link|html|body|head)\b`. Hard gate.
- Every `<a>` tag's attributes are a subset of `{href, title, rel, target, class, data-mention-type, data-mention-id}` (no `data-aeko-product-ref`, no `data-product-sku`). Hard gate.
- Every `<img src>` in `.html` is a `cdn.aeko.shop/...` URL. Hard gate. (Confirms §5.4 upload step ran and no external URL leaked in.)
- Every `<img>` carries `alt`, `width`, `height`, `loading` attributes. Hard gate.
- Zero `[image: …pending]` placeholder markers remain in `.md`, `.html`, or `.meta.json`. Hard gate. (Confirms no `aeko_request_media_upload` failure was unresolved.)
- **ID-match gate.** Set of `data-product-source-id` values across all `<figure data-variant="product">` in `.html` equals the set of `featured_products[].product_source_id` values in `.meta.json`. Count + set match. Hard gate.
- Body contains zero `<figure data-variant="product">` callouts when `featured_products[]` is empty (no orphans). Hard gate.
- When `featured_products[]` has > 3 entries and the body has zero inline `<figure>` callouts: soft warning (body may be too short to incorporate all products inline; not every product needs an inline callout — bottom "Featured products" cards always render from `.meta.json`).
- **No schema parity check** for `aeko_shop` — the rendered page always emits `Article` from `aeko-shop-front/lib/structured-data.ts`; no in-body JSON-LD to check.

Any HTML-side hard-gate failure → one fix iteration → leave `pending`.

### 6.4 Social channels (`instagram`, `tiktok`, `youtube`)

Substitute the recipe's "Acceptance gates" section in `references/recipes/<channel>.md` as the gates. The §6.1 universal hard gates still apply.

### 6.5 Iteration budget

Weak on a soft-warning dimension → iterate that artifact's affected section. Cap at **2 soft iterations per artifact**. Hard-gate failures get **1 fix iteration** before failing the artifact. If any artifact still fails its hard gates, leave the entire item `pending` (do NOT call `aeko_complete_action_item`) and surface which channels failed and which dimensions need work.

## Step 7 — Mark complete

```
aeko_complete_action_item(
    item_id=frontmatter.item_id,
    artifact_summary="<N channels: reddit, naver_blog, 보도자료, instagram> · mimicked: <top 2 source patterns>",
    artifact_paths=[<absolute paths of every file written across all channels>],
    write_result=None,  # content artifacts never do store writes
)
```

Only complete if:
- ≥1 artifact written AND every written artifact passed its acceptance gates AND citability self-check passed for every artifact.

## Step 8 — User-facing summary

```
✔ Content drafted across <N> channels: <comma list>
  Domain:        <domain>
  Action item:   <item_id>
  Mimicked:      <top 2-3 source domains + format patterns>
  Refs loaded:
    - instagram    → recipes/instagram.md + examples/instagram-post-example.md
    - 보도자료      → recipes/보도자료.md + recipes/editorial-html-jsonld.md
    - naver_blog   → recipes/naver_blog.md + forensics template + examples/blog-example.md
    - tistory      → recipes/tistory.md + forensics template + examples/blog-example.md
    - reddit       → forensics-derived (no recipe file)
    - …            (one line per channel; show "no exemplar" when example file absent)
  Artifacts:
    - reddit       → <path>
    - naver_blog   → <path>
    - 보도자료      → <path>
    - instagram    → <path>
  Media refs:    <N attached, M skipped>
  Citability:    passed on N/N · failed on: <list or 'none'>
```

The **Refs loaded** block exists so users can verify their `references/examples/<file>.md` is being picked up — if a channel's line shows only `recipes/<channel>.md` and no `examples/...`, their exemplar isn't matching the filename pattern.

If any artifact targets a client-managed channel (anything except `aeko_shop`), append a publish checklist:

```
Client-managed channels publish checklist (never auto-published by AEKO):
  - reddit: review + post to <subreddit guess from forensics>
  - naver_blog / tistory: post under your account
  - 보도자료: distribute via your PR channel
  - instagram / tiktok / youtube: schedule via your scheduling tool
  - magazine / partner_media: send the .md + .html pair to the editorial contact
  - Add canonical link back to <domain> when permitted
  - Mark the AEKO action complete after publishing (already done by this run if all checks passed)

Note: `aeko_shop` is NOT on this checklist — it's handled by /aeko-publish-content (see Publish handoff below).

Next: /aeko-action-center <domain_id> content
```

## Step 9 — Publish handoff

This skill never publishes — Step 8 stops at local files plus the manual checklist. Publishing is the job of `/aeko-publish-content`, which routes only to **aeko.shop**. All other channels (Tistory, Naver Blog, Instagram, TikTok, YouTube, 보도자료, magazine, partner_media) are generation-only outputs — the client posts them however they want; AEKO does not route them anywhere. This step adds a **read-only handoff line** at the very end of the user-facing summary so the publish path is visible from day one.

### 9.1 Always print the publish-content line — when aeko_shop was drafted

If `aeko_shop` is in the drafted channel set, insert immediately under the `Next:` line in §8 — unconditionally, no detection step:

```
Publish: /aeko-publish-content <item_id>
  ↳ publishes the rich aeko_shop artifact (body_html + .meta.json + featured_products) to aeko.shop — N products linked to live catalog, structured data regenerated at render time for ChatGPT/Claude/Perplexity citation.
  ↳ aeko.shop is the only destination this skill family routes to. Other channels' drafts stay local.
```

If `aeko_shop` is **not** in the drafted channel set, omit the publish line entirely — there's nothing to publish via `/aeko-publish-content`. Leave the External-media publish checklist (§8) in place as the only post-creation guidance.

### 9.2 Optional Chrome-bridge hint for client-managed channels

The drafted Tistory / Naver Blog / Instagram / TikTok / YouTube / 보도자료 / magazine / partner_media artifacts are the client's responsibility to post — AEKO does not route them. If a Chrome-bridge is detected on this session, append one extra hint line so the user knows the bridge can help with those manual posts:

```
For client-managed channels (tistory / naver_blog / instagram / youtube / 보도자료 / etc.):
  connect Claude for Chrome via /chrome to assist with the checklist items above.
```

Detection signals (any one is sufficient): session started with `claude --chrome`, user invoked `/chrome` earlier and the bridge ack'd, or a prior tool call in this session used a Chrome-bridge tool successfully. If unsure, do not probe — silence is the safe default.

### 9.3 Hard rules for this step

- **Never invoke** `/aeko-publish-content`, never simulate it, never click compose forms, never fill publish fields. This step is text-only — it adds the handoff line(s) and stops.
- **Never alter** the External-media publish checklist in §8. The checklist remains the canonical reminder that non-aeko_shop channels are client-managed.
- **Never widen** `allowed-tools` for this skill to include browser-bridge tools or any external-channel posting API. The only publish-side capability this skill has is `aeko_request_media_upload` for the aeko_shop image flow at §5.4.

This keeps `aeko-create-content` honest about its boundary ("never auto-publishes") while making the aeko.shop publish path discoverable to users the moment they're ready.

## Error paths

- Plan endpoint unavailable / parse error → stop; surface detail.
- Contract mismatch → stop.
- Stale brand kit + user declines → stop.
- No tracked prompts resolve in 3A.0 → hard-stop per 3A.0's precondition (research-prompt fallback is explicitly out per 3A.8 — different cited sources optimize for the wrong queries). Tell user to run `/aeko-find-prompts-to-track` first.
- All resolved prompts return no responses in 3A.1 (`latest` window) → 3A.7 reports `low selection confidence`; surface in §4a; user may still proceed at Step 4b for fully-manual format choices, but the structural-template quality drops.
- `aeko_crawl_url` 4xx/5xx or unavailable (backend route not yet shipped) → log a single warning line in 3B.3 and §4e (recrawl row in the enrichment summary marks the URL as `recrawled_failure`), continue on the snapshot signal alone. Live recrawl is enriching, not gating.
- `aeko_list_own_content` 4xx/5xx or unavailable → log "no in-store signature — drafting from cited-source signal only" once, continue. In-store signature is enriching, not gating.
- Step 4e returns 0 selected channels → stop without writing or completing.
- User cancels at Step 4e → stop without writing or completing.
- Citability self-check hard-gate fails after the §6.5 iteration budget on any artifact → leave item `pending`; surface failed channels + dimensions.
- HTML emission fails on an editorial channel (markdown rendered, but JSON-LD won't validate) → write the `.md`, skip the `.html`, surface the JSON-LD error in the user summary, and treat the channel as failed for completion purposes.
- Non-interactive caller (e.g., dispatched from another agent): if `frontmatter.non_interactive == true` (forward-compat), skip 4b/4c/4d asks and default to: all auto-detected channels, no addons, no media. If 0 auto-detected, stop with "non-interactive run needs at least one auto-detected channel".

## What this skill never does

- Never writes to a connected store (PDP work is `/aeko-update-pdp`).
- Never publishes to external media automatically — always leaves local files only. (Publishing to **aeko.shop** is `/aeko-publish-content`'s job — this skill does not call it.)
- Never copies or uploads media for non-aeko_shop channels — only references URLs / paths the user supplies, plus the `media_specs:` YAML stubs when media was skipped. The `aeko_shop` channel is the **single exception**: §5.4 uploads supplied images to `cdn.aeko.shop` via `aeko_request_media_upload` so the artifact is publish-ready.
- Never emits `[Image #N]` / `[Image]` / `[placeholder]` / `[photo]` / `TODO` markers in body text. Real markdown image syntax with a URL or path, or a `media_specs:` block — nothing else.
- Never fabricates the citation forensics; if tracked prompts have no responses for the `latest` window, surface as `low selection confidence` and let the user decide whether to proceed — never substitute research-prompt signal. Live `aeko_crawl_url` results never get faked when the backend is unavailable.
- Never copies text from cited sources verbatim; mimics format, not content. Cited-source `extracted_text` is for tone calibration only — never paste.
- Never invents URLs in artifacts — every URL must come from forensics, in-store content, live crawls, or user-supplied media.
- Never regenerates the Plan.md.
- Never reads machine values from prose.
- Never echoes raw frontmatter.
- Never proceeds past Step 4e without explicit user confirmation (except in non-interactive mode with a valid auto-detected channel set).
