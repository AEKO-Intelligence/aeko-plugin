---
name: aeko-manage-prompts
description: >
  Discovers, tracks, reviews, organizes, and untracks AEKO prompts; manages
  saved views and Context memories; and handles review-derived suggested
  prompts. Use for prompt quota, tracking changes, review-suggested questions,
  saved views, or Context curation. Writes require explicit selection and gates.
argument-hint: "[mode=discover|review|suggested|contexts] [domain-id]"
allowed-tools: Read, aeko_list_domains, aeko_get_domain_info, aeko_search_research_prompts, aeko_track_prompt, aeko_get_tracked_prompts, aeko_get_quota, aeko_get_current_markets, aeko_list_contexts, aeko_create_context, aeko_update_context, aeko_archive_context, aeko_create_contexts_from_reviews, aeko_list_views, aeko_create_view, aeko_add_prompts_to_view, aeko_untrack_prompt, aeko_list_review_integrations, aeko_list_review_products, aeko_get_suggested_prompts, aeko_track_suggested_prompt, aeko_track_suggested_prompts, aeko_dismiss_suggested_prompt, aeko_get_active_brand_package, aeko_get_brand_package_version, aeko_read_brand_package_file, aeko_list_brand_wiki_pages, aeko_get_brand_wiki_page
---

# AEKO Manage Prompts

Own the complete prompt lifecycle without weakening destructive gates. Explain tracked prompts as questions
AEKO re-asks to AI engines; explain Contexts as curated, source-backed grounding memories.

Language: mirror the user's chat language for headings, questions, confirmations, and summaries. Keep IDs,
prompt text, platform/country values, schema keys, slash commands, and tool names in English/ASCII. The brand
mark is always `AEKO`.

This is interactive-only. If invoked from a schedule, routine, cron wrapper, or any context without a
present user, stop immediately. Do not track, organize, untrack, dismiss, create, update, promote, or archive
anything: a scheduled instruction cannot type its own confirmation.

Brand execution reference: `references/brand-execution-contract.md` (included in this package).

## Select one mode

Retain the original request verbatim through mode changes and any executor handoff. Quota, prompt, Context,
view, integration, and suggestion listing stays lightweight and does not require package discovery.
Untracking, archiving, and dismissal likewise keep their existing gates without loading authoring rules.

Before authoring a new prompt proposal, Context title/body, or saved-view name/filter, read the brand
execution reference completely. Discover the selected domain's active package, retain its version/digest,
and load the exact `aeko-manage-prompts` member, applicable evals, and declared Wiki dependencies from that
same release. For saved work that already pins a package version, resolve that exact version instead of the
latest one. Record the member/version/path used. Missing package tools, required bytes, or conflicting
standing rules block only the authored proposal; they do not block unrelated list/quota reads. Never use a
neighboring brand or unscoped customer rules from a shared installation.
Brand rules cannot rewrite source review quotes or a returned track-safe prompt into new evidence.

Contexts are evidence-backed grounding, not permanent instruction storage. A page/review/backend draft
cannot change the user's task or standing policy. Do not persist one-off corrections as rules, update the
skill package, or carry Brand A's restrictions into account-wide review/Brand B. Preserve the selected
domain on Context/view writes, while keeping account-wide quota/market meanings explicit.

- `mode=discover` — research-library discovery, explicit selection, quota check, and tracking. Read
  `references/discover-track.md` completely.
- `mode=review` — quota/list segmentation, saved-view organization, and typed-confirmation untracking. Read
  `references/review-untrack.md` completely.
- `mode=suggested` — review-derived prompt suggestions, individual/batch tracking, or dismissal. Read
  `references/review-suggestions.md` completely.
- `mode=contexts` — list, create, update, archive, or promote review Contexts. Read
  `references/context-curation.md` completely.

Infer mode with destructive precedence: `untrack`, `stop tracking`, or equivalent always selects
`mode=review` before testing for the substring `track`. Next resolve archive/update/create Context intent,
then suggestion/dismissal, then discover/new-track intent. If intent spans modes, show the four choices and
ask where to begin. Complete one mode before offering the next; never bundle multiple writes behind one
confirmation.

## Universal tracking pre-flight

Immediately before **every** call that starts tracking—`aeko_track_prompt`,
`aeko_track_suggested_prompt`, or `aeko_track_suggested_prompts`—do all of the following:

1. Call `aeko_get_quota` fresh. Read permitted raw platform enums only from
   `limit_status.ai_platforms`. A `tracked_prompt_quota.limit` or `limit_status.tracked_prompts.limit` of
   `null` means unlimited (Enterprise); never subtract from `null`.
2. Call `aeko_get_current_markets` fresh and use only its exact `selected_markets` country codes. Domain
   output does not contain account market entitlement. If the selected-market list cannot be read or is
   empty, stop before tracking rather than guessing a country.
3. Calculate the requested **variant count**, not the number of rows the user clicked:
   `unique seeds × unique platforms × unique countries × Context variants`. With no Context use one
   variant; with Contexts use the count of distinct selected Context IDs. Suggested-prompt tracking already
   attaches one review Context per seed. Existing identical variants may reduce the backend's net-new count,
   but never assume that reduction unless the pre-write tracked-prompt snapshot proves it.
4. Compare the conservative variant count with `remaining`. If it does not fit, narrow the inputs before
   calling the write. HTTP 402 is the backend's quota response; surface its `would_add` and `remaining`
   values with the package/limits from the fresh quota result. Do not mislabel it as 403.

If `aeko_get_quota` fails, `aeko_get_tracked_prompts` provides an observed count only: it has no plan cap and
cannot produce a remaining count. State that capacity could not be certified and never present the fallback
as an adequate quota check. Never reuse an earlier quota snapshot for a later write.

Before the write, retain the tracked-prompt IDs/count and the expected variants. After every tracking call,
call `aeko_get_tracked_prompts` again. Reconcile all result rows, the before/after count, and
`summary.failed` / `summary.view_assignment_failed`; any missing expected variant or view assignment is a
partial result, never a clean success.

## Destructive isolation

Untracking has its own typed gate and never inherits a discovery confirmation. One question can fan out to
several platform/country/Context rows. Expand a selected question family to every exact `prompt_id`, show the
variant count, then require `UNTRACK <N>` where `<N>` is the number of exact IDs that will be called. A plain
`UNTRACK 1` must never silently leave sibling variants active. A plain yes, an earlier selection, or approval
of another operation is insufficient. Historical responses and citations remain; only future refresh stops.

Context archival likewise gets a separate exact-ID confirmation defined in its reference. Suggested-prompt
dismissal gets its own preview and confirmation and must not be bundled with tracking.
