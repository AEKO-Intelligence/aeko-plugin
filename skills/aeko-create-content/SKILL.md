---
name: aeko-create-content
version: 0.10.2
description: >
  Multi-channel content executor for Action-tab items with
  `execution_class=local_content_artifact`. Fetches a Plan.md, runs
  tracked-prompt citation forensics to identify the source structures
  AI engines actually cite (Reddit threads, Naver blogs, partner media,
  etc.), then fans out into per-channel drafts: auto-detected channels
  from forensics PLUS user-added formats (보도자료 / magazine /
  Instagram / TikTok / YouTube / free-form). Optional image/video
  reference per channel. Saves local artifacts; auto-saves aeko.shop
  publish variations to the AEKO backend; never writes to a connected
  store and never auto-publishes. Splits the content branch out of the retired
  `/aeko-run-action`.
argument-hint: "<item-id>"
allowed-tools: aeko_get_action_plan, aeko_get_brand_kit, aeko_get_brand_kit_by_id, aeko_list_brand_kits, aeko_resolve_prompts_by_text, aeko_get_tracked_prompts, aeko_get_tracked_prompt, aeko_crawl_url, aeko_list_own_content, aeko_request_media_upload, aeko_complete_action_item, aeko_save_content_variation, aeko_list_content_variations, Read, Write, Bash, WebFetch, WebSearch
---

# AEKO Create Content

**Changelog v0.12.0** — aeko.shop posts now get a **meaningful English URL slug** instead of a Korean one (which 404'd on non-ASCII lookup). §5.5.6: the skill writes a translated English `slug` to `.meta.json` (distinct from the romanized *filename* slug); it threads through `aeko_save_content_variation` metadata → publish → aeko.shop `PostUpsert.slug` (validated lowercase-ASCII, 422 on non-ASCII). When omitted, the backend now transliterates the title to ASCII (never Korean). Recipe + fixture updated.

**Changelog v0.11.0** — Fixes the aeko.shop image host-contract drift: the skill now embeds the presign `public_url` **verbatim** (the backend-configured AEKO media CDN, e.g. `*.azurefd.net`) instead of asserting/hand-writing a non-serving `cdn.aeko.shop` URL — the §6.3 body-image gate validates the real allowed origins and the hero may be a brand-CDN product image (rendered by `next/image`). Recipe/fixtures updated to match. Adds a §6.3 structured-data completeness gate (brand+post always; product block when products attached) so a post never publishes silently non-citable, and documents `price_minor`/`currency`/`available` in the save-payload snapshot for complete Product `offers`. Products selected in the AEKO app now flow end-to-end (backend `build_plan_md()` hydrates `products[]` with `source_id`). Pairs with the new `aeko_update_content_variation` MCP tool for editing drafts (see `/aeko-publish-content`).

**Changelog v0.10.2** — Resolves the exact `brand_kit_id` selected in the AEKO app before falling back to active-by-domain lookup; fixes aeko.shop media upload to presign with `brand_kit_id`; degrades failed image uploads to valid text-only aeko.shop drafts.

**Changelog v0.10.1** — Makes `aeko_shop` backend-save mandatory once the channel is selected and artifacts validate; deletes the backend-save decline path for `aeko_shop`; threads uploaded aeko.shop media `public_url` into `.meta.json hero_image_url`; drops `wikipedia` / generic `web_article` from auto-detected draft channels; aligns plugin manifests.

**Changelog v0.10.0** — Front-loaded tool/reference batching (§0); annotated AEKO data-gap diagnostics with graded defaults + 3-option proceed prompt (§3A); opt-in WebFetch with heavy-host guard + 50k char cap (§3B); two-form §4 elicitation (channels then media+alt) with required alt-text; channel-aware filename basenames (`<slug>__<filename_token>.<ext>`) + `보도자료` → `press_release` filesystem alias (§5.5); structural-summary aeko.shop publish block with bilingual HTML→aeko.shop callout (§9); Korean channel labels in summary + handoff. **Breaking:** filename pattern changed, alt-text now a hard gate, WebFetch is opt-in only.

Executes one Action-tab content item end-to-end: fetch Plan.md → pull citation-forensics on tracked prompts → identify winning source structures + auto-detect channels → confirm channels with user + collect optional add-on formats and per-channel media → draft N channel-fitted artifacts in the brand voice → save local artifacts → auto-save `aeko_shop` publish variations when selected → mark complete only after required saves succeed.

Contract reference: `docs/contracts/action-item-contract.md` §3 (Plan.md), §3.2.1 (ProductRef), §6 (completion). Pinned to contract minor `v1.5` for selected `brand_kit_id` resolution and backend-saved content variations; remains tolerant of v1.3/v1.4 Plans where `brand_kit_id` or `products[]` is absent.

## Input

- `item-id` (required) — `$1`. If missing, stop and point user to `/aeko-action-center <domain_id> content`.

## Step 0 — Front-load deferred resources (do this FIRST, once per run)

Wall-clock observability: deferred tools loaded one-at-a-time across a run cost a round-trip each. Reference files loaded serially during drafting block the per-channel loop. Both are issued up front as single batched operations.

### 0a. Deferred-tool batch (very first call of the skill)

Issue exactly ONE `ToolSearch` call before any other tool use:

```
ToolSearch(query="select:aeko_get_action_plan,aeko_get_brand_kit,aeko_get_brand_kit_by_id,aeko_list_brand_kits,aeko_resolve_prompts_by_text,aeko_get_tracked_prompts,aeko_get_tracked_prompt,aeko_crawl_url,aeko_list_own_content,aeko_request_media_upload,aeko_save_content_variation,aeko_list_content_variations,aeko_complete_action_item,TaskCreate,TaskUpdate,WebFetch,WebSearch", max_results=20)
```

Record which tools the host actually exposed (`loaded_tools[]`) for diagnostics only. Do not add stale-MCP fallback branches here: if `aeko_save_content_variation` is missing from the host, the existing §7.5 save-failure branch handles it and the user should update the AEKO MCP.

**Do not load deferred tools one-at-a-time mid-run.** If a later step needs a tool not in the §0a batch, surface a single bilingual notice and stop — the missing tool is a spec drift, not a runtime fallback.

### 0b. Reference-file batch (deferred to after §4-Form-1)

Reference files (`references/recipes/*.md`, `references/examples/*.md`, `references/style/voice-overrides.md`) MUST NOT be loaded one-at-a-time per channel during the Step 5 loop. Hold the read until §4-Form-1 returns the selected channel set, then issue a single parallel `Read` batch covering:

1. **`references/style/voice-overrides.md`** — load ONCE (global file, not per-channel). Skip silently if absent.
2. **Per selected channel C, the recipe file** when one exists in the §5.0 channel-to-file map (e.g., `references/recipes/<C>.md` plus `references/recipes/editorial-html-jsonld.md` for editorial channels).
3. **Per selected channel C, the example file** per the §5.0 example-file table.

All three categories go in the same parallel batch. The per-channel Step 5 loop reads from the in-memory cache produced here, NOT from disk.

Batch shape for verification: `Read references/recipes/...` and `Read references/examples/...` entries appear only in this §0b batch description; Step 5 uses cached content.

If a recipe or example file 404s, log a single warning and continue — recipes are nice-to-have for some channels (reddit, own_store_blog have none).

## Step 1 — Fetch and parse the Plan.md

Call `aeko_get_action_plan(item_id)`. Parse YAML frontmatter + prose.

**Validate:**
- `contract_version` starts with `2026-04-17.action.v1.` — else stop.
- Minor versions `v1.3` (older live), `v1.4` (`products[]` tolerant), and `v1.5` (`brand_kit_id` frontmatter + backend-saved variations) are accepted. This skill must run cleanly on v1.3/v1.4 Plans where `brand_kit_id` or `products[]` is absent. Greater minor → print advisory + proceed.
- `tab == "action"` — else stop.
- `execution_class == "local_content_artifact"` — else redirect to the right executor.
- `artifact_type ∈ {own_store_markdown, external_media_markdown, own_store_content, external_media_content}` (accept both v1 and v2 names for forward-compat). In v2 this is **advisory** — actual channel set is decided in Step 4 — but it must be present.
- `status ∈ {pending, ready}` — else stop.
- `write_target == "local"` — content artifacts never write to store; mismatch → stop.
- `tier_required` gate via brand kit metadata.

**Sanity checks (post-validation):**

- **Dedupe `prompts_to_rank_on`.** Some Plan-builder versions emit the same prompt multiple times (observed in production: 3 copies of one prompt). Collapse duplicates (preserve first occurrence's order). If duplicates were found, print one notice: `ℹ Dedupe: collapsed N duplicate prompts in prompts_to_rank_on (Plan-builder upstream bug — file separately).` Carry the deduped list into §3A.
- **Title fallback chain (for filenames + display).** Compute `resolved_title` once and carry it through Step 5. Chain:
  1. `frontmatter.title` if present and non-empty → use as-is.
  2. Else the **first H1 in Plan body**, stripped of any leading `Plan:` prefix (the Plan template starts with `# Plan: <title>`).
  3. Else `frontmatter.item_id` (UUID fallback).

  Without this chain, Korean-titled Plans with no `frontmatter.title` collapse to `<item_id>.<ext>` everywhere (production bug). `resolved_title` feeds the §5.5 slug derivation; the raw `resolved_title` (not the slug) is what Step 8 / §9 print as the human-readable label.

**Parse `products[]` (optional; contract minor v1.4 — see `docs/contracts/action-item-contract.md §3.2.1`).** Plan.md generated from the dashboard's `상품 선택` mode carries a `products[]` array — the backend `build_plan_md()` hydrates it from the selected store products (each `source_id` = the store's `external_product_id`). Brand-wide mode omits the key. Each entry shape:

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
    image_url: <absolute https URL — usually the brand catalog CDN (Shopify/Cafe24); fine for the hero + bottom product card. To use it inside an inline body callout it must be re-hosted on the AEKO media CDN (§5.4).>  # Required.
    short_description: <≤240 chars, optional>
```

**`id` vs `source_id`.** Different ID spaces — `id` is AEKO's internal UUID for cross-AEKO references; `source_id` is the brand-registered external identifier and is what `PostUpsert.featured_products[].product_source_id` joins on at publish time. Both must be present for v1.4. See `docs/contracts/action-item-contract.md §3.2.1` for the authoritative definition.

If `products[]` is present:
- Validate each entry has at minimum `id`, `source_id`, `name`, `outbound_url`, `image_url`. Entries missing any of those → drop, and **warn loudly** (not a silent one-liner): print a visible block naming each dropped product and the reason, and state that **it will NOT appear in the published post** (no product card, no Product JSON-LD). A product is most often dropped because it has no `source_id` — i.e. it isn't synced from the brand's connected store (`build_plan_md` maps `source_id` from `StoreProducts.external_product_id`). Tell the user to sync/connect the store catalog so the product carries a store id, then re-run.
- Do **not** fabricate `source_id`; do **not** fall back to `id` for the `product_source_id` slot. Without `source_id` the publish-time backend join fails and downstream product callouts are inert.
- Carry the validated list into Step 4 and Step 5 as `parsed_products[]`.
- The list is only consumed by the `aeko_shop` channel's draft (§5.3 + the editorial recipe's "Product callout pattern" section). Other channels render product names as plain text in the body when relevant; they do not generate product reference links.

If `products[]` is empty or absent:
- `aeko_shop` (if selected) still drafts a rich article without product callouts. `.meta.json` has empty `featured_products[]` and no `<figure data-variant="product">` blocks appear in `.html`. Non-fatal.
- **Warn loudly when the user expected products but none came through.** If `frontmatter.content_scope == "products"` (`상품 선택` mode was used) AND `products[]` is absent/empty AND `aeko_shop` is in the selected channel set, the user picked specific products on the dashboard but none survived to the plan. The cause is **not** a pending backend release (hydration is shipped) — it's that the selected product(s) have no store-synced `source_id` (`build_plan_md` only emits products that resolve to a `StoreProducts.external_product_id`). Surface a visible warning in §4a:
  - EN: `⚠ You selected products (상품 선택 mode) but none reached this draft — they have no store product id (source_id). This usually means the brand's store catalog isn't connected/synced in AEKO, so the products can't be linked or rendered on aeko.shop. Connect/sync the store catalog, then re-run. This draft will publish in your brand's general voice with no product cards.`
  - KO: `⚠ 상품을 선택(상품 선택 모드)하셨지만 이번 초안에 반영되지 않았습니다 — 스토어 상품 ID(source_id)가 없습니다. 보통 브랜드의 스토어 카탈로그가 AEKO에 연결/동기화되지 않은 경우이며, 이 경우 상품을 aeko.shop에 연결하거나 렌더링할 수 없습니다. 스토어 카탈로그를 연결/동기화한 뒤 다시 실행해 주세요. 이번 초안은 상품 카드 없이 브랜드 전체 톤으로 게시됩니다.`
  - If `frontmatter.content_scope` is absent or is `"brand"`, do NOT surface this — an empty `products[]` in brand-wide mode is the expected shape.

The §4a.5 warning ("Plan carries N products but aeko_shop not active") fires only if `parsed_products[]` is non-empty AND `aeko_shop` is not in the final selected channel set after §4-Form-1.

Print header in `target_language`:
1. Action label — KO (own): "자사 콘텐츠 생성: `<artifact_type>`" / KO (external): "외부 매체 콘텐츠 생성: `<artifact_type>`" / EN: "Generating {own-site|external-media} content: `<artifact_type>`"
2. Context: domain, channels suggested by Plan (comma-joined).
3. Persona: `persona_label` if present.
4. Note: "Final channel set decided after forensics in Step 4."

Print prose verbatim. Never echo frontmatter.

## Step 2 — Stale brand-kit check

If `frontmatter.requires_brand_kit == true`:
- Resolve the Brand Kit in this order and carry the winning `resolved_brand_kit_id` through the rest of the run:
  1. If `frontmatter.brand_kit_id` is present and non-empty, call `aeko_get_brand_kit_by_id(frontmatter.brand_kit_id)`. This is the preferred path because it uses the exact kit selected in the AEKO app, including draft kits.
  2. If `brand_kit_id` is absent or the by-id call fails, call `aeko_get_brand_kit(frontmatter.domain_id)` for backward compatibility with older Plan.md files that only carry `domain_id`.
  3. If both reads miss, call `aeko_list_brand_kits(domain_id=frontmatter.domain_id)` and report whether draft/generating/failed kits exist. **Record into `aeko_data_gaps[]`** (key: `brand_kit`, status: `404` or `empty`) and continue — don't stop. The §3A.8 diagnostic surfaces the gap with the rest.
- If brand kit is present, verify voice minimum: `tone_of_voice` present + at least one of `{brand_voice_summary, target_audience}`. Thin kit → warn + offer to abort (`/aeko-brand-kit <domain_id> edit`).
- If brand kit is present, check snapshot-version drift and ask user when drift exists.

If `frontmatter.requires_brand_kit == false`, skip this step (don't add to `aeko_data_gaps[]`) and leave `resolved_brand_kit_id = null`.

## Step 3 — Citation forensics (two phases)

This is what makes AEKO-grounded content beat vanilla Claude. Build a structural model of what AI engines currently cite for this topic, then mimic — across one OR many channels.

The work splits in two:

- **Phase 3A — Selection forensics** (runs before Step 4). Cheap signal only: prompt resolution, compact tracked-prompt snapshot, cited-domain ranking, channel auto-detection, in-store dedupe index, selection-confidence score. No live recrawls; no full-body harvesting. Feeds Step 4's channel-selection UX.
- **Phase 3B — Post-selection enrichment** (runs at §4e, after §4-Form-2's submit captures both channel and media selection). Live recrawls and the full structural template — but only for channels the user actually kept. Feeds Step 5's drafting. No separate proceed-to-draft prompt; the form submit IS the proceed.

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

**Track per-prompt outcomes** into `aeko_wait_cycles[]`: if a tracked prompt returns zero citations for the `latest` window, append `{prompt_id, prompt_text, citation_count: 0}`. This is a wait-cycle state (the prompt was tracked but AEKO hasn't re-queried it yet) — NOT a backend error. The §3A.8 diagnostic surfaces wait-cycle states in a separate section from genuine 404s.

If the snapshot carries an embedded `crawl` payload per cited URL (the prompt-collection-time crawl alongside the citation), preserve it under `cached_crawl_by_url{}` for 3A.5 and 3B.2 — those payloads are older but free, and the 3B.2 stale-gate can reuse them when fresh enough.

#### 3A.2 Rank cited sources

Rank the aggregated sources by **citation frequency × inverse average position × citability score** (when the score is present). Surface the top 5–10 source domains and their canonical URLs.

#### 3A.3 Auto-detect candidate channels

Classify each top source domain into a channel slug per the table in `references/forensics/channel-detection.md`. Read that file lazily on first need (once per skill run). Discard rows whose channel slug is `—` (currently `wikipedia.org` and generic no-match sources); they remain citation/context signal but are not draft channels. Deduplicate supported slugs while preserving rank order. Carry `auto_detected_channels[]` into Step 4.

#### 3A.4 List in-store content

Single call: `aeko_list_own_content(domain_id, type="all", limit=15)`. Issue this in the same parallel batch as 3A.1's tracked-prompt fan-out — independent.

Split the result client-side by `content_type`:
- Build `in_store_topic_index[]` from the (title, url) pairs across blog and PDP rows. Used in §4a duplicate detection: if the working draft title is ≥80% token-overlap with an existing page, surface the conflict in §4a so the user can deselect or pivot before submitting §4-Form-1.

**Do not crawl in-store posts in 3A.** Tone-signature crawling is conditional and moves to 3B.4.

New domain with no in-store content → call returns empty; record `{key: "list_own_content", status: "empty"}` in `aeko_data_gaps[]` and continue silently. The diagnostic in §3A.8 surfaces it; §4a still notes "no in-store signature — drafting from cited-source signal only." Non-fatal.

If `aeko_list_own_content` returns 404 (domain not indexed in AEKO at all) — distinct from an empty-but-indexed response — record `{key: "list_own_content", status: "404"}` in `aeko_data_gaps[]` and continue. The diagnostic surfaces this as a backend/indexing issue, not a wait-cycle state.

#### 3A.5 Build light structural template stubs

For each `auto_detected_channels` entry, build a *stub* of `structural_template_by_channel[channel]` from snapshot-only signals:

- Citability score across the channel's top cited URLs.
- JSON-LD `@type`s aggregated across the channel's cited sources (from snapshot citation data).
- `Extracted: …` body slices joined for tone calibration.
- If `cached_crawl_by_url{}` (from 3A.1) carries data for any of this channel's top sources, derive approximate numeric targets (paragraph word counts, heading depth, list density) from the cached crawl. Mark these stubs with `freshness: cached` for §4a transparency. If no cached crawl is available for a channel, omit the numeric-targets line at §4a for that channel and report `freshness: pending`.

These stubs power §4a's "Structural targets" hint so the user can pick channels intelligently. 3B.5 upgrades them with live-crawl data for the channels the user keeps; deselected channels' stubs are discarded.

#### 3A.6 Initialize `cited_url_allowlist[]`

Seed `cited_url_allowlist[]` with every `source_url` harvested in 3A.1. 3B.6 and §4-Form-2 append to it; Step 6.1 reads it as the source of truth for "no invented URLs."

#### 3A.7 Compute selection confidence

Purely pre-crawl, no recrawl dependency:

- `high` — ≥3 prompts resolved × ≥3 distinct cited domains × JSON-LD `@type` present on ≥50% of citations.
- `medium` — ≥1 prompt × ≥2 cited domains.
- `low` — anything weaker (single prompt resolved, no citations, every prompt empty for the latest window, etc.).

Reported in §4a as `Selection confidence: high|medium|low`. Drives 3B.1's recrawl escalation: `low` selection confidence triggers the 3-URL escalation in 3B even on non-editorial channels.

#### 3A.8 AEKO data-gap diagnostic + graded proceed prompt

After §3A.1–§3A.7 finish, evaluate the gathered telemetry. Two categories:

- **`aeko_data_gaps[]`** — genuine backend/config/indexing problems worth fixing:
  - `brand_kit: 404|empty` from Step 2
  - `list_own_content: 404` from §3A.4 (distinct from empty-but-indexed)
  - `crawl_url: <url> → 404` from §3B.2 if it has already run (typically not yet at this point; see §3B for runtime tracking)
- **`aeko_wait_cycles[]`** — tracked prompts with zero citations in the `latest` window, recorded in §3A.1. NOT a backend error; the prompt was tracked but AEKO hasn't re-queried since. Will populate on the next response cycle.

If both arrays are empty → no diagnostic; proceed silently to §4a. If either is non-empty, print the bilingual diagnostic block:

```
⚠ AEKO 데이터 누락 (백엔드/인덱싱 확인 필요) / Missing AEKO data (backend/indexing)
  - domain_id: <id>
  - <for each entry in aeko_data_gaps[]>: <key>: <status> [<url if applicable>]
  Suggested action: verify the domain is indexed; check backend logs for <domain_id>.

ℹ AEKO 큐 대기 (재쿼리 사이클 대기) / AEKO queue waiting (re-query pending)
  - tracked prompts with 0 citations: <N>/<M> — will populate after AEKO's next re-query cycle; not a backend error.
```

Print only the sections with non-empty arrays.

**Graded default** — drive the proceed prompt's default option from §3A.7's `selection_confidence`:

- `selection_confidence == high` — proceed silently to §4a; no prompt. (Forensics is grounded regardless of any non-blocking gaps.)
- `selection_confidence == medium` — print prompt, **default option 1 (Plan-only)**.
- `selection_confidence == low` — print prompt, **default option 3 (abort)**.

**The proceed prompt** (printed only when default is not silent-proceed):

```
How would you like to proceed?
  1. Proceed Plan-only — draft from Plan.md description + products[] alone; skip external enrichment.
  2. Proceed with single capped WebFetch on <target_url> — explicit opt-in (see §3B caps).
  3. Abort and investigate the diagnostic above.

Default: <1|3 per selection_confidence>. Reply with `1`, `2`, or `3`.
```

`<target_url>` resolution for option 2 (in priority order):
1. `frontmatter.target_url` if present.
2. First entry of `parsed_products[].outbound_url` if Step 1 carried any.
3. The top-ranked `source_url` from §3A.2 if any survived the 404 storm.
4. None → option 2 is unavailable; print "Option 2 not available — no target URL in Plan or partial 3A signal." and show only options 1 and 3.

**No research-prompt fallback.** Do not invoke `aeko_search_research_prompts` when 3A returns thin signal — research prompts optimize for unrelated queries and produce drafts that look forensics-grounded but rank for the wrong things. (Note retained from prior 3A.8.)

On option 1: proceed to §4a with `forensics_mode = "plan_only"` carried as state — Step 5's drafting downgrades structural-template usage and relies on Plan description + brand kit.
On option 2: invoke §3A.9 (immediate opt-in WebFetch) before §4a.
On option 3: stop here. Do NOT call `aeko_complete_action_item`. Surface a one-line bilingual exit notice.

#### 3A.9 Opt-in WebFetch path (invoked only from §3A.8 option 2)

Fires synchronously the moment the user picks option 2 at §3A.8, BEFORE §4a / §4-Form-1. The resulting `external_enrichment_paste` is carried as state into Step 4 (for selection-summary context) and Step 5 (for drafting enrichment).

Never silent, never automatic, never invoked as a fallback when `aeko_crawl_url` 4xx/5xx (those failures stay logged and skipped per §3B.3 / Error paths). The §5.1 `other:<name>` fallback and §5.2 frontmatter-research call sites ALSO apply the rules below.

**Pre-fetch heavy-host guard.** Before calling `WebFetch`, parse the host out of `<target_url>` and match against this allowlist of known-heavy PDP hosts:

```
cafe24.com, *.cafe24.com, cafe24cdn.com,
myshopify.com, *.myshopify.com,
smartstore.naver.com,
gmarket.co.kr, auction.co.kr,
coupang.com, *.coupang.com
```

If the host matches, **DO NOT call WebFetch**. Print this bilingual prompt and wait for the user to paste facts:

```
이 호스트는 일반적으로 100k+ 자의 PDP를 반환합니다. 핵심 제품 정보(가격/성분/특장점)를 직접 붙여넣어 주세요.
This host typically returns 100k+ char PDPs. Please paste the load-bearing product facts (price / ingredients / claims) directly.
```

Treat the user's paste as `external_enrichment_paste`. Continue to §4a.

**Post-fetch cap (non-allowlist hosts).** If the host does not match the allowlist, call `WebFetch(target_url)` exactly once. If the returned body length is >50,000 chars OR >1,000 lines:

- DO NOT subagent-extract.
- Print the page `<title>` + first 5,000 chars of the body.
- Then print the same bilingual "paste facts" prompt above and wait for the user's paste.

If the body is within the cap, parse it as `external_enrichment_paste` directly (title, meta description, first 3 paragraphs, any JSON-LD `<script>` block).

**Scope.** WebFetch is restricted here to the single `<target_url>`. No recursive crawling, no per-prompt-source re-crawls, no fallback fetches when this one fails.

**Failure.** If `WebFetch` itself errors (network, 4xx/5xx), print one warning line and fall through to the "paste facts" prompt — never auto-retry, never fall back to a different URL.

### Phase 3B — Post-selection enrichment (runs at §4e, after §4-Form-2 submit)

3B runs after §4-Form-2 submits (≥1 selected channel + per-channel media/alt captured). Enrichment is scoped to the selected channels — deselected auto-detected channels pay nothing. The §4e summary reports freshness so the user can see what 3B produced; the submit was already the proceed-to-draft confirmation, so no further user prompt fires here. Step 5 drafting begins immediately after 3B completes.

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

On any recrawl failure (4xx/5xx, connect error), append `{key: "crawl_url", url: <url>, status: <status-or-error>}` to `aeko_data_gaps[]`, log a single warning line, and keep going on the snapshot signal alone. Recrawl is enriching, not gating.

Per recrawled URL, merge into the channel's structural template (in 3B.5):

- **Numeric targets** (override snapshot when fresher): `paragraphs.avg_word_count`, `paragraphs.median_word_count`, heading count + max depth, `lists.ul_count`/`ol_count`/`total_items`, `images.count`, `images.with_alt`.
- **Schema signal**: collect `json_ld[]` raw blocks across the top sources; aggregate `@type`s. Drives the editorial-channel HTML JSON-LD recipe in Step 5.
- **Title / meta seeds**: `title` and `meta_description` seed the draft's own title and meta when the channel has metadata slots.
- **Visual seeds**: `og.image` and `images.alt_examples` feed the Step 5.4 `media_specs:` block when the user skipped media.
- **Tone signal**: combined with the snapshot's `Extracted: …` text from 3A.1, the live crawl's title + meta + first heading establish the cited source's diction; carry into Step 5.3.

#### 3B.4 Conditional in-store crawl

Fetch the top **1** in-store blog post via `aeko_crawl_url(url)` (cached default — in-store pages are slower-changing; the 24h cache is fine here) **only when**:

- Any selected channel is an own-store channel (`own_store_blog` or a future `own_store_*` slug), **or**
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

Every URL passed to `aeko_crawl_url` in 3B.2 or 3B.4 — success or failure both count — appends to `cited_url_allowlist[]`. Failure URLs may still be referenced via §4-Form-2 media so they remain allowlist-eligible.

#### 3B.7 Compute freshness confidence

Post-crawl:

- `high` — ≥50% of attempted recrawls succeeded, **or** all selected channels' templates derived from snapshots ≤7 days old (stale-gate fully suppressed the recrawls because cached data was fresh).
- `medium` — at least one selected channel has fresh signal (`cached_fresh` or `recrawled_success`); others may be stale or failed.
- `low` — all recrawls failed and no snapshot is ≤7 days old.

Reported at §4e as `Freshness confidence: high|medium|low` alongside the recrawl tally (informational only — no user prompt at this point). Distinct label from selection confidence — never collapse them.

(The opt-in WebFetch path lives in §3A.9 — see Phase 3A. No subsection at 3B.8.)

## Step 4 — Channel & media selection (interactive)

This step is the v2 fanout. Always run; respect `skip` / `none` for empty selections.

### 4.0. Auto-add `aeko_shop` for tenant brands (runs before §4a prints)

This substep mutates `auto_detected_channels[]` so the §4a summary below reflects the final pre-selection set. Run it before any §4a output.

aeko.shop is AEKO's canonical publishing destination for tenant brands. Content generation is already gated Pro+ at skill entry per contract §3.2, so this substep must not re-check account tier. Read only the brand-kit response's destination flag from Step 2:

> The brand kit is the **content voice kit**; the public aeko.shop brand identity (the brand page) is **derived from it on publish** and keyed by store domain — there is no separate shop brand to create or claim before publishing. (See `/aeko-brand-kit`.)

**Canonical destination rule:** For every tenant brand, prepend `aeko_shop` to `auto_detected_channels[]`. Only skip when `brand_kit.aeko_shop_disabled === true`.

- `aeko_shop_disabled === true` → no-op; `aeko_shop` never appears in the channel set.
- `aeko_shop_disabled === false`, absent, malformed, or otherwise not strictly `true` → prepend `aeko_shop` to `auto_detected_channels[]`. The channel appears in §4a's "Auto-detected channels" line and is preselected in §4-Form-1 — the user can still deselect it.

When `aeko_shop_disabled` is absent or malformed, emit a one-line warning in §4a: "ℹ aeko.shop status not surfaced by brand-kit response — assuming enabled. Verify in the dashboard if aeko_shop draft is unexpected."

**Own-store content seed:** For every tenant brand, append `own_store_blog` to `auto_detected_channels[]` when absent. This exposes the tenant's connected Store Content draft option in §4a / §4-Form-1 alongside the canonical aeko.shop option. It is a backend-saved draft target only — this skill never writes to the connected store, and publish later creates an AEKO-owned draft row rather than pushing to Cafe24/Shopify.

**Backend wiring note** — as of the current MCP minor version, `aeko_get_brand_kit` may not surface `aeko_shop_disabled` in its response. `metadata.account_tier` is not load-bearing for this gate. Missing `aeko_shop_disabled` means include `aeko_shop`; only explicit `true` disables the canonical destination. Track surfacing `aeko_shop_disabled` as a backend visibility improvement, not as a prerequisite for preselection.

`aeko_shop` is **not** forensics-detected; it's a brand destination flag. Its §4a "Structural targets" line reads `freshness: pending` until 3B runs (3B will recrawl 1–2 representative pages from the brand's existing aeko.shop content via the same `aeko_list_own_content` → `aeko_crawl_url` flow used for any other selected channel, then derive numeric structural targets).

When `aeko_shop` lands in the final selected set, drafting for it uses `references/recipes/editorial-html-jsonld.md` (the same recipe `보도자료`/`magazine`/`partner_media` use; aeko_shop has its own section in that file with the sanitizer-safe body-only HTML shape, the `<slug>.meta.json` sidecar, and the product callout pattern — see §5.6 and §5.6.6). aeko.shop is the **only** channel that consumes `parsed_products[]` (from Step 1) — rendered as `<figure role="callout" data-variant="product" data-product-source-id="<source_id>">` callouts in body HTML and `featured_products[]` entries in `.meta.json`. **No in-body JSON-LD** — the aeko.shop frontend regenerates Article + Product structured data from `PostUpsert` fields at render time. If `parsed_products[]` is non-empty but `aeko_shop` is **not** in the final selected channel set after §4-Form-1, surface a warning before drafting: "Plan carries `<N>` products but `aeko_shop` channel is not active — products won't be linked. Re-select `aeko_shop` and re-submit §4-Form-1 to use them, or accept that other channels render product names as plain text only."

**User-facing channel label.** Use the bilingual label from §8.0 (`aeko.shop용 HTML / aeko.shop HTML`) for §4a, §4-Form-1, the §4e enrichment summary, Step 8, and §9. The legacy "aeko_shop (브랜드 스토어 · aeko.shop)" inline label is superseded by the §8.0 table.

### 4a. Print selection summary

Print the Phase 3A signal so the user can tell at a glance whether forensics is grounded **before** committing to channels. This is pre-crawl — the live recrawl runs in Phase 3B at §4e (after §4-Form-2 submit captures both channels and media), so the recrawl line is "deferred" here and reported separately at §4e.

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

If `Selection confidence: low`, warn before §4-Form-1: "the structural template will be thin — consider tracking more prompts first via `/aeko-find-prompts-to-track` for higher-quality output. Phase 3B will escalate to a 3-URL recrawl per channel to compensate." User may still proceed via §3A.8's 3-option prompt.

If 3A.4 surfaced a likely duplicate (≥80% title token-overlap with an in-store page from `in_store_topic_index[]`), append a single-line warning above the §4-Form-1 channel toggles: "⚠ This draft topic looks ≥80% similar to <existing-url> — consider pivoting the angle or deselecting `own_store_blog` to avoid a duplicate."

### 4-Form-1. Channel selection (replaces former §4b + §4c)

Issue ONE structured elicitation form with both auto-detected channels (pre-checked) and addon channels. Eliminate the previous two-question sequence — one submit captures everything.

**Form fields:**

1. **Auto-detected channels** (pre-checked toggles, user can deselect):
   - Bullet list of `auto_detected_channels[]` from §3A.3, each rendered with bilingual label from §8.0 (e.g., "Reddit 포스트 초안 / Reddit post — auto-detected from `reddit.com/r/<sub>`").
   - The `aeko_shop` entry from §4.0 is pre-checked when the brand-kit flag allows.
   - The `own_store_blog` entry from §4.0 is pre-checked when present.
   - **Selecting `aeko_shop` is consent to backend-save** after drafting succeeds. This required save creates the backend variation that `/aeko-publish-content <item_id>` publishes later; deselect `aeko_shop` here if the user wants local-only outputs.

2. **Addon channels** (unchecked toggles):
   - 보도자료 — 보도자료 초안 / Press release draft (합니다체)
   - magazine — 매거진 기고용 / Magazine pitch (Vogue-style editorial)
   - instagram — Instagram용 캡션 / Instagram caption (caption + hashtags + alt text)
   - tiktok — TikTok용 스크립트 / TikTok script (30–60s with beats)
   - youtube — YouTube용 스크립트 / YouTube script (title + description + chapters)
   - naver_blog, tistory (also offered here even when not auto-detected)
   - other:`<name>` — free-form (one text input for `<name>` and one for "reference URL(s) or short description"). `<name>` must be ASCII; reject submissions with non-ASCII characters in the name field (collapsed to `other_<ascii_name>` for filesystem use per §5.5.1).

3. **Single submit button:** "Proceed to media step" (KO: "미디어 단계로 진행").

**Mechanism note.** The implementing session picks the best available elicitation mechanism: a true multi-select form if the host supports it, otherwise a structured prompt with checkbox-style text input. Either way, ONE round-trip — not a sequence of asks.

Parse user reply into `selected_detected_channels[]` (subset of `auto_detected_channels`) and `selected_addon_channels[]`. For each `other:<name>`, the reference URLs / description were captured inline in the form (no follow-up ask).

**If 0 channels selected → stop here.** Print bilingual "no channels selected" and do NOT call `aeko_complete_action_item`. Do not run §0b reference batch, do not run §4-Form-2, do not run Phase 3B.

**Otherwise — run §0b reference batch now** (the per-channel recipe + example reads, plus the global voice-overrides read) in a single parallel `Read`. Hold the results in memory for Step 5.

### 4-Form-2. Per-channel media + alt-text (replaces former §4d + §4e)

Issue a SECOND structured elicitation form. This is the only other interactive turn before drafting.

**Channel class split** — render channels in two groups within the form so the UI doesn't look like 8 identical blobs:

- **Editorial class** (`aeko_shop`, `naver_blog`, `tistory`, `magazine`, `보도자료`, `partner_media`, `own_store_blog`): for each selected channel in this class, render:
  - **Hero image** slot — one file picker / URL input + one alt-text input. For `aeko_shop` this is the post's **standalone featured/lead image** (the big image at the top of the rendered post) — it is NOT one of the inline body images, so a user who just wants "a picture on the post" fills THIS slot. If the user supplies exactly one image for `aeko_shop` and leaves the inline slots empty, treat it as the hero. (When `parsed_products[]` exists, the first product image auto-fills the hero, so an explicit hero upload is optional.)
  - **Inline image** slots — up to TWO additional slots per channel, COLLAPSED by default (user expands the ones they want to fill). Each expanded slot has the same file + alt-text pair.

- **Social class** (`instagram`, `tiktok`, `youtube`, `reddit`): for each selected channel in this class, render:
  - **One image slot** — single file picker / URL input + one alt-text input.
  - For `tiktok` / `youtube`: a separate **video reference** input (URL or local path) — NOT a file picker (video files are NOT uploaded via `aeko_request_media_upload`; only referenced). Optional.

- **`other:<name>` channels:** one image slot + alt-text, same as social class.

**Per-slot rules (apply to every slot above):**

- **Image inputs** accept `image/jpeg`, `image/png`, `image/webp`, `image/gif` ONLY (matches `aeko_request_media_upload`'s MIME validator in `aeko-mcp/aeko_mcp/tools/media_upload.py:7`). Reject other MIME types in the form.
- **URL fallback** is always available alongside the file picker for users who'd rather paste a URL.
- **Alt-text input is REQUIRED** the moment a file or URL is staged in that slot. The form CANNOT submit if any populated media slot has empty alt-text — surface "Alt text required for `<channel>` `<slot>`" inline.
- **"Skip media for this channel"** checkbox per channel (collapses that channel's slots). Allowed for prose-only channels (`reddit`, `보도자료`); for visual-first channels, skip emits `media_specs:` YAML blocks at §5.4 as today.
- **Video references** (tiktok/youtube only): URL or local-path string only; no upload; alt-text still required (used as accessible caption).

**Mechanism note.** Same as §4-Form-1: pick the best available file-attachment elicitation, with structured-prompt fallback. If the host elicitation truly does not support file attachments, ask the user to attach files in chat referencing each by a stable label ("aeko_shop hero", "naver_blog inline #1") and capture alt-text inline — but always offer the URL fallback as a first-class option.

**Submit button:** "Generate drafts" (KO: "초안 생성"). The submit IS the proceed-to-draft confirmation — no separate §4e re-confirmation.

Parse the form into `media_by_channel{}` with per-slot metadata:

```
media_by_channel = {
  "aeko_shop": {
    "hero": {"src": "<file|url|local_path>", "alt": "<required>", "type": "image"},
    "inline_1": {...} | null,
    "inline_2": {...} | null,
    "video": null,
  },
  "tiktok": {
    "image": {"src": "...", "alt": "..."},
    "video": {"src": "https://...", "alt": "...", "type": "video_reference"} | null,
  },
  ...
}
```

For every URL captured here (and every URL pasted into `other:<name>` references in §4-Form-1), append to `cited_url_allowlist[]` so Step 6.1's "no invented URLs" gate accepts the user-supplied media link.

### 4e. Phase 3B enrichment (runs after §4-Form-2 submit, before Step 5)

The §4-Form-2 submit triggers Phase 3B immediately. No separate "Proceed to draft?" ask — Form-2's submit already captured proceed.

**Run Phase 3B now** (`§3` → Phase 3B). 3B scopes its recrawl budget to the selected channels only, so the cost is bounded. When 3B completes, print the enrichment summary:

```
Enrichment summary (Phase 3B, selected channels only):
  Recrawls attempted:    4   (1-2 / channel, escalated to 3 on `보도자료`)
  Recrawls succeeded:    3   (1 stale-gated via snapshot ≤7d, 0 failed)
  In-store crawl:        ran (top blog post — own_store_blog selected)
  Freshness confidence:  high
```

Render `Freshness confidence` as a distinct label from `Selection confidence` (§4a) — never collapse them. The two answer different questions: selection confidence is "is the channel auto-detect grounded?"; freshness confidence is "is the structural template fresh enough to draft against?"

If Phase 3B appended any new `crawl_url` entries to `aeko_data_gaps[]`, print the same bilingual "Missing AEKO data" diagnostic section from §3A.8 immediately under the enrichment summary. This is not a prompt and it does not block drafting; it makes post-selection backend/indexing gaps visible instead of burying them in warning lines.

Proceed to Step 5 with `structural_template_by_channel{}` populated for selected channels only. The summary is informational; no user prompt here.

## Step 5 — Per-channel draft loop

Loop over the final selected channel list. For each channel:

### 5.0 Use the §0b reference cache

Reference content lives under `skills/aeko-create-content/references/`. The maps below define what §0b loads in one parallel `Read` batch immediately after §4-Form-1. During the Step 5 loop, use the in-memory cache from §0b; do not issue new per-channel `Read` calls unless the user edited the channel set after the batch.

For each selected channel `C`, §0b loads:

1. **Recipe cache entry** (always, when a recipe file exists for the channel). Channel-to-file map:
    - `보도자료` → `references/recipes/보도자료.md` (also load `references/recipes/editorial-html-jsonld.md`)
    - `magazine` → `references/recipes/magazine.md` (also load `references/recipes/editorial-html-jsonld.md`)
    - `partner_media` → forensics-derived; load `references/recipes/editorial-html-jsonld.md` for the HTML/JSON-LD pair
    - `aeko_shop` → load `references/recipes/editorial-html-jsonld.md` (the aeko_shop section + product reference rendering + AEKO-media-CDN image rules). No channel-specific recipe file; the editorial recipe is the single source. Forensics template from 3B.5 supplies numeric targets for the aeko.shop body (paragraph / heading / image-density stats sampled from the brand's existing aeko.shop content).
    - `instagram` → `references/recipes/instagram.md`
    - `tiktok` → `references/recipes/tiktok.md`
    - `youtube` → `references/recipes/youtube.md`
    - `naver_blog` → `references/recipes/naver_blog.md` (layered on top of the forensics template from 3B.5 — recipe provides platform conventions, forensics provides measured numeric targets)
    - `tistory` → `references/recipes/tistory.md` (same layering pattern as `naver_blog`)
    - `own_store_blog` — no recipe file; structural and voice template comes from the in-store crawl in 3B.4 plus `references/examples/in-store-content-example.md` when present.
    - `reddit` — no recipe file; structural template comes from 3B.5 alone (Q&A locked when forensics 3B.5 detects `QAPage` / `DiscussionForumPosting`).
    - `other:<name>` — no recipe file; structural template comes from §5.1's mini-forensics.

2. **Brand-specific exemplar cache entry** (if it exists, conditional). Filename pattern: `references/examples/<C>-*example*.md` or the explicit names in the table below. Use check-exists semantics during the §0b batch — silently skip if absent. Treat each match as style guidance:

    | channel | example file the skill scans for |
    | --- | --- |
    | `naver_blog`, `tistory` | `references/examples/blog-example.md` |
    | `own_store_blog` | `references/examples/in-store-content-example.md` |
    | `instagram` | `references/examples/instagram-post-example.md` |
    | `보도자료` | `references/examples/press-release-example.md` |
    | `tiktok` | `references/examples/tiktok-script-example.md` (optional) |
    | `youtube` | `references/examples/youtube-description-example.md` (optional) |
    | `magazine` | `references/examples/magazine-feature-example.md` (optional) |
    | (any) | `references/examples/in-store-content-example.md` — voice signal across all channels |

3. **Voice-overrides cache entry** (if it exists): `references/style/voice-overrides.md`. Filter to blocks scoped to `domain: <frontmatter.domain_id>` and/or `channel: <C>`. Skip silently if the file doesn't exist or no scoped block matches.

**Example-file rules** (mirror §6.1 hard-gate intent):

- Example files are loaded as **style reference**, not as cited content. Any URL inside an example file MUST NOT be carried into the artifact — the §6.1 "no invented URLs" gate still applies, scoped to `cited_url_allowlist[]`.
- Example files may legitimately contain `[Image]` placeholders as part of demonstrating a brand's pattern. The §6.1 placeholder gate scans the *generated artifact*, not the example file.
- Mimic structure (paragraph length, hook style, hashtag density, heading cadence) and tone (sensory verbs, register, glossary). Do not copy phrases verbatim — even your brand's own exemplar.

The user-facing summary at Step 8 must list which reference files were loaded per channel so the user can verify their exemplars are picked up (e.g., `Mimicked: examples/instagram-post-example.md + recipes/instagram.md`).

### 5.1 Pick the structural source

- **Auto-detected channel without recipe** (`reddit`): use `structural_template_by_channel[channel]` from Step 3 alone (snapshot + live crawl already merged in 3B.3 / 3B.5).
- **Own-store channel** (`own_store_blog`): use the in-store crawl/tone signature from 3B.4 as the primary structural source, plus `references/examples/in-store-content-example.md` when present. If no in-store content exists, draft from brand-kit voice and cited-source signal, and surface "no in-store signature — drafting from cited-source signal only" once.
- **Auto-detected channel with recipe** (`naver_blog`, `tistory`): use BOTH the forensics template (3B.5 numeric targets) AND the recipe loaded in §5.0 from `references/recipes/<channel>.md` (platform conventions, register, acceptance gates). When the two disagree on a numeric target, forensics wins; when they disagree on register or platform conventions, the recipe wins. Recipe acceptance gates apply *alongside* §6.2 structural-target deltas.
- **Brand-destination editorial** (`aeko_shop`): use BOTH the forensics template (3B.5 numeric targets sampled from the brand's existing aeko.shop content via in-store recrawl) AND `references/recipes/editorial-html-jsonld.md`'s aeko_shop section (sanitizer-safe body HTML, product callout pattern, `<slug>.meta.json` field constraints, AEKO-media-CDN image rules — **no in-body JSON-LD**, the frontend regenerates it from `PostUpsert` fields). Recipe wins for product-callout rules, body HTML structure, and `.meta.json` shape; forensics wins for measured paragraph / heading / list / image-density numeric targets.
- **Built-in addon** (`보도자료`, `magazine`, `instagram`, `tiktok`, `youtube`): use the recipe loaded in §5.0 from `references/recipes/<channel>.md` (and `references/recipes/editorial-html-jsonld.md` for editorial channels' HTML pair).
- **`other:<name>`**: if reference URLs were provided, fetch them via `aeko_crawl_url(url)` and derive an ad-hoc template (mini-forensics: title, meta, paragraph length, heading depth, list usage, JSON-LD `@type`s). Fall back to `WebFetch` if the crawl tool returns 4xx/5xx — **but apply the same heavy-host guard + 50k char / 1k line cap from §3A.9**. For `other:<name>` channels, JSON-LD signal is nice-to-have, not required. If only a description was given, use the description plus brand-voice defaults.

### 5.2 Optional research

If frontmatter prose requests external research OR an `other:<name>` channel needs reference fetching:
- `WebSearch` for related context (competitor brand names, recent news, review themes).
- `WebFetch` on specific URLs called out in prose or supplied by user. **Apply the §3A.9 heavy-host guard + 50k char / 1k line cap to every WebFetch call here, without exception.** Do NOT invent URLs.
- Append a research-log to the channel's artifact directory.

### 5.3 Draft the artifact

**Output format per channel** (overridden by `frontmatter.output_artifact_format` when present):

| channel | default format(s) |
| --- | --- |
| `reddit`, `naver_blog`, `tistory`, `instagram`, `tiktok`, `youtube`, `own_store_blog` | `markdown` |
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
5. **In-store tone signature** (3B.4) — fills gaps when the brand kit's `tone_of_voice` is thin or absent. May be absent when 3B.4 didn't trigger (no own-store channel selected and template not thin); in that case treat as null. When brand kit and in-store conflict, brand kit wins; surface the conflict once at the §4e enrichment summary.

Plus the always-on rules:
- Target audience from brand kit shapes word choice (beginner vs expert vocabulary).
- For `보도자료` specifically: 합니다체 is required even if brand voice elsewhere is 요체 — the format wins; surface the conflict before resolving.
- **No hard CTAs** ("Buy now" / "Click here" / promotional commands) in the body. Citability content earns the click via authority, not commands. Same principle as `/aeko-update-pdp`: AEKO injects citability content; the host channel owns the action UI.

**Structural discipline** (from Step 3 template or `references/recipes/<channel>.md`):
- Match the winning-source format the forensics identified.
- Be honest about what this is: Reddit-style Q&A is fine, but do NOT fake Reddit thread formatting or pretend the content is crowd-sourced.
- Link out to the top cited sources where the draft genuinely benefits from them (prevents the "generic AEO mush" failure mode).

### 5.4 Embed media reference

**Hard rule (placeholders):** never emit `[Image #N]`, `[image placeholder]`, `[Image]`, `[photo]`, `[Video:` (without a real URL inside), `[Photo:`, `[graphic]`, or any unfilled `[…]` media marker in body text. Markdown image syntax (`![alt](url-or-path)`) is only permitted with a real URL or local path. If you find yourself wanting to write a placeholder, stop and use the `media_specs:` block below instead (except for `aeko_shop` — see below). The §6.1 hard gate scans for any `[Image`/`[image`/`[Video`/`[video`/`[Photo`/`[photo`/`[Graphic`/`[graphic`/`[placeholder` token followed by a non-URL — fail the artifact if any match.

**Hard rule (alt-text required everywhere):** every emitted image — Markdown `![alt](url)`, HTML `<img alt="…">`, `meta.json alt_text` field, or `media_specs.alt_text` YAML — MUST carry non-empty alt text. The alt-text comes from `media_by_channel[<channel>][<slot>].alt` captured in §4-Form-2 (required at form-submit time). The §6 citability check fails any artifact with an empty `alt=""` or missing `alt_text` field. This applies to both user-supplied media AND `parsed_products[]` image references (use `product.short_description` truncated to ≤125 chars, or `product.name` as fallback).

**Input shape** (from §4-Form-2): `media_by_channel[<channel_slug>] = {<slot_name>: {src, alt, type} | null, ...}` where `slot_name` is `hero` / `inline_1` / `inline_2` / `image` / `video` per the channel class. Iterate slots in declaration order; emit slots whose value is non-null.

**For the `aeko_shop` channel specifically** (publish-ready path; the artifact lands on aeko.shop without further transformation):

- **No `media_specs:` YAML for aeko_shop.** The channel needs concrete AEKO-media-CDN URLs in the body — the absolute `public_url` returned by `aeko_request_media_upload`. The CDN host is **backend-configured** (`settings.media_public_base_url`, today `https://aekoshop-….azurefd.net/…`); do **not** assume or hand-write `cdn.aeko.shop` (it is not a serving origin and is rejected by the sanitizer). If the user populated zero slots in `media_by_channel[aeko_shop]` AND `parsed_products[]` is empty, the recipe still produces a text-only article (no hero, no inline images) — the §6.3 acceptance gates accept image-count = 0 for this case.
- **For each user-supplied image** (URL or local path from §4-Form-2's `media_by_channel[aeko_shop]`, iterating slots in declaration order: `hero` → `inline_1` → `inline_2`): upload to the AEKO media CDN (via presign) before embedding. The contract is enforced by `aeko-shop-backend/app/schemas.py::MediaPresignRequest` (which uses base64 MD5, not hex) and Azure Blob's signed-URL PUT requirements (which need `x-ms-blob-type` and `Content-MD5` headers). Mismatch returns HTTP 400 or 403. Steps:
  1. **Stage the bytes locally.** For local-path inputs the file already exists; for remote URLs, fetch first into a temp file at `./aeko-artifacts/<domain_id>/<item_id>/aeko_shop/.uploads/<sha256_of_url>.<ext>` (deterministic temp path; safe under parallel runs; auto-cleaned at Step 7 success). Create the `.uploads/` subdir if missing.
  2. **Compute digests.** `content_sha256` = **SHA-256 hex** (lowercase, 64 chars, no separators). `content_md5` = **base64-encoded raw MD5 digest** (exactly 24 chars including padding; do **NOT** use hex — the backend's Pydantic field is `min_length=24, max_length=24`). `byte_length` = file size. Reference implementation: `aeko-mcp/aeko_mcp/tools/store_write.py:84-85` (`base64.b64encode(hashlib.md5(data).digest()).decode()`).
  3. **Call `aeko_request_media_upload`** per `aeko-mcp/aeko_mcp/tools/media_upload.py` — args: `brand_kit_id=<frontmatter.brand_kit_id if present, else resolved_brand_kit_id>`, `source_content_id=frontmatter.item_id`, `filename=<basename only — no path separators>`, `content_type=<MIME, must match `^image/(jpeg|jpg|png|webp|gif)$`>`, `content_sha256=<hex>`, `content_md5=<base64>`, `byte_length=<n>`. Presign must use `frontmatter.brand_kit_id` when available even if the Step 2 voice-read failed or fell back, because upload/publish accepts draft kits by id. Response: `{upload_url, public_url, blob_key, expires_at}`.
  4. **PUT the bytes** via `Bash` with the Azure-required headers — every header is required (Azure rejects with 403 otherwise): `curl -X PUT --data-binary @<staged_path> -H "x-ms-blob-type: BlockBlob" -H "Content-Type: <type>" -H "Content-MD5: <base64>" "<upload_url>"`. The `Content-MD5` value MUST equal the `content_md5` passed at step 3 — Azure verifies the body against this header. Verify HTTP 2xx before proceeding; treat 4xx/5xx as upload failure per the rule below.
  5. **Verify the public URL.** After a 2xx PUT, issue `curl -fsSI "<public_url>"` (fallback to `curl -fsS -r 0-0 "<public_url>"` if HEAD is blocked). Continue only if the public URL returns HTTP 2xx. A successful PUT is not enough: if Front Door/CDN pathing or blob container configuration is wrong, the page will render a broken image even though upload appeared successful.
  6. **Record and embed `public_url` verbatim.** Store each verified upload in `uploaded_media_by_slot[slot_name] = {public_url, blob_key, alt, staged_path}`. Embed the returned `public_url` **exactly as returned** (do not rewrite its host) in the artifact body for inline slots — Markdown `![<alt>](<public_url>)` and HTML `<figure><img src="<public_url>" alt="<alt>" width="<w>" height="<h>" loading="lazy"></figure>` (per the recipe's image-attribute hard gate at §6.3). The `alt` value MUST be the `alt` field from `media_by_channel[aeko_shop][<slot>].alt`. Never invent alt text; never leave empty.
- **For `parsed_products[]` image references**: `product.image_url` comes from the brand's catalog and is often on the **brand's own** store CDN (Shopify/Cafe24), not the AEKO media CDN. Where it renders decides whether that's allowed:
  - **Bottom "Featured products" cards and the hero** are rendered by the page's `next/image`, which accepts any HTTPS origin — reference `product.image_url` directly there; do **not** re-upload.
  - **Inline body `<figure data-variant="product">` callout images are sanitizer-gated** to `settings.allowed_image_origins` (AEKO media CDN only). If `product.image_url` is **not** on an AEKO media origin, either re-host it via §5.4's presign+PUT steps and embed the returned `public_url`, **or omit the inline `<img>`** (keep the callout `<figcaption>` text) and let the bottom product card carry the image. Never place a brand-domain image URL in body HTML — it returns HTTP 400 at publish.
  - Alt-text for product images derives from `product.short_description` truncated to ≤125 chars; fall back to `product.name` when short_description is absent.
- **Hero image**: written to `<slug>.meta.json` `hero_image_url` (top-level publish field) — NOT embedded as an in-body `<figure>` (the rendered page emits its own hero `<Image>` from the publish payload; embedding it in body HTML produces a duplicate hero). First entry of `parsed_products[]` (if any) wins — its `image_url` populates `hero_image_url`. If `parsed_products[]` is empty, fall back to `uploaded_media_by_slot["hero"].public_url` when the user supplied a hero and upload succeeded. The `.meta.json` value MUST be an **absolute https URL** — either the `public_url` returned by `aeko_request_media_upload` (uploaded hero) or `parsed_products[0].image_url` (product hero, which may be on the brand's own https CDN since the hero is rendered by `next/image`, not the sanitizer) — or `null`. Never the original local path, and never a hand-written `cdn.aeko.shop` URL. If neither a product image nor uploaded hero exists, leave `hero_image_url` as `null` in `.meta.json` and omit the hero entirely.
- **`.meta.json` alt-text propagation:** for every image emitted in body HTML (inline images uploaded via §5.4 steps 1-6, plus product callouts), the corresponding `media[]` entry in `.meta.json` MUST carry `alt_text` matching the body HTML's `alt=` attribute. Hard-gated in §6.3.
- On upload failure (missing both `frontmatter.brand_kit_id` and `resolved_brand_kit_id`, network error, presign 4xx/5xx, PUT non-2xx, or the §5.4-step-5 `public_url` reachability check returning non-2xx): **warn loudly and specifically — never let an intended image vanish silently** (the #1 "I added an image but it didn't show up" report). Surface a visible block, not a one-liner:
  - For a **hero** slot failure (EN): `⚠ Hero image upload failed for <filename> (<reason: presign 4xx / PUT failed / public_url not reachable>). The post will publish with NO lead image. Fix and re-run, or proceed text-only.` / KO: `⚠ 대표 이미지 업로드 실패: <filename> (<사유>). 이 포스트는 대표 이미지 없이 게시됩니다. 수정 후 다시 실행하거나 텍스트만으로 진행하세요.`
  - For an **inline body** slot failure (EN): `⚠ Inline image upload failed for <filename> (<reason>); it was dropped from the body. The rest of the draft is intact.` / KO: `⚠ 본문 이미지 업로드 실패: <filename> (<사유>) — 본문에서 제외했습니다. 나머지 초안은 정상입니다.`
  - If the failure reason is a **non-2xx `public_url`** despite a successful PUT, name the likely cause (CDN/Front Door container-path or `media_public_base_url` misconfig) so it's actionable, not mysterious.
  Then omit that image from `.html` and `.meta.json` and continue with a valid text-only/partial aeko.shop draft. Do not write `[image: ...pending]` placeholders for `aeko_shop`; the publish-ready path must either contain concrete AEKO-media-CDN URLs (the presign `public_url`) or no image at all. Do not delete the staged file on failure — it speeds up retry. (No-image publishing is fully valid — `hero_image_url: null` renders a clean text-only post; the warning is so the user *chose* text-only rather than losing an image they expected.)

**If `media_by_channel[channel]` has any populated slot** (real URL or local path supplied) for **non-aeko_shop channels**:

Iterate the slots in declaration order. For each slot with non-null `{src, alt, type}`:

- Markdown channels (`naver_blog`, `tistory`, `partner_media`, `own_store_blog`, `reddit`, `magazine`, `보도자료`):
  - Image (`type == "image"`): emit `![<alt>](<src>)` — the alt MUST be the slot's `alt` field, never empty.
  - Video reference (`type == "video_reference"`): emit `[<alt>](<src>)` link with the alt as link text; alt doubles as accessible caption. Bracket form `[Video: <url>]` (with a colon and inlined URL) is **not** allowed because the §6.1 scanner would flag it; use the link form so the URL parses cleanly.
- Instagram → `media:` field at the top of the file referencing the asset; alt text rendered in its own `alt:` field below.
- TikTok → reference inside the relevant beat (`[on-screen]: image at <src>, alt: <alt>`). For tiktok video references, emit `[video: <src>, alt: <alt>]` in the relevant beat.
- YouTube → reference in description (`Thumbnail: <src> (alt: <alt>)`). For youtube video references, emit `Video URL: <src>` plus a separate `Alt text: <alt>` line.

For non-aeko_shop channels, the skill **does not copy or upload** the media — references only.

**If `media_by_channel[channel]` is null or every slot is null** (user picked "Skip media" in §4-Form-2) — excludes `aeko_shop` (its skip behavior is handled above):

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

**Always use channel-segmented paths.** Do not flatten artifacts into one folder. Both the directory and the basename carry the channel — basenames look identical in Claude Desktop's working-folder UI without the suffix, which makes drafts indistinguishable.

#### 5.5.1 Channel slug vs filename token (alias layer)

Each channel has three identifiers:

- **`channel_slug`** — canonical lookup key. Used for recipe/example file paths in §5.0 (e.g., `references/recipes/<channel_slug>.md`), error messages, contract references, and any cross-skill grep.
- **`display_label_ko` / `display_label_en`** — bilingual human label. Used in §4a / §4-Form-1 prompts, Step 8 summary, and §9 publish handoff. See the §8.0 channel-label table.
- **`filename_token`** — ASCII-safe slug used ONLY in directory + basename suffix. For nearly every channel `filename_token == channel_slug`. The one exception today is `보도자료` → `press_release` (Korean characters in filenames break some downstream tooling and indexing).

Allowlist (canonical slug → filename token):

| channel_slug | filename_token |
|---|---|
| `aeko_shop` | `aeko_shop` |
| `naver_blog` | `naver_blog` |
| `tistory` | `tistory` |
| `instagram` | `instagram` |
| `tiktok` | `tiktok` |
| `youtube` | `youtube` |
| `magazine` | `magazine` |
| `보도자료` | `press_release` |
| `partner_media` | `partner_media` |
| `reddit` | `reddit` |
| `own_store_blog` | `own_store_blog` |
| `other:<ascii_name>` | `other_<ascii_name>` (collapse `:` → `_`; reject if `<ascii_name>` has non-ASCII chars at §4-Form-1) |

Recipe loader still reads `references/recipes/<channel_slug>.md` — the alias affects filesystem OUTPUT only, never lookup. A recipe filename or lookup key named `press_release` must not exist; an existing human-facing `other:press_release` example inside `references/recipes/보도자료.md` is allowed.

#### 5.5.2 Path template

`./aeko-artifacts/<domain_id>/<item_id>/<filename_token>/<slug>__<filename_token>.<ext>`

- Directory uses `<filename_token>` (so `보도자료/` becomes `press_release/`).
- Basename suffix `__<filename_token>` so flattened views still identify the channel.
- `<slug>` is derived per §5.5.3 from the `resolved_title` produced in Step 1.

#### 5.5.3 Slug derivation

1. Source: `resolved_title` from Step 1 (frontmatter.title → Plan H1 → item_id chain).
2. Lowercase, ASCII-fold non-ASCII characters (Hangul → romanization via standard fold; if no fold available, drop the character).
3. Replace any run of non-alphanumeric characters with a single hyphen.
4. Truncate to **60 characters at the nearest word boundary** (don't truncate mid-word).
5. Strip leading and trailing hyphens.
6. On filename collision within the same channel directory, append `-2`, `-3`, … until unique.
7. **Empty-slug fallback.** If steps 1–5 produce an empty string (most common cause: 100% Hangul `resolved_title` with no romanization fold available AND no Plan H1), use `<frontmatter.item_id>` as the slug. Never write to a hidden filename like `__naver_blog.md`. Example: a Plan with H1 `# Plan: 여름철 침구 가이드` and no frontmatter.title — `resolved_title` becomes `여름철 침구 가이드`; if Hangul fold yields nothing, slug becomes `<item_id>` (a UUID), so the file lands at `.../naver_blog/3f2c1a04-…__naver_blog.md`.

#### 5.5.4 Filename rules per channel

| channel_slug | basename pattern | extension(s) |
| --- | --- | --- |
| `reddit`, `naver_blog`, `tistory`, `partner_media`, `own_store_blog` | `<slug>__<filename_token>` | `.md` |
| `보도자료`, `magazine` | `<slug>__<filename_token>` | `.md` AND `.html` (see `references/recipes/editorial-html-jsonld.md`) |
| `aeko_shop` | `<slug>__aeko_shop` | `.html` AND `.meta.json` AND `.md` — three files (the publish-ready triple; see `references/recipes/editorial-html-jsonld.md` for the per-file shape and §6.3 for the acceptance gates) |
| `instagram`, `tiktok`, `youtube` | `<slug>__<filename_token>` (slug still derives from `resolved_title`; do NOT use the literal channel name as the basename) | `.md` |

#### 5.5.5 Worked-example directory tree

For a draft with `resolved_title = "Summer Cooling Bedding — 2026 Guide"` and 11 selected channels:

```
aeko-artifacts/
  <domain_id>/
    <item_id>/
      reddit/summer-cooling-bedding-2026-guide__reddit.md
      own_store_blog/summer-cooling-bedding-2026-guide__own_store_blog.md
      naver_blog/summer-cooling-bedding-2026-guide__naver_blog.md
      tistory/summer-cooling-bedding-2026-guide__tistory.md
      partner_media/summer-cooling-bedding-2026-guide__partner_media.md
      press_release/summer-cooling-bedding-2026-guide__press_release.md
      press_release/summer-cooling-bedding-2026-guide__press_release.html
      magazine/summer-cooling-bedding-2026-guide__magazine.md
      magazine/summer-cooling-bedding-2026-guide__magazine.html
      aeko_shop/summer-cooling-bedding-2026-guide__aeko_shop.html
      aeko_shop/summer-cooling-bedding-2026-guide__aeko_shop.meta.json
      aeko_shop/summer-cooling-bedding-2026-guide__aeko_shop.md
      instagram/summer-cooling-bedding-2026-guide__instagram.md
      tiktok/summer-cooling-bedding-2026-guide__tiktok.md
      youtube/summer-cooling-bedding-2026-guide__youtube.md
```

Note the `press_release/` directory (NOT `보도자료/`) — that's the `filename_token` alias from §5.5.1.

The `aeko_shop/` channel is the only one that produces a **triple** (`.html` + `.meta.json` + `.md`). All other editorial channels produce a pair (`.md` + `.html`) or a single `.md`. There is no `.jsonld.json` file for any channel — editorial channels embed JSON-LD inside the `.html`, and aeko.shop regenerates structured data at render time.

#### 5.5.6 aeko_shop publish slug (meaningful English) — `aeko_shop` only

The §5.5.3 slug is romanized for **local file organization**. The **published aeko.shop URL** uses a *separate* slug carried in `<slug>.meta.json`'s top-level `slug` field. Do **NOT** reuse the romanized filename slug for the URL — for a Korean title it transliterates to phonetic gibberish (`eseutetig-mogongpaegeul-…`) that reads as noise to humans and AI engines. Instead, write a **meaningful English** slug:

1. **Translate the meaning, don't transliterate.** From the post topic/title, write a concise English slug: 3–8 words, lowercase, hyphen-joined, ASCII `[a-z0-9-]` only, drop stop-words (`a`/`the`/`of`/`for`/`in`/`to`/`은`/`는`…), ≤ 70 chars. Example: `에스테틱 모공팩을 집에서 — 팜스 테라비타 화산토 모공팩 콜모 구매 가이드` → `volcanic-clay-pore-pack-home-guide`.
2. **Use a brand/product's established Latin name** when it has one (e.g. the brand's official English spelling); translate the descriptive terms otherwise. Don't invent product names.
3. Write it to `.meta.json` `slug`. It MUST match `^[a-z0-9]+(?:-[a-z0-9]+)*$` (lowercase ASCII, hyphen-separated, no leading/trailing/double hyphens) — the backend rejects anything else with HTTP 422 at save/publish.
4. The aeko.shop backend uses this as the post's URL slug and enforces uniqueness (appends `-2`/`-3` on collision). If you omit `slug`, the backend falls back to an ASCII transliteration of the title — valid and routable, but less readable, so always supply a meaningful English slug for `aeko_shop`.

### 5.6 Channel recipes (loaded from `references/recipes/`)

Built-in addon channels use recipe files under `references/recipes/` when one exists; own-store and forensics-derived channels use their structural templates instead. References were loaded in §5.0; apply them now. Acceptance bullets in each recipe file ARE the §6.4 social-channel gates and the §6.2 prose-channel structural-target source.

| channel | recipe file | output |
| --- | --- | --- |
| `보도자료` | `references/recipes/보도자료.md` + `references/recipes/editorial-html-jsonld.md` | `.md` + `.html` |
| `magazine` | `references/recipes/magazine.md` + `references/recipes/editorial-html-jsonld.md` | `.md` + `.html` |
| `partner_media` | forensics template (3B.5) + `references/recipes/editorial-html-jsonld.md` | `.md` + `.html` |
| `aeko_shop` | `references/recipes/editorial-html-jsonld.md` (aeko_shop section — sanitizer-safe body HTML + product callout pattern + AEKO-media-CDN image rules; **no in-body JSON-LD** — the frontend regenerates Article + Product schemas from `PostUpsert` fields at render time) + 3B.5 forensics template for paragraph/heading targets | `.html` + `.meta.json` + `.md` (publish-ready triple) |
| `own_store_blog` | in-store crawl/tone signature (3B.4) + `references/examples/in-store-content-example.md` when present | `.md` |
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

The recipe enumerates the allow-list, the `<slug>.meta.json` field constraints, the product-callout pattern (`<figure role="callout" data-variant="product" data-product-source-id="…">`), the ID-space rules (`ProductRef.source_id`, not `id`), the body-image origin rule (AEKO media CDN only — the presign `public_url`; `settings.allowed_image_origins`), and the per-channel acceptance gates this skill enforces at §6.3.

Common content rules that apply to all four editorial channels (the recipe folds these in too; restating only what the executor needs to keep in mind at draft time):

- `inLanguage` / `locale` is a valid ISO-639-1 / BCP 47 code (`ko`, `en`, `en-US`). Defensively normalize: `"Korean"`/`"한국어"` → `ko`, `"English"`/`"영어"` → `en`; unrecognized → fall back to `ko` with a one-line warning.
- For the three editor-facing channels: if `frontmatter.canonical_url` is absent, omit the `<link rel="canonical">` tag — do not emit an empty `href`.
- For `aeko_shop`: every body `<img src>` is an AEKO-media-CDN URL (the presign `public_url`; never a hand-written `cdn.aeko.shop`) and every `<img>` carries `alt`/`width`/`height`/`loading`. §6.3 rejects the artifact otherwise.
- **Schema parity** (editor-facing channels only): if `structural_template_by_channel[channel]` carries observed JSON-LD `@type`s from cited sources, the artifact's emitted `@type` SHOULD be in the same family. Soft warning at §6, not a hard fail. `aeko_shop` has no in-body JSON-LD, so no parity check applies.

Authoring against this section without loading the recipe will produce sanitizer-invalid `aeko_shop` artifacts (full-document HTML, embedded JSON-LD, and `<h1>`/`<script>` all return HTTP 400). Load the recipe first.

## Step 6 — Citability self-check (per artifact)

Run per artifact before completion.

### 6.1 Universal hard gates (every channel)

These fail the artifact immediately — one fix iteration, then leave the item `pending`:

- **No image placeholders.** Zero occurrences of `[Image`, `[image`, `[Photo`, `[photo`, `[placeholder`, `[Placeholder`, or `TODO` in body text. Real markdown image syntax with a URL or path is allowed; `media_specs:` YAML is allowed (it's a distinct format).
- **Alt-text non-empty.** Every emitted image — Markdown `![alt](url)`, HTML `<img alt="…">`, `meta.json` `alt_text` / `media[].alt_text` fields, `media_specs.alt_text` YAML entries — MUST have non-empty alt. Scan for `![](`, `alt=""`, `alt_text: ""`, `alt_text: ''`, or unset `alt_text` on any media entry. Any match fails the artifact. Alt-text originates in §4-Form-2 (required at submit) or from `parsed_products[].short_description`/`.name` (for product callouts).
- **No invented URLs.** Every external URL in the artifact must appear in `cited_url_allowlist[]` — the union of: every cited `source_url` from 3A.1 (seeded into the allowlist at 3A.6), every URL passed to `aeko_crawl_url` in 3B.2 or 3B.4 (appended at 3B.6), every URL returned by `aeko_list_own_content` in 3A.4 (when surfaced as a draft reference), every URL in `media_by_channel{}` from §4-Form-2, plus any URL the user pasted into an `other:<name>` reference in §4-Form-1. Step 6's URL extractor scans the artifact for `https?://…` tokens and fails the artifact if any URL is not in the allowlist. Brand-internal anchor links (`#section`) and `mailto:` are exempt.
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
- Every `<img src>` in `.html` is an absolute `https://` URL that the skill obtained from a trusted provenance this run — i.e. a `public_url` returned by `aeko_request_media_upload` (uploaded media re-hosted on the AEKO media CDN). Hard gate. A brand-domain `parsed_products[].image_url` is **not** allowed in body HTML (the aeko-shop sanitizer rejects any origin outside `settings.allowed_image_origins` with HTTP 400) — it must be re-hosted via §5.4 or omitted from the body and shown only as a bottom product card. Do **not** hand-write `cdn.aeko.shop` or any host the presign did not return. (`hero_image_url` in `.meta.json` is exempt from the sanitizer origin rule — it is rendered by `next/image` — so a product hero on the brand's own https CDN is permitted there.)
- Every `<img>` carries `alt`, `width`, `height`, `loading` attributes. Hard gate.
- Zero `[image: …pending]` placeholder markers remain in `.md`, `.html`, or `.meta.json`. Hard gate. Upload failures should have been handled by omitting the failed image and producing a text-only draft, not by leaving placeholders.
- **ID-match gate.** Set of `data-product-source-id` values across all `<figure data-variant="product">` in `.html` equals the set of `featured_products[].product_source_id` values in `.meta.json`. Count + set match. Hard gate.
- Body contains zero `<figure data-variant="product">` callouts when `featured_products[]` is empty (no orphans). Hard gate.
- When `featured_products[]` has > 3 entries and the body has zero inline `<figure>` callouts: soft warning (body may be too short to incorporate all products inline; not every product needs an inline callout — bottom "Featured products" cards always render from `.meta.json`).
- **No schema parity check** for `aeko_shop` — the rendered page always emits `Article` from `aeko-shop-front/lib/structured-data.ts`; no in-body JSON-LD to check.

**Structured-data completeness gate (the AEO/GEO payload).** A post publishes to aeko.shop so AI engines cite it — the rendered page regenerates Article + Brand/Organization + Product JSON-LD from the publish fields, so an incomplete `.meta.json` ships a post that is live but not fully citable. Before saving the variation, verify and — when something is missing — surface a one-block "structured data" summary and ask the user whether to fix or proceed (soft gate; the backend re-checks the hard-required subset at save and returns 422 if `og_description` is absent or `hero_image_url` is malformed):
  - **Always (Article + Brand):** `title` non-empty; `og_description` non-empty (drives `<meta description>`, OG, and the `speakable` block — absent → speakable doesn't render); a brand kit resolved this run (`frontmatter.brand_kit_id` or `resolved_brand_kit_id`) so the page can emit the brand's Organization schema. `hero_image_url` is recommended (absolute https — presign `public_url` or a product image) for the Article `image`. **Brand-kit richness (warn, don't block):** the rendered Brand/Organization schema only carries `logo`/`sameAs`/`description` when the kit has `logo_url`/`primary_url`/`tagline` or `about_md` — if those are missing the Organization renders thin (a bare `{name, url}` adds little citation value), so warn the user to enrich the brand kit.
  - **When products are attached** (`parsed_products[]` non-empty / dashboard product-select): `featured_product_source_ids` is non-empty and every entry has a matching `featured_products[]` snapshot carrying `source_id`, `name`, `slug`, `outbound_url`, and `image_url` (Product schema basics + the clickable bottom card). For **complete `offers`** (price/availability — what shopping/AI engines cite), also include `price_minor`, `currency`, and `available`; warn (don't block) when they're absent, since `offers` is simply omitted then. Keep the inline-callout ↔ `featured_products` **ID-match** hard gate above.
  - If products were expected (Plan.md carried `products[]`) but `featured_products[]` came out empty, surface that explicitly — it usually means `source_id` didn't survive hydration; the post would publish Article-only with no product cards or Product schema.

Any HTML-side hard-gate failure → one fix iteration → leave `pending`.

### 6.4 Social channels (`instagram`, `tiktok`, `youtube`)

Substitute the recipe's "Acceptance gates" section in `references/recipes/<channel>.md` as the gates. The §6.1 universal hard gates still apply.

### 6.5 Iteration budget

Weak on a soft-warning dimension → iterate that artifact's affected section. Cap at **2 soft iterations per artifact**. Hard-gate failures get **1 fix iteration** before failing the artifact. If any artifact still fails its hard gates, leave the entire item `pending` (do NOT call `aeko_complete_action_item`) and surface which channels failed and which dimensions need work.

## Step 7 — Validate artifacts

Gate completion on the artifact set produced so far. The actual `aeko_complete_action_item` call moves into Step 7.5 so it's conditional on the backend-save outcome.

Only proceed past this step (i.e., into Step 7.5) if:
- ≥1 artifact written AND every written artifact passed its acceptance gates AND citability self-check passed for every artifact.

If the artifact set fails this gate → leave the item `pending` (do NOT enter Step 7.5; do NOT call `aeko_complete_action_item`) and surface which channels failed and which dimensions need work.

## Step 7.5 — Save publishable variations to backend

After Step 7's validation passes, save publishable variations to the AEKO backend so they can be published from another machine, by another flow, or later in time. This step also owns the `aeko_complete_action_item` call — completion is gated on the save outcome per the lifecycle locked in the plan.

### 7.5.1 Identify publishable artifacts

Build `publishable_artifacts[]` = subset of channels drafted in §5.3 whose destination slug is in `{aeko_shop, own_store_blog}`. Every other channel (`reddit`, `naver_blog`, `tistory`, `instagram`, `tiktok`, `youtube`, `보도자료`, `magazine`, `partner_media`, `other:<name>`) is local-only and not eligible for backend save.

**Auto-save required for `aeko_shop`.** Selecting `aeko_shop` in §4-Form-1 is the user's consent to save its backend variation after drafting succeeds. There is no Step 7.5 opt-out prompt for `aeko_shop`; deselecting the channel in §4-Form-1 is the local-only escape hatch. Without the backend variation, `/aeko-publish-content <item_id>` has nothing to publish.

If `publishable_artifacts` is empty → skip the save prompt. Call `aeko_complete_action_item` immediately (local-only completion is valid):

```
aeko_complete_action_item(
    item_id=frontmatter.item_id,
    artifact_summary="<N channels: reddit, naver_blog, 보도자료, instagram> · mimicked: <top 2 source patterns>",
    artifact_paths=[<absolute paths of every file written across all channels>],
    write_result=None,  # content artifacts never do store writes
)
```

Set `saved_variations = []` and proceed to Step 8.

### 7.5.2 Auto-save backend variations

If `publishable_artifacts` is non-empty, print one progress line before the first save:

- EN: `Saving <N> publishable variation(s) to AEKO backend for later publishing: <destinations>.`
- KO: `나중에 게시할 수 있도록 <N>개의 게시 가능한 변형본을 AEKO 백엔드에 저장합니다: <destinations>.`

For `aeko_shop`, this progress line is informational only — no prompt follows.

Iterate `publishable_artifacts[]`. For each:

```
metadata = <artifact.meta_json dict>
if destination == "aeko_shop":
    metadata = {
        **metadata,
        # Flat IDs drive aeko.shop post_products mapping.
        "featured_product_source_ids": [
            p.product_source_id for p in metadata.featured_products
        ],
        # Full snapshots let publish upsert missing aeko.shop products before
        # inserting the post. Source ID is still the join key; never use ProductRef.id
        # as product_source_id.
        "featured_products": [
            {
                "product_source_id": p.product_source_id,
                "source_id": p.product_source_id,
                "id": parsed_products_by_source[p.product_source_id].id,
                "slug": parsed_products_by_source[p.product_source_id].slug,
                "name": parsed_products_by_source[p.product_source_id].name,
                "sku": parsed_products_by_source[p.product_source_id].sku,
                "outbound_url": parsed_products_by_source[p.product_source_id].outbound_url,
                "image_url": parsed_products_by_source[p.product_source_id].image_url,
                "short_description": parsed_products_by_source[p.product_source_id].short_description,
                "display_order": p.display_order,
            }
            for p in metadata.featured_products
        ],
    }

# `featured_product_source_ids` is required for aeko_shop metadata but may be [].
# Text-only / product-free aeko_shop posts are valid when Plan.md has no products.
aeko_save_content_variation(
    item_id=frontmatter.item_id,
    destination=<"aeko_shop" or "own_store_blog">,
    title=<artifact.title>,
    body_html=<artifact.body_html or None>,  # populated for aeko_shop
    body_markdown=<artifact.body_markdown or None>,  # populated for own_store_blog (and aeko_shop's .md debug mirror)
    metadata=metadata,
    artifact_paths=[<absolute paths of this channel's files>],
)
```

For `aeko_shop`, `metadata.featured_product_source_ids` is required and may be an empty list. Product-free and text-only aeko.shop posts are valid. The richer `featured_products[]` snapshots are mandatory only when `.meta.json featured_products[]` is non-empty. Publish uses them to upsert the aeko.shop `products` table first, then the post publish maps `post_products` by `featured_product_source_ids`. If a product lacks `source_id`, drop it earlier per Step 1.1 and keep the draft product-free; do not fabricate a join key.

Collect the returned `variation_id`s into `saved_variations[]`.

**On ANY save failure mid-loop** (HTTP 4xx/5xx, MCP error, network failure):
- Do NOT call `aeko_complete_action_item`. Item stays in `pending`.
- Surface bilingual retry guidance and STOP — do not continue with remaining destinations:
  - EN: `⚠ Save failed for <destination>: <error>. Item left pending. Re-run /aeko-create-content <item_id> to retry.`
  - KO: `⚠ <destination> 저장 실패: <error>. 항목이 pending 상태로 남아 있어요. /aeko-create-content <item_id>를 다시 실행해 재시도해 주세요.`
- Skip Step 8 (no completion summary); skip Step 9 (no publish handoff).

**On ALL saves succeed**:

```
aeko_complete_action_item(
    item_id=frontmatter.item_id,
    artifact_summary="<N channels> · saved <K> backend variation(s): <destinations>",
    artifact_paths=[<absolute paths of every file written across all channels>],
    write_result={"backend_variations": saved_variations},  # records the variation_ids on the action item for audit
)
```

Print a one-line summary: `Saved <K> variation(s) to backend (destinations: <list>) | Failed: 0` so the outcome lands in the user transcript. Proceed to Step 8.

## Step 8 — User-facing summary

### 8.0 Channel label table (used in §8 + §9 + §4-Form-1)

Every channel reference in user-facing output uses the bilingual label — never a bare slug. Generic labels like `[Image #1]`, `Draft 1`, or `Output 3` are forbidden.

| channel_slug | Korean label | English label |
|---|---|---|
| `aeko_shop` | aeko.shop용 HTML | aeko.shop HTML |
| `naver_blog` | 네이버 블로그용 초안 | Naver Blog draft |
| `tistory` | 티스토리용 초안 | Tistory draft |
| `instagram` | Instagram용 캡션 | Instagram caption |
| `tiktok` | TikTok용 스크립트 | TikTok script |
| `youtube` | YouTube용 스크립트 | YouTube script |
| `magazine` | 매거진 기고용 | Magazine pitch |
| `보도자료` | 보도자료 초안 | Press release draft |
| `partner_media` | 파트너 미디어용 | Partner media draft |
| `reddit` | Reddit 포스트 초안 | Reddit post |
| `own_store_blog` | 자사몰 블로그 초안 | Own-store blog draft |
| `other:<name>` | `<name> 초안` | `<name> draft` |

For Korean target_language, lead with the KO label and pair the EN label after a slash. For EN target_language, lead with EN. Example: `aeko.shop용 HTML / aeko.shop HTML` (KO target) or `aeko.shop HTML / aeko.shop용 HTML` (EN target).

### 8.1 Summary block

```
✔ Content drafted across <N> channels: <comma list of Korean labels>
  Domain:        <domain>
  Action item:   <item_id>
  Title:         <resolved_title from Step 1>
  Mimicked:      <top 2-3 source domains + format patterns>
  Refs loaded:
    - Instagram용 캡션 / Instagram caption    → recipes/instagram.md + examples/instagram-post-example.md
    - 보도자료 초안 / Press release draft       → recipes/보도자료.md + recipes/editorial-html-jsonld.md
    - 네이버 블로그용 초안 / Naver Blog draft   → recipes/naver_blog.md + forensics template + examples/blog-example.md
    - 티스토리용 초안 / Tistory draft           → recipes/tistory.md + forensics template + examples/blog-example.md
    - Reddit 포스트 초안 / Reddit post           → forensics-derived (no recipe file)
    - …                                          (one line per channel; show "no exemplar" when example file absent)
  Artifacts:
    - Reddit 포스트 초안 / Reddit post          → ./aeko-artifacts/<domain_id>/<item_id>/reddit/<slug>__reddit.md
    - 네이버 블로그용 초안 / Naver Blog draft   → ./aeko-artifacts/<domain_id>/<item_id>/naver_blog/<slug>__naver_blog.md
    - 보도자료 초안 / Press release draft       → ./aeko-artifacts/<domain_id>/<item_id>/press_release/<slug>__press_release.md
    - Instagram용 캡션 / Instagram caption     → ./aeko-artifacts/<domain_id>/<item_id>/instagram/<slug>__instagram.md
  Media refs:    <N attached with alt-text, M skipped>
  Citability:    passed on N/N · failed on: <list of Korean labels or 'none'>
```

The **Refs loaded** block exists so users can verify their `references/examples/<file>.md` is being picked up — if a channel's line shows only `recipes/<channel>.md` and no `examples/...`, their exemplar isn't matching the filename pattern.

**Hard rule:** every artifact line uses the bilingual channel label from §8.0; never refer to drafts generically as "Draft 1", "Image #1", "Output 3", or by bare slug alone.

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

### 9.1 Print the publish-content line — conditional on Step 7.5 outcome

The handoff line is gated on `saved_variations` (set in Step 7.5), not on the drafted channel set alone. Publishing now reads from backend rows, not local files — if nothing was saved to backend, there's nothing for `/aeko-publish-content` to publish.

- **`saved_variations` includes an `aeko_shop` entry** — print the dedicated aeko.shop block FIRST (this is the most actionable handoff and must be unmissable):

  ```
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ▶ aeko.shop용 HTML / aeko.shop HTML
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  파일 / Files:
    - ./aeko-artifacts/<domain_id>/<item_id>/aeko_shop/<slug>__aeko_shop.html
    - ./aeko-artifacts/<domain_id>/<item_id>/aeko_shop/<slug>__aeko_shop.meta.json
    - ./aeko-artifacts/<domain_id>/<item_id>/aeko_shop/<slug>__aeko_shop.md

  구조 요약 / Structural summary:
    <N> H2 sections · <N> tables · <N> inline images · <N> chars body · hero: <cdn_url|null> · product callouts: <N>

  게시 명령어 / Publish command:
    /aeko-publish-content <item_id>

  ℹ 이 HTML이 aeko.shop으로 게시됩니다 / This HTML is what publishes to aeko.shop.
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ```

  Then add the non-aeko_shop tail underneath (when other destinations are also in `saved_variations`):

  ```
  Other saved variation(s): /aeko-publish-content <item_id> also handles:
    ↳ own_store_blog → creates an AEKO-owned draft row you push to your connected store later (never auto-pushed to Cafe24/Shopify).
  ```

  **Structural summary computation** — produce one scannable line covering: count of `<h2>` tags in the body HTML, count of `<table>` tags, count of `<figure>`/`<img>` inline image elements, character count of body text (HTML stripped), `hero_image_url` value from meta.json (or `null`), count of `<figure data-variant="product">` callouts in body HTML. Computed from the produced `<slug>__aeko_shop.html` + `<slug>__aeko_shop.meta.json`; do NOT include an inline raw-HTML preview (aeko_shop HTML is body-only and a 15-line preview adds context bloat without comprehension gain — the structural summary is more scannable, and the file path lets the user click through to the real HTML).

- **`saved_variations` non-empty but contains NO `aeko_shop` entry** (only `own_store_blog`) — skip the dedicated aeko.shop block and print only:

  ```
  Publish: /aeko-publish-content <item_id>
    ↳ publishes <K> saved backend variation(s) — destinations: <comma list>.
    ↳ own_store_blog → creates an AEKO-owned draft row you push to your connected store later (never auto-pushed to Cafe24/Shopify).
  ```

- **`publishable_artifacts` was empty** (no `aeko_shop` / `own_store_blog` channels were drafted) — omit the publish line entirely. The External-media publish checklist (§8) is the only post-creation guidance for those local-only channels.

- **Item is pending due to Step 7.5 save failure** — Step 8 / §9 are skipped entirely (already handled in §7.5.2); this branch never fires.

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
- All resolved prompts return no responses in 3A.1 (`latest` window) → `aeko_wait_cycles[]` populated; §3A.8 prints the wait-cycle section and (when selection_confidence drops to medium/low) offers the 3-option proceed prompt. User may still proceed Plan-only.
- `aeko_crawl_url` 4xx/5xx or unavailable (backend route not yet shipped) → record into `aeko_data_gaps[]` and log a single warning line in 3B.3 and at §4e (recrawl row in the enrichment summary marks the URL as `recrawled_failure`). Continue on the snapshot signal alone. Live recrawl is enriching, not gating. **Do NOT fall back to WebFetch** — WebFetch is only invoked via §3A.8 option 2 (explicit user opt-in).
- `aeko_list_own_content` 4xx/5xx or unavailable → record into `aeko_data_gaps[]`, log "no in-store signature — drafting from cited-source signal only" once, continue. In-store signature is enriching, not gating.
- §3A.8 user picks option 3 (abort) → stop without writing or completing; surface bilingual exit notice.
- §4-Form-1 returns 0 selected channels → stop without writing or completing.
- §4-Form-2 submit fails alt-text validation → form re-renders inline with "Alt text required for `<channel>` `<slot>`"; user fills missing alts and resubmits. No skill-level exit.
- Citability self-check hard-gate fails after the §6.5 iteration budget on any artifact → leave item `pending`; surface failed channels + dimensions.
- HTML emission fails on an editorial channel (markdown rendered, but JSON-LD won't validate) → write the `.md`, skip the `.html`, surface the JSON-LD error in the user summary, and treat the channel as failed for completion purposes.
- Non-interactive caller (e.g., dispatched from another agent): if `frontmatter.non_interactive == true` (forward-compat), skip §4-Form-1 and §4-Form-2 and default to: all auto-detected channels, no addons, no media. If 0 auto-detected, stop with "non-interactive run needs at least one auto-detected channel".

## What this skill never does

- Never writes to a connected store (PDP work is `/aeko-update-pdp`).
- Never publishes to external media automatically — always leaves local files only. (Publishing to **aeko.shop** is `/aeko-publish-content`'s job — this skill does not call it.)
- Never copies or uploads media for non-aeko_shop channels — only references URLs / paths the user supplies, plus the `media_specs:` YAML stubs when media was skipped. The `aeko_shop` channel is the **single exception**: §5.4 uploads supplied images to the AEKO media CDN via `aeko_request_media_upload` so the artifact is publish-ready.
- Never emits `[Image #N]` / `[Image]` / `[placeholder]` / `[photo]` / `TODO` markers in body text. Real markdown image syntax with a URL or path, or a `media_specs:` block — nothing else.
- Never fabricates the citation forensics; if tracked prompts have no responses for the `latest` window, surface as `low selection confidence` and let the user decide whether to proceed — never substitute research-prompt signal. Live `aeko_crawl_url` results never get faked when the backend is unavailable.
- Never copies text from cited sources verbatim; mimics format, not content. Cited-source `extracted_text` is for tone calibration only — never paste.
- Never invents URLs in artifacts — every URL must come from forensics, in-store content, live crawls, or user-supplied media.
- Never regenerates the Plan.md.
- Never reads machine values from prose.
- Never echoes raw frontmatter.
- Never proceeds past §4-Form-2 submit without an explicit user submit on both forms (except in non-interactive mode with a valid auto-detected channel set and no required alt-text gaps).
