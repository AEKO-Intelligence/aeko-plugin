---
name: aeko-openai-guardrails
description: >
  Interactive, account-gated AEKO workflow for OpenAI Ads pacing rules. Anchors
  thresholds on observed merchant data, creates rules disabled, requires a
  successful blast-radius preview before arming, safely edits enabled rules by
  disarming first, and confirm-gates both directions of the account-wide switch.
  Bounded by hourly reporting; entity resume is always a separate server-gated action.
argument-hint: "[domain-id]"
allowed-tools: aeko_list_domains, aeko_list_campaigns, aeko_list_ad_groups, aeko_list_ads, aeko_get_ad_insights, aeko_list_ad_rules, aeko_get_ad_rule, aeko_get_ad_rule_capabilities, aeko_validate_ad_rule, aeko_create_ad_rule, aeko_update_ad_rule, aeko_delete_ad_rule, aeko_preview_ad_rule, aeko_set_ad_rule_enabled, aeko_set_ad_automation_enabled, aeko_list_ad_rule_executions, aeko_list_ad_rule_runs
---

# AEKO OpenAI Guardrails

Set up or manage rules that automatically pause OpenAI Ads entities when merchant-defined pacing or cost
limits are crossed. This skill never operates Meta, TikTok, or Google Ads.

If invoked from a schedule, routine, cron wrapper, or any context without a present user, stop immediately:

```text
/aeko-openai-guardrails is interactive only. Run it in a foreground conversation so every live rule,
automation-switch, edit, and delete decision is visible and explicitly confirmed.
```

This stop applies to `aeko_set_ad_rule_enabled` in both directions,
`aeko_set_ad_automation_enabled` in both directions, `aeko_update_ad_rule`, and `aeko_delete_ad_rule`.
Never let a wrapper, thread reply, config value, delegated skill, or the skill's own preview text stand in for
a present user's reply.

## Honesty contract

- OpenAI Ads reporting is roughly hourly. Never promise real-time or sub-hourly protection.
- A triggered rule pauses entities; it never resumes them. Restarting spend is a separate flow in
  `/aeko-openai-budget-shift`, whose real backend gate is `confirm_active=True`. Invoking that skill is not
  itself approval: it must run interactively, re-fetch state, show the exact IDs, and obtain fresh human
  confirmation before the server-gated resume call.
- The account-wide switch is not inherently safe in either direction. `enabled=False` removes all automated
  pacing protection; `enabled=True` resumes evaluation of every individually enabled rule.
- No conversion/ROAS rules: the backend can observe spend, CPM, and CPC, not conversion revenue.
- CPM/CPC rules use `rolling_24h` or `daily`; only cumulative spend may use `last_n_hours`.
- The confirmation phrases in this file are **instruction-level gates only**. They are not sent to or
  validated by the backend. `aeko_set_ad_automation_enabled` accepts only `domain_id` and `enabled`;
  `aeko_update_ad_rule` has no confirmation field. `aeko_set_ad_rule_enabled` accepts
  `acknowledge_broad_match`, but that acknowledges only a broad latest preview—it is not proof of general
  human confirmation. The backend's broad-match check consults the latest successful account preview and
  accepts no preview run ID, so it is not a complete rule-specific gate. This skill therefore requires its
  own immediate exact-rule preview, saved-definition check, and matching counts; concurrent or unknown
  preview state means re-preview and never guess the acknowledgement. The backend does enforce one useful
  invariant: a newly created rule is always disabled.

Mirror the user's language for explanations and confirmations. Keep IDs/tool names ASCII. Convert micros to
the account currency for display.

## Step 0 — resolve the domain and current automation state

Resolve `$1` through `aeko_list_domains`, then call `aeko_get_ad_rule_capabilities(domain_id)` and
`aeko_list_ad_rules(domain_id, include_disabled=True)`. Build all menus from current capabilities, not fixed
assumptions. Retain the account-wide switch state and every rule's exact ID, enabled state, version, scope,
conditions, guards, cooldown, daily cap, and per-run cap.

## Global switch — both directions require the same class of gate

Handle a global stop/restart request before rule setup. For either direction:

1. Re-fetch all rules and show every individually enabled rule, its scope, and what changing the global
   switch means. Explain that existing paused entities do not change state.
2. Show the direction-specific risk:
   - stopping removes every rule's runaway-spend protection;
   - restarting resumes every individually enabled rule.
3. Require the exact fresh phrase in the current foreground turn:
   - stop EN: `DISABLE ALL AD AUTOMATION`
   - stop KO: `모든 광고 자동화 끄기`
   - restart EN: `ENABLE ALL AD AUTOMATION`
   - restart KO: `모든 광고 자동화 다시 켜기`
4. Any ambiguity, missing turn, or non-interactive context means no call. Only the exact phrase permits one
   `aeko_set_ad_automation_enabled(domain_id=<domain_id>, enabled=<False|True>)` call.
5. Read the tool result and report success only when the backend confirms it. End the run after this path.

The text request is not authorization by itself. Both phrases are instruction-level only because the tool
has no confirmation parameter; state that limitation in the risk block.

## Step 1 — anchor thresholds on merchant numbers

1. Show similar existing rules first so the merchant can edit instead of stacking duplicates.
2. Pull account insights over about 14 days and campaign insights by exact campaign ID.
3. Compute typical daily/hourly spend, CPM, and CPC. Present the baselines in account currency.
4. Explain proposed multiples: for example, an hourly spend threshold at 2–3× normal or daily CPM around
   2× trailing average. If history is thin, use only a spend cap the merchant explicitly states; never guess
   CPM/CPC.

## Step 2 — construct only supported definitions

Use `aeko_get_ad_rule_capabilities` for the metric × window × scope matrix. Resolve entity names through the
campaign/ad-group/ad list tools. Never approximate ROAS, conversion, unsupported action, or one-hour CPM/CPC
with a different rule.

## Step 3 — validate and create disabled

Call `aeko_validate_ad_rule` on the complete definition. Surface every correction instead of silently
widening scope or weakening intent. After validation, `aeko_create_ad_rule` may create the draft: the backend
always persists new rules as disabled. Tell the merchant nothing can pause until the separate preview and
enable flow succeeds.

Creation is still a state write, so the foreground-only gate applies; however it cannot arm a rule.

## Step 4 — successful preview is an arming precondition

Before every `aeko_set_ad_rule_enabled(rule_id, enabled=True)` call:

1. Fetch the saved rule and retain its exact ID/version/definition.
2. Call `aeko_preview_ad_rule(rule_id=<rule_id>)` in this run.
3. Require a successful response for that exact saved rule with `dry_run=true`, `run_id`, `data_through_hour`,
   `target_count`, `matched_count`, and matched entities. An error, missing field, partial result, stale
   response, or preview-rate-limit failure blocks arming.
4. Fetch the rule again. If its version/definition changed after preview, discard the preview and restart.
5. Show the complete blast-radius table with exact IDs, current metric, threshold, target count, matched
   count, data-through hour, and warnings.

```text
If armed right now, this rule would pause:
Entity / exact ID                Current      Threshold    Status
Campaign "Summer KR" / <id>      ₩6.1k/hr     ₩4.0k/hr     WOULD PAUSE
Campaign "Brand US" / <id>       ₩1.2k/hr     ₩4.0k/hr     ok
```

If the preview matches most of the account, recommend correcting the rule. Never interpret a failed preview
as zero matches. No successful current preview means no enable call.

## Step 5 — arm only after the preview and fresh confirmation

After Step 4, require the merchant to confirm the exact rule ID/version and displayed blast radius in the
current foreground turn with EN `ENABLE RULE <rule_id> VERSION <version>` or the natural KO equivalent that
retains the exact ASCII ID/version. Record no durable approval token—the backend accepts none. Then call
`aeko_set_ad_rule_enabled(rule_id, enabled=True, acknowledge_broad_match=False)` exactly once.

If the backend returns `MARKETING_RULE_BROAD_MATCH_ACK_REQUIRED`, do not retry from the error alone. Require
that its counts correspond to the successful current preview; otherwise re-fetch and re-preview. Show the
broad match again and obtain a second fresh confirmation naming the exact rule/counts. Only that permits the
re-call with `acknowledge_broad_match=True`. Use EN
`ACKNOWLEDGE BROAD MATCH <rule_id> <matched_count>/<target_count>` or the natural KO equivalent retaining
those exact ASCII values. Never pass it on the first attempt or from model judgment.

If global automation is off, enabling the rule only makes it ready; do not turn the global switch on as a
side effect. Global restart uses its separate Step 0 gate.

## Managing existing rules

Every mutation below is foreground-only and requires an exact before/after display plus a fresh reply.

### Update an enabled rule — disarm before editing

An enabled rule edit is a live re-arm because the backend leaves it enabled and clears per-entity rule state.
This resets cooldown tracking and can immediately re-pause entities. Never call `aeko_update_ad_rule` on an
enabled rule.

1. Fetch the exact current rule and merge the requested patch locally into a full create-shaped definition.
2. Validate that complete proposed definition, then preview it **before any mutation** with
   `aeko_preview_ad_rule(rule=<full proposed definition>)`.
3. Require the same successful-preview fields as Step 4. Show old → proposed definition, old/new blast radius,
   and the cooldown-state-reset risk.
4. Obtain the fresh phrase `DISARM AND UPDATE RULE <rule_id>` or the natural KO equivalent retaining the
   exact ID. This confirmation is instruction-level; `aeko_update_ad_rule` has no confirmation parameter.
5. Call `aeko_set_ad_rule_enabled(rule_id, enabled=False)` and verify disabled. Then call
   `aeko_update_ad_rule(rule_id, <exact approved patch>)` once. If update fails, leave the rule disabled.
6. Fetch and verify the saved disabled definition. Run a new successful saved-rule preview.
7. Re-enabling is a separate armed-state transition: show that new preview and require a second fresh
   confirmation through Step 5. Without it, leave the edited rule disabled.

This sequence moves the gate to the armed state; it does not trust a post-update preview after a live edit.

### Update a disabled rule

Fetch, merge, validate, and preview the full proposed definition; show the exact diff and state reset. Require
`UPDATE DISABLED RULE <rule_id>` or the natural KO equivalent retaining the exact ID before
`aeko_update_ad_rule`. Verify the saved rule remains disabled. Enabling later still requires Steps 4–5.

### Disable one rule

Disabling removes a protection and therefore is not auto-safe. Show the rule, its scope, recent executions,
and the consequence; require `DISABLE RULE <rule_id>` or the natural KO equivalent retaining the exact ID before
`aeko_set_ad_rule_enabled(rule_id, enabled=False)`. No thread/config text substitutes for that reply.

### Delete one rule

Show that delete soft-deletes and disables the rule while retaining audit history. Prefer disable when the
merchant may reuse it. Require `DELETE RULE <rule_id>` or the natural KO equivalent retaining the exact ID before
`aeko_delete_ad_rule`; the backend accepts no confirmation token.

## “What did automation do while I was away?”

- `aeko_list_ad_rule_executions(domain_id, rule_id=...)` shows actions, exact entities, metric values, and
  errors.
- `aeko_list_ad_rule_runs(domain_id)` shows evaluation history, including runs where nothing fired.

If the merchant wants paused spend restarted, explain that this skill never restarts it. Route to the
foreground `/aeko-openai-budget-shift` flow and cite its server-enforced `confirm_active=True` parameter, not
a generic claim that a person will handle it.

## Error paths

- No account/campaigns: stop; nothing to guard.
- No history: skip CPM/CPC and offer only a merchant-stated spend cap.
- Validation/create/update rejection: surface it; never silently widen scope or weaken guards.
- Preview failure, partial response, missing counts, or version drift: do not enable or update an enabled
  rule. Re-preview only after the cause is resolved.
- A disarm succeeds but update/re-preview fails: leave the rule disabled and report the exact state.
- Global switch failure: do not claim the direction changed and never compensate by toggling rules.
- Any mutating result is ambiguous: stop, report uncertainty, and do not retry automatically.

## What this skill never does

- Never mutates rules or the global switch unattended.
- Never treats its confirmation phrases as backend-enforced; they are instruction-level gates.
- Never calls `aeko_update_ad_rule` while the rule is enabled.
- Never enables without a successful current saved-rule preview and fresh foreground confirmation.
- Never passes `acknowledge_broad_match=True` without the distinct re-confirmation after matching counts.
- Never assumes disabling a rule or all automation is harmless.
- Never invents thresholds, conversion/ROAS rules, or faster-than-hourly reaction.
- Never resumes paused entities; the separate resume surface enforces `confirm_active=True`.
