# Related questions from selected Contexts

Use only for `contexts.related_questions_report.v1`. The saved scope must select 1–60 active curated Context IDs. Read their frozen `assistant_context` facet JSON and keep each evidence ID mapped to its selected Context ID. Missing or redacted evidence narrows the useful basis; it never authorizes reading another Context.

Propose natural shopper questions tied to the actual customer state, concern, occasion, intended outcome or product experience in the selected facets. Explain which facets led to each question, using `[evidence:<UUID>]` citations. Do not turn a reported experience into a verified product claim. Keep distinctions between different Contexts; avoid a generic question list that obscures the saved selection. The question text should follow the task's output language, while evidence quotations retain their original language when precision matters.

Save `kind=report_markdown`, `schema_version=assistant-output-v1`, and exactly the cited evidence IDs. This is a reviewable question proposal, not a prompt-tracking receipt: do not create, track, dismiss or edit prompts or Contexts. A later tracking request needs its own explicit selected rows and quota check.
