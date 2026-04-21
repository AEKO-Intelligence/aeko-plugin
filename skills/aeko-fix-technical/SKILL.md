---
name: aeko-fix-technical
description: >
  Executor for Technical-tab items. Fetches a guide.md for one item
  (llms.txt, robots.txt patch, site-level JSON-LD, or technical bundle),
  generates the artifact locally, optionally deploys when the guide says
  so, and marks the item complete. Enforces execution_class=technical_artifact.
argument-hint: "<item-id>"
allowed-tools: aeko_get_technical_guide, aeko_prepare_llms_txt, aeko_validate_llms_txt, aeko_prepare_robots_txt_fix, aeko_prepare_json_ld, aeko_check_brand_entity, aeko_complete_action_item, aeko_get_brand_kit, Read, Write, WebFetch
---

# AEKO Fix Technical

Executes one Technical-tab item end-to-end: fetch guide.md → parse frontmatter + prose → validate contract → produce artifact → optional deploy → mark complete.

The required MCP tools are registered on the hosted AEKO MCP server. Do NOT run a separate tool-availability check before starting — just call the tool; if the server returns an error, surface it verbatim. Only the explicit error cases at the end of this skill cause an abort.

Contract reference: `docs/contracts/action-item-contract.md` §4 (guide.md format), §6 (completion).

## Input

- `item-id` (required) — `$1`. If missing, stop and tell the user how to get one (`/aeko-action-center <domain_id> technical`).

## Step 1 — Fetch and parse the guide.md

Call `aeko_get_technical_guide(item_id)`. The response is a single markdown string: YAML frontmatter between `---` fences, followed by a Sonnet-authored prose body. Parse both.

- `frontmatter` = YAML block between the opening `---` and the first following `---` alone on a line.
- `prose` = everything after the closing `---` (with the leading blank line trimmed).

All dispatch decisions are driven by `frontmatter`. Prose is narrative guidance only.

Validate frontmatter before proceeding:
- `contract_version` starts with `2026-04-17.technical.v1.` — else stop, report mismatch. (Gate on major only; minor bumps are additive and must not break the skill.)
- This skill is pinned to contract minor `v1.1`. If the incoming guide's minor is strictly greater, print the minor-version advisory (see §Copy) above the header, then proceed (forward-compat per §11.1).
- `tab == "technical"` — else stop with mismatch.
- `execution_class == "technical_artifact"` — else stop, tell user this item belongs in `aeko-run-action`.
- `artifact_type` ∈ {`llms_txt`, `robots_txt_patch`, `json_ld`, `technical_bundle`} — else stop.
- `status ∈ {pending, ready}` — executable states per contract §1. Prose is now templated server-side at create time, so new rows land in `ready` directly; `pending` remains valid for legacy rows. If an older row is encountered with `status == "generating_prose"`, render the backend's 409 body verbatim and stop. If `completed` / `failed` / `dismissed`, stop with the appropriate message.
- `tier_required` gate: if present AND caller tier is known AND caller tier is below `tier_required` → stop with the bilingual tier-gate message (see §Copy). Caller tier is resolved from `aeko_get_brand_kit(...).metadata.account_tier`; unresolved → proceed with backend as authoritative gate.

Print a plain-language header in `target_language` (fall back per §3.1 of the contract), then the prose body verbatim. Header format (3 lines):
1. Action label — KO: "<artifact_type>를 생성합니다 (`<deploy_mode>`)" / EN: "Generating <artifact_type> (`<deploy_mode>`)." Translate `llms_txt` → "llms.txt", `robots_txt_patch` → "robots.txt 패치" / "robots.txt patch", `json_ld` → "JSON-LD 구조화 데이터" / "JSON-LD structured data", `technical_bundle` → "기술 번들" / "technical bundle".
2. Context line: `domain_id`, `target_url` (if present).
3. Sections line: comma-joined `sections_required`, if non-empty.

After the header, print a blank line, then the full `prose` body verbatim. Never print the raw frontmatter block.

### Copy (user-facing message templates)

- **Brand Kit missing** (Step 2) — KO: "이 기술 수정을 실행하려면 <domain>의 브랜드 키트가 필요합니다. 브랜드 키트는 톤·샘플 문구·라이팅 가이드를 담아 일관된 목소리를 만들어 줍니다. `/aeko-brand-kit`를 먼저 실행해 설정한 뒤 다시 시도해 주세요." / EN: "This technical fix needs a Brand Kit for <domain>. A Brand Kit captures your tone and writing guidelines so every future output stays consistent. Run `/aeko-brand-kit` to set it up, then re-run this command."

- **Tier gate** — same template and tier-benefit lookup as `aeko-run-action` §Copy (see `skills/aeko-run-action/SKILL.md`).

- **Minor-version advisory** — KO: "이 기술 수정은 계약 v<guide_minor> 기준입니다. 현재 스킬은 v1.1 — `/plugin update aeko`로 업데이트해 주세요." / EN: "This guide uses contract v<guide_minor>; this skill is pinned to v1.1 — run `/plugin update aeko`."

## Step 2 — Stale brand-kit check (if kit used)

If `frontmatter.requires_brand_kit == true`:
- Call `aeko_get_brand_kit(frontmatter.domain_id)` for the live snapshot.
- If the live Brand Kit is missing or empty (first-time user with no kit), stop with the Brand-Kit-missing message from §Copy (rendered in `target_language`). Do NOT phrase this as a contract breach.
- Otherwise, if `frontmatter.brand_kit_snapshot_version` is missing, log it to the completion payload's `artifact_summary` and proceed using the live kit. Do not surface as a user-facing warning.
- If `frontmatter.brand_kit_snapshot_version` is present and the live `snapshot_version` is newer → tell the user in `target_language` and ask whether to abort or proceed with the snapshot. Default to asking; do NOT silently use a stale snapshot.

## Step 3 — Branch on artifact_type

### 3a. `llms_txt`
- Call `aeko_prepare_llms_txt(frontmatter.domain_id)` to pull the domain-aware brief (product list, key pages, brand entity).
- Follow `prose` (narrative) + hard rules from frontmatter: `must_include` (every string MUST appear), `forbidden` (none MAY appear). Acceptance gate for `sections_required`: every entry MUST map to a top-level or sub-heading in the llms.txt. Missing section → iterate or fail.
- Write to `./aeko-artifacts/<frontmatter.domain_id>/<frontmatter.item_id>/llms.txt`.
- **Validation:** `aeko_validate_llms_txt` fetches over HTTP and does not accept local files. So:
  - If `frontmatter.deploy_mode == "artifact_only"` → skip remote validation. Do an inline content-shape check instead: confirm top-level H1 present, each section is a valid markdown list, and URLs parse. Record findings in the completion summary.
  - If `frontmatter.deploy_mode == "deploy_if_supported"` → deploy first, then call `aeko_validate_llms_txt(url=<published-url>)`. Abort completion if validation fails.

### 3b. `robots_txt_patch`
- `aeko_prepare_robots_txt_fix` requires the current robots body as an input; it does not fetch from a URL for you. Sourcing `current_robots_txt`:
  1. `frontmatter.site_base_url` is required for this artifact type per contract §4.2. If missing OR it doesn't parse as a URL (`https?://host[/]`), stop with: "site_base_url not set or malformed on this item — backend must populate a valid site origin before this fix can run." Do NOT fall back to `target_url` (may be a specific page path, not the site root). Do NOT ask the user to paste a URL; this is a backend data problem.
  2. Derive `{frontmatter.site_base_url}/robots.txt`. Fetch with `WebFetch`.
  3. If fetch succeeds → use the body as `current_robots_txt`.
  4. If fetch fails (404, timeout, non-200) → the site URL is correct but the file itself may legitimately not exist or be paywalled. Ask the user in `target_language`: "Couldn't read <url>. Paste your current robots.txt content, or confirm the site has none (empty is fine)." Accept empty string.
- Call `aeko_prepare_robots_txt_fix(domain_id=frontmatter.domain_id, current_robots_txt=<resolved text>)`.
- Produce a unified diff + the final merged robots.txt.
- Write both to `./aeko-artifacts/<frontmatter.domain_id>/<frontmatter.item_id>/` as `robots.txt.diff` and `robots.txt`.
- Acceptance gate for `sections_required`: for robots.txt, each entry is a logical rule group name (e.g. "AI crawlers", "default allowlist"). Every entry MUST appear in the merged file either as a block comment header (`# <name>`) or as a labeled group in the diff rationale. Missing section → iterate or fail.

### 3c. `json_ld`
- Call `aeko_prepare_json_ld(frontmatter.domain_id, schema_type=<derived from prose + frontmatter.validation_hints>, page_url=frontmatter.target_url)`.
- Validate brand entity via `aeko_check_brand_entity(brand_name, brand_name_en)` if the schema is Organization or Brand; reflect findings in `sameAs`.
- Write `./aeko-artifacts/<frontmatter.domain_id>/<frontmatter.item_id>/schema.json` — pretty-printed.
- Acceptance gate for `sections_required`: each entry is a top-level JSON-LD property name (e.g. `name`, `sameAs`, `brand`). Every entry MUST be a present, non-empty key in the emitted JSON (dotted paths like `brand.name` permitted). Missing key → iterate or fail.

### 3d. `technical_bundle`
- Combination: run 3a–3c as the prose specifies. Each sub-artifact lands in the same item directory; compose a `README.md` listing them.
- Acceptance gate for `sections_required`: each entry names a sub-artifact (e.g. `llms.txt`, `robots.txt`, `schema.json`). Every entry MUST correspond to a file written to the item directory and listed in the `README.md` index. Missing sub-artifact → iterate or fail.

## Step 4 — Optional deploy

If `frontmatter.deploy_mode == "deploy_if_supported"` AND the target platform supports it (llms.txt → upload, robots.txt → PR/CDN update, JSON-LD → site injection):
- Deploy using whatever platform-specific path the prose instructs. For v1 the backend does NOT expose a technical-deploy tool for every platform; if no deploy path is wired, treat as `artifact_only` and tell the user to copy the file to their site.

If `frontmatter.deploy_mode == "artifact_only"`: just leave the artifact on disk.

## Step 5 — Mark complete

Build the completion payload:

```python
aeko_complete_action_item(
    item_id=frontmatter.item_id,
    artifact_summary="<one-line summary of what was produced + whether deployed>",
    artifact_paths=[<absolute path(s) to artifact file(s)>],
    write_result=None,   # technical items don't do store writes
)
```

Only call complete if:
- At least one artifact was written to disk successfully
- Validation (if any) passed

If complete() returns an error, leave the item `pending` and surface the error.

## Step 6 — User-facing summary

Print:

```
✔ Technical item complete: <artifact_type>
  Artifact(s): <paths>
  Validation:  <pass/fail summary>
  Deployed:    <yes|no + where>
  Next:        <next pending technical item command, if any>
```

## Error paths

- Guide endpoint unavailable → stop; advise to try later.
- guide.md frontmatter fails to parse (no opening `---`, YAML syntax error, missing required key) → stop; surface the exact parse error and the first 20 lines of the response for debugging.
- Contract mismatch → stop; surface exact mismatch.
- Stale brand kit and user declines → stop; leave item pending.
- Validation fails → do not mark complete; write artifact anyway and tell user what to fix.

## What this skill never does

- Never writes to the store (no PDP, no product changes).
- Never handles Action-tab items. If `frontmatter.execution_class != "technical_artifact"`, stop.
- Never regenerates the guide. Fetch once; follow it.
- Never reads a machine value from the prose body. If a value is needed, it must come from `frontmatter`. Prose is narrative only.
- Never echoes the raw frontmatter block to the user in chat. Print a short human-friendly header (Step 1) and the prose body only. The full guide.md is available if the user explicitly asks for it.
