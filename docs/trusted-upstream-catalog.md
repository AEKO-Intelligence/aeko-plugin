# Trusted upstream catalog

The customer plugin ships 26 canonical `aeko-*` command entrypoints. The current backend seed
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

The reviewed artifact currently contains 26 commands, 135 explicitly allowlisted files, and
1,163,588 source bytes. Its aggregate content digest is
`0a0681d0b66c7e8e07af00eec29552f99d69017ccf3d0e9a768249f0a5de261d`; the JSON file digest is
`a5511677577078a7b2024d40df6e7dcc1a5aebeb6a94f81decada97c27fa1d3f`. Per-command digests frame
the actual path, file digest, and byte count, so same-size content or path substitutions change
the command fingerprint.

Each command also has an explicit category and bounded feedback/dependency metadata. Only
`aeko-create-content`, `aeko-fix-technical`, `aeko-update-pdp`, and `aeko-manage-prompts` are
generic-feedback targets. Their typed subject/execution-class routes and required Wiki paths are
reviewed data, not classifications inferred from feedback prose or model output.

## Required backend consumer seam

The backend consumer now vendors and validates this exact artifact. Its implementation:

1. Vendor the generated JSON at a reviewed release boundary and reject an unknown schema, plugin
   version, count, bound, path, or SHA before any database write.
2. Reconcile stable AEKO-default documents for all 26 `(skill, customer_plugin, aeko-*)`
   identities through the existing trusted package validator (`trusted_files=True`,
   `metadata_writer=aeko_default`). Do not accept a model- or request-supplied checkout path.
3. Preserve the source command slug and catalog/package/file hashes as immutable upstream
   provenance while letting the backend assign its tenant-safe document/package identities.
4. Insert a new immutable version only when the reviewed source package digest changes. Existing
   tenant releases stay pinned until the normal explicit adoption/reset/publication seam moves
   them forward.
5. Run this only from deployment/bootstrap reconciliation. GET routes and customer runs must not
   fetch current source, provision defaults, or silently add new commands to an accepted package.

An initialized brand can therefore discover all 26 command documents in its whole package. The
existing hosted automation templates still select their legacy runtime components; the catalog
does not implement canonical-command routing, the full Responses/MCP runner, a contextual chat
executor, or GitHub App provisioning and sync.
