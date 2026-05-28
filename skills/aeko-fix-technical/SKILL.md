---
name: aeko-fix-technical
description: >
  Executor for Technical-tab items (`execution_class=technical_artifact`).
  Fetches a Plan.md, generates llms.txt / robots.txt patches / JSON-LD
  structured data / bundled technical fixes using embedded spec rules and
  Claude's reasoning — no prepare-* backend wrappers. Writes artifacts
  locally, surfaces a deploy checklist, marks the item complete.
argument-hint: "<item-id>"
allowed-tools: aeko_get_action_plan, aeko_get_brand_kit, aeko_get_brand_kit_by_id, aeko_list_brand_kits, aeko_get_domain_info, aeko_complete_action_item, Read, Write, WebFetch, WebSearch, Bash
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
- `tier_required` gate: compare against the resolved Brand Kit metadata (`aeko_get_brand_kit_by_id` when `brand_kit_id` is present, otherwise `aeko_get_brand_kit`); block if caller tier is below (bilingual tier-gate copy in §Copy).

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

- Resolve the Brand Kit in this order:
  1. If `frontmatter.brand_kit_id` is present and non-empty, call `aeko_get_brand_kit_by_id(frontmatter.brand_kit_id)` for the exact selected kit.
  2. Else fall back to `aeko_get_brand_kit(frontmatter.domain_id)` for older Plan.md files.
  3. If both miss, call `aeko_list_brand_kits(domain_id=frontmatter.domain_id)` for diagnostics, then stop with Brand-Kit-missing message and include any draft/generating/failed kit state shown by the list response.
- If `frontmatter.brand_kit_snapshot_version` is present and live version is newer → ask user whether to abort or proceed with snapshot. Default to asking.

## Step 3 — Dispatch by artifact_type

Each branch uses **embedded spec rules** loaded from `references/recipes/` instead of backend prepare-tools. Read the live brand kit (if requested) and domain info via `aeko_get_domain_info(domain_id)` for context.

### 3.0 Load references (per-artifact, on-demand)

Anthropic progressive-disclosure pattern — recipe detail loads only when its branch runs.

For the dispatched `frontmatter.artifact_type`:

| `artifact_type` | Recipe(s) to load |
| --- | --- |
| `llms_txt` | `references/recipes/llms-txt.md` |
| `robots_txt_patch` | `references/recipes/robots-txt-patch.md` |
| `json_ld` | `references/recipes/json-ld.md` |
| `technical_bundle` | All three of the above (per the prose's sub-artifact selection) |

Always load `references/recipes/deploy-checklist.md` before Step 4 — it's the source for the per-platform DEPLOY.md.

**Conditional loads** (silent skip if absent):
- `references/examples/<artifact_type>-*example*.{txt,json,md}` — brand-specific exemplar; mimic its conventions on top of recipe rules.
- `references/style/voice-overrides.md` — domain-scoped overrides (Korean section headings, glossary, deploy notes); filter to blocks where `domain: <frontmatter.domain_id>` matches.

**Precedence:** `voice-overrides` > `examples/*` > `recipes/*`. Recipe spec rules (llms.txt H1 line, robots.txt syntax, JSON-LD JSON validity) cannot be relaxed by examples — the skill fails the run if violated.

### 3a–3d. Apply

Apply the recipe loaded for the dispatched `artifact_type`:

- **`llms_txt`** → see `references/recipes/llms-txt.md`. Output: `llms.txt` in the item directory.
- **`robots_txt_patch`** → see `references/recipes/robots-txt-patch.md`. Output: `robots.txt.diff` + `robots.txt` in the item directory.
- **`json_ld`** → see `references/recipes/json-ld.md`. Output: `schema.json` in the item directory. Note: site-level / brand-level JSON-LD only; product-level lives in `/aeko-update-pdp`.
- **`technical_bundle`** → run the three branches above as the prose specifies. Each sub-artifact lands in the same item directory. Compose `./aeko-artifacts/<frontmatter.domain_id>/<frontmatter.item_id>/README.md` listing the sub-artifacts with deployment order. Acceptance gate for `sections_required`: each entry names a sub-artifact file. Missing file → iterate or fail.

Honor frontmatter `must_include` / `forbidden` / `sections_required` per each recipe's specifics.

## Step 4 — Deploy checklist (never auto-deploy)

For all technical artifact types, write a `DEPLOY.md` alongside the artifact. Source: `references/recipes/deploy-checklist.md` (loaded in §3.0). If `references/examples/deploy-notes-example.md` exists, append its contents after the recipe's per-platform section.

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
  Artifacts:       <paths>
  Refs loaded:     recipes/<artifact_type>.md + recipes/deploy-checklist.md
                   + examples/<artifact_type>-example.<ext>  (when present)
                   + style/voice-overrides.md  (when present, scoped to this domain)
  Self-validation: <pass summary>
  Deploy:          see DEPLOY.md in the same directory
  Next:            /aeko-action-center <domain_id> technical
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
