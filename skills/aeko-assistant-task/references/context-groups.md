# Saved Context group proposal

Use this mode only for `contexts.group_proposal.v1` in an `assistant-task-v1` Plan.md. The frozen `scope.selection` must be `{mode: explicit, resource: contexts, ids: [...]}` with 1–60 unique Context IDs. Read each listed `assistant_context` evidence ID through `aeko_get_action_evidence` after claiming. Preserve the saved facet JSON, source revision, and evidence-to-Context ID mapping. If a selected Context is now unavailable, stop or clearly omit it; do not substitute a current, nearby, or newly created Context.

Propose 1–12 coherent groups as structured data:

```json
{"groups":[{"name":"Gift moments","rationale":"The selected Contexts share a gift occasion and buyer intent.","context_ids":["<selected-context-uuid>"]}]}
```

Use only Context IDs from the saved selection, with each ID in at most one group. A Context may be left ungrouped when no useful cluster fits; mention that omission in the final response. Ground names and rationales in the frozen facets. A shared keyword alone need not imply the same customer situation, outcome, or product experience. Do not invent product claims or expose review-personal details beyond what the saved Context already says.

Save the proposal through `aeko_save_action_output` with the active `item_id`, `claim_id`, a stable idempotency key, `kind=context_group_proposal`, `schema_version=assistant-output-v1`, and `data` containing the groups. Set `markdown=null` and `evidence_ids=[]`; the server already binds the selected source evidence to the task. The saved output is for user review. It does not create Context groups, campaigns, ads, or tracked prompts. Complete only after the output save succeeds; reconcile an uncertain save by reading the task's outputs before retrying.
