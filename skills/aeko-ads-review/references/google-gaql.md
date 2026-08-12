# Google Ads GAQL reads

Use the discovered official Google Ads read-only GAQL search capability. Substitute only the validated
customer ID and ISO dates; never splice untrusted pasted text into a query.

## Query 1 — delivery and conversions by date/action

```sql
SELECT
  segments.date,
  segments.conversion_action,
  segments.conversion_action_name,
  metrics.cost_micros,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions,
  metrics.conversions_value
FROM customer
WHERE segments.date BETWEEN '<date_from>' AND '<date_to>'
ORDER BY segments.date, segments.conversion_action
```

If the connector's advertised Google Ads API version does not allow `segments.conversion_action_name` from
`customer`, retain `segments.conversion_action` and obtain names from Query 2. Do not remove the action
segment or collapse all goal types.

## Query 2 — conversion-action configuration

```sql
SELECT
  conversion_action.resource_name,
  conversion_action.name,
  conversion_action.status,
  conversion_action.primary_for_goal,
  conversion_action.category,
  conversion_action.click_through_lookback_window_days,
  conversion_action.attribution_model_settings.attribution_model
FROM conversion_action
WHERE conversion_action.status = 'ENABLED'
ORDER BY conversion_action.resource_name
```

Join on the conversion-action resource name. The deterministic inclusion rule is: enabled,
`primary_for_goal = true`, and category/name unambiguously denotes purchase. Include every matching purchase
action in resource-name order and list it. Never choose by volume, value, or whichever appears first. When
none qualifies, interactive mode asks the user to choose from the sorted candidates; weekly mode marks the
conversion basis incomparable and retains evidenced spend/delivery only.

Google's click-through lookback window is configured per conversion action; the search call cannot select a
different 1-day/7-day window. Daily segmentation does not convert one configured window into another.
