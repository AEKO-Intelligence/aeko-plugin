# Review-derived suggested prompts

Use this mode when the user wants shopper questions mined from real contextual reviews. Context Reviews and
review-derived suggestions are **Pro+**. A 403 on a Starter account is a tier result: explain the Pro+
requirement. Do not send that user to connect Crema/Judge.me as though a connector would change the tier,
and do not invent suggestions.

## Resolve the reviewed product

1. Resolve `domain_id` from the argument or `aeko_list_domains`.
2. Call `aeko_list_review_integrations(domain_id)` and let the user choose the exact `integration_id` when
   more than one exists.
3. Call `aeko_list_review_products(integration_id)` and show products with their raw and contextual-review
   counts. Select an exact `external_product_ref`; never guess from a broad category.
4. Call `aeko_get_suggested_prompts(integration_id, external_product_ref, limit=<1..50>)`.

Show a compact table containing row number, exact `suggestion_id`, exact `suggestion_hash`, prompt text,
source-review/context signals, and score when returned. Preserve the originating review Context relationship;
it is auto-attached when tracking.

## Track one

After the user selects one row, read allowed platform enums and selected markets through the universal
pre-flight, then ask which of those `ai_platforms`, `countries`, and optional real `view_id` to use. A view
requires a resolved domain and a real ID from `aeko_list_views(domain_id)`. Immediately before the write,
perform the universal quota pre-flight from `SKILL.md`; this one suggestion requests
`1 × platforms × countries × 1 review-Context` variants. Then call:

```text
aeko_track_suggested_prompt(
  integration_id=<integration_id>,
  suggestion_id=<exact suggestion_id>,
  ai_platforms=<selected permitted enum list>,
  countries=<selected account-market list>,
  view_id=<real saved-view id or omitted>,
)
```

Report every result row and summary field exactly, then perform the post-track reconciliation from
`SKILL.md`. HTTP 402 is quota; 403 is tier/authorization. A short count, failed row, or view assignment
failure is partial even when the first result succeeded.

## Track a reviewed set

Use batch tracking only after showing the exact review IDs/filter and receiving explicit selection. Ask for
`min_context_score` (0–100, default 60), optional `review_ids`, platforms, countries, and a real `view_id`.
The batch tool is integration-wide, not product-scoped, and the backend considers at most 500 reviews. Size
the conservative seed count as follows:

- explicit `review_ids`: number of unique IDs;
- no IDs and `min_context_score >= 60`: `min(500, sum(contextual-review counts))`;
- no IDs and `min_context_score < 60`: `min(500, sum(raw-review counts))`, because the contextual count only
  describes score >=60 and underestimates the widened filter.

Multiply that seed count by selected platforms and countries (one auto-attached review Context per seed).
If the upper bound exceeds remaining quota, require bounded explicit `review_ids`; do not hope the backend
will fit. Immediately before the call, repeat the complete universal pre-flight. Then call:

```text
aeko_track_suggested_prompts(
  integration_id=<integration_id>,
  min_context_score=<0..100>,
  review_ids=<selected ids or omitted>,
  ai_platforms=<selected permitted enum list>,
  countries=<selected account-market list>,
  view_id=<real saved-view id or omitted>,
)
```

The tool tracks the top review-derived prompt for each review in the filtered set. Do not describe it as
tracking every suggestion. Report tracked, associated, reactivated, already-tracked, and failed rows
separately when returned. Compare the backend's `requested`, `tracked`, `already_tracked`, `failed`,
`skipped_no_suggestion`, and `view_assignment_failed` with the conservative seed count, then run the fresh
tracked-list reconciliation. A skipped review is not a tracked prompt.

## Dismiss one suggestion

Dismissal hides a suggestion; it does not untrack an already-tracked prompt. Echo the exact prompt and
`suggestion_hash`, ask for a separate confirmation, then call
`aeko_dismiss_suggested_prompt(integration_id, suggestion_hash)`. Never use `suggestion_id` in the hash slot.

## Error paths

- Starter/feature 403 → explain that this mode is Pro+; do not prescribe a connector as the fix.
- Pro+ with no review integration → explain that review suggestions need a connected review source; stop.
- No contextual-review products or no suggestions → say so and stop without writing.
- Product/ref mismatch → return to the product list; never guess.
- Quota full → do not call either tracking tool; offer review/untrack mode. A quota block is HTTP 402.
- Partial batch failure → list already-applied results before the error and do not retry the whole batch.
