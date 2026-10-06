# Review-only ad rule change proposal

Use only for `ads.rule_change_proposal.v1`. Require a single explicit selected rule ID under the saved connected `ad_account_id`; read its one frozen `assistant_ad_rule` evidence ID. Preserve the rule's current version, scope level, conditions, guards, match mode, context-rule status and action. The server rechecks current ownership/version before saving. If the rule changed, stop and ask for a new saved task; do not reinterpret an older version as current.

Propose only changes that the task permits: `name`, `description`, `match` (`all` or `any`), `conditions`, or `guards`. Use the existing typed rule schema for condition and guard structures. Conditions must be compatible with the frozen scope level. A context rule cannot change conditions through this proposal because that would require revisiting its context basis. Do not include `enabled`, `action`, `action_params`, budget, account switch, scope level/filter or activation fields. Explain the reason and the effect of the proposed threshold in plain language; metrics are only as current as the frozen rule evidence.

Save `kind=ad_rule_proposal`, `schema_version=assistant-output-v1`, `markdown=null`, exactly one `evidence_ids` entry (the frozen rule evidence UUID), and structured data:

```json
{"rule_id":"<selected-rule-uuid>","expected_version":1,"rationale":"<why this edit fits the saved rule>","changes":{"description":"<reviewed wording>"}}
```

Use a real `expected_version` from evidence; the example is only a shape. This output is a review proposal. Do not call rule-create, rule-update, rule-enable, account automation or ad budget tools. The native rule editor is the separate apply path with its own validation and explicit activation step. Complete only after the server has saved the proposal under the active claim.
