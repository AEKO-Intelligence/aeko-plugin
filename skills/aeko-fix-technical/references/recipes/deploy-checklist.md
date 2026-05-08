---
recipe: deploy-checklist
purpose: Per-platform deploy guidance written to DEPLOY.md alongside every technical artifact
load_when: SKILL.md §4 generates the deploy checklist
---

# Deploy checklist (per-platform)

For all technical artifact types, write a `DEPLOY.md` alongside the artifact describing the manual deploy steps per platform. **No deploy path is wired into the MCP for v0.5.0** — always instruct manual deploy.

## llms.txt

Upload to site root.

- **Cafe24:** `/web/product/xxx` → upload via admin or FTP.
- **Shopify:** use a custom page at `/pages/llms-txt` + redirect from `/llms.txt` via theme.liquid (documentation link in the file).
- **Plain hosting:** drop in web root.

## robots.txt

Upload to site root.

- **Cafe24:** restricted — warn user their admin may override the uploaded file.
- **Shopify:** edit `robots.txt.liquid` in the theme; upload the diff content.
- **Plain hosting:** replace the file at web root.

## JSON-LD (site-level)

Inject into the target page's `<head>` via theme/template, OR add to a global include if the schema is `Organization` / `WebSite`.

- **Cafe24:** edit `/web/skin/.../layout/basic.html` `<head>` or use the "공통 영역 편집" admin section.
- **Shopify:** edit `theme.liquid` `<head>` for site-wide schemas; per-page schemas go in the relevant template.
- **Plain hosting:** edit the template that renders `<head>`.

## Brand-specific override

If `references/examples/deploy-notes-example.md` exists, append its platform-specific notes (e.g., your team's CI deploy script, an internal staging URL to test on first, a contact for whom owns each domain). Recipe defaults still ship in DEPLOY.md; the example adds.
