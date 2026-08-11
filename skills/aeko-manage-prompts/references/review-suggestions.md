# Review-derived suggested prompts

Use this mode when the user wants shopper questions mined from real contextual reviews. Context Reviews are
AEKO-account features; surface a backend 403 verbatim and do not invent suggestions.

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

After the user selects one row, ask which supported `ai_platforms`, `countries`, and optional real `view_id`
to use. Immediately before the write, perform the universal quota pre-flight from `SKILL.md`; then call:

```text
aeko_track_suggested_prompt(
  integration_id=<integration_id>,
  suggestion_id=<exact suggestion_id>,
  ai_platforms=<selected list or omitted>,
  countries=<selected list or omitted>,
  view_id=<real saved-view id or omitted>,
)
```

Report the backend status exactly. On a cap/403, stop and say how many writes, if any, succeeded.

## Track a reviewed set

Use batch tracking only after showing the exact review IDs/filter and receiving explicit selection. Ask for
`min_context_score` (0–100, default 60), optional `review_ids`, platforms, countries, and a real `view_id`.
The batch tool is integration-wide, not product-scoped. If `review_ids` is omitted, sum the contextual-review
counts returned by `aeko_list_review_products` and use that integration-wide total as the conservative maximum
batch size; if it exceeds remaining quota, require a bounded explicit `review_ids` selection instead of hoping
the backend will fit. Immediately before the call, perform the universal quota pre-flight and ensure this
maximum selected review count fits the remaining slots. Then call:

```text
aeko_track_suggested_prompts(
  integration_id=<integration_id>,
  min_context_score=<0..100>,
  review_ids=<selected ids or omitted>,
  ai_platforms=<selected list or omitted>,
  countries=<selected list or omitted>,
  view_id=<real saved-view id or omitted>,
)
```

The tool tracks the top review-derived prompt for each review in the filtered set. Do not describe it as
tracking every suggestion. Report tracked, associated, reactivated, already-tracked, and failed rows
separately when returned.

## Dismiss one suggestion

Dismissal hides a suggestion; it does not untrack an already-tracked prompt. Echo the exact prompt and
`suggestion_hash`, ask for a separate confirmation, then call
`aeko_dismiss_suggested_prompt(integration_id, suggestion_hash)`. Never use `suggestion_id` in the hash slot.

## Error paths

- No review integration → explain that review suggestions need a connected review source; stop.
- No contextual-review products or no suggestions → say so and stop without writing.
- Product/ref mismatch → return to the product list; never guess.
- Quota full → do not call either tracking tool; offer review/untrack mode.
- Partial batch failure → list already-applied results before the error and do not retry the whole batch.
