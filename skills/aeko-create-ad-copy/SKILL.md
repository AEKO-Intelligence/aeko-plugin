---
name: aeko-create-ad-copy
description: Draft or revise product ad copy from supplied customer contexts and accepted brand guidance, then check the exact copy against the brand's evals. Use for copy creation, not campaign reporting or account setup.
---

# Create ad copy

Produce useful ad copy for the requested product, market and language. Keep the
user's Automation Prompt separate from this reusable skill: it defines the job,
while the accepted brand package defines the brand's rules and evidence.

## Load the brand's accepted instructions

In AEKO, consume the run's pinned skill, evals, support files and Brand Wiki;
never switch to a newer release halfway through a run. In an external AI client,
use the authenticated `aeko_get_active_brand_package` tool to select this command,
then `aeko_get_brand_package_version` and `aeko_read_brand_package_file` to read
the exact accepted versions. Read every required chunk before generating.
An exported package can provide the same files locally through its manifest.

Use this command's accepted guidance and applicable evals, including declared
brand-specific support files. Read the required Wiki pages for brand voice,
product facts and market guidance, retaining their authority and scope metadata.
A draft page, a cited source or an AI observation is not an accepted brand fact.
If a required file, eval or source is unavailable, report the missing dependency;
do not substitute another brand's package or silently omit its rules.

## Draft or revise

- Ground product claims in the supplied product data and accepted Wiki. Customer
  contexts describe a situation or need; they do not prove product capabilities.
- Follow the requested market, language, format and any optional style preset.
  When no style is specified, write a clear, natural product benefit for the
  supplied situation. Do not invent rankings, certifications, prices or claims.
- Apply brand preferences only within their recorded scope. An ad wording
  preference does not restrict research questions, quoted evidence or other
  brands unless that scope was explicitly accepted.
- For a revision, use the selected output, its original source, and the correction
  conversation. Preserve useful factual content while making the requested change.
  A request to revise one output does not authorize changing future brand rules.
- In hosted ads, emit exactly the requested structured fields `title` and
  `description`, within the supplied limits. Do not put explanations or tool
  receipts into those fields. External clients may show a short copy table when
  the user has not requested a machine-readable format.

## Evaluate the exact result

Read [the ad-copy checks](references/ad-copy-evals.md) and every applicable accepted
brand eval. Check the final strings after revision, not an earlier draft. Resolve
objective failures directly; use the available judge for subjective criteria.
An unavailable or failed judge is not a passed check. Return the checked draft
with its check result, or explain the unresolved requirement.

Keep drafting and delivery separate. A draft is not uploaded, and a tool call is
not a delivery receipt. In AEKO the configured deterministic save/delivery stages
handle the destination after evals; an external client needs the user's actual
delivery request and an available authorized tool before it can publish.

## Learn from feedback

Offer a lasting brand update only when the user wants the correction applied to
future work. Record the rejected text, the accepted replacement, the requested
scope and the relevant source. Propose a change to this brand's skill guidance
and applicable eval/example, preserving existing instructions. The brand package
changes only after its activation policy or explicit review succeeds. Report the
recorded event, proposed change and accepted version as distinct receipts.
If the host lacks an updater tool, present the proposed change for AEKO review or
local editing; never claim it was saved. Keep credentials out of package files.
