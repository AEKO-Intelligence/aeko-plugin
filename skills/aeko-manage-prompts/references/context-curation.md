# Context curation

Use this mode to keep the Context library useful rather than append-only. Context is Pro+; a 403 is a tier
result, not an empty library.

## List

Resolve `domain_id`, then call `aeko_list_contexts(domain_id, scope=<optional>, kind=<optional>)`. Preserve
exact IDs and show title, `context_for_prompt`, scope/kind, product/category refs, source review, and the
available customer-state / concern / occasion / recipient / experience / effect facets.

## Create manually

Collect `title` plus an evidence-backed, non-empty `problem`; it is operationally required even though the
transport schema marks it optional. Prompt grounding reads `context_for_prompt` or falls back to `problem`,
and manual create cannot set `context_for_prompt`, so a facets-only Context would have an empty grounding
snapshot and fail when attached. Then collect only evidence-backed optional fields accepted by
`aeko_create_context`: `problem`,
`solution`, `outcome`, `customer_state`, `recent_concern`, `product_experience`, `felt_effect`, `occasion`,
`recipient`, `evidence`, `summary`, `kind`, `scope`, `category_ref`, `context_type`, `lang`,
`source_review_id`, `source_review_snapshot`, and `product_external_ref`. Show the proposed memory and get
explicit confirmation before `aeko_create_context(domain_id, title, ...)`. Never fabricate a review snapshot.

## Promote reviews in bulk

Resolve a real review integration and, when useful, call `aeko_list_review_products` first. Show the exact
filter: `domain_id`, `integration_id`, `min_context_score` (0–100, default 60), and optional `review_ids`.
After explicit confirmation call
`aeko_create_contexts_from_reviews(domain_id, integration_id, min_context_score, review_ids)` once. Report
created/promoted/skipped counts and partial errors verbatim.

## Update

Load the exact Context first. Ask which fields should change, then show a field-level before/after diff.
Omitted fields remain unchanged. In this skill, **ban `status` from every `aeko_update_context` call**;
`status=archived` must route to the Archive section and its typed gate. Also do not patch
`context_for_prompt`: the backend will not create that field on a Context that lacks it. Change the
evidence-backed `problem` and other supported source fields instead, and disclose that an already-materialized
`context_for_prompt` cannot be repaired through this PATCH surface. After explicit confirmation call
`aeko_update_context(context_id, ...)` with only the allowed changed fields. An empty patch is not a write.

## Archive

Archival removes the Context from active listings while keeping historical prompt references. Echo the exact
`context_id`, title, and affected grounding text, then require the user to type
`ARCHIVE <context_id>` exactly. Only then call `aeko_archive_context(context_id)`. Never treat an earlier
create/update confirmation as archive approval. Never archive in a schedule/routine/cron or without a
present user.

## Error paths

- 403 → surface the Context tier message; do not substitute uncurated memory.
- Missing or ambiguous ID → show the list and ask; never infer an ID from title alone.
- Update/archive 404 or ownership failure → stop and surface verbatim.
- Bulk review promotion partially succeeds → report applied rows; do not replay the full request blindly.
