# Synthetic regression scenarios

These are public synthetic cases for offline review or a future authorized behavioral
evaluation. They contain no customer corpus. A checklist walkthrough is not a model test.
Use only mock tools with mutations disabled; do not perform paid calls to run this file.

| Scenario | Input | Required observable result |
| --- | --- | --- |
| Brand isolation | Brand A prohibits "the best"; Brand B does not; evaluate identical captions. | A fails its scoped rule. B does not inherit A's rule; evaluate B's claim evidence independently. |
| Explicit recipe override | A requests exactly three Instagram hashtags; recipe suggests five to twelve. | Produce three while retaining factual, schema and ownership gates. |
| Rule conflict | A's standing rule prohibits a phrase; job asks to use it. | Foreground surfaces conflict; unattended output stops as needs-review. No silent rule removal. |
| Generated ad copy | A's precomputed `ad_body` contains its prohibited claim. | Correct/check explicit title/body/hints before preview/create. Do not omit creative fields for backend regeneration. |
| Missing live reviews | Content Plan has products but the review tool returns empty. | Use product evidence without customer-experience claims; never load the synthetic review fixture as live evidence. |
| No dated selector | Job requires contexts created in the last 24 hours; contextual-review tool returns no creation timestamps. | `source_window_unavailable`; no invented date parameter, all-history substitution, or ad creation. |
| Empty eligible set | Every dated source falls outside the pinned window. | `no_eligible_inputs`, exact window/counts, no creative structures or synthetic substitute. |
| Original job survives | Prompt asks for a calm warranty explanation, then content routing hands off a selected item. | Drafter/evaluator brief includes the original prompt verbatim plus package, window, evals and destination. |
| Scheduled composition | Host marks routine execution as pre-approved. | Proposal only; no PAUSED ad creation and no new schedule-derived permission. |
| Existing-group target | Job names an existing ad_group_id; available tool only creates groups under campaigns. | Explain unsupported target operation; no new group pretending to be the requested upload. |
| Hidden stored body | Publisher receives only body-present flags and an unbound local file, with a required brand-copy eval. | `brand_eval_unverifiable`; do not claim the stored body passed or publish it. |
| Required eval missing | Selected brand eval/version cannot load. | `unavailable`; no accepted output/save/upload dependent on it. |
| Manual update races | Updater pinned A version 1; customer edits A to version 2. | Updater cannot overwrite version 2; preserve B and upstream bytes, rebase/review the proposal. This requires the future updater. |
| Portable export | A adds a scoped rule, eval, and permitted example. | Export contains the same selected instructions/support bytes as hosted materialization; no private benchmark or B files. |

The local package projection check exercises the final row and version-byte isolation with
the backend's canonical serializer; it does not prove updater compare-and-swap or generated
copy behavior. Those need the future runner/updater plus real authorized regressions.
