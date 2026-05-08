<!--
  Internal deploy notes. Appended to DEPLOY.md whenever /aeko-fix-technical writes one.
  Intended for things like CI deploy scripts, staging URLs, or owner contacts —
  workflow context the skill can't infer.

  Delete this comment block once you paste your real notes.
-->

## Internal deploy steps

- **Staging:** test on `https://staging.example.com` first. Run `npm run deploy:staging` from `repo/`.
- **Production:** `npm run deploy:prod` triggers CI. Owner: @yourname on Slack.
- **Rollback:** every deploy creates a tagged release. Revert via `git checkout <previous-tag> && npm run deploy:prod`.

## Per-artifact notes

- **llms.txt:** lives at `repo/public/llms.txt`. Don't edit in Cafe24 admin — gets overwritten on next deploy.
- **robots.txt:** Cafe24 admin overrides FTP uploads. Open a ticket with Cafe24 to request custom robots.txt — no self-serve path.
- **JSON-LD:** Organization-level lives in `theme/layout/basic.html`. Page-level lives in template renderers — see `theme/skin/...`.
