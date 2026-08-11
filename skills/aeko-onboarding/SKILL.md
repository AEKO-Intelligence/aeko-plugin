---
name: aeko-onboarding
description: >
  Compatibility router for the renamed first-run flow. Routes the original
  command and arguments to aeko-start, which completes its tour without an
  AEKO account and offers connection only as optional depth.
argument-hint: none
allowed-tools: Skill
disallowed-tools: Write, Edit, Bash
---

# AEKO Onboarding — Compatibility Router

`aeko-onboarding` was renamed to `/aeko-start`.

Attempt delegation through the host's skill-invocation mechanism and invoke `/aeko-start`. If the host
cannot invoke another skill, does not expose a `Skill` tool, or rejects the invocation, print exactly:

```text
This host cannot delegate to another skill. Run this command:
/aeko-start
```

Do not probe an AEKO account, run onboarding here, or call any other tool. The successor owns the complete
zero-account tour and its optional connection guidance.
