# Shared Audit Severity Vocabulary

The copies at `skills/aeko-site-audit/references/severity.md` and
`skills/aeko-pdp-audit/references/severity.md` must stay byte-identical. Keep both in sync.

Use only these keys and copy the wording exactly into the report's severity legend.

| Key | Label | Exact wording |
|---|---|---|
| `critical` | Critical | Prevents the site or page from being fetched or interpreted at all. Fix before relying on AI discovery. |
| `high` | High | Blocks a core machine-readable signal or leaves essential facts unverifiable. Fix next. |
| `medium` | Medium | Weakens extraction, disambiguation, or citation confidence but does not block access. Plan soon. |
| `low` | Low | Optional enhancement or polish with limited immediate impact. Address after higher-severity items. |

## Classification rules

- Classify the observed impact, not the effort required to fix it.
- Use `critical` only when the observed failure prevents retrieval or useful interpretation of the audited target as a whole.
- Use `high` for a failed required structural signal or a crawler block that affects the audited target.
- Use `medium` for incomplete or conflicting evidence that leaves the target readable but less verifiable.
- Use `low` for optional signals and limited-scope cleanup. A missing `llms.txt` is `low` because it is an optional curated index, not a requirement for AI search.
- An unavailable or unevaluated check is `not_assessed`, not a severity. State what evidence was unavailable and do not infer a pass or failure.
