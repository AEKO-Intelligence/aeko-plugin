# Message-audit render contract

Lead with the result, then receipts. Do not render a claims table in the zero-connector terminal branch.

## Sweep

Render one spend-ranked table per currency:

```text
CLAIM                 SAID IN                ADS   ATTACHED SPEND   OWNED BACKING                         IN AI ANSWERS
48-hour hydration     TikTok x3, Meta x1     4     USD 18,420       not found in 3 checked landing pages  competitor cited in ChatGPT/2026-08-01
vegan                 Meta x2                2     USD 7,810        PDP — exact: "Vegan formula"           echoed in ChatGPT/2026-08-03
```

Every claim links to exact ad IDs in the evidence ledger. Attached spend is union spend within that claim;
rows overlap. Never sum row amounts.

When several claims share a complete negative-backing class, calculate the headline from the union of their
distinct carrying ad IDs:

```text
3 claims were not found in the complete checked-source set; the distinct ads carrying one or more of them had USD 18,420 in union spend.
```

Do not print this when backing is gated, partial, or unavailable. Always print the unreadable-coverage line:

```text
USD <N> of window spend (<X>%) produced no readable claim.
```

When exact total spend is unavailable, omit the percentage and say it could not be calculated.

## Drill

Render: normalized claim plus every verbatim variant; every carrying ad/ID/field/spend; owned sources with
exact fragments and retrieval state; monitored answers with prompt/engine/date/citations; one fix plus its
evidence prerequisite.

## Required receipt and coverage note

After a successful Stage 1, end with:

1. requested platform/account connector receipt;
2. ads and spend with readable claim surfaces versus unreadable surfaces;
3. owned URLs and images actually inspected, plus caps/failures;
4. prompts/answers actually inspected, plus domain/window limitations;
5. a literal coverage note that says:
   - `Inspected:` only the connector fields/static images and owned surfaces actually read;
   - `Not inspected:` video speech, audio, subtitles, and in-video text; TikTok/video-heavy coverage is
     partial by construction;
   - `Google:` ad text was inspected only where GAQL exposed compatible ad-level text; inaccessible assets
     were unavailable, not zero claims.

Never claim a surface was inspected merely because it was in the intended scope.
