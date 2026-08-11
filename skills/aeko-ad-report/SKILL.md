---
name: aeko-ad-report
description: >
  Compatibility router for the former standalone OpenAI Ads performance
  report. Routes the original domain and lookback arguments to
  aeko-openai-ads-reporting without changing report scope.
argument-hint: "[domain-id] [days]"
allowed-tools: Skill
disallowed-tools: Write, Edit, Bash
---

# AEKO Ad Report — Compatibility Router

The client-ready OpenAI Ads performance report moved to `/aeko-openai-ads-reporting`.

Attempt delegation through the host's skill-invocation mechanism, preserving the original domain and
lookback arguments:

```text
This host cannot delegate to another skill. Run this command:
/aeko-openai-ads-reporting <original-arguments>
```

If delegation is unavailable or rejected, print exactly the resolved command above after removing an empty
argument suffix. Do not fetch domains, ads, insights, or visibility here; the successor owns the complete
account-gated paid hierarchy, optional organic fold, client-ready file, scheduling path, and error handling.
