# Customizing the AEKO Plugin

> [한국어](#한국어-버전)

AEKO supplies upstream skills and evaluation guidance. Each customer develops a **brand-owned
version** through manual edits and, when implemented, AEKO's automated updater. The same
versioned instructions, applicable evals, and permitted examples must feed hosted automation
and export for the customer's Codex, Claude Desktop, or other capable client. Brand wiki is
planned later. Credentials are never part of a package; each host authenticates separately.

Keep four things separate:

| Object | What it contains |
| --- | --- |
| Upstream plugin | AEKO's generic skills, recipes, and regression guidance |
| Brand package | That brand's versioned skill/eval instructions and selected examples |
| Automation template | An editable whole-job prompt with setup placeholders |
| Configured job | Saved prompt, attached brand skill/evals, sources/window, destination, schedule, and limits |

An automation prompt adds the customer's purpose; attaching a skill does not replace it.
See [whole-job prompt examples](docs/automation-prompt-examples.md), each labeled with its
current execution status, and the [execution contract](docs/contracts/brand-execution-contract.md).

## Start with a brand-owned working copy

Use the selected brand's editable package or an explicitly chosen customer-owned checkout.
Keep an immutable previous version before changes. Installed plugin paths vary by host/version;
`/aeko-start` can locate the installation, but caches can be overwritten during an upgrade.
Do not make a cache, global chat memory, or the shared upstream repo the only copy of brand learning.

For a simple local customization, retain the existing canonical skill directory, such as
`skills/aeko-create-content/`, and edit its `SKILL.md` and relevant supporting references in
that brand's working copy. The source skill slug stays stable. A backend-exported document may
have a separately assigned package identity; that does not rename upstream commands.

1. Select the exact brand/domain and skill, then read its existing rules.
2. Add a small explicit rule or example in the relevant reference and make sure `SKILL.md`
   instructs the executor to load it. Files are not discovered just because they exist.
3. Add applicable eval instructions and a rejected/acceptable example pair for a lasting rule.
4. Review the diff and run the appropriate checks against synthetic or permitted brand inputs.
5. Activate/import the validated version through a supported lifecycle. Export and hosted runs
   must resolve that same version. A local edit or GitHub connection alone does not activate it.

## Portable document package seam

The backend foundation being developed uses one immutable document version per skill or eval:

| Field | Meaning |
| --- | --- |
| `text` | Skill/eval Markdown body; the canonical projection adds one frontmatter block |
| `metadata` | Canonical `name`, `description`, `kind`, `subkind`, `applies_to`, `declared_inputs`, plus validated metadata |
| `support_files` | Relative `path`, UTF-8 `content`, and `editable` flag for each supporting file |
| Version/digest | Identity of the exact projected `SKILL.md` and supporting bytes |

The deterministic export has `<package-name>/SKILL.md` and its supporting files. Both hosted
materialization and export must use those bytes. The job separately selects the skill and
applicable eval document versions; an `evals/` folder is not an automatic evaluator runner.
Ownership comes from authenticated backend document/domain records, never a model-supplied
frontmatter tenant field. The backend assigns export identity; do not reuse another brand's ID.

Current foundation constraints: skill text at most 128 KiB, 64 support files, 256 KiB per
support file, 2 MiB total, 16 KiB metadata, and a 200-character single-line description.
Brand-editable support files are Markdown. Paths are normalized relative paths without `..`,
absolute paths, backslashes, case collisions, reserved filenames, or another `SKILL.md`.
Trusted upstream non-Markdown helpers may be retained read-only by the backend; brand editors
cannot upload scripts through that seam. Local HTML/JSON examples below are existing plugin
patterns, not a claim that the current brand editor accepts those file types.

The backend package validator/serializer owns these limits and projections; this document
creates no new endpoint. A seed/import adapter must supply canonical document metadata, a
concise description, and all referenced support files rather than upload an arbitrary plugin
folder. The shared execution contract is copied into each adopting skill's `references/` so
individual exports can include it without reading outside their package. Release lint verifies
those copies. A GitHub importer/sync service and the multi-stage hosted agent runner are not
implemented by this plugin; never claim a local edit is already synchronized.

## Brand rules, examples, and evals

The content, PDP-update, and technical executors retain `references/{recipes,examples,style}/`.
Ad composition also reads its selected brand package before creating any creative. The selected
job can attach brand eval packages; retain their exact text/version in every drafting/checking
brief. If a required eval cannot load or run, report unavailable rather than pass.

Example scope in `references/style/voice-overrides.md`:

```markdown
## domain: synthetic-brand-a, channel: instagram

- Keep the caption under 80 words and use three hashtags.
- Do not use "the best" as a claim for this brand.
```

This is a synthetic illustration, **not an upstream ban on those words**. Brand B retains
its own rules. Both domain and channel must match. Channel-only and unscoped customer files
apply only inside a verified single-brand package; in a shared installation they need an
explicit owner scope. Never load a neighboring brand's rules or examples.

Resolve explicit task instructions and applicable standing brand rules before recipe defaults.
A job may be stricter or customize style, but conflicting explicit rules need resolution; a
scheduled run stops the affected output. Examples and backend-generated copy cannot overrule
explicit instructions. Actual platform/schema requirements, ownership, factual grounding, and
execution gates still apply. Hashtag count, register, section order, and CTA style are normally
recipe defaults that a brand can change.

A useful brand eval specifies its scope, required inputs, pass/fail criterion, and an acceptable
counterexample. For the synthetic rule above, reject an unsupported "the best" caption and
accept a grounded specific caption without it. Preserve the source feedback/reviewer/run,
market/language, rationale, and version diff. A one-off copy correction is not automatically
a lasting rule. Missing evidence is unavailable, not a failed quality judgment or invented fact.

### Existing local example routes

| Skill | Supporting files |
| --- | --- |
| `/aeko-create-content` | `examples/instagram-post-example.md`, `<channel>-*example*.md`, bundled `blog-example.md` and `press-release-example.md`, scoped `style/voice-overrides.md` |
| `/aeko-update-pdp` | `examples/pdp-html-example.html`, optional `json-ld-preferences.json`, scoped voice rules |
| `/aeko-fix-technical` | llms.txt, robots.txt, JSON-LD and deploy-note examples under `references/examples/` |

Add a supported channel recipe only in the brand copy and update that skill's recipe routing.
Keep canonical ASCII slugs such as `press_release`. A custom recipe does not add a publish API
or platform integration. Source examples shape style/structure; they are never factual proof,
customer experience, or permission to repeat prices and claims without current evidence.
Inspect `Refs loaded` and the brand-eval results to verify the chosen files actually applied.

## Automated updates and rollback

Automatic evolution is the intended AEKO service alongside manual editing. The updater is
not implemented yet. Its proposed policy is to activate bounded, nonconflicting improvements
only after actual validation and regressions; conflicts, ambiguous feedback, and changes to
existing explicit rules go to review. The current exact-version preview/promote gate remains.

An updater must target the same document `text`, `metadata`, and `support_files`, pin the base
digest, attribute feedback and changes, and compare the base before activation. Concurrent
manual edits must survive. Failed checks/budget/transport preserve the active version. Keep
version history and rollback; next runs/exports use the activated version, while in-flight
runs retain their pins where the runtime supports them. The current review-classification
path resolves its active extraction skill at classification start, so atomic whole-run
pinning is not yet universal.

## What travels and what stays private

- **Brand export:** that brand's approved rules, applicable eval instructions, selected
  redistributable examples, and regression cases permitted by that customer.
- **Upstream release:** generic recipes and synthetic regression cases without customer data.
- **Never ship:** AEKO's private benchmark corpus, `skills/*-workspace/`, private eval scratch,
  `outputs/`, credentials, personal data, other brands' examples, or raw production histories.

Use explicit package file lists and the canonical serializer; never recursively archive an
original checkout. Run package regressions at version change, not the full benchmark on every
scheduled output. Runtime output checks still apply. The release checks are local and do not
invoke paid models:

```sh
./scripts/lint-release-contracts.sh
```

## 한국어 버전

AEKO의 공통 스킬·평가 지침을 출발점으로 **브랜드 소유 패키지**를 발전시킵니다. 수동 편집과
향후 자동 업데이트는 같은 버전의 스킬·eval·허용된 예시 파일을 수정해야 합니다. 이 버전을
AEKO 호스팅 실행과 Codex/Claude Desktop용 내보내기에서 함께 사용합니다. 브랜드 wiki,
자동 updater, GitHub 자동 동기화, 다단계 호스팅 agent runner는 이 플러그인에서 구현하지
않았습니다. 각 클라이언트의 인증은 별도이며 자격 증명은 패키지에 넣지 않습니다.

작업별 자유 텍스트 프롬프트와 연결된 스킬은 별개입니다. 원래 프롬프트를 그대로 보존하고,
브랜드·기간·채널·eval·목적지·한도·입력 없음 동작을 명확히 하세요.
[작업 프롬프트 예시](docs/automation-prompt-examples.md)는 실행 가능 여부를 각각 표시합니다.

설치 캐시는 업데이트 때 교체될 수 있으므로 브랜드 소유 작업 사본을 사용하세요. 한 브랜드의
피드백은 그 브랜드의 명시적 규칙과 평가 예시로만 반영합니다. 다른 브랜드나 AEKO 공통 규칙에
전파하지 않습니다. 기존 규칙과 충돌하면 해결이 필요하며, 일회성 수정은 영구 규칙으로 만들지
않습니다. 예시·생성된 문구보다 명시적 브랜드 규칙이 우선이고, 실제 플랫폼·스키마·권한·근거
조건은 유지합니다. 리뷰가 없다고 합성 리뷰를 실제 고객 경험으로 대체하지 않습니다.

백엔드 패키지 기반은 `text`, `metadata`, `support_files`를 버전화하고 같은 바이트로
`SKILL.md`와 참조 파일을 내보냅니다. 브랜드 편집용 참조 파일은 Markdown이며, 로컬 HTML/JSON
예시가 있다고 현재 편집 API도 그 파일을 받는 것은 아닙니다. 위의 크기·경로·소유권 규칙과
실제 백엔드 검증기를 따르세요. 로컬/GitHub 편집만으로 호스팅 활성화가 완료되지는 않습니다.

자동 updater의 의도된 정책은 실제 검증·회귀 검사를 통과한 제한적이고 충돌 없는 개선의 자동
활성화입니다. 충돌과 기존 명시 규칙 변경은 검토하고, 현재 exact-version preview/promote
게이트를 유지합니다. 수동 동시 편집을 덮어쓰지 않고 변경 이력과 롤백을 보존해야 합니다.

브랜드 소유 eval·배포 가능한 예시·허용된 회귀 사례는 내보내기에 포함합니다. AEKO 비공개
벤치마크, `skills/*-workspace/`, `outputs/`, 자격 증명, 다른 고객 데이터는 포함하지 않습니다.
예약 실행은 그 자체로 게시·광고 쓰기 권한이 아니며, 없는 기능을 실행했다고 표시하지 않습니다.
