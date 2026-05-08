# Brand-specific technical exemplars

Drop your brand's preferred technical-artifact shapes here. `/aeko-fix-technical` mimics them on the next run. **No forking the plugin.**

## Files

| File | What to put in it | What it changes |
| --- | --- | --- |
| `llms-txt-example.txt` | A real llms.txt you'd be proud of | Section ordering, heading wording, link-description style |
| `robots-txt-additions-example.txt` | Custom partner-crawler rules or path disallows | Appended after the AEKO AI-crawler allowlist |
| `json-ld-example.json` | Your preferred Organization / WebSite shape | `@graph` shape, optional fields you always emit |
| `deploy-notes-example.md` | Internal deploy steps (CI script, staging URL, owner contacts) | Appended to DEPLOY.md per artifact |

## Precedence

> example file (if present) > recipe defaults

Recipe **spec rules** (llms.txt H1 line, robots.txt valid syntax, JSON-LD valid JSON) cannot be relaxed by examples — the skill will fail the run if they're violated.

## What NOT to put here

- **No internal credentials** — strip API keys, FTP passwords, admin URLs you don't want exposed.
- **No PII** — strip customer-list links, internal-only paths.
- **No JavaScript** in JSON-LD examples — the skill will reject anything with `<script>` outside the JSON-LD wrapper.
