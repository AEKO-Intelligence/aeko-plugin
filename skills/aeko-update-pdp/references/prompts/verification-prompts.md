---
recipe: verification-prompts
purpose: User-language prompt templates for Step 5b — resolving pending_verifications with the user
load_when: SKILL.md §5b runs (pending_verifications non-empty)
---

# Step 5b — verification prompt templates

When `pending_verifications` is non-empty after Step 5, pause and ask the user in their chat language. Show a numbered list of every pending field with: which `<section>` it appears in, why it's needed (one short phrase), and any candidate value derived from prose / OCR (if none, say "확인 안 됨" / "not found" or a natural equivalent in the user's language).
Use the KO/EN templates below when they match the user's language. For other languages, translate the EN
template naturally while keeping reply keywords `omit` and `leave` available as stable shortcuts.

## KO

```
이 PDP에서 확인이 필요한 정보가 N개 있습니다. 각 항목에 대해 답해 주세요:

1. <field_label> — <section_label> 섹션에 들어갈 <one-line description>.
   현재 추정값: <suggested_value or "확인 안 됨">.
   응답: 값을 직접 입력하거나, "빼기"(해당 문장 제거) 또는 "두기"(나중에 직접 채우도록 HTML 주석으로 보존) 중 선택.
2. ...

전부 한 번에 같은 처리를 원하면 "전부 빼기" 또는 "전부 두기"로 답해 주세요.
```

## EN

```
I found N items in this PDP that need verification. Please respond to each:

1. <field_label> — for the <section_label> section: <one-line description>.
   Current candidate: <suggested_value or "not found">.
   Reply with a value, or `omit` to remove the sentence, or `leave` to preserve as an HTML comment.
2. ...

Reply `omit all` or `leave all` to apply the same action to every remaining item.
```

## Reply handling

For each item, the user can reply:

- **A concrete value** → substitute into the in-memory draft, replacing the placeholder. The surrounding sentence remains visible.
- **`빼기` / `omit`** → cleanly remove the sentence (or list item, or attribute) that contained the placeholder. Preserve paragraph flow; if the entire `<p>` becomes empty, drop the `<p>` too.
- **`두기` / `leave`** → replace the placeholder with `<!-- pending: <field> -->` (HTML comment, invisible to end users). Track in `left_pending` for the Step 9 summary.

Batch shortcuts: `전부 빼기` / `omit all` and `전부 두기` / `leave all` apply the same action to every remaining pending item.

After collecting all answers, apply substitutions in-memory. Re-validate `must_include` (every required string still present) and `forbidden` (no banned strings introduced). If a substitution drops a `must_include` string, surface the conflict and re-ask only that item.

## Brand-specific override

If `references/examples/verification-prompt-example.md` exists, mirror its register and phrasing — keep the structure (numbered list, current candidate, reply options) but adopt the brand's voice. Useful for brands that prefer a particular formality level or use a specific term in place of "확인 안 됨".
