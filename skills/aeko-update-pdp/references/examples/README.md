# Brand-specific PDP exemplars

Drop your brand's preferred PDP HTML structure, JSON-LD field choices, or verification prompt voice here. `/aeko-update-pdp` will mimic them on the next run. **No forking the plugin.**

## Files

| File | What to put in it | What it changes |
| --- | --- | --- |
| `pdp-html-example.html` | A real, well-performing PDP description block from your store | Section ordering, heading copy, class-name conventions, paragraph cadence |
| `json-ld-preferences.json` | A JSON object naming optional fields to always-include or always-omit | Which optional Product / FAQPage / Review fields the skill emits |
| `verification-prompt-example.md` | A draft of how you'd phrase the Step 5b user-facing question | Step 5b register / wording — recipe structure stays |

## Precedence

> example file (if present) > recipe defaults > Plan/content context

The hard contract in `references/recipes/responsive-html-contract.md` (mobile-first, no JS, no action buttons, semantic tags only, citability baseline) **always applies** — examples can't relax it.

## What NOT to put here

- **No PII** — strip customer names, real phone numbers, internal SKUs you don't want indexed.
- **No external action links** — `<a href>` and `<button>` are forbidden in PDP output regardless of what your example contains. The skill strips them.
- **No JavaScript** — same rule.

## Verifying it worked

After running `/aeko-update-pdp <item_id>`, check the user-facing summary at the bottom for a `Refs loaded:` line listing which example files were picked up. If your example isn't named there, check the filename matches one of the three above.
