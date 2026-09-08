# Review, organize, and untrack prompts

Use this when the user wants to review, organize, or stop tracking prompts already in AEKO.

Language: mirror the user's chat language for user-facing explanations, confirmations, and summaries. Keep tool names, IDs, and schema keys in English/ASCII.

## Safety

- Never untrack a prompt without explicit user confirmation.
- Never infer prompt IDs from prose when the user gave ambiguous labels. Show the list again and ask for exact IDs or row numbers.
- Untracking preserves historical responses and citations; it only stops future refreshes.
- Discovery and new tracking use `/aeko-manage-prompts mode=discover`; never carry its permissive selection
  into this mode's destructive gate.
- If there is no present user, stop before any untrack call. A routine cannot supply `UNTRACK <N>` for the
  user.

## Step 1 - Resolve optional domain

If `$1` is set, keep it as `domain_id`. Domain is optional for account-wide prompt review because
`aeko_get_tracked_prompts` lists the account's tracked prompts. A domain is **required** for saved-view or
Context operations: if the user requests either and no domain is known, call `aeko_list_domains` and have
them choose before calling `aeko_list_views` or `aeko_create_view`.

## Step 2 - Quota snapshot

Call `aeko_get_quota`.

Report:
- tracked count
- plan cap
- remaining slots
- package/tier if present

If the returned limit is `null`, report unlimited. If quota is unavailable, continue with
`aeko_get_tracked_prompts`, but label its count as an observation only: that tool exposes no cap, so no
remaining value can be calculated.

## Step 3 - Pull prompts and angle catalogs

Call `aeko_get_tracked_prompts`.

If `domain_id` is known, also call:
- `aeko_list_contexts(domain_id=domain_id)`
- `aeko_list_views(domain_id=domain_id)`

Use those catalogs only to make IDs human-readable. The tracked-prompt list is authoritative.

## Step 4 - Segment the list

Render a compact grouped view. Prefer these groups in order when the data exists:

1. Context: `context_title` / `context_id`
2. Platform + country
3. Funnel stage + query type
4. Tags

Do not group or label a row by `view_id`: `aeko_get_tracked_prompts` does not emit that field. A separate
`aeko_list_views(domain_id)` result is a catalog, not proof of prompt membership.

Show a table with:

```
| # | prompt_id | Prompt | Platform | Country | Context | Status |
|---|-----------|--------|----------|---------|---------|--------|
```

Keep prompt text to about 80 characters. Include exact `prompt_id` values in monospace.

Also group identical full question text into a **question family** only for selection convenience. Under
each family show every platform/country/Context variant and its exact `prompt_id`. Do not collapse the IDs:
the backend untracks one variant row per call.

## Step 5 - Ask for action

Ask what the user wants to do:

- Review only
- Untrack selected prompts
- Find new prompts to fill quota
- Create a saved view or add existing prompts to one

If they choose "find new prompts", route to `/aeko-manage-prompts mode=discover`.

### Saved-view operations

- To create a view, collect `name` plus optional `product_label`, `description`, `scope`, and exact existing
  `prompt_ids`. Show the proposed grouping and confirm before
  `aeko_create_view(domain_id, name, product_label, description, scope, prompt_ids)`.
- To add prompts to an existing view, resolve a real ID from `aeko_list_views`, echo the exact prompt IDs,
  confirm the non-destructive organization change, then call
  `aeko_add_prompts_to_view(view_id, prompt_ids)`. An empty list is not a write.

## Step 6 - Untrack selected prompts

When the user selects prompts to untrack:

1. Resolve row numbers or a selected question family to exact `prompt_id` values from the displayed table.
   If a family has three platform/country variants, expand it to three IDs; never interpret "untrack 1" as
   permission to leave two hidden sibling variants running.
2. Echo every exact prompt ID, platform, country, Context (when present), and first 80 characters. State the
   number of **variant rows** that will stop.
3. Require the user to type `UNTRACK <N>` exactly, where `<N>` is that expanded exact-ID count. Do not
   accept yes, approval of the displayed list, or any confirmation from discovery/view operations.
4. Only after the exact typed confirmation, call `aeko_untrack_prompt(prompt_id)` once per selected prompt.

Stop on backend 403/404 and surface the backend message.

## Step 7 - Summary

Print:

```
Untracked N variant row(s) across M question family/families.

Still tracking: <count if known>
Remaining quota: <remaining if known>

Historical response and citation data is preserved.
```

Count only successful calls. If any call fails, list the variants still active; do not claim the whole
question family was untracked. If nothing changed, say so plainly.
