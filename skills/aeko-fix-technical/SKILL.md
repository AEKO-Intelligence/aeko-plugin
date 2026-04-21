---
name: aeko-fix-technical
description: >
  Executor for Technical-tab items (`execution_class=technical_artifact`).
  Fetches a Plan.md, generates llms.txt / robots.txt patches / JSON-LD
  structured data / bundled technical fixes using embedded spec rules and
  Claude's reasoning — no prepare-* backend wrappers. Writes artifacts
  locally, surfaces a deploy checklist, marks the item complete.
argument-hint: "<item-id>"
allowed-tools: aeko_get_action_plan, aeko_get_brand_kit, aeko_get_domain_info, aeko_complete_action_item, Read, Write, WebFetch, WebSearch, Bash
---

# AEKO Fix Technical

Executor for one Technical-tab item, end-to-end: fetch Plan.md → parse frontmatter + prose → validate contract → produce artifact using embedded spec rules → write locally → mark complete. No separate backend "prepare" tools — the skill is self-contained.

Contract reference: `docs/contracts/action-item-contract.md` §4 (guide.md / Plan.md format for technical items), §6 (completion).

## Input

- `item-id` (required) — `$1`. If missing, stop and point user to `/aeko-action-center <domain_id> technical`.

## Step 1 — Fetch and parse the Plan.md

Call `aeko_get_action_plan(item_id)`. The response is a single markdown string: YAML frontmatter between `---` fences + prose body. Parse both.

- `frontmatter` = YAML block between the opening `---` and the first following `---` alone on a line.
- `prose` = everything after the closing `---` (with leading blank line trimmed).

Dispatch is driven by `frontmatter`. Prose is narrative guidance only.

**Validate frontmatter:**

- `contract_version` starts with `2026-04-17.action.v1.` (technical items share the Plan.md contract in v0.5.0) — else stop.
- This skill is pinned to contract minor `v1.2`. Greater minor → print advisory (see §Copy) then proceed.
- `tab == "technical"` — else stop; redirect to `/aeko-update-pdp` or `/aeko-create-content` based on `execution_class`.
- `execution_class == "technical_artifact"` — else stop.
- `artifact_type ∈ {llms_txt, robots_txt_patch, json_ld, technical_bundle}` — else stop.
- `status ∈ {pending, ready}` — else stop with appropriate message.
- `tier_required` gate: compare against `aeko_get_brand_kit(...).metadata.account_tier`; block if caller tier is below (bilingual tier-gate copy in §Copy).

Print a plain-language header in `target_language` (default English if unsupported), then the prose body verbatim. Header format:

1. Action label — KO: "기술 수정 생성: `<artifact_type>` (`<deploy_mode>`)" / EN: "Generating technical fix: `<artifact_type>` (`<deploy_mode>`)"
2. Context: `domain_id`, `target_url` if present.
3. Sections: comma-joined `sections_required` if non-empty.

Never echo the raw frontmatter to the user.

### Copy templates (target_language)

- **Brand Kit missing** — KO: "이 기술 수정을 실행하려면 <domain>의 브랜드 키트가 필요합니다. `/aeko-brand-kit`을 먼저 실행해 주세요." / EN: "This technical fix needs a Brand Kit for <domain>. Run `/aeko-brand-kit` first."
- **Tier gate** — same template as `/aeko-update-pdp`.
- **Minor-version advisory** — KO: "이 가이드는 계약 v<plan_minor> 기준입니다. 현재 스킬은 v1.2 — `/plugin update aeko`." / EN: "This plan uses contract v<plan_minor>; this skill is on v1.2 — run `/plugin update aeko`."

## Step 2 — Stale brand-kit check (if used)

If `frontmatter.requires_brand_kit == true`:

- Call `aeko_get_brand_kit(frontmatter.domain_id)` for the live snapshot.
- If missing or empty → stop with Brand-Kit-missing message.
- If `frontmatter.brand_kit_snapshot_version` is present and live version is newer → ask user whether to abort or proceed with snapshot. Default to asking.

## Step 3 — Dispatch by artifact_type

Each branch uses **embedded spec rules** instead of backend prepare-tools. Read the live brand kit (if requested) and domain info via `aeko_get_domain_info(domain_id)` for context.

### 3a. `llms_txt`

**Spec rules (llmstxt.org):**
- First line: `# <site name>` (single H1).
- Optional blockquote summary on line 2-3.
- Subsequent sections are H2 headings with markdown lists of links. Each link line: `- [title](url): optional description`.
- Recommended sections: `## Docs`, `## Examples`, `## Optional`. Vertical-specific sections are fine (e.g. `## Products`, `## Guides`).
- Keep URLs absolute, prefer canonical origin.

**Generation:**
1. Pull domain context from `aeko_get_domain_info(frontmatter.domain_id)`. Gather: `base_url`, `brand_keywords`, any `key_pages` or `product_urls` the backend surfaces.
2. If the domain's key product pages aren't surfaced, do a light WebFetch on `base_url` to discover top navigation links. Do NOT crawl deeply — llms.txt is a hand-curated index, not a sitemap.
3. Compose the file following the spec. Honor `frontmatter.must_include` (every string must appear) and `frontmatter.forbidden` (none may appear). For `sections_required` — every entry maps to an H2 heading, case-insensitive trim match. Missing section → iterate or fail; do NOT call `aeko_complete_action_item`.
4. Write to `./aeko-artifacts/<frontmatter.domain_id>/<frontmatter.item_id>/llms.txt`.
5. **Self-validation:** check H1 present, sections are `## ` + list items, URLs parse. Record findings in completion summary.

### 3b. `robots_txt_patch`

**Spec rules (AI-crawler coverage for AEO):**
- The AI crawlers AEKO cares about: `GPTBot`, `ChatGPT-User`, `OAI-SearchBot`, `ClaudeBot`, `Claude-User`, `Google-Extended`, `PerplexityBot`, `PerplexityBot-User`, `Applebot-Extended`, `CCBot`, `Bytespider`.
- **Allow** these crawlers by default unless the merchant has explicit reason to block.
- Cafe24 hosting caveat: some Cafe24 plans auto-inject a restrictive `robots.txt` that blocks non-standard user agents. If the current file looks auto-generated (starts with `# Cafe24` or has a single `Disallow: /admin` block), advise the user that their robots.txt may need to be patched via the Cafe24 admin, not file upload.

**Generation:**
1. Resolve `site_base_url`:
   - Required per contract §4.2. If missing or malformed → stop with: "site_base_url not set on this item; backend must populate the site origin."
   - Derive `{site_base_url}/robots.txt`.
2. Fetch current robots.txt via `WebFetch`. On 404 or empty → treat as empty baseline (legitimate case).
3. On fetch failure (timeout, non-200, non-404) → ask user in `target_language`: "Couldn't read <url>. Paste your current robots.txt, or confirm the site has none."
4. Parse the current file into rule groups (User-agent + Allow/Disallow blocks).
5. Compute a patch that:
   - Adds `User-agent: <crawler>\nAllow: /` blocks for each AI crawler missing from the current file (unless a `Disallow: /` rule explicitly targets that crawler — in which case surface the conflict and ask the user).
   - Preserves all existing rules untouched.
   - Adds a single comment header above the new section: `# AEKO: AI crawler allowlist`.
6. Produce unified diff + final merged file. Honor `must_include` / `forbidden` / `sections_required` (each required section maps to a block with matching user-agent or comment-header label).
7. Write both to `./aeko-artifacts/<frontmatter.domain_id>/<frontmatter.item_id>/` as `robots.txt.diff` and `robots.txt`.

### 3c. `json_ld`

**Spec rules (schema.org + AEO):**
- `@context: "https://schema.org"` on every block.
- Common types: `Organization`, `WebSite`, `Product`, `FAQPage`, `BreadcrumbList`, `Article`, `BlogPosting`, `Review`, `AggregateRating`.
- Include `sameAs` on Organization when Wikipedia / Wikidata entity exists (use WebSearch to verify; don't fabricate).
- No trailing commas, no comments — valid JSON only.
- Script tag for embedding: `<script type="application/ld+json">...</script>`. `type` attribute exactly that string.
- For Korean brands, include Korean and English forms via `alternateName` or `@graph` split.

**Generation:**
1. Derive `schema_type` from prose + `frontmatter.validation_hints` (contract field for JSON-LD items).
2. For `Organization` / `Brand` schemas: run a targeted `WebSearch` for "<brand name> Wikipedia" and "<brand name> Wikidata". If confident match found, add the canonical URL to `sameAs[]`. If uncertain, omit `sameAs` rather than guess.
3. Pull brand fields from `aeko_get_brand_kit(domain_id)` (`brand_name`, `tagline`, `logo_url`, `brand_voice_summary`).
4. For Product schemas: the skill won't have StoreProducts data here — if `frontmatter.product_id` is present it's a pointer, not a payload. Surface the constraint and recommend the user run `/aeko-update-pdp <item_id>` instead for product-specific JSON-LD.
5. Emit pretty-printed JSON to `./aeko-artifacts/<frontmatter.domain_id>/<frontmatter.item_id>/schema.json`.
6. Acceptance gate for `sections_required`: each entry is a top-level JSON-LD property (e.g. `name`, `sameAs`, `brand.name` — dotted paths permitted). Missing key → iterate or fail.

### 3d. `technical_bundle`

- Run 3a-3c as the prose specifies. Each sub-artifact lands in the same item directory.
- Compose `./aeko-artifacts/<frontmatter.domain_id>/<frontmatter.item_id>/README.md` listing the sub-artifacts with deployment order.
- Acceptance gate for `sections_required`: each entry names a sub-artifact file. Missing file in directory → iterate or fail.

## Step 4 — Deploy checklist (never auto-deploy)

For all technical artifact types, write a `DEPLOY.md` alongside the artifact describing the manual deploy steps per platform:

- **llms.txt**: upload to site root. Cafe24: `/web/product/xxx` → upload via admin or FTP. Shopify: use a custom page at `/pages/llms-txt` + redirect from `/llms.txt` via theme.liquid (documentation link in the file). Plain hosting: drop in web root.
- **robots.txt**: upload to site root. Cafe24 restricted — warn user their admin may override.
- **JSON-LD**: inject into the target page's `<head>` via theme/template, OR add to a global include if the schema is Organization/WebSite.

**No deploy path is wired into the MCP for v0.5.0.** Always instruct manual deploy.

## Step 5 — Mark complete

```
aeko_complete_action_item(
    item_id=frontmatter.item_id,
    artifact_summary="<one-line: artifact_type + path(s) + deploy guidance included>",
    artifact_paths=[<absolute paths of every file written>],
    write_result=None,  # technical items don't do store writes
)
```

Only call complete if every acceptance-gate check passed AND all artifacts were written. If complete errors, leave item `pending` and surface the error verbatim.

## Step 6 — User-facing summary

```
✔ Technical item complete: <artifact_type>
  Artifacts: <paths>
  Self-validation: <pass summary>
  Deploy: see DEPLOY.md in the same directory
  Next: /aeko-action-center <domain_id> technical
```

## Error paths

- Plan endpoint unavailable → stop; suggest retry.
- Plan.md parse error → stop; surface exact parse failure + first 20 lines of response.
- Contract mismatch → stop; exact mismatch surfaced.
- Stale brand kit + user declines → stop; leave `pending`.
- Self-validation fails → do NOT call complete; write artifact anyway and tell user what to fix.
- `robots_txt_patch` with missing `site_base_url` → stop; backend data problem.

## What this skill never does

- Never writes to a connected store (no PDP, no product changes).
- Never handles Action-tab items (execution_class != `technical_artifact`).
- Never auto-deploys — always emits a `DEPLOY.md` checklist.
- Never regenerates the Plan.md; fetch once, follow it.
- Never reads machine values from prose — all machine values come from frontmatter.
- Never echoes the raw frontmatter block to the user.
- Never fabricates `sameAs` for JSON-LD; use WebSearch + user confirmation or omit.
