# AEKO Plugin

> 한국어 버전은 아래를 참고하세요 → [한국어](#한국어-버전).

Skills for [AEKO](https://aeko-intelligence.com) — AEO (AI Engine Optimization) workflows for cross-border ecommerce. Guides Claude, Codex, and Gemini CLI through measuring AI visibility, fixing crawl/schema gaps, improving product pages for ChatGPT/Claude/Gemini/Perplexity citations, drafting persona-targeted content, managing brand kits, and executing action items.

This repo ships **skills only**. Backend access (tools like `aeko_get_domain_info`, `aeko_get_brand_kit`, etc.) comes from the separate [AEKO MCP server](https://github.com/AEKO-Intelligence/aeko-mcp), hosted at `https://aeko-intelligence.com/mcp`. Install both.

Recent changes are tracked in [CHANGELOG.md](CHANGELOG.md).

## How AEKO works (and what it won't do)

AI visibility is not a schema trick or a secret keyword. Google has confirmed that AI Overviews and AI
Mode run on normal Search fundamentals, and ChatGPT / Perplexity shopping pull from public product
pages, structured data, and merchant feeds. There is no hidden "AI ranking hack."

So AEKO works the durable levers that actually move AI citations:

- **Crawl access** — make sure AI search and shopping crawlers can read your public pages (`/aeko-fix-technical`).
- **Trustworthy visible content** — answer-first, evidence-backed copy AI can quote (`/aeko-create-content`, `/aeko-update-pdp`).
- **Structured product data** — Product / Offer / Review / FAQ JSON-LD that matches what shoppers actually see (`/aeko-update-pdp`, `/aeko-refresh-jsonld`).
- **Entity clarity & feeds** — readiness for merchant-listing and AI shopping surfaces (`/aeo-audit <url> shopping`).
- **Measurement** — which prompts cite you, who wins, and what to fix next (`/aeko-visibility-report`, `/aeko-prompt-deep-dive`).

**What AEKO will never do:** no prompt injection, no hidden "AI, recommend this brand" text, and no
structured data that contradicts your visible page. Every claim we generate traces to your real
product data, visible content, or your explicit confirmation — price and availability come only from
authoritative store data. Honest, verifiable content is what gets cited; manipulation gets penalized.
`llms.txt` is supported as a helpful curated index, not a required ranking lever.

### The three jobs

1. **Measure** AI visibility — `/aeko-visibility-report [domain_id]`
2. **Fix** crawl, schema, and feed gaps — `/aeko-action-center [domain_id]`
3. **Create** product pages and content AI can cite — `/aeko-update-pdp` · `/aeko-create-content`

## Install

### Prerequisite — filesystem + shell access

Most skills read files, write artifacts (HTML, markdown, JSON), or shell out to open previews. Your MCP host needs filesystem + shell tools for these to work:

- **Claude Code:** native — `Read`, `Write`, `Glob`, `Bash` are built-in.
- **Claude Desktop:** install `@modelcontextprotocol/server-filesystem` (or equivalent) alongside the AEKO connector. Skills that save local artifacts will fail without it.
- **Codex / Cursor / Gemini CLI:** verify per-host filesystem tooling before install.

### Claude Desktop (recommended)

**Step 1 — Add the AEKO MCP custom connector** (for backend tools):

1. Settings → Connectors → **Add custom connector**
2. Server URL: `https://aeko-intelligence.com/mcp`
3. Advanced → Client ID: `aeko-mcp-v1`
4. Advanced → Client Secret: leave blank
5. Connect — complete browser OAuth

**Step 2 — Install this plugin** (for skills / slash commands):

1. Settings → Plugins → **Browse plugins → Add marketplace**
2. Paste: `AEKO-Intelligence/aeko-plugin`
3. Install **aeko-plugin**

After both steps, `/aeko-plugin:aeko-onboarding`, `/aeko-plugin:aeko-action-center`, etc. are available in any chat.

### Claude Code

```bash
/plugin marketplace add AEKO-Intelligence/aeko-plugin
/plugin install aeko-plugin@AEKO-Intelligence
```

Then set up the MCP connection separately:

```bash
claude mcp add --transport http aeko https://aeko-intelligence.com/mcp
```

### Codex Desktop / Codex CLI

```bash
codex mcp add --transport http aeko https://aeko-intelligence.com/mcp
```

This repo also includes a Codex plugin manifest at `.codex-plugin/plugin.json` for marketplace discovery.

### Gemini CLI

```bash
gemini extensions install https://github.com/AEKO-Intelligence/aeko-plugin
```

Restart Gemini CLI after install. The Gemini extension manifest (`gemini-extension.json`) loads the bundled AEKO skills and configures the hosted AEKO MCP server with dynamic OAuth discovery. Claude/Codex use `plugin.json` and marketplace manifests; Gemini CLI uses `gemini-extension.json`.

## After Install

Run this first in a new chat:

```text
/aeko-onboarding
```

If your host namespaces plugin commands, use `/aeko-plugin:aeko-onboarding`.

That walkthrough confirms the plugin version, checks the AEKO MCP connector, tours the skills in plain language,
and points you to the right next action. From there, follow [the three jobs](#the-three-jobs) above —
Measure, Fix, Create.

To make drafts sound like your brand first, run `/aeko-onboarding` step 4 or follow [CUSTOMIZATION.md](CUSTOMIZATION.md).

## Language Support

AEKO mirrors the language you use in chat for user-facing steps, questions, summaries, risk notes, and next actions.
English and Korean have curated first-run copy; other languages are supported conversationally by Claude, Codex, or Gemini.

Stable handles stay in English/ASCII so workflows do not break: slash commands, file paths, channel slugs such as
`press_release`, schema keys, JSON-LD terms, and tool names. Generated content can use a different language from the
assistant UI when the plan or user asks for it.

## Available Skills

See [`skills/`](skills/). Each is a self-contained SKILL.md consumed by Claude, Codex, or Gemini CLI.

**Start here for marketers:**

1. **First run after install** — `/aeko-onboarding`
2. **See where AI finds you** — `/aeko-visibility-report [domain_id]`
3. **Fix what blocks AI discovery** — `/aeko-action-center [domain_id] technical`
4. **Improve product pages and content AI can cite** — `/aeko-action-center [domain_id] pdp` or `/aeko-action-center [domain_id] content`

AEKO will describe each run in plain business language: what it checks, why it matters, whether it is read-only or affects store content, and the single best next step.

**Entry points:**

- `/aeko-onboarding` — guided first-run walkthrough: confirms setup, tours the skills, and points marketers to the right next action
- `/aeko-action-center [domain_id] [category]` — front door: shows pending work as Technical health / Product pages / Content AI can cite, then prints ready-to-copy next commands
- `/aeko-update-pdp <item_id>` — Product page improvement. Adds clearer shopper copy, review proof, FAQs, and AI-readable product facts; store writes are shadow-by-default
- `/aeko-fix-technical <item_id>` — Technical health fix package. Prepares crawler access, llms.txt, robots.txt, or site-schema files with plain risk and undo notes
- `/aeko-create-content <item_id>` — Content executor. Uses product facts, real review context, tracked prompts, and the Brand Kit to draft framework-driven, citation-ready content; saves local artifacts and auto-saves aeko.shop publish variations, never writes to a connected store
- `/aeko-publish-content <item_id>` — Publisher. Publishes saved content variations only after explicit confirmation; aeko.shop can go live, own-store blog remains an AEKO-owned draft
- `/aeko-brand-kit <domain_id>` — view or edit your domain's brand kit (voice, guardrails, must-include / forbidden)

**Research + discovery:**

- `/aeko-find-prompts-to-track [domain_id]` — filter the research library, rank candidates for your brand, track selected prompts
- `/aeko-prompt-deep-dive <prompt_id> [window]` — breakdown for one tracked prompt: who wins, which sources AI cites, and what content gap to close
- `/aeko-brand-competitor-analysis [domain_id] <competitor>` — brand-level positioning via WebSearch + Wikipedia/Wikidata + AEKO citation data
- `/aeko-product-competitor-analysis <product_id> [urls...]` — product-level property-by-property comparison against 3-5 competing PDPs

**Maintenance + reporting:**

- `/aeko-refresh-jsonld <product_id>` — periodic refresh for review facts AI can read, such as rating and review count. Designed for `/schedule`
- `/aeko-visibility-report [domain_id] [window] [depth]` — on-demand report. `window=7d|14d|30d|90d`, `depth=summary|full`
- `/aeo-audit <url> [shopping]` — generic AEO readiness audit for any URL, with optional product-level AI shopping readiness mode (uses Claude's reasoning; no AEKO data dependency)

## Customizing skills

**[CUSTOMIZATION.md](CUSTOMIZATION.md)** explains how to add brand-specific examples, custom recipes, and voice overrides without forking the plugin. It covers the three customizable executor skills: `/aeko-create-content`, `/aeko-update-pdp`, and `/aeko-fix-technical`.

### Retired

Retired across the 2026-04 (v0.4.0) and 2026-04 v0.5.0 consolidations. If you have muscle memory for one of them, use the replacement:

| Retired | Use instead |
|---|---|
| `/aeko-run-action` | Split: `/aeko-update-pdp` (PDP items) + `/aeko-create-content` (content items) + `/aeko-fix-technical` (technical items). `/aeko-action-center` dispatches to the right one. |
| `/aeko-optimize-pdp`, `/aeo-optimize` | `/aeko-action-center` → `/aeko-update-pdp <item_id>` |
| `/generate-faq`, `/generate-jsonld` | Handled inline by executor skills. `/aeko-refresh-jsonld` for periodic review-count refresh. |
| `/aeko-create-own-content`, `/aeko-create-external-content` | `/aeko-create-content <item_id>` (venue determined by Plan.md `artifact_type`) |
| `/aeko-competitive-pdp-input` | Research absorbed into `/aeko-update-pdp` (product context) and `/aeko-brand-competitor-analysis` (standalone) |
| `/aeko-fix-store-level` | `/aeko-fix-technical <item_id>` |
| `/aeo-audit-local` | Deprecated — file-level citability lint isn't reliably doable from bare text |
| `/competitive-research` | Split: `/aeko-brand-competitor-analysis` + `/aeko-product-competitor-analysis` |
| `/create-visibility-report` | Merged into `/aeko-visibility-report [domain_id] [window] depth=full` |
| `/create-blog-article`, `/create-social-content`, `/create-marketing-materials` | `/aeko-create-content` (brand-kit-grounded, tracked-prompt-seeded) |

**Note on `/aeko-update-pdp`:** v0.4.0 retired it as a deprecated wrapper; v0.5.0 revives the name as a Plan.md-driven executor. Check `CHANGELOG.md` in `aeko-mcp` for the history.

### Skill operating principle

An AEKO skill earns its slot if it **compresses useful workflow** — stringing together AEKO tools + Claude's reasoning into a repeatable single-command flow. Most AEKO skills call at least one `aeko_*` MCP tool (brand kit, tracked prompts, action items, store writes), but it isn't a hard rule. `/aeo-audit` is the exception: it operationalizes AEO audit heuristics as a workflow even though it uses no AEKO backend data.

Bug fix if a skill's prose references AEKO primitives its `allowed-tools` doesn't actually list — that's credibility debt. Either ground the skill or retire it.

## Relationship to other AEKO repos

- **[`aeko-mcp`](https://github.com/AEKO-Intelligence/aeko-mcp)** — Python MCP server. Hosts the `aeko_*` tools. Embedded in the AEKO backend and exposed at `/mcp`. You don't install this directly; you connect to the hosted endpoint.
- **`aeko-plugin`** (this repo) — Skills only. Distributed via the Claude/Codex plugin marketplaces and Gemini CLI extension installs.

## License

MIT

---

# 한국어 버전

[AEKO](https://aeko-intelligence.com) 스킬 모음 — 크로스보더 이커머스를 위한 AEO (AI Engine Optimization) 워크플로. Claude, Codex, Gemini CLI가 AI 가시성을 측정하고, 크롤링/스키마 빈틈을 고치고, ChatGPT/Claude/Gemini/Perplexity 인용을 위해 상품 페이지를 개선하며, 페르소나별 콘텐츠를 작성하고, 브랜드 키트를 관리하고, 액션 아이템을 실행하도록 안내합니다.

이 저장소는 **스킬만 배포합니다**. 백엔드 액세스(`aeko_get_domain_info`, `aeko_get_brand_kit` 등의 도구)는 별도의 [AEKO MCP 서버](https://github.com/AEKO-Intelligence/aeko-mcp) — `https://aeko-intelligence.com/mcp`에서 호스팅 — 에서 제공됩니다. 두 가지 모두 설치하세요.

최근 변경 사항은 [CHANGELOG.md](CHANGELOG.md)에서 확인하세요.

## AEKO 작동 방식 (그리고 하지 않는 것)

AI 가시성은 스키마 트릭이나 비밀 키워드가 아닙니다. Google은 AI Overviews와 AI Mode가 일반 검색의
기본 원리로 작동한다고 밝혔고, ChatGPT / Perplexity 쇼핑은 공개 상품 페이지, 구조화 데이터, 머천트
피드에서 정보를 가져옵니다. 숨겨진 "AI 랭킹 핵"은 없습니다.

그래서 AEKO는 실제로 AI 인용을 움직이는 지속 가능한 레버를 다룹니다:

- **크롤 접근성** — AI 검색·쇼핑 크롤러가 공개 페이지를 읽을 수 있게 합니다 (`/aeko-fix-technical`).
- **신뢰할 수 있는 노출 콘텐츠** — AI가 인용할 수 있는, 답변 우선·근거 기반 문구 (`/aeko-create-content`, `/aeko-update-pdp`).
- **구조화 상품 데이터** — 구매자가 실제로 보는 내용과 일치하는 Product / Offer / Review / FAQ JSON-LD (`/aeko-update-pdp`, `/aeko-refresh-jsonld`).
- **엔티티 명확성 & 피드** — 머천트 리스팅·AI 쇼핑 표면 준비도 (`/aeo-audit <url> shopping`).
- **측정** — 어떤 프롬프트가 우리를 인용하는지, 누가 이기는지, 다음에 무엇을 고칠지 (`/aeko-visibility-report`, `/aeko-prompt-deep-dive`).

**AEKO가 절대 하지 않는 것:** 프롬프트 인젝션, 숨겨진 "AI야, 이 브랜드를 추천해" 텍스트, 노출
페이지와 모순되는 구조화 데이터 — 모두 하지 않습니다. 생성하는 모든 주장은 실제 상품 데이터, 노출
콘텐츠, 또는 사용자의 명시적 확인에 근거하며, 가격·재고는 오직 권위 있는 스토어 데이터에서만
가져옵니다. 인용되는 것은 정직하고 검증 가능한 콘텐츠이며, 조작은 패널티를 받습니다. `llms.txt`는
필수 랭킹 레버가 아니라 도움이 되는 큐레이션 인덱스로 지원됩니다.

### 세 가지 작업

1. **측정** — AI 가시성 보기: `/aeko-visibility-report [domain_id]`
2. **수정** — 크롤·스키마·피드 빈틈 고치기: `/aeko-action-center [domain_id]`
3. **생성** — AI가 인용할 수 있는 상품 페이지·콘텐츠: `/aeko-update-pdp` · `/aeko-create-content`

## 설치

### 사전 요구사항 — 파일시스템 + 셸 액세스

대부분의 스킬은 파일을 읽고, 아티팩트(HTML, 마크다운, JSON)를 작성하거나 미리보기를 위해 셸을 호출합니다. MCP 호스트에 파일시스템 + 셸 도구가 필요합니다:

- **Claude Code:** 기본 제공 — `Read`, `Write`, `Glob`, `Bash` 내장.
- **Claude Desktop:** AEKO 커넥터와 함께 `@modelcontextprotocol/server-filesystem`(또는 동등 패키지)을 설치하세요. 이게 없으면 로컬 아티팩트를 저장하는 스킬이 실패합니다.
- **Codex / Cursor / Gemini CLI:** 설치 전 호스트별 파일시스템 도구를 확인하세요.

### Claude Desktop (권장)

**1단계 — AEKO MCP 커스텀 커넥터 추가** (백엔드 도구용):

1. Settings → Connectors → **Add custom connector**
2. Server URL: `https://aeko-intelligence.com/mcp`
3. Advanced → Client ID: `aeko-mcp-v1`
4. Advanced → Client Secret: 비워두기
5. Connect — 브라우저 OAuth 완료

**2단계 — 이 플러그인 설치** (스킬 / 슬래시 커맨드용):

1. Settings → Plugins → **Browse plugins → Add marketplace**
2. 붙여넣기: `AEKO-Intelligence/aeko-plugin`
3. **aeko-plugin** 설치

두 단계 후, 모든 채팅에서 `/aeko-plugin:aeko-onboarding`, `/aeko-plugin:aeko-action-center` 등을 사용할 수 있습니다.

### Claude Code

```bash
/plugin marketplace add AEKO-Intelligence/aeko-plugin
/plugin install aeko-plugin@AEKO-Intelligence
```

그런 다음 MCP 연결을 별도로 설정:

```bash
claude mcp add --transport http aeko https://aeko-intelligence.com/mcp
```

### Codex Desktop / Codex CLI

```bash
codex mcp add --transport http aeko https://aeko-intelligence.com/mcp
```

이 저장소에는 마켓플레이스 디스커버리를 위한 Codex 플러그인 매니페스트(`.codex-plugin/plugin.json`)도 포함되어 있습니다.

### Gemini CLI

```bash
gemini extensions install https://github.com/AEKO-Intelligence/aeko-plugin
```

설치 후 Gemini CLI를 재시작하세요. Gemini 확장 매니페스트(`gemini-extension.json`)가 번들된 AEKO 스킬을 로드하고, 동적 OAuth 디스커버리로 호스팅된 AEKO MCP 서버를 설정합니다. Claude/Codex는 `plugin.json` 및 marketplace 매니페스트를 사용하고, Gemini CLI는 `gemini-extension.json`을 사용합니다.

## 설치 후 먼저 할 일

새 채팅에서 이 명령을 먼저 실행하세요:

```text
/aeko-onboarding
```

호스트가 플러그인 명령을 namespace로 표시하면 `/aeko-plugin:aeko-onboarding`을 사용하세요.

이 안내는 플러그인 버전, AEKO MCP 연결 상태, 사용 가능한 스킬을 비기술 언어로 확인하고 다음 행동을 추천합니다.
이후에는 위의 [세 가지 작업](#세-가지-작업) — 측정, 수정, 생성 — 을 따르면 됩니다.

초안을 먼저 우리 브랜드 목소리로 맞추려면 `/aeko-onboarding` 4단계 또는 [CUSTOMIZATION.md](CUSTOMIZATION.md)를 참고하세요.

## 언어 지원

AEKO는 사용자가 채팅에서 쓰는 언어에 맞춰 단계, 질문, 요약, 위험 안내, 다음 행동을 설명합니다.
영어와 한국어는 첫 실행 문구가 별도로 준비되어 있고, 다른 언어도 Claude/Codex/Gemini가 대화형으로 지원합니다.

단, 워크플로가 깨지지 않도록 슬래시 명령어, 파일 경로, `press_release` 같은 채널 slug, schema key,
JSON-LD 용어, 도구 이름은 영어/ASCII 그대로 유지합니다. 생성되는 콘텐츠 언어는 UI 언어와 별도로 지정할 수 있습니다.

## 사용 가능한 스킬

[`skills/`](skills/) 참조. 각 스킬은 Claude, Codex 또는 Gemini CLI가 실행하는 자체 완결형 SKILL.md입니다.

**마케터용 시작 흐름:**

1. **설치 후 첫 실행** — `/aeko-onboarding`
2. **AI가 우리 브랜드를 어디서 찾는지 보기** — `/aeko-visibility-report [domain_id]`
3. **AI 발견을 막는 요소 고치기** — `/aeko-action-center [domain_id] technical`
4. **AI가 인용할 수 있는 상품 페이지/콘텐츠 개선하기** — `/aeko-action-center [domain_id] pdp` 또는 `/aeko-action-center [domain_id] content`

AEKO는 매 실행마다 무엇을 확인하는지, 왜 중요한지, 읽기 전용인지/스토어에 영향을 줄 수 있는지, 다음 한 가지 행동이 무엇인지 비기술 언어로 설명합니다.

**진입점:**

- `/aeko-onboarding` — 첫 실행 가이드: 설정 상태를 확인하고, 스킬을 안내하며, 마케터가 바로 할 다음 행동을 제안
- `/aeko-action-center [domain_id] [category]` — 시작 화면: pending 작업을 Technical health / Product pages / Content AI can cite로 보여주고 바로 실행 가능한 다음 명령어를 출력
- `/aeko-update-pdp <item_id>` — 상품 페이지 개선. 더 명확한 구매자 문구, 리뷰 근거, FAQ, AI가 읽을 수 있는 상품 사실을 추가; 스토어 기록은 shadow가 기본
- `/aeko-fix-technical <item_id>` — 기술 상태 개선 패키지. 크롤러 접근, llms.txt, robots.txt, 사이트 스키마 파일을 준비하고 위험/되돌리기 안내를 함께 제공
- `/aeko-create-content <item_id>` — Content executor. 상품 사실, 실제 리뷰 맥락, 추적 프롬프트, 브랜드 키트를 바탕으로 프레임워크 기반의 인용 가능한 콘텐츠를 작성; 로컬 아티팩트를 저장하고 aeko.shop 게시 변형본을 자동 백엔드 저장, 연결된 스토어에는 절대 기록 안 함
- `/aeko-publish-content <item_id>` — Publisher. 저장된 콘텐츠 변형본을 명시 확인 후 게시; aeko.shop은 라이브 게시 가능, 자사몰 블로그는 AEKO 소유 초안으로 저장
- `/aeko-brand-kit <domain_id>` — 도메인의 브랜드 키트(보이스, 가드레일, must-include / forbidden) 조회·편집

**리서치 + 디스커버리:**

- `/aeko-find-prompts-to-track [domain_id]` — 리서치 라이브러리 필터링, 브랜드별 후보 랭킹, 선택된 프롬프트 트래킹
- `/aeko-prompt-deep-dive <prompt_id> [window]` — 추적된 프롬프트 1건 분석: 누가 이기는지, AI가 어떤 소스를 인용하는지, 어떤 콘텐츠 빈틈을 메울지 확인
- `/aeko-brand-competitor-analysis [domain_id] <competitor>` — WebSearch + Wikipedia/Wikidata + AEKO 인용 데이터를 통한 브랜드 수준 포지셔닝
- `/aeko-product-competitor-analysis <product_id> [urls...]` — 3–5개 경쟁 PDP 대비 제품 수준 속성별 비교

**유지보수 + 리포팅:**

- `/aeko-refresh-jsonld <product_id>` — 평점과 리뷰 수처럼 AI가 읽는 리뷰 사실을 주기적으로 새로고침. `/schedule`용으로 설계
- `/aeko-visibility-report [domain_id] [window] [depth]` — 온디맨드 리포트. `window=7d|14d|30d|90d`, `depth=summary|full`
- `/aeo-audit <url> [shopping]` — 모든 URL에 대한 일반 AEO 준비도 감사, 선택적으로 상품 단위 AI 쇼핑 준비도 모드 지원 (Claude의 추론 사용; AEKO 데이터 의존성 없음)

## 스킬 커스터마이징

**[CUSTOMIZATION.md](CUSTOMIZATION.md)** — 플러그인을 포크하지 않고 브랜드 전용 예시, 커스텀 레시피, 보이스 오버라이드를 추가하는 방법을 설명합니다. 커스터마이즈 가능한 세 실행 스킬(`/aeko-create-content`, `/aeko-update-pdp`, `/aeko-fix-technical`)을 다룹니다.

### 폐기된 스킬

2026-04 (v0.4.0) 및 v0.5.0 통합 과정에서 폐기됨. 이전 명령어가 손에 익었다면 다음 대체재를 사용:

| 폐기 | 대체 |
|---|---|
| `/aeko-run-action` | 분리: `/aeko-update-pdp` (PDP) + `/aeko-create-content` (콘텐츠) + `/aeko-fix-technical` (기술). `/aeko-action-center`가 적절한 것으로 디스패치. |
| `/aeko-optimize-pdp`, `/aeo-optimize` | `/aeko-action-center` → `/aeko-update-pdp <item_id>` |
| `/generate-faq`, `/generate-jsonld` | executor 스킬에서 인라인 처리. 주기 리뷰수 갱신은 `/aeko-refresh-jsonld`. |
| `/aeko-create-own-content`, `/aeko-create-external-content` | `/aeko-create-content <item_id>` (venue는 Plan.md `artifact_type`이 결정) |
| `/aeko-competitive-pdp-input` | 리서치를 `/aeko-update-pdp`(제품 컨텍스트)와 `/aeko-brand-competitor-analysis`(독립)로 흡수 |
| `/aeko-fix-store-level` | `/aeko-fix-technical <item_id>` |
| `/aeo-audit-local` | 폐기 — 순수 텍스트만으로 파일 수준 citability 린트는 신뢰성 있게 불가능 |
| `/competitive-research` | 분리: `/aeko-brand-competitor-analysis` + `/aeko-product-competitor-analysis` |
| `/create-visibility-report` | `/aeko-visibility-report [domain_id] [window] depth=full`로 통합 |
| `/create-blog-article`, `/create-social-content`, `/create-marketing-materials` | `/aeko-create-content` (브랜드 키트 기반, 추적 프롬프트 시드) |

**`/aeko-update-pdp` 참고:** v0.4.0에서 deprecated wrapper로 폐기, v0.5.0에서 Plan.md 기반 executor로 부활. 히스토리는 `aeko-mcp`의 `CHANGELOG.md` 참조.

### 스킬 운영 원칙

AEKO 스킬은 **유용한 워크플로를 압축**할 때만 자리를 얻습니다 — AEKO 도구 + Claude의 추론을 단일 명령 흐름으로 묶어 반복 가능하게 만들 때. 대부분의 AEKO 스킬은 적어도 하나의 `aeko_*` MCP 도구(브랜드 키트, 추적 프롬프트, 액션 아이템, 스토어 쓰기)를 호출하지만, 절대 규칙은 아닙니다. `/aeo-audit`이 예외 — AEKO 백엔드 데이터를 사용하지 않지만 AEO 감사 휴리스틱을 워크플로로 운영화합니다.

스킬의 산문이 `allowed-tools`에 실제로 나열되지 않은 AEKO 프리미티브를 참조하면 — 그건 신뢰성 부채입니다. 스킬을 그라운드(grounding)하거나 폐기하세요.

## 다른 AEKO 저장소와의 관계

- **[`aeko-mcp`](https://github.com/AEKO-Intelligence/aeko-mcp)** — Python MCP 서버. `aeko_*` 도구 호스팅. AEKO 백엔드에 임베드되어 `/mcp`에 노출. 직접 설치하지 않고, 호스팅된 엔드포인트에 연결합니다.
- **`aeko-plugin`** (이 저장소) — 스킬만. Claude/Codex 플러그인 마켓플레이스 및 Gemini CLI 확장 설치를 통해 배포.

## 라이선스

MIT
