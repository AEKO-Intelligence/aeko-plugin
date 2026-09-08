# Trusted upstream catalog

The customer plugin ships 27 canonical `aeko-*` command entrypoints. The current backend seed
defines nine older automation skill/eval documents for review classification and ad-copy runtime
prompts. These are different catalogs. The two related workflows below share a job area, but none
of the nine backend documents is a substitute for a customer command.

## Exact inventory

| Canonical command | Relationship to the nine legacy backend documents |
| --- | --- |
| `/aeko-action-center` | None |
| `/aeko-ads-review` | None |
| `/aeko-ai-visibility` | None |
| `/aeko-competitor-analysis` | None |
| `/aeko-connect` | None |
| `/aeko-content-ideas` | None |
| `/aeko-create-ad-copy` | Canonical hosted ad drafting/revision entrypoint; accepted brand and style evals supplement it |
| `/aeko-create-content` | None |
| `/aeko-create-loop` | None |
| `/aeko-fix-technical` | None |
| `/aeko-ga4` | None |
| `/aeko-manage-prompts` | None |
| `/aeko-message-audit` | None |
| `/aeko-openai-ads-reporting` | None |
| `/aeko-openai-budget-shift` | None |
| `/aeko-openai-compose-ads` | Related runtime components only: the three `skill:ad_copy:*` documents and four `eval:ad_*:*` documents |
| `/aeko-openai-guardrails` | None |
| `/aeko-pdp-audit` | None |
| `/aeko-pdp-build` | None |
| `/aeko-publish-content` | None |
| `/aeko-run-loop` | None |
| `/aeko-site-audit` | None |
| `/aeko-source-analysis` | None |
| `/aeko-start` | None |
| `/aeko-store` | Related runtime components only: `skill:context_extract:default` and `eval:context_quality:default` |
| `/aeko-update-pdp` | None |
| `/aeko-weekly-report` | None |

The nine backend identities are:

1. `skill:context_extract:default`
2. `eval:context_quality:default`
3. `skill:ad_copy:situation_question`
4. `skill:ad_copy:conversational`
5. `eval:ad_brand:default`
6. `eval:ad_skill:situation_question`
7. `eval:ad_skill:conversational`
8. `skill:ad_copy:general`
9. `eval:ad_skill:general`

The backend also seeds seven Brand Wiki documents. Those pages are package knowledge, not extra
customer-plugin commands.

## Reproducible artifact

[`scripts/build-trusted-upstream-catalog.py`](../scripts/build-trusted-upstream-catalog.py)
contains the exact allowlist for every command package. It reads only those public files, refuses
symlinks and unsafe paths, requires UTF-8 text, applies the backend-aligned file/package/total byte
limits, and records the content plus SHA-256 provenance. It never fetches a branch, reads ignored
workspaces or `outputs/`, or recursively archives a checkout.

The generated [`catalog/trusted-upstream-catalog.json`](../catalog/trusted-upstream-catalog.json)
is self-contained and deterministic. Rebuild and verify it with:

```sh
python scripts/build-trusted-upstream-catalog.py
python scripts/build-trusted-upstream-catalog.py --check
```

The artifact uses `kind=skill`, `subkind=customer_plugin`, and the canonical `aeko-*` slug as its
key and source package identity. Non-Markdown support files are marked read-only. Per-file SHA-256,
per-command package SHA-256, and a catalog content SHA-256 let a backend vendor the exact reviewed
bytes without a runtime source checkout.

The reviewed artifact currently contains 27 commands, 137 explicitly allowlisted files, and
1,169,108 source bytes. Its aggregate content digest is
`48f56c1b9218c5ecf2e555353789d68b4c3bb68e4234ed235e7aeb1a45c88d38`; the JSON file digest is
`44dc21f52fdb93116c88adda685a87e837625a34117243e1c484119d7390add7`. Per-command digests frame
the actual path, file digest, and byte count, so same-size content or path substitutions change
the command fingerprint.

Each command also has an explicit category and bounded feedback/dependency metadata. Only
`aeko-create-ad-copy`, `aeko-create-content`, `aeko-fix-technical`, `aeko-update-pdp`, and `aeko-manage-prompts` are
generic-feedback targets. Their typed subject/execution-class routes and required Wiki paths are
reviewed data, not classifications inferred from feedback prose or model output.

## Required backend consumer seam

The backend consumer now vendors and validates this exact artifact. Its implementation:

1. Vendor the generated JSON at a reviewed release boundary and reject an unknown schema, plugin
   version, count, bound, path, or SHA before any database write.
2. Reconcile stable AEKO-default documents for all 27 `(skill, customer_plugin, aeko-*)`
   identities through the existing trusted package validator (`trusted_files=True`,
   `metadata_writer=aeko_default`). Do not accept a model- or request-supplied checkout path.
3. Preserve the source command slug and catalog/package/file hashes as immutable upstream
   provenance while letting the backend assign its tenant-safe document/package identities.
4. Insert a new immutable version only when the reviewed source package digest changes. Existing
   tenant releases stay pinned until the normal explicit adoption/reset/publication seam moves
   them forward.
5. Run this only from deployment/bootstrap reconciliation. GET routes and customer runs must not
   fetch current source, provision defaults, or silently add new commands to an accepted package.

An initialized brand can therefore discover all 27 command documents in its whole package. The
legacy hosted model classes retain their existing runtime components. The hosted MCP ad runner
selects `aeko-create-ad-copy` from the accepted release, including its supporting files and evals.
Other commands remain portable; listing a command does not claim a hosted executor for it.
The catalog itself does not provision or synchronize GitHub repositories.
