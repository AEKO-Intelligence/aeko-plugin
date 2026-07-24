---
name: aeko-ad-guardrails
description: >
  Set up an automated pacing rule for OpenAI Ads that pauses campaigns, ad groups,
  or ads when spend runs too fast or CPM/CPC crosses a threshold. Anchors every
  threshold on the merchant's own observed numbers, creates the rule disabled,
  previews exactly what would pause right now, and arms it only after explicit
  confirmation. Bounded by OpenAI's hourly reporting data; pausing is automatic,
  resuming is always manual.
argument-hint: "[domain-id]"
allowed-tools: aeko_list_domains, aeko_list_campaigns, aeko_list_ad_groups, aeko_list_ads, aeko_get_ad_insights, aeko_list_ad_rules, aeko_get_ad_rule, aeko_get_ad_rule_capabilities, aeko_validate_ad_rule, aeko_create_ad_rule, aeko_update_ad_rule, aeko_delete_ad_rule, aeko_preview_ad_rule, aeko_set_ad_rule_enabled, aeko_list_ad_rule_executions, aeko_list_ad_rule_runs
---

# AEKO Ad Guardrails

Set up a rule that watches your OpenAI Ads spend and pauses things automatically when a limit is
crossed — so a runaway campaign can't burn through budget overnight. **An armed rule pauses real
campaigns**, so this skill is deliberately slow to arm one: thresholds come from the merchant's own
numbers, the rule is created disabled, and it goes live only after the merchant sees exactly what it
would pause and says yes.

## Honesty contract (read first, repeat to the user)

- **Reaction time is bounded by OpenAI's reporting.** Ad metrics arrive with roughly hourly
  freshness. A rule reacts within about an hour of the data showing a breach — not the second it
  happens. Never promise real-time or sub-hourly protection.
- **Pause is automatic; resume is manual.** A triggered rule pauses the matched entities and stops
  there. Nothing un-pauses automatically — the merchant restarts spend themselves (dashboard, or the
  explicit spend-restart confirmation in `/aeko-optimize-budget`). Say this up front so nobody
  expects the ads to come back on their own.
- **No conversion or ROAS rules.** Conversion/revenue data is not ingested, so rules can only watch
  spend, CPM, and CPC. If the merchant asks for "pause when ROAS drops," explain that isn't
  measurable yet and offer the closest supported guard instead.
- **CPM/CPC rules use a day of data, not an hour.** One hour of CPM is noise — a handful of
  impressions can double it. Cost-efficiency rules only run on `rolling_24h` or `daily` windows.
  Only spend (a cumulative number) makes sense over `last_n_hours`.

Language: mirror the user's chat language for explanations, previews, and confirmations. Keep
IDs/tool names ASCII. Money values arrive in micros (×1,000,000) — show them in account currency.

## Inputs

- `domain-id` (optional) — `$1`. Resolve via `aeko_list_domains`.

## Step 1 — Anchor on the merchant's real numbers

Never invent a threshold. Before proposing anything:

1. Resolve the domain, then `aeko_list_ad_rules(domain_id)` — if a similar rule already exists,
   show it and offer to adjust it (`aeko_update_ad_rule`) instead of stacking a duplicate.
2. Pull observed performance: `aeko_get_ad_insights(scope="account")` over the last ~14 days, plus
   per-campaign (`scope="campaign"` requires a `scope_id` — loop over `aeko_list_campaigns`).
3. Compute the baselines the thresholds will hang on: typical daily spend, typical spend per hour,
   CPM (spend / impressions × 1000), CPC. Present them plainly:
   "You normally spend about ₩45k/day (~₩1.9k/hour). CPM has stayed between ₩3.2k and ₩4.1k."
4. Propose thresholds as multiples of those baselines — e.g. hourly-spend guard at 2–3× the normal
   hourly rate, CPM guard at ~2× the trailing average — and explain the multiple. A threshold too
   close to normal will fire on ordinary variance; the preview in Step 4 exposes that.

If the account has no meaningful history, say so and anchor on the merchant's stated budget
instead — a spend cap they name is real data; a CPM guess is not (skip CPM/CPC rules until there
is history to base them on).

## Step 2 — Offer only what the backend supports

Call `aeko_get_ad_rule_capabilities(domain_id)` and build the menu from its metric × window ×
scope combinations. Do not offer a combination it doesn't list. Map plain language onto them:

- "It's spending too fast" → **spend** over `last_n_hours` (pick hours from the baseline).
- "I'm paying too much per view / per click" → **CPM** or **CPC** over `rolling_24h` or `daily`.
- Scope: whole account, specific campaigns, ad groups, or ads. Use `aeko_list_campaigns` /
  `aeko_list_ad_groups` / `aeko_list_ads` to turn ids into names the merchant recognizes. Broad
  scopes are legitimate ("stop everything if the account doubles its burn rate") but get extra
  scrutiny in Step 5.

If the merchant asks for something outside the list (ROAS, single-hour CPM, a metric the
capabilities call doesn't return), say it's not supported and why — don't approximate it silently
with a different rule shape.

## Step 3 — Validate, then create disabled

1. `aeko_validate_ad_rule(rule=<draft>)` — fix any rejection by adjusting the draft, not by
   loosening the intent behind the merchant's back; surface what changed.
2. `aeko_create_ad_rule(...)` — the rule is created **disabled**. Creation never arms anything.
   Tell the merchant that explicitly: "The rule exists but is off. Nothing pauses until you arm it."

## Step 4 — Show the blast radius before arming

`aeko_preview_ad_rule(rule_id=<new rule>)` — this evaluates the rule against current data and
returns what would pause **right now**, with each entity's trigger value vs the threshold. Show it
as a table:

```
If armed right now, this rule would pause:
Entity                     Current      Threshold    Status
Campaign "Summer KR"       ₩6.1k/hr     ₩4.0k/hr     WOULD PAUSE
Campaign "Brand US"        ₩1.2k/hr     ₩4.0k/hr     ok
```

Read the result critically with the merchant:

- **Pauses nothing** — good default state for a guardrail; it should only fire on abnormal days.
- **Pauses something** — is that entity genuinely misbehaving, or is the threshold set inside
  normal range? If the latter, adjust with `aeko_update_ad_rule` and preview again.
- **Pauses most of the account** — the threshold is almost certainly wrong. Do not proceed to
  arming until the merchant has seen this and either fixed the threshold or explicitly wants a
  kill-switch that aggressive.

(`aeko_preview_ad_rule(rule=<draft>)` also works before creation, for comparing candidate
thresholds without saving anything.)

## Step 5 — Arm only on explicit confirmation

After the merchant has seen the preview and confirms in so many words, call
`aeko_set_ad_rule_enabled(rule_id, enabled=True)`.

If the call returns a **broad-match acknowledgement error** (the rule matches a wide slice of the
account), do not retry reflexively. Show the blast radius from Step 4 again, state plainly how much
of the account this one rule can pause, and only on a fresh confirmation re-call with
`acknowledge_broad_match=True`. Never pass `acknowledge_broad_match=True` on the first attempt or
on your own judgment — it exists so a human sees the width of the match first.

Close with what to expect:

```
✔ Rule armed — "Pause Summer KR if hourly spend passes ₩4.0k"
  Checks run against OpenAI's hourly reporting data; reaction lag is up to ~1 hour.
  If it fires, the campaign pauses and STAYS paused until you restart it.
  See what it did anytime: /aeko-ad-guardrails → "show rule activity"
```

## Step 6 — "What did automation do while I was away?"

When the merchant comes back and asks:

- `aeko_list_ad_rule_executions(rule_id=...)` — the actions taken: what was paused, when, and the
  metric value that tripped the threshold. This is the answer to "why is my campaign paused."
- `aeko_list_ad_rule_runs(rule_id=...)` — the evaluation history: proof the rule was being checked
  even on days nothing fired. Useful when the merchant wonders whether the guardrail is actually on.

If something was paused and the merchant wants it back, restate that resume is a manual, explicit
step — hand off to the spend-restart flow in `/aeko-optimize-budget` or the dashboard. This skill
never restarts spend.

## Managing existing rules

- `aeko_list_ad_rules` / `aeko_get_ad_rule` — review what's set up and armed.
- `aeko_update_ad_rule` — change thresholds/scope. If the rule is currently **enabled**, re-run
  `aeko_preview_ad_rule` after the change and show the new blast radius — an edit can widen a rule
  as easily as a new one.
- `aeko_set_ad_rule_enabled(rule_id, enabled=False)` — disarm without deleting (keeps history).
- `aeko_delete_ad_rule` — only on explicit request; prefer disarming so the execution history and
  the tuned thresholds survive.

## Error paths

- No connected ad account / no campaigns → stop; nothing to guard.
- No performance history → skip CPM/CPC rules; offer only a spend cap anchored on the merchant's
  stated budget (Step 1).
- `aeko_validate_ad_rule` or `aeko_create_ad_rule` rejects the rule → show the reason, adjust with
  the merchant, retry. Never work around a validation error by changing scope or metric silently.
- Enable fails with the broad-match error → Step 5 path. Any other enable failure → surface it
  verbatim; the rule stays disabled, say so.

## What this skill never does

- Never proposes a threshold that isn't derived from the merchant's observed numbers or their
  explicitly stated budget.
- Never creates a rule armed, and never enables one without showing the current blast radius and
  getting explicit confirmation first.
- Never passes `acknowledge_broad_match=True` except on a re-call the merchant confirmed after
  seeing what the broad match covers.
- Never offers conversion/ROAS rules or single-hour CPM/CPC rules, and never implies faster than
  hourly reaction.
- Never resumes paused campaigns, ad groups, or ads — restarting spend is a separate, explicit,
  human action.
