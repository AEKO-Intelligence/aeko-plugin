# AEKO Plugin

> 한국어 버전은 아래를 참고하세요 → [한국어](#한국어-버전).

Skills for cross-border ecommerce marketing in Claude, Codex, and Gemini CLI. Audit public sites and
product pages, build PDP HTML, review advertising through your own connectors, measure traffic and AI
visibility, operate guarded marketing workflows, and assemble a weekly read-and-propose loop.

This repository ships **skills, supporting recipes, and evaluation guidance**. AEKO-backed tools come from the separate
[AEKO MCP server](https://github.com/AEKO-Intelligence/aeko-mcp), hosted at
`https://aeko-intelligence.com/mcp`. The plugin does not claim native Meta, Google Ads, TikTok, GA4,
Notion, Slack, or Calendar integrations: free connector paths read the customer's own installed
connectors after capability detection.

Recent changes are tracked in [CHANGELOG.md](CHANGELOG.md).

## Works with no AEKO account

The free catalog is:

- `/aeko-site-audit <site-root-url-or-domain>` — audit whether a public site is readable by AI.
- `/aeko-pdp-audit <product-page-url-or-local-html-file>` — audit one PDP, including facts trapped in detail images.
- `/aeko-pdp-build <aeko_pdp_image_facts/v1-json-or-product-url>` — build paste-ready PDP HTML and matching JSON-LD.
- `/aeko-ads-review [week-of] [platforms=meta,tiktok,google,openai]` — render the same four-platform glance every time: Meta/TikTok/Google Ads use your connectors or exports, while only the OpenAI Ads row requires AEKO.
- `/aeko-ga4 [window]` — read the customer's own official GA4 connector for free. Its optional AEKO GA4 join requires AEKO.
- `/aeko-connect` — show which capability slots are filled and the exact steps for filling the rest.
- `/aeko-start` — tour the plugin and route to a useful first workflow without probing an AEKO account.
- `/aeko-weekly-report [window]` — assemble normalized rows from the simple skills, degrading per source.
- `/aeko-create-loop` — interactively compose and dry-run a schedule on the current host.
- `/aeko-run-loop config=<notion-page-id>` — run the scheduled entry point in read-and-propose mode.

The first three `/aeko-ads-review` rows and the free `/aeko-ga4` path use customer-owned connectors; AEKO
contributes none of those vendor numbers. The fourth ads row comes from AEKO and exposes spend/efficiency,
while its conversion and ROAS cells remain dashed because those metrics are not ingested. If a connector is
unavailable, the skills show an exact manual export or connect path instead of treating absence as zero.

The AEKO connector is needed for AI-answer monitoring and source history, tracked prompts, Action items,
store changes, publishing, OpenAI Ads operations, and the AEKO GA4 join. `/aeko-content-ideas` checks the connected deployment for
`aeko_list_content_ideas`, `aeko_start_content_idea`, and `aeko_dismiss_content_idea`. These wrappers
exist in sibling MCP source; an older deployment may still lack them.

Scheduling does not add marketing-write capability. `/aeko-create-loop` is an interactive composer, and
`/aeko-run-loop` reads approvals and evidence but only proposes changes. Scheduled marketing writes remain
unsupported in the plugin loop; AEKO hosted automation is a separate capability. A cloud schedule also needs Notion or Slack for a durable
destination and approval surface.

## How AEKO works (and what it will not do)

AI visibility is not a schema trick or a secret keyword. AEKO works the durable levers that make public
information easier to crawl, understand, verify, and cite:

- **Access and structure** — `/aeko-site-audit`, `/aeko-pdp-audit`, `/aeko-fix-technical`.
- **Visible product evidence** — `/aeko-pdp-build`, `/aeko-update-pdp`, `/aeko-create-content`.
- **Measurement and reconciliation** — `/aeko-ga4`, `/aeko-ads-review`, `/aeko-ai-visibility`, `/aeko-weekly-report`.
- **Guarded execution** — `/aeko-action-center`, `/aeko-store`, `/aeko-publish-content`, `/aeko-openai-guardrails`.

AEKO does not create hidden recommendation text, fabricate claims, or publish structured data that
contradicts visible content. Prices and availability come only from authoritative store evidence. Marketing
writes keep their documented confirmation and undo gates; scheduled runs do not perform them.

## Install

### Prerequisite — host capabilities

Some skills save local artifacts or open previews and need the host's filesystem and shell tools. Free
measurement and delivery paths need the customer's corresponding connectors. Run `/aeko-connect` to inspect
capabilities by schema and provider metadata rather than guessing from tool names.

Review-platform credentials and ad-account tokens are dashboard-only; no skill can complete those credential
flows.

### Claude Desktop

Install the plugin from **Settings → Plugins → Browse plugins → Add marketplace** using
`AEKO-Intelligence/aeko-plugin`. The zero-account workflows are ready immediately.

For optional AEKO-backed workflows, add a custom connector at
`https://aeko-intelligence.com/mcp` and complete OAuth. Do not connect AEKO merely to use the free catalog.

### Claude Code

```bash
/plugin marketplace add AEKO-Intelligence/aeko-plugin
/plugin install aeko-plugin@aeko-plugin
```

Optional AEKO connection:

```bash
claude mcp add --transport http aeko https://aeko-intelligence.com/mcp
```

### Codex Desktop / Codex CLI

Install from the Codex plugin catalog or use the manifest at `.codex-plugin/plugin.json`. Optional AEKO
connection:

```bash
codex mcp add --transport http aeko https://aeko-intelligence.com/mcp
```

### Gemini CLI

```bash
gemini extensions install https://github.com/AEKO-Intelligence/aeko-plugin
```

Restart Gemini CLI after installation. Gemini uses `gemini-extension.json`; Claude and Codex use their
respective plugin manifests.

## After install

Start a new chat with:

```text
/aeko-start
```

Use `/aeko-connect` when you want the capability slot board. If the host namespaces plugin commands, use
the host's displayed plugin prefix, for example `/aeko-plugin:aeko-start`.

## Language support

User-facing questions, summaries, risk notes, and next actions mirror the chat language. English and Korean
have curated copy; other languages are supported conversationally. Commands, slugs, paths, IDs, provider
labels, schema keys, JSON-LD terms, and the brand mark `AEKO` stay in English/ASCII.

## Skill catalog by job

The shipped catalog contains 26 active skills. Each active folder under [`skills/`](skills/) contains one
`SKILL.md`; compatibility-only command stubs are intentionally not shipped because this is the catalog's
first release.

### Start and connect

- `/aeko-start` — zero-account first-run tour and routing.
- `/aeko-connect` — capability slot board for AEKO, ads, analytics, store, docs/Notion, chat/Slack, and calendar.

### Audit, build, and fix

- `/aeko-site-audit` — public site readability audit.
- `/aeko-pdp-audit` — product-page citability and image-dependency audit.
- `/aeko-pdp-build` — verified-fact PDP HTML and JSON-LD builder; never writes to a store.
- `/aeko-action-center [domain_id] [category]` — review and dispatch AEKO Action items.
- `/aeko-update-pdp <item_id>` — guarded PDP executor; `mode=refresh` surgically refreshes review JSON-LD.
- `/aeko-fix-technical <item_id>` — crawler, sitemap, `llms.txt`, robots, and site-schema fix package.

### Measure and report

- `/aeko-ads-review` — four-row cross-platform glance: three free customer-connector rows plus an account-gated OpenAI Ads spend/efficiency row whose conversion and ROAS cells are explicitly unavailable.
- `/aeko-openai-ads-reporting [domain_id] [days]` — account-gated OpenAI Ads depth report with top/bottom campaign, ad-group, ad, and product rankings plus an optional organic AI-visibility fold.
- `/aeko-ga4` — customer-owned GA4 connector or optional AEKO GA4 join.
- `/aeko-ai-visibility [domain_id] [window] [depth]` — AI visibility, Share of Voice, and answer drift.
- `/aeko-source-analysis` — tracked-answer or cited-page source analysis with full AEKO evidence when connected.
- `/aeko-message-audit` — spend-ranked paid-message claims, with optional owned-backing and AI-answer checks.
- `/aeko-weekly-report [window]` — provenance-carrying composite report with no direct MCP calls.

### Research and control

- `/aeko-manage-prompts mode=discover|review` — prompt discovery, tracking, Views, Contexts, suggestions, and guarded untracking.
- `/aeko-competitor-analysis scope=brand|product` — free public research stage plus optional AEKO enrichment.
- `/aeko-content-ideas` — account-gated content-idea review/start/dismiss flow with live MCP capability checks.

### Store and content

- `/aeko-store mode=setup|reviews` — domain/store setup and the agent's only review-intake path.
- `/aeko-create-content <item_id>` — evidence-grounded content executor.
- `/aeko-publish-content <item_id>` — guarded publisher for saved content variations.

### Ads operations

- `/aeko-openai-compose-ads [domain_id] [min_score]` — account-gated composition of paused, review-grounded OpenAI Ads groups.
- `/aeko-openai-budget-shift [domain_id] [days]` — account-gated dry-run OpenAI Ads budget and entity-state changes with caps and explicit confirmation.
- `/aeko-openai-guardrails [domain_id]` — account-gated preview, arm, inspection, and emergency stop for OpenAI Ads automation.

### Weekly loop

- `/aeko-create-loop` — interview, durable Notion config, host-specific schedule composition, and foreground dry run.
- `/aeko-run-loop config=<notion-page-id>` — approvals-first scheduled read-and-propose entry point.

## Customizing skills

[CUSTOMIZATION.md](CUSTOMIZATION.md) describes brand-owned skill/eval packages, manual edits, scoped
examples, and the seam for the planned automated updater. Hosted runs and exports must select the same
version; private AEKO benchmarks never ship. [Whole-job prompt examples](docs/automation-prompt-examples.md)
keep the saved task prompt separate from attached skills and label unavailable hosted execution.
The automatic updater, multi-stage hosted agent runner, and GitHub synchronization are not implemented
by this plugin.

## Relationship to other AEKO repositories

- [`aeko-mcp`](https://github.com/AEKO-Intelligence/aeko-mcp) — optional hosted AEKO tool server.
- `aeko-plugin` — this skills-only plugin for Claude, Codex, and Gemini CLI.

## License

MIT

---

# 한국어 버전

Claude, Codex, Gemini CLI에서 사용하는 크로스보더 이커머스 마케팅 스킬 모음입니다. 공개 사이트와
상품 페이지를 감사하고, PDP HTML을 만들고, 사용자의 자체 커넥터로 광고를 검토하고, 트래픽과 AI
가시성을 측정하며, 보호된 마케팅 워크플로와 주간 읽기·제안 루프를 구성합니다.

이 저장소는 **스킬만 배포합니다**. AEKO 기반 도구는 별도의
[AEKO MCP 서버](https://github.com/AEKO-Intelligence/aeko-mcp)에서 제공하며,
`https://aeko-intelligence.com/mcp`에 호스팅됩니다. 이 플러그인은 Meta, Google Ads, TikTok, GA4,
Notion, Slack, Calendar와의 자체 통합을 주장하지 않습니다. 무료 커넥터 경로는 capability detection
후 사용자가 설치한 자체 커넥터를 읽습니다.

최근 변경 사항은 [CHANGELOG.md](CHANGELOG.md)에서 확인하세요.

## AEKO 계정 없이 사용

무료 카탈로그는 다음과 같습니다:

- `/aeko-site-audit <site-root-url-or-domain>` — 공개 사이트를 AI가 읽을 수 있는지 감사합니다.
- `/aeko-pdp-audit <product-page-url-or-local-html-file>` — 상세 이미지에 갇힌 사실을 포함해 PDP 한 개를 감사합니다.
- `/aeko-pdp-build <aeko_pdp_image_facts/v1-json-or-product-url>` — 붙여넣기 가능한 PDP HTML과 일치하는 JSON-LD를 만듭니다.
- `/aeko-ads-review [week-of] [platforms=meta,tiktok,google,openai]` — 항상 같은 4-platform 요약을 보여줍니다. Meta/TikTok/Google Ads는 자체 커넥터 또는 export를 사용하고 OpenAI Ads row만 AEKO가 필요합니다.
- `/aeko-ga4 [window]` — 사용자의 공식 GA4 커넥터를 무료로 읽습니다. 선택형 AEKO GA4 join에는 AEKO가 필요합니다.
- `/aeko-connect` — 채워진 capability slot과 나머지를 채우는 정확한 절차를 보여줍니다.
- `/aeko-start` — AEKO 계정을 확인하지 않고 플러그인을 안내하고 첫 워크플로로 라우팅합니다.
- `/aeko-weekly-report [window]` — 단순 스킬의 정규화된 row를 조합하고 소스별로 degrade합니다.
- `/aeko-create-loop` — 현재 호스트에서 대화형으로 schedule을 구성하고 dry-run합니다.
- `/aeko-run-loop config=<notion-page-id>` — 예약 진입점을 읽기·제안 모드로 실행합니다.

`/aeko-ads-review`의 첫 3개 row와 `/aeko-ga4` 무료 경로는 사용자가 소유한 커넥터를 사용하며,
해당 vendor 수치에 AEKO 데이터는 들어가지 않습니다. 네 번째 OpenAI Ads row는 AEKO의 지출/효율
수치를 사용하지만 전환과 ROAS는 아직 수집되지 않아 이유가 붙은 대시로 표시합니다. 커넥터가 없으면
0으로 처리하지 않고 정확한 수동 export 또는 연결 절차를 보여줍니다.

AI 답변 모니터링과 출처 이력, 추적 프롬프트, Action item, 스토어 변경, 게시, OpenAI Ads 운영,
AEKO GA4 join에는 AEKO 커넥터가 필요합니다. `/aeko-content-ideas`는 연결된 배포의
`aeko_list_content_ideas`, `aeko_start_content_idea`, `aeko_dismiss_content_idea` 기능을 확인합니다.
형제 MCP 소스에 구현되어 있으며, 이전 배포에서 빠진 기능만 unavailable로 표시합니다.

Schedule은 마케팅 쓰기 권한을 추가하지 않습니다. `/aeko-create-loop`는 대화형 composer이고,
`/aeko-run-loop`는 승인과 근거를 읽지만 변경을 제안하기만 합니다. 이 플러그인의 loop는
예약된 마케팅 쓰기를 지원하지 않습니다. AEKO 호스팅 자동화는 별도의 기능입니다. Cloud schedule에는 지속 가능한 목적지와 승인 공간으로
Notion 또는 Slack도 필요합니다.

## AEKO 작동 방식 (그리고 하지 않는 것)

AI 가시성은 스키마 트릭이나 비밀 키워드가 아닙니다. AEKO는 공개 정보를 더 쉽게 크롤하고,
이해하고, 검증하고, 인용하게 만드는 지속 가능한 레버를 다룹니다:

- **접근성과 구조** — `/aeko-site-audit`, `/aeko-pdp-audit`, `/aeko-fix-technical`.
- **노출된 상품 근거** — `/aeko-pdp-build`, `/aeko-update-pdp`, `/aeko-create-content`.
- **측정과 대조** — `/aeko-ga4`, `/aeko-ads-review`, `/aeko-ai-visibility`, `/aeko-weekly-report`.
- **보호된 실행** — `/aeko-action-center`, `/aeko-store`, `/aeko-publish-content`, `/aeko-openai-guardrails`.

AEKO는 숨겨진 추천 텍스트를 만들거나, 주장을 조작하거나, 노출 콘텐츠와 모순되는 구조화 데이터를
게시하지 않습니다. 가격과 재고는 권위 있는 스토어 근거만 사용합니다. 마케팅 쓰기는 문서화된 확인과
되돌리기 gate를 유지하며, 예약 실행은 이를 수행하지 않습니다.

## 설치

### 사전 요구사항 — 호스트 capability

일부 스킬은 로컬 아티팩트를 저장하거나 미리보기를 열기 위해 호스트의 파일시스템과 셸 도구가
필요합니다. 무료 측정과 전달 경로에는 사용자의 해당 커넥터가 필요합니다. `/aeko-connect`를 실행하면
도구 이름을 추측하지 않고 schema와 provider metadata로 capability를 확인합니다.

리뷰 플랫폼 자격 증명과 광고 계정 token은 dashboard-only이며 어떤 스킬도 해당 자격 증명 흐름을
완료할 수 없습니다.

### Claude Desktop

**Settings → Plugins → Browse plugins → Add marketplace**에서
`AEKO-Intelligence/aeko-plugin`을 사용해 설치하세요. 계정 없는 워크플로는 즉시 사용할 수 있습니다.

선택형 AEKO 기반 워크플로가 필요하면 `https://aeko-intelligence.com/mcp`를 custom connector로
추가하고 OAuth를 완료하세요. 무료 카탈로그만 사용하려고 AEKO를 연결할 필요는 없습니다.

### Claude Code

```bash
/plugin marketplace add AEKO-Intelligence/aeko-plugin
/plugin install aeko-plugin@aeko-plugin
```

선택형 AEKO 연결:

```bash
claude mcp add --transport http aeko https://aeko-intelligence.com/mcp
```

### Codex Desktop / Codex CLI

Codex 플러그인 카탈로그에서 설치하거나 `.codex-plugin/plugin.json` manifest를 사용하세요. 선택형 AEKO
연결:

```bash
codex mcp add --transport http aeko https://aeko-intelligence.com/mcp
```

### Gemini CLI

```bash
gemini extensions install https://github.com/AEKO-Intelligence/aeko-plugin
```

설치 후 Gemini CLI를 다시 시작하세요. Gemini는 `gemini-extension.json`, Claude와 Codex는 각각의
plugin manifest를 사용합니다.

## 설치 후 먼저 할 일

새 채팅에서 다음을 실행하세요:

```text
/aeko-start
```

Capability slot board가 필요하면 `/aeko-connect`를 사용하세요. 호스트가 플러그인 명령에 namespace를
붙이면 호스트가 표시한 prefix를 사용하세요. 예: `/aeko-plugin:aeko-start`.

## 언어 지원

사용자에게 보이는 질문, 요약, 위험 안내, 다음 행동은 채팅 언어를 따릅니다. 영어와 한국어는 직접
작성된 문구를 제공하며 다른 언어도 대화형으로 지원합니다. 명령어, slug, 경로, ID, provider label,
schema key, JSON-LD 용어, 브랜드 표기 `AEKO`는 영어/ASCII로 유지합니다.

## 작업별 스킬 카탈로그

배포 카탈로그에는 26개의 활성 스킬이 있습니다. [`skills/`](skills/) 아래 각 활성 폴더에는 하나의
`SKILL.md`가 있으며, 이번 카탈로그가 첫 릴리스이므로 호환 전용 명령 stub은 배포하지 않습니다.

### 시작과 연결

- `/aeko-start` — 계정 없는 첫 실행 안내와 라우팅.
- `/aeko-connect` — AEKO, ads, analytics, store, docs/Notion, chat/Slack, calendar의 capability slot board.

### 감사, 빌드, 수정

- `/aeko-site-audit` — 공개 사이트 가독성 감사.
- `/aeko-pdp-audit` — 상품 페이지 인용 준비도와 이미지 의존성 감사.
- `/aeko-pdp-build` — 검증된 사실 기반 PDP HTML 및 JSON-LD builder; 스토어에는 쓰지 않음.
- `/aeko-action-center [domain_id] [category]` — AEKO Action item 검토와 dispatch.
- `/aeko-update-pdp <item_id>` — 보호된 PDP executor; `mode=refresh`는 리뷰 JSON-LD만 정밀 갱신.
- `/aeko-fix-technical <item_id>` — crawler, sitemap, `llms.txt`, robots, 사이트 schema 수정 패키지.

### 측정과 리포트

- `/aeko-ads-review` — 3개의 무료 사용자 커넥터 row와 전환/ROAS가 명시적으로 unavailable인 AEKO 계정 기반 OpenAI Ads 지출/효율 row를 합친 4-platform 요약.
- `/aeko-openai-ads-reporting [domain_id] [days]` — 상·하위 campaign/ad group/ad/product와 선택형 organic AI visibility를 포함하는 계정 기반 OpenAI Ads 심층 리포트.
- `/aeko-ga4` — 사용자 소유 GA4 커넥터 또는 선택형 AEKO GA4 join.
- `/aeko-ai-visibility [domain_id] [window] [depth]` — AI 가시성, Share of Voice, answer drift.
- `/aeko-source-analysis` — 연결 시 완전한 AEKO 근거를 사용하는 추적 답변 또는 인용 페이지 출처 분석.
- `/aeko-message-audit` — 지출순 paid-message claim과 선택형 owned backing 및 AI 답변 확인.
- `/aeko-weekly-report [window]` — MCP를 직접 호출하지 않는 provenance 포함 composite 리포트.

### 리서치와 제어

- `/aeko-manage-prompts mode=discover|review` — 프롬프트 discovery, tracking, View, Context, suggestion, 보호된 untrack.
- `/aeko-competitor-analysis scope=brand|product` — 무료 공개 리서치 단계와 선택형 AEKO 보강.
- `/aeko-content-ideas` — 계정 기반 콘텐츠 아이디어 검토/start/dismiss 흐름; 연결된 MCP 기능을 확인.

### 스토어와 콘텐츠

- `/aeko-store mode=setup|reviews` — domain/store 설정과 에이전트의 유일한 review intake 경로.
- `/aeko-create-content <item_id>` — 근거 기반 콘텐츠 executor.
- `/aeko-publish-content <item_id>` — 저장된 콘텐츠 variation을 위한 보호된 publisher.

### 광고 운영

- `/aeko-openai-compose-ads [domain_id] [min_score]` — AEKO 계정 기반으로 review 기반 OpenAI Ads group을 paused 상태로 구성.
- `/aeko-openai-budget-shift [domain_id] [days]` — AEKO 계정 기반으로 cap과 명시 확인이 있는 OpenAI Ads 예산 및 entity-state dry-run 변경.
- `/aeko-openai-guardrails [domain_id]` — AEKO 계정 기반 OpenAI Ads automation 미리보기, 활성화, 이력 확인, emergency stop.

### 주간 루프

- `/aeko-create-loop` — 인터뷰, 지속 가능한 Notion config, 호스트별 schedule 구성, foreground dry run.
- `/aeko-run-loop config=<notion-page-id>` — approval-first 예약 읽기·제안 진입점.

## 스킬 커스터마이징

[CUSTOMIZATION.md](CUSTOMIZATION.md)는 브랜드 소유 스킬·eval 패키지, 수동 편집, 범위가 지정된
예시와 향후 자동 updater의 연결 지점을 설명합니다. 호스팅 실행과 내보내기는 같은 버전을
선택해야 하며 AEKO 비공개 벤치마크는 배포하지 않습니다. [작업 프롬프트 예시](docs/automation-prompt-examples.md)는
스킬 외에 별도 작업 지시를 보존하고 미지원 호스팅 실행을 표시합니다. 자동 updater, 다단계
호스팅 agent runner와 GitHub 동기화는 이 플러그인에서 구현하지 않았습니다.

## 다른 AEKO 저장소와의 관계

- [`aeko-mcp`](https://github.com/AEKO-Intelligence/aeko-mcp) — 선택형 hosted AEKO tool server.
- `aeko-plugin` — Claude, Codex, Gemini CLI용 skills-only 플러그인.

## 라이선스

MIT
