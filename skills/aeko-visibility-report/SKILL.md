---
name: aeko-visibility-report
description: >
  Compatibility router for the renamed AI visibility report. Routes every
  original domain, window, and depth argument to aeko-ai-visibility.
argument-hint: "[domain-id] [window] [depth]"
allowed-tools: Skill
disallowed-tools: Write, Edit, Bash
---

# AEKO Visibility Report — Compatibility Router

`aeko-visibility-report` was renamed to `/aeko-ai-visibility`.

Attempt delegation through the host's skill-invocation mechanism, passing every original argument unchanged:

```text
This host cannot delegate to another skill. Run this command:
/aeko-ai-visibility <original-arguments>
```

If delegation is unavailable or rejected, print exactly the resolved command above after removing an empty
argument suffix. Do not fetch visibility data or render a report here; the successor owns Starter disclosure,
tracked-prompt routing, Share of Voice, answer drift, and all original report paths.
