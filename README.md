# AEKO Plugin

> 한국어 버전은 아래를 참고하세요 → [한국어](#한국어-버전).

Skills for [AEKO](https://aeko-intelligence.com) — AEO (AI Engine Optimization) workflows for cross-border ecommerce. Guides Claude and Codex through optimizing product pages for ChatGPT/Claude/Gemini/Perplexity citations, drafting persona-targeted content, generating JSON-LD, managing brand kits, and executing action items.

This repo ships **skills only**. Backend access (tools like `aeko_get_domain_info`, `aeko_get_brand_kit`, etc.) comes from the separate [AEKO MCP server](https://github.com/AEKO-Intelligence/aeko-mcp), hosted at `https://aeko-intelligence.com/mcp`. Install both.

## Install

### Prerequisite — filesystem + shell access

Most skills read files, write artifacts (HTML, markdown, JSON), or shell out to open previews. Your MCP host needs filesystem + shell tools for these to work:

- **Claude Code:** native — `Read`, `Write`, `Glob`, `Bash` are built-in.
- **Claude Desktop:** install `@modelcontextprotocol/server-filesystem` (or equivalent) alongside the AEKO connector. Skills that save local artifacts will fail without it.
- **Codex / Cursor:** verify per-host filesystem tooling before install.

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

After both steps, `/aeko-plugin:aeko-brand-kit`, `/aeko-plugin:aeko-action-center`, etc. are available in any chat.

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

## Available Skills

See [`skills/`](skills/). Each is a self-contained SKILL.md consumed by Claude or Codex.

**Entry points:**

- `/aeko-action-center [domain_id] [category]` — router: lists pending items in three categories (Technical / PDP / Content generation) and prints ready-to-copy executor commands
- `/aeko-update-pdp <item_id>` — PDP executor. Fetches Plan.md, asks image strategy, WebFetches the live page, generates responsive HTML + JSON-LD, writes to store (shadow-by-default) with audit trail
- `/aeko-fix-technical <item_id>` — Technical executor. Generates llms.txt / robots.txt patches / site-level JSON-LD with embedded spec rules
- `/aeko-create-content <item_id>` — Content executor. Pulls tracked-prompt citation forensics to mimic winning source structures; saves locally, never writes to store
- `/aeko-brand-kit <domain_id>` — view or edit your domain's brand kit (voice, guardrails, must-include / forbidden)

**Research + discovery:**

- `/aeko-find-prompts-to-track [domain_id]` — filter the research library, rank candidates for your brand, track selected prompts
- `/aeko-prompt-deep-dive <prompt_id> [window]` — citation-forensics on one tracked prompt (which competitors win it, which sources AI cites, what to mirror)
- `/aeko-brand-competitor-analysis [domain_id] <competitor>` — brand-level positioning via WebSearch + Wikipedia/Wikidata + AEKO citation data
- `/aeko-product-competitor-analysis <product_id> [urls...]` — product-level property-by-property comparison against 3-5 competing PDPs

**Maintenance + reporting:**

- `/aeko-refresh-jsonld <product_id>` — periodic JSON-LD refresh (review counts, ratings) via read-patch-write. Designed for `/schedule`
- `/aeko-visibility-report [domain_id] [window] [depth]` — on-demand report. `window=7d|14d|30d|90d`, `depth=summary|full`
- `/aeo-audit <url>` — generic AEO readiness audit for any URL (uses Claude's reasoning; no AEKO data dependency)

## Customizing skills

**[CUSTOMIZATION.md](CUSTOMIZATION.md)** explains how to add brand-specific examples, custom recipes, and voice overrides without forking the plugin. Currently covers `/aeko-create-content` (Skills 2.0 / progressive-disclosure pattern with `references/` folder); future skills will follow the same model.

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
- **`aeko-plugin`** (this repo) — Skills only. Distributed via the Claude/Codex plugin marketplaces.

## License

MIT

---

# 한국어 버전

[AEKO](https://aeko-intelligence.com) 스킬 모음 — 크로스보더 이커머스를 위한 AEO (AI Engine Optimization) 워크플로. Claude와 Codex가 ChatGPT/Claude/Gemini/Perplexity 인용을 위해 상품 페이지를 최적화하고, 페르소나별 콘텐츠를 작성하며, JSON-LD를 생성하고, 브랜드 키트를 관리하고, 액션 아이템을 실행하도록 안내합니다.

이 저장소는 **스킬만 배포합니다**. 백엔드 액세스(`aeko_get_domain_info`, `aeko_get_brand_kit` 등의 도구)는 별도의 [AEKO MCP 서버](https://github.com/AEKO-Intelligence/aeko-mcp) — `https://aeko-intelligence.com/mcp`에서 호스팅 — 에서 제공됩니다. 두 가지 모두 설치하세요.

## 설치

### 사전 요구사항 — 파일시스템 + 셸 액세스

대부분의 스킬은 파일을 읽고, 아티팩트(HTML, 마크다운, JSON)를 작성하거나 미리보기를 위해 셸을 호출합니다. MCP 호스트에 파일시스템 + 셸 도구가 필요합니다:

- **Claude Code:** 기본 제공 — `Read`, `Write`, `Glob`, `Bash` 내장.
- **Claude Desktop:** AEKO 커넥터와 함께 `@modelcontextprotocol/server-filesystem`(또는 동등 패키지)을 설치하세요. 이게 없으면 로컬 아티팩트를 저장하는 스킬이 실패합니다.
- **Codex / Cursor:** 설치 전 호스트별 파일시스템 도구를 확인하세요.

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

두 단계 후, 모든 채팅에서 `/aeko-plugin:aeko-brand-kit`, `/aeko-plugin:aeko-action-center` 등을 사용할 수 있습니다.

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

## 사용 가능한 스킬

[`skills/`](skills/) 참조. 각 스킬은 Claude 또는 Codex가 실행하는 자체 완결형 SKILL.md입니다.

**진입점:**

- `/aeko-action-center [domain_id] [category]` — 라우터: pending 아이템을 세 카테고리(Technical / PDP / Content generation)로 나열하고 바로 실행 가능한 executor 커맨드를 출력
- `/aeko-update-pdp <item_id>` — PDP executor. Plan.md를 가져오고, 이미지 전략을 묻고, 라이브 페이지를 WebFetch하고, 반응형 HTML + JSON-LD를 생성하여 스토어에 기록(shadow 기본) — 감사 추적 포함
- `/aeko-fix-technical <item_id>` — Technical executor. llms.txt / robots.txt 패치 / 사이트 수준 JSON-LD를 임베디드 스펙 규칙과 함께 생성
- `/aeko-create-content <item_id>` — Content executor. 추적된 프롬프트의 인용 포렌식으로 우승 소스 구조를 모방; 로컬에 저장만, 스토어에는 절대 기록 안 함
- `/aeko-brand-kit <domain_id>` — 도메인의 브랜드 키트(보이스, 가드레일, must-include / forbidden) 조회·편집

**리서치 + 디스커버리:**

- `/aeko-find-prompts-to-track [domain_id]` — 리서치 라이브러리 필터링, 브랜드별 후보 랭킹, 선택된 프롬프트 트래킹
- `/aeko-prompt-deep-dive <prompt_id> [window]` — 추적된 프롬프트 한 개에 대한 인용 포렌식 (어떤 경쟁자가 이기는지, AI가 어떤 소스를 인용하는지, 무엇을 모방할지)
- `/aeko-brand-competitor-analysis [domain_id] <competitor>` — WebSearch + Wikipedia/Wikidata + AEKO 인용 데이터를 통한 브랜드 수준 포지셔닝
- `/aeko-product-competitor-analysis <product_id> [urls...]` — 3–5개 경쟁 PDP 대비 제품 수준 속성별 비교

**유지보수 + 리포팅:**

- `/aeko-refresh-jsonld <product_id>` — 리뷰 수, 평점 등 JSON-LD 주기 갱신 (read-patch-write). `/schedule`용으로 설계
- `/aeko-visibility-report [domain_id] [window] [depth]` — 온디맨드 리포트. `window=7d|14d|30d|90d`, `depth=summary|full`
- `/aeo-audit <url>` — 모든 URL에 대한 일반 AEO 준비도 감사 (Claude의 추론 사용; AEKO 데이터 의존성 없음)

## 스킬 커스터마이징

**[CUSTOMIZATION.md](CUSTOMIZATION.md)** — 플러그인을 포크하지 않고 브랜드 전용 예시, 커스텀 레시피, 보이스 오버라이드를 추가하는 방법을 설명합니다. 현재 `/aeko-create-content`를 다룹니다 (`references/` 폴더를 사용한 Skills 2.0 / 점진적 공개 패턴). 향후 스킬도 동일 모델을 따를 예정입니다.

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
- **`aeko-plugin`** (이 저장소) — 스킬만. Claude/Codex 플러그인 마켓플레이스를 통해 배포.

## 라이선스

MIT
