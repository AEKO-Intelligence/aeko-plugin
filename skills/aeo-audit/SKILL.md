---
name: aeo-audit
description: >
  Compatibility router for the former combined audit. Product-page and shopping
  requests route to aeko-pdp-audit; site and domain requests route to
  aeko-site-audit.
argument-hint: "<url-or-file-path> [shopping]"
allowed-tools: Skill
disallowed-tools: Write, Edit, Bash
---

# AEO Audit — Compatibility Router

`aeo-audit` was split into two focused successors:

- `/aeko-pdp-audit <product-page-url-or-local-html-file>` — "Is this product page ready to be cited?"
- `/aeko-site-audit <site-root-url-or-domain>` — "Is my site readable by AI at all?"

Route the original argument without auditing it here:

1. If any argument is exactly `shopping`, remove that token and invoke `/aeko-pdp-audit` with the remaining
   URL or file argument. This preserves the former `shopping` mode. If no target remains, ask for a product
   page URL or local HTML file before invoking it.
2. Otherwise, invoke `/aeko-pdp-audit` when the user explicitly says product, PDP, item, SKU, Cafe24 product,
   or Naver Smart Store product, or when the URL/file name visibly identifies a product page. Common URL
   signals include `/product/`, `/products/`, `/goods/`, `/item/`, `product_no=`, `goodsNo=`, `productId=`,
   and `itemId=`.
3. Otherwise, invoke `/aeko-site-audit` with the original argument.

Attempt delegation through the host's skill-invocation mechanism. If the host cannot invoke another skill,
does not expose a `Skill` tool, or rejects the invocation, do not dead-end and do not recreate the audit.
Print exactly one runnable fallback command with the resolved target:

```text
This host cannot delegate to another skill. Run this command:
/aeko-pdp-audit <resolved-product-target>
```

or:

```text
This host cannot delegate to another skill. Run this command:
/aeko-site-audit <resolved-site-target>
```

Do not fetch the target, calculate a result, call an AEKO tool, or reproduce the retired combined audit. The
selected successor owns the complete report and its read-only guarantees.
