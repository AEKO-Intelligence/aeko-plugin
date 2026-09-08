# Message-audit evidence vocabulary

Use only these classes and mappings. A class is an evidence state, not a tone suggestion.

## 1. Connector classes

| Class | Evidence required | User-facing meaning |
|---|---|---|
| `connected` | qualifying read succeeds for the full window | inspected |
| `partial` | some ads/dates/creative fields are missing | partially inspected: `<reason>` |
| `expired` | structured call error explicitly says expired/reauthorize | authorization expired: `<provided path or host settings>` |
| `not_connected` | call explicitly says account/provider disconnected or never authorized | connector not connected: `<host connection step>` |
| `not_detected` | no qualifying tool and no auth history evidence | qualifying connector not detected; connection history unknown |
| `ambiguous` | multiple qualifying tools/accounts cannot be distinguished | selection required: `<candidates>` |
| `not_requested` | user excluded platform | not requested |

Never convert `not_detected` into `never_connected`.

## 2. Owned-backing classes

| Class | Evidence required |
|---|---|
| `exact` | URL/product ID plus literal text/image fragment states the claim with the same qualifiers |
| `qualified` | fragment supports a weaker/narrower form and the difference is shown |
| `contradicted` | fragment explicitly conflicts with the claim |
| `not_found` | claim absent from a named, bounded, completely fetched checked-source set, including relevant pixels |
| `unavailable` | partial index, image-only page without inspected pixels, crawl delay/error/truncation, cap, or domain mismatch |
| `account_gated` | AEKO auth absent/401; retain any free landing-page result separately |
| `tier_gated` | structured 403/feature-lock identifies a higher tier; retain free results |

Absence from `aeko_list_own_content` is never site-wide absence. Citability, schema, and ad repetition are
not factual backing.

## 3. Answer-engine classes

| Class | Evidence required |
|---|---|
| `echoed` | relevant same-window monitored answer repeats the claim |
| `qualified` | answer repeats a narrower/qualified form |
| `contradicted` | answer explicitly conflicts |
| `competitor_cited` | relevant answer gives/cites a competitor for the claim |
| `absent_in_monitored_answers` | exact-window relevant monitored answers exist and omit the claim/owned citation |
| `no_relevant_tracked_prompt` | selected-domain prompt set is valid but contains no relevant prompt |
| `unavailable` | domain filtering, exact window, response body, or monitoring evidence cannot be established |
| `account_gated` | AEKO absent/401 |
| `tier_gated` | structured plan/feature gate |

Use `absent_in_monitored_answers`, never an unbounded “AI never says this.”

## 4. Class-to-cell text

| Class | Cell text |
|---|---|
| backing `exact` | `<source> — exact: “<verbatim>”` |
| backing `qualified` | `<source> — qualified: “<verbatim>”` |
| backing `contradicted` | `<source> — contradicted: “<verbatim>”` |
| backing `not_found` | `not found in <named checked-source set>` |
| echo `echoed` | `echoed in <engine/date>` |
| echo `qualified` | `qualified in <engine/date>` |
| echo `contradicted` | `contradicted in <engine/date>` |
| echo `competitor_cited` | `competitor cited in <engine/date>` |
| echo `absent_in_monitored_answers` | `not found in relevant monitored answers (<exact window>)` |
| `no_relevant_tracked_prompt` | `no relevant tracked prompt` |
| `unavailable` | `— unavailable: <reason>` |
| `account_gated` | `— AEKO account-gated; <free landing-page state if any>` |
| `tier_gated` | `— AEKO tier-gated: <returned requirement>; <free landing-page state if any>` |

Never render gated, partial, unauthorized, unmonitored, or image-unread evidence as `none`, `never`, or
numeric zero.
