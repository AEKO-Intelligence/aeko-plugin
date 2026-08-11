---
name: aeko-prompt-deep-dive
description: >
  Compatibility router for tracked-prompt source analysis. Routes the original
  prompt ID and window to aeko-source-analysis prompt mode.
argument-hint: "<prompt-id> [window]"
allowed-tools: Skill
disallowed-tools: Write, Edit, Bash
---

# AEKO Prompt Deep-Dive — Compatibility Router

The tracked-prompt workflow moved to `/aeko-source-analysis`.

Attempt delegation through the host's skill-invocation mechanism, passing the original prompt ID and window
unchanged:

```text
This host cannot delegate to another skill. Run this command:
/aeko-source-analysis <prompt-id> [window]
```

If delegation is unavailable or rejected, print exactly the resolved command above. Do not fetch or
summarize prompt evidence here; the successor owns the complete response/citation/crawl analysis.
