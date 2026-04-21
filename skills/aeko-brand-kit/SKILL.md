---
name: aeko-brand-kit
description: >
  View and edit the Brand Kit for an AEKO domain — brand name, tagline,
  tone_of_voice, brand_voice_summary, target_audience, primary_color,
  logo_url, sample_urls, must_include, forbidden. Surfaces the current
  snapshot_version + updated_at so users can see freshness. `snapshot_version`
  bumps on semantic changes (voice / target_audience / must_include /
  forbidden) but not on cosmetic edits.
argument-hint: "[domain-id] [view|edit]"
allowed-tools: aeko_get_brand_kit, aeko_update_brand_kit, aeko_get_domain_info, aeko_list_domains
---

# AEKO Brand Kit

Manages the live Brand Kit consumed by Plan.md and guide.md generation. The live kit is the source of truth; Plan.md snapshots point back at a `snapshot_version`. Every edit here bumps the version — downstream `aeko-run-action` / `aeko-fix-technical` runs will warn if their plan is older than the live kit.

Contract reference: `docs/contracts/action-item-contract.md` (`AekoBrandKit`, `AekoBrandKitUpdate`).

## Inputs

- `domain-id` (optional) — UUID. If omitted, Step 1 auto-resolves or prompts.
- mode (optional, default `view`):
  - `view` — print the full kit with version + updated_at
  - `edit` — interactive edit of one or more fields

## Step 1 — Resolve the domain

The user usually does NOT know their domain UUID. Never demand it cold.

1. If `$1` is a valid UUID → use it; skip to Step 2.
2. If `$1` looks like a domain name (e.g. `aeko.ai`, `slound.co.kr`), call `aeko_list_domains` and pick the row whose `base_url` matches (case-insensitive substring match). If no match, fall through to 3.
3. If `$1` is missing or unresolvable, call `aeko_list_domains`:
   - **Zero domains** → tell the user to connect a domain in the AEKO dashboard (`https://aeko-intelligence.com`) and stop.
   - **Exactly one domain** → auto-select it; echo back `Using <name> (<base_url>)` so the user sees what was picked.
   - **Multiple domains** → show the rendered list verbatim and ask the user to paste the UUID (or the brand name) back.

Only call `aeko_get_domain_info` when you already have a UUID and want to confirm metadata. Do NOT use it for discovery — it can't list domains.

## Step 2 — Read the live kit

Call `aeko_get_brand_kit(domain_id)`. The tool returns a pre-formatted markdown block; pass it through verbatim. Capture the `Kit ID` line (renders as `- **Kit ID**: \`<uuid>\``) into a local variable — Step 5 needs it to PATCH.

Backend-exposed fields (source: `api/schemas/brand_kits.py::BrandKitResponse`):

- Identity: `brand_name`, `tagline`, `logo_url`, `primary_color`
- Voice: `tone_of_voice`, `brand_voice_summary`, `target_audience`
- Guardrails: `must_include` (phrases to always use), `forbidden` (phrases to never use), `sample_urls` (reference pages for voice grounding)
- Account: `metadata.account_tier`, `metadata.billing_url` (drives tier-gate copy in other skills)
- Versioning: `snapshot_version` (bumps only on semantic changes — voice/target_audience/must_include/forbidden), `updated_at`, `status` (active / draft / generating / failed)

Fields that are null/empty show as `(unset)` in the formatter — never hide missing fields; missing fields are what the user should consider filling in. Voice fields (`tone_of_voice` + `brand_voice_summary`) are the highest-leverage — they feed `aeko-run-action` and `aeko-fix-technical` at execution time.

## Step 3 — If mode is `view`, stop here.

Offer follow-ups at the bottom of the output:
- "Run `/aeko-brand-kit <domain_id> edit` to change fields."
- "Run `/competitive-research <brand_or_competitor>` to research a competitor you're considering adding to the kit's `forbidden` / reference copy."

## Step 4 — If mode is `edit`, gather changes

Ask which fields the user wants to change. Accept multiple at once. Every field on `BrandKitUpdate` is optional and PATCH-style — omitted fields are preserved server-side. Editable fields:

- Scalars: `name`, `status` (only `active` or `draft` allowed from the client — `generating` / `failed` are system-controlled), `brand_name`, `tagline`, `tone_of_voice`, `brand_voice_summary`, `target_audience`, `primary_color` (hex `#rgb` or `#rrggbb`), `logo_url` (absolute URL).
- Lists: `sample_urls`, `must_include`, `forbidden`.

For list fields (`sample_urls`, `must_include`, `forbidden`):
- Ask whether the user wants to REPLACE the list or APPEND.
- Replace → send the full new list.
- Append → reuse the current list from Step 2's render, concat, send the full merged list. (Backend does not support append-patch; do the merge client-side.)

Validate before sending:
- `logo_url` — must be an absolute URL. If missing scheme, prepend `https://`.
- `primary_color` — must match `^#(?:[0-9a-fA-F]{3}){1,2}$`; reject otherwise.
- `sample_urls` — must all be URLs; drop invalid entries with a warning.
- `must_include` / `forbidden` — strip whitespace, de-duplicate case-insensitively, cap each entry at 200 chars.
- `status` — only `active` or `draft` from the client.

## Step 5 — Write the patch

Use the `kit_id` captured in Step 2 and call `aeko_update_brand_kit(kit_id=<uuid>, <field>=<value>, ...)`. The tool accepts the editable fields as named kwargs (see Step 4's list). Server returns the full updated kit, formatted.

Semantic vs cosmetic note: `snapshot_version` only bumps when a SEMANTIC field changes (`brand_voice_summary`, `tone_of_voice`, `target_audience`, `must_include`, `forbidden`). Cosmetic edits (`name`, `tagline`, `logo_url`, `primary_color`, `brand_name`, `sample_urls`) preserve the snapshot so downstream plans don't show a false stale-kit warning.

Show a short diff-style summary:

```
Updated Brand Kit — <domain_id>
Snapshot version: <old> → <new>   (or "unchanged — cosmetic edit")
Changed: tone_of_voice, must_include (+2), forbidden (replaced)
```

Then re-print the relevant updated sections (not the whole kit unless asked).

## Step 6 — Reference-research launch

If the user added `sample_urls` or wants to expand reference material, offer:
- `/competitive-research "<brand_or_competitor>"`
so they can deep-dive a reference brand before adding its URL to the kit.

## Error paths

- `aeko_get_brand_kit` returns not-found → suggest the domain may not be provisioned; show domain info via `aeko_get_domain_info`.
- `aeko_update_brand_kit` returns 4xx with a field error → print the field + reason; do not re-send blindly.
- Backend stub (tool unavailable) → tell the user the Brand Kit endpoints aren't wired yet; stop.

## What this skill never does

- Never calls `aeko_get_action_plan` / `aeko_get_technical_guide`.
- Never calls `aeko_complete_action_item` or any store-write tool.
- Never generates artifacts. Brand Kit editing only.
