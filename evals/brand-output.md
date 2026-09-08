# Brand output evaluation

This is upstream evaluation guidance, not a registered backend evaluator or an executable
test. A brand can copy/customize it as an eval document and attach that version to a job.
The host must supply the exact task prompt, brand rules, selected evidence/window, output
payload, and package/eval versions. Missing required inputs produce `unavailable`.

Evaluate the actual output, including title, body, targeting hints, and relevant metadata:

| Check | Pass condition |
| --- | --- |
| Task preserved | Output satisfies the original purpose, audience, channel and destination; a skill name/style has not replaced the job instructions. |
| Brand scope | Every applied customer rule/example belongs to this brand; another brand's restrictions are absent. |
| Explicit rules | All applicable standing brand rules and task constraints are satisfied; no recipe/example/generated text silently overrides them. |
| Evidence | Factual claims trace to selected source evidence; synthetic/style examples are not treated as real experience or current product facts. |
| Window and limits | Evidence comes from the required window and declared scope; truncation and unavailable selectors are reported rather than hidden. |
| Required brand evals | Each selected required eval has a result against the exact output/version; a missing or unrun eval is never marked passed. |
| Destination contract | Payload fits the actual platform/schema and permitted action; no invented integration, credential, schedule permission, or destination. |
| Empty-input behavior | No eligible evidence produces the job's declared no-input result and no fabricated substitute or downstream marketing mutation. |

Return a result for each applicable check: `pass`, `fail`, or `unavailable`, with the rule
ID/version, offending output excerpt or supporting evidence, and a short reason. A failed or
unavailable required check prevents acceptance; at most one bounded correction is allowed.
Do not re-run a full private benchmark for each output or charge a model call without the
job's model/budget authorization. Deterministic checks run before subjective judging.

There is no universal ban on a specific brand's disliked phrase. For a synthetic Brand A
that explicitly prohibits "the best", that phrase fails A's claim rule. A synthetic Brand B
without that rule does not inherit it; B still needs evidence for any factual comparison.
