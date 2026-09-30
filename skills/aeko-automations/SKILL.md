---
name: aeko-automations
description: >
  Guided setup and one-time runs for AEKO dashboard automation templates:
  Reviews to Contexts, Contexts to Ad Drafts, and Marketing Data to Low
  Performers. Use when a user asks to create or run one of these repeatable
  workflows; never publishes ads or enables a schedule.
allowed-tools: aeko_list_domains, aeko_list_automations, aeko_list_ad_accounts, aeko_list_campaigns, aeko_list_ad_groups, aeko_resolve_automation_contract, aeko_create_automation_instance, aeko_run_automation_instance, aeko_get_automation_run
---

# AEKO Automations

Help the user create a reusable manual workflow from one dashboard template, optionally run it once, and
report the actual run result. This is a guided customer workflow, not a general automation editor.

## Choose a template

Map the user's request to exactly one template:

| User goal | `automation_key` | What it does |
|---|---|---|
| Turn reviews into reusable customer context | `review_context_workflow` | Reviews selected source data and saves only context that passes review. |
| Draft ads from existing contexts | `review_based_ads` | Creates ad copy drafts and keeps the destination on hold for review. |
| Find low-performing ads from marketing data | `ad_performance_shortlist` | Builds a shortlist using the user's chosen CTR or CPC KPI. |

These templates require the **Pro** or **Enterprise** plan. If AEKO returns `FEATURE_LOCKED`, explain the
plan requirement and stop; do not route the user to another workflow to bypass it.

Do not route to a sales, ROAS, CPA, budget, publishing, or generic scheduler workflow. The low-performer
template currently supports **CTR** and **CPC** only. Ask which one the user wants when they have not
specified a KPI; never infer a revenue or sales objective.

## Discover and prepare

1. Resolve a domain with `aeko_list_domains` if the user has not given its exact `domain_id`. Never guess
   or select a domain by ordinal position. If there is no usable domain, stop and direct the user to add one
   in the AEKO dashboard.
2. Call `aeko_list_automations(domain_id)` and confirm the requested template is returned as available.
   Use the returned definitions and saved instances; do not assume an installed MCP server supports this
   skill just because the skill is present. If the user asks to run a saved workflow, select its exact
   `instance_id`, show its stored settings, and resolve those settings before running; do not create a copy.
   Before using the run tool, require the saved instance to be manual cadence and the basic model; for
   `review_based_ads`, also require destination policy `hold`. The resolver checks a fresh manual/basic
   template setup, so it does not replace checking those stored fields. If an existing instance is outside
   this contract, do not run it through this skill.
3. Collect required choices from the user and resolve human names against the read results. Get accounts
   from `aeko_list_ad_accounts(domain_id)`, campaigns from `aeko_list_campaigns(domain_id, ad_account_id)`,
   and groups from `aeko_list_ad_groups(campaign_id)`. Match the user's account/campaign/group description
   to returned names and use their exact IDs in params. If there is exactly one connected account or one
   group in the user-selected campaign, it is safe to use that unique result; otherwise ask the user to
   disambiguate by name. Do not ask for UUIDs or pick the first result from an ambiguous list.

   For `ad_performance_shortlist`, require an explicit CTR or CPC KPI plus an account and ad-group scope.
   Resolve the campaign as needed to list that group's parent; campaign ID is not a template parameter.
   The existing form defaults are percentile 20, minimum impressions 3,000, lookback 14 days, and minimum
   ad age 7 days. Use and announce those values unless the user asks to change them. The shortlist uses
   verified, current daily delivery reports and never changes ads; fewer than five eligible ads, a tied
   cutoff, or missing report coverage can produce an empty shortlist.

   For `review_based_ads`, require the intended account, target market, and target language. Use the
   user's workflow name as `ad_group_name` (minimum 3 characters), or the localized template title if no
   name was supplied, and show that choice in the summary. Keep the form defaults `filter.min_score: 80`,
   `filter.has_ads: false`, and `max_bid_micros: 500000`; explain them in ordinary language as a minimum
   context score of 80, contexts without existing ads, and the template's standard bid setting. Do not ask
   the user to enter a micros value. Use `campaign_id: null` and no product/date filters unless the user
   asks to narrow the source contexts. Propose the chat language as target language only when it is Korean,
   English, or Japanese, and show it for correction; otherwise ask.

   For `review_context_workflow`, product reference and review language are optional; keep them unset
   unless requested. Do not require a currently connected review integration: already-imported review rows
   can be eligible. Readiness validates setup and credits but does not promise eligible source rows, so say
   that a run can finish without new contexts if no unprocessed, classified reviews match.
4. Call `aeko_resolve_automation_contract(domain_id, automation_key, params)` with candidate inputs before
   creating or running anything. It returns compact JSON with `ready`, `reason_code`, `job_contract`, and
   `credits_remaining`; it validates setup but does not discover selectable IDs or create a row/run. If
   `ready` is false, explain the reason and ask for a correction. Do not silently replace an unavailable
   account, campaign, ad group, market, language, or KPI with another value.
5. Show a concise summary of the template, domain, selected inputs, expected output, manual cadence, and
   the resolved job contract. For ad drafts, say clearly that generated ads remain **on hold** and this
   workflow does not publish them. For a performance shortlist, state whether CTR or CPC will be used.

## Optional ad approach

For the ad-draft template, `params.creative_strategy` may be `context` (the
compatible default), `conversational`, or `auto`. Preserve the user's choice;
`auto` lets the existing generation call select an eligible pinned approach for
each item. It does not predict the best-performing ad. Do not overwrite an
explicit skill selection saved through the dashboard. Response-informed drafts
need the original response and comparison evidence intake in
`/aeko-create-ad-copy`; this automation does not accept that strategy or promise
response-level ad placement.

## Create and optionally run

Create when the user explicitly asks to save/create the workflow, or explicitly asks to run a new workflow
once. For an explicit one-time run request, the requested run authorizes creating its manual instance and
running it after you show the prepared summary; do not ask for another confirmation. If the user only asks
for options or a readiness check, stop before create.
Call `aeko_create_automation_instance(domain_id, automation_key, name, params)` once. The server forces a
manual cadence, the basic model class, and a hold destination for ad drafts; do not promise or request a
schedule or live ad action.

If creation returns an error or the response is ambiguous, do not call create again. The server may have
saved the workflow before the connection failed. Before create, retain the IDs from `instances` in the
latest `aeko_list_automations(domain_id)` result. Re-read the list and compare IDs; a candidate must be a
new instance with the exact automation key, workflow name, and params. If exactly one candidate matches,
report its ID. If the user explicitly requested a one-time run, continue that authorized request using the
candidate; otherwise ask whether they want to continue. If none or multiple candidates match, explain that
the save result is uncertain and direct the user to verify in the dashboard.

Run only when the user explicitly requests a one-time run or confirms that choice after seeing the prepared
summary. Reuse the exact saved `instance_id` selected above or returned by the successful create call, then call
`aeko_run_automation_instance(domain_id, instance_id, idempotency_key)` with one stable key for this
logical run attempt. If a run response is ambiguous or the call fails after dispatch may have occurred,
preserve that exact key and use it only to retry the same run request when the tool contract permits; never
mint a replacement key or create a second instance to get around an uncertain run. The MCP run tool does
not hide retries.

After an accepted run, poll `aeko_get_automation_run(domain_id, run_id)` until it reaches a terminal state
or the tool/runtime limit is reached. Treat `queued` and `running` as active, and use the returned
`finished_at` and `status` together; do not assume an unfamiliar status is terminal. Report the returned
status, outputs, warnings, and `partial_reason` when present. If the run status is `error` but the MCP
result contains no diagnostic reason, say the run failed and its error detail is not available in this
result; direct the user to the dashboard run record. If `items_truncated` is true, say the result list is
partial. Do not describe an accepted or running job as completed. Do not claim ads were published; the ad
draft workflow's destination is held.

If the user asks only to save a workflow, stop after the successful create and report its instance ID and
dashboard location. Do not start a run automatically.

## What this skill does not do

- Never enable schedules, change ad account state, publish ads, or make live campaign changes.
- Never use sales, ROAS, or CPA as a substitute KPI. Low-performer analysis accepts CTR or CPC only.
- Never create or run before resolving the live template contract and showing the user the selected inputs.
- Never duplicate an instance after an ambiguous create or retry a run with a new idempotency key.
- Never treat old instances or prior approvals as authorization for a new run.
