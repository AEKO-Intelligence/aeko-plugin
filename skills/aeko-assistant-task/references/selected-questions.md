# Review selected suggested questions

Use only for `tracking.selected_questions_report.v1`. It shares the explicit Tracking scope with the tracking-write task, but its output is `report_markdown` and its permitted operation is `save_report`. Read the frozen `assistant_suggestion` evidence and exact selected rows, including any edited `prompt`, market codes, platform codes and evidence-language scope. Do not call `aeko_track_task_suggestions`, `aeko_track_suggested_prompts`, a single-track tool, or a dismiss/edit tool in this report mode.

Compare the questions by buyer situation, intent and overlap visible in their text. Suggestions are questions worth considering, not evidence of actual search volume, response quality, AI visibility, conversion, or product facts. If the byte or evidence-ID cap prevents full review, state the number selected, the number read and which part remains unreviewed; do not present a subset as a complete ranking. Preserve the selected variant scope without claiming that any variant has been tracked.

Save a concise cited Markdown report. Use `[evidence:<UUID>]` for every cited suggestion and pass precisely those IDs in `evidence_ids` to `aeko_save_action_output(kind=report_markdown, schema_version=assistant-output-v1, ...)`. The result is a review only. Tracking or organizing questions requires a separate explicit task and its own server receipt.
