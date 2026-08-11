---
name: aeko-manage-prompts
description: >
  Discovers, tracks, reviews, organizes, and untracks AEKO prompts; manages
  saved views and Context memories; and handles review-derived suggested
  prompts. Use for prompt quota, tracking changes, review-suggested questions,
  saved views, or Context curation. Writes require explicit selection and gates.
argument-hint: "[mode=discover|review|suggested|contexts] [domain-id]"
allowed-tools: aeko_list_domains, aeko_get_domain_info, aeko_search_research_prompts, aeko_track_prompt, aeko_get_tracked_prompts, aeko_get_quota, aeko_list_contexts, aeko_create_context, aeko_update_context, aeko_archive_context, aeko_create_contexts_from_reviews, aeko_list_views, aeko_create_view, aeko_add_prompts_to_view, aeko_untrack_prompt, aeko_list_review_integrations, aeko_list_review_products, aeko_get_suggested_prompts, aeko_track_suggested_prompt, aeko_track_suggested_prompts, aeko_dismiss_suggested_prompt
---

# AEKO Manage Prompts

Own the complete prompt lifecycle without weakening destructive gates. Explain tracked prompts as questions
AEKO re-asks to AI engines; explain Contexts as curated, source-backed grounding memories.

Language: mirror the user's chat language for headings, questions, confirmations, and summaries. Keep IDs,
prompt text, platform/country values, schema keys, slash commands, and tool names in English/ASCII. The brand
mark is always `AEKO`.

## Select one mode

- `mode=discover` — research-library discovery, explicit selection, quota check, and tracking. Read
  `references/discover-track.md` completely.
- `mode=review` — quota/list segmentation, saved-view organization, and typed-confirmation untracking. Read
  `references/review-untrack.md` completely.
- `mode=suggested` — review-derived prompt suggestions, individual/batch tracking, or dismissal. Read
  `references/review-suggestions.md` completely.
- `mode=contexts` — list, create, update, archive, or promote review Contexts. Read
  `references/context-curation.md` completely.

Infer the mode from an explicit verb such as find, track, untrack, suggestion, dismiss, view, or Context.
If intent spans modes, show the four choices and ask where to begin. Complete one mode before offering the
next; never bundle multiple writes behind one confirmation.

## Universal tracking pre-flight

Immediately before **every** call that starts tracking—`aeko_track_prompt`,
`aeko_track_suggested_prompt`, or `aeko_track_suggested_prompts`—call `aeko_get_quota` and compare the
selected fan-out/batch size with remaining capacity. If quota is unavailable, call
`aeko_get_tracked_prompts` for a fallback count and state that the backend still enforces the hard cap.
Never reuse an earlier quota snapshot for a later write. Narrow the selection before the call when it
would exceed the returned cap.

## Destructive isolation

Untracking has its own typed gate and never inherits a discovery confirmation. Echo exact IDs and prompt
text, then require the user to type `UNTRACK <N>` where `<N>` is the displayed count. A plain yes, an earlier
selection, or approval of another operation is insufficient. Historical responses and citations remain;
only future refresh stops.

Context archival likewise gets a separate exact-ID confirmation defined in its reference. Suggested-prompt
dismissal gets its own preview and confirmation and must not be bundled with tracking.

