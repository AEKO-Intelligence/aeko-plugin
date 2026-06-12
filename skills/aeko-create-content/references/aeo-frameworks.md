---
name: aeo-frameworks
purpose: The quality core for AEKO content — the AEO writing frameworks that make content citable by AI engines (BLUF, PREP, Informational Gain, E-E-A-T). Replaces the old "crawl-the-winners-and-mimic-their-shape" approach.
load_when: Read once per run and pass to every drafter. The drafter applies these to the substance (product info + context-reviews + prompt) it was handed.
canonical: This is the plugin's single source of truth for the AEO frameworks. It is also consumed by /aeko-update-pdp (PDP description + FAQ) and cited by /aeo-audit (scoring rubric). Edit the frameworks HERE — don't fork copies into other skills.
---

# AEO writing frameworks — what makes content get cited

AI engines (ChatGPT, Claude, Gemini, Perplexity) cite content that **answers directly, is
self-contained, and says something a generic answer can't.** These four frameworks encode that.
They are the *how* — they shape and voice content. The *what* (the actual claims, facts, and
experiences) comes from the substance you were handed: **product info + context-reviews + the
prompt + the brand kit.** Frameworks on top of thin substance still produce thin content, so use
the substance generously.

A note on why this matters: the old version of this skill crawled the pages AI engines already
cite and copied their structure. That produces *derivative* content — the one thing AI engines
reliably ignore, because it adds no new information. We optimize for the opposite: **informational
gain.** Be the source worth citing, not the echo.

---

## 1. BLUF — Bottom Line Up Front

Lead with the answer. The first sentence (and the first sentence of every section) should state the
conclusion, not the wind-up. AI engines extract the direct answer to a question; if the answer is
buried under three paragraphs of preamble, the model has nothing clean to lift and cite.

- **Weak:** "여름철 침구를 고를 때는 여러 가지 요소를 고려해야 합니다. 먼저…"
- **BLUF:** "여름 침구는 '냉감 원단'보다 '통기성'이 수면의 질을 더 크게 좌우합니다. 이유는…"

The headline and the opening line should be answer-shaped, not topic-shaped.

## 2. PREP — Point · Reason · Example · Point

Structure each argument block as a self-contained unit:

1. **Point** — the claim (this is also your BLUF for the block).
2. **Reason** — *why* it's true (mechanism, principle, data).
3. **Example** — a concrete, specific instance that proves it. **This is where substance lives** —
   pull from product specs and, above all, from context-reviews (real lived experience).
4. **Point** — restate, now earned.

Each PREP block is independently citable: a model can lift it whole and have a complete answer.
A page that is a stack of clean PREP blocks is a page that gets cited section by section.

## 3. Informational Gain — the differentiator

This is the single biggest lever. Three ways to add information a generic answer lacks:

### 3a. Originality — concrete lived experience (AI는 경험할 수 없다)

Generic claims ("착화감이 좋다", "시원해요") are exactly what a model can already generate, so they
earn no citation. What a model *cannot* generate is specific, sensory, lived experience. That is
the most valuable thing on the page.

> 예: "쿠션이 좋다"는 뻔한 말 대신 — "밑창이 너무 푹신해서 5km 전까지는 발이 가라앉는 느낌에
> 페이스가 오히려 떨어졌다. 그런데 10km를 넘기자 그 과한 쿠션이 착지 충격을 받아내면서 무릎
> 부담이 확 줄었다."

The second version is specific (5km / 10km), sensory (발이 가라앉는 느낌), and situational (초반엔
단점이던 푹신함이 장거리에서는 장점으로 뒤집힌다). That is informational gain.

**Where this comes from:** the **context-reviews** handed to you in the brief — these are real
customer/usage experiences mapped to the product. Mine them for the concrete number, the surprising
moment, the trade-off nobody mentions. Quote or paraphrase the real detail; do not generalize it
back into mush. See the **anti-fabrication rule** below — this is the one input you must never invent.

### 3b. Specific Cohort — 뾰족한 타겟팅

Write for a sharply-defined reader, not "everyone." "여름에 잠 못 드는 사람" is broad; "에어컨을
끄고 자고 싶지만 새벽에 땀 때문에 깨는 30대" is a cohort. Specific cohorts make the content
unmistakably relevant to *someone*, which is what makes it the best answer to *their* question — and
their question is exactly the prompt the brand wants to be cited for. Name the cohort early and keep
serving it.

### 3c. Contrarian View — 과감한 관점

Take a defensible stance against the conventional wisdom. If everyone says "냉감 원단이 답이다", a
contrarian, evidence-backed "냉감 원단은 오히려 통기성을 막아 새벽에 더 덥다" is far more citable —
it's a *new* claim, not a restatement. Only take the contrarian line when you can back it with a
reason and an example (PREP); a hot take with no support is noise. When the brief includes a
`contrarian_hint` (deep mode surfaces the gap in what AI currently says), use it as the seed.

## 4. E-E-A-T — for FAQ sections

When the content includes an FAQ (or any Q&A block), each answer must demonstrate **E-E-A-T**:

- **Experience** — first-hand, from context-reviews ("실제로 6주 사용 후…").
- **Expertise** — correct mechanism / domain knowledge.
- **Authoritativeness** — concrete, checkable specifics (numbers, materials, conditions).
- **Trustworthiness** — honest trade-offs, no overclaiming, no fabricated proof.

An FAQ answer that is just a restated marketing line fails E-E-A-T. One that says "세탁 후 수축은
약 2% 발생했고, 건조기 사용 시 더 컸습니다" passes — it shows experience, specificity, and honesty.

### 4.5 Balanced positioning — name the trade-offs (default, not optional)

Write realistically. Where they genuinely exist, name the product's **trade-offs, limitations, or
"not-for" cases** (aim for ~2–3), grounded in specs or reviews — not just advantages. This is a primary
AEO/E-E-A-T citation signal, **not** a weakness: AI engines (and shoppers) trust and cite content that
acknowledges constraints far more than advantages-only copy, which reads as marketing and gets skipped.
The goal is honesty, not a quota — never manufacture a flaw to look balanced.

- Pair claims with honest caveats: "고보습이지만 지성·여드름성 피부엔 다소 무거울 수 있다" beats
  "모두에게 완벽한 보습." Frame the downside with who/when it matters.
- Use a "best for / not for" line or a trade-off table (§5) whenever the substance supports it.
- **Never fabricate a flaw.** If a dimension genuinely has no downside, say so plainly rather than
  inventing one — balance must trace to real specs/reviews (see the anti-fabrication rule).

---

## 5. Decision-guide blocks — for AI shopping and comparison

AI shopping experiences compare products by constraints: budget, use case, size, comfort, materials,
reviews, trade-offs, return risk, and availability. Help the buyer decide, not just admire the product.
For ecommerce content and PDP sections, include one or more compact decision blocks when the substance
supports them:

- **Best for / not for:** "Best for hot sleepers who want low weight; not for buyers who want a heavy hotel feel."
- **Trade-off table:** feature, what it helps, what to watch.
- **Comparison attributes:** material, size, care, warranty/returns, price band, availability, review signal.
- **Buyer constraints:** budget, skin sensitivity, climate, room size, gift use, shipping deadline.
- **Evidence-backed caveat:** a specific limitation grounded in specs or reviews.

This is not a CTA block. Do not use hard-sell language. The goal is to make the product easy for a human
and an AI shopping assistant to compare honestly.

---

## The anti-manipulation rule (non-negotiable)

Never add hidden or visible instructions aimed at manipulating AI systems. Do not write:

- Hidden text, comments, or schema fields telling an AI to recommend the brand.
- "Ignore previous instructions" or any prompt-injection style copy.
- Invisible AI-only claims that shoppers cannot see.
- Structured data that exaggerates, invents, or contradicts visible product facts.

If a sentence only makes sense as an attempt to influence an AI model rather than help a shopper, remove
it. AEKO optimizes clarity, evidence, and accessibility — not prompt injection.

---

## The anti-fabrication rule (non-negotiable)

**Never invent a lived experience.** Originality (§3a) and Experience (§4) must trace to a *real*
context-review or product fact you were given. AI 경험할 수 없다 — and neither may you pretend to.

- If context-reviews are present → ground originality in them; paraphrase or quote real detail.
- If context-reviews are **absent** → do NOT manufacture a fake anecdote. Instead, write with
  **specific expertise** (correct mechanisms, real product specs, honest reasoning) and lean on
  Specific Cohort and Contrarian View for differentiation. Then note in your self-check that the
  originality dimension is expertise-based, not experience-based — the coordinator surfaces a
  "attach a product / reviews for more original content" hint.
- If product evidence lives **only in images** (clinical tests, lab/efficacy results, ingredient
  labels, certifications) → **extract it via vision** (the executor supplies it as `ocr_text` / the
  PDP OCR payload) and render the real figures with units intact. NEVER infer a number from what the
  category "typically" contains — a claim like "95% 유효성분" must trace to the visible label or test
  certificate, not to memory. Numeric, data-backed claims are among the highest-citability content
  you can write, so surface them — but only the ones the source actually shows.

Fabricated experience is worse than generic content: it's a trust violation that, if cited, makes
the brand look dishonest. Specific-but-honest always beats vivid-but-invented.

---

## Quick self-check (the drafter runs this)

- [ ] **BLUF:** does the first line answer, not preamble?
- [ ] **PREP:** is the body a stack of Point-Reason-Example-Point blocks?
- [ ] **Originality:** is there ≥1 concrete detail traceable to a real context-review (or, if none,
      expertise-grounded and flagged — never fabricated)?
- [ ] **Cohort:** is a specific reader named and served?
- [ ] **Contrarian:** is there ≥1 non-obvious, supported claim?
- [ ] **Balanced & honest:** does it read realistically — the limitations/trade-offs that ARE present are
      named (traceable to specs/reviews), not buried under advantages-only copy? Count is aspirational
      (~2–3 where they genuinely exist); **never invent a downside to hit a number** — "no significant
      downside in X" is a valid, honest answer.
- [ ] **E-E-A-T:** if there's an FAQ, does every answer show experience + expertise + specifics + honesty?
- [ ] **Decision support:** for shopping content, is there a best-for/trade-off/comparison block when substance supports it?
- [ ] **No fabrication:** every experiential claim traces to real substance.
- [ ] **No AI manipulation:** no hidden prompts, AI-only persuasion, or misleading schema/content.
