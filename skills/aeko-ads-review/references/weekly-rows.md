# Weekly ads rows

Read `arow-contract.md` completely before emitting rows. Weekly mode has
no conversational ground-truth question and no interactive table.

Emit exactly one `ad_metric` `arow/1` row for Meta, TikTok, Google Ads, and OpenAI Ads, even when unavailable
or not requested. Customer connectors are rung `2`; validated manual exports are rung `3`; AEKO OpenAI Ads
is rung `1`. Use the exact called capability in `source.tool`, window/fetch time, native currency, attribution
configuration, and the evidence-based state/reason.

Map only evidenced numeric keys: `spend_micros`, `impressions`, `clicks`, `ctr_ratio`, `cpc_micros`,
`cpm_micros`, `conv_1d_click`, `conv_7d_click`, `revenue_1d_click_micros`,
`revenue_7d_click_micros`, `roas_1d_click_ratio`, and `roas_7d_click_ratio`. The OpenAI row omits every
conversion/revenue/ROAS key and always states that AEKO does not ingest those metrics, even when its access
is also gated.

When exact-window store truth is supplied, emit a separate `ad_metric` row with provider `manual`, rung `3`,
orders/revenue only, and no attribution claim. When absent, emit the same row unavailable; never prompt.

Then emit exactly one `ad_reconciliation` row produced by this skill. This is the only source from which the
weekly composite may repeat the claimed total/gap; the composite must not recompute it. Use provider
`cross_platform_claims`, rung `mixed`, tool `derived_by_aeko_ads_review`, and confidence `derived`. Include
source row IDs and contributing/excluded platform sets in `evidence`/`dimensions`. Populate only aggregates
per SKILL.md Step 5. An empty contributor set yields `status: unavailable`, `metrics: {}`, and no gap. Missing
store truth permits claimed metrics but omits gap metrics. Keep the required claimed-total disclaimer in
`evidence`.

This source-produced row is a claimed reconciliation, not attributed truth. Its existence does not permit
the weekly composite to sum platform rows.
