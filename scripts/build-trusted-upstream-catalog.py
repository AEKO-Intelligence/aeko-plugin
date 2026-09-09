#!/usr/bin/env python3
"""Build the bounded public AEKO skill catalog from an explicit file allowlist."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "catalog" / "trusted-upstream-catalog.json"
SCHEMA = "aeko-trusted-upstream-catalog-v1"
MAX_DOCUMENTS = 128
MAX_FILES_PER_DOCUMENT = 64
MAX_SKILL_BYTES = 128 * 1024
MAX_FILE_BYTES = 256 * 1024
MAX_TOTAL_SOURCE_BYTES = 4 * 1024 * 1024
FORBIDDEN_PARTS = frozenset({".git", ".env", "__pycache__", "outputs", "private"})
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")

# Every byte admitted to the catalog is named here. The builder never archives
# a checkout, follows a symlink, or fetches a branch/tag at build or run time.
PACKAGE_ALLOWLIST = {
    "aeko-create-ad-copy": ("SKILL.md", "references/ad-copy-evals.md"),
    "aeko-action-center": (
        "SKILL.md",
        "references/action-item-contract.md",
        "references/arow-contract.md",
    ),
    "aeko-ads-review": (
        "SKILL.md",
        "references/arow-contract.md",
        "references/brand-execution-contract.md",
        "references/brand-output-eval.md",
        "references/google-gaql.md",
        "references/manual-inputs.md",
        "references/weekly-rows.md",
    ),
    "aeko-ai-visibility": (
        "SKILL.md",
        "references/aeo-frameworks.md",
        "references/arow-contract.md",
        "references/brand-execution-contract.md",
        "references/brand-output-eval.md",
    ),
    "aeko-competitor-analysis": (
        "SKILL.md",
        "references/aeo-frameworks.md",
        "references/brand-execution-contract.md",
        "references/brand-mode.md",
        "references/brand-output-eval.md",
        "references/product-mode.md",
    ),
    "aeko-connect": ("SKILL.md",),
    "aeko-content-ideas": (
        "SKILL.md",
        "references/brand-execution-contract.md",
    ),
    "aeko-create-content": (
        "SKILL.md",
        "references/saved-content-plan.md",
        "references/aeo-frameworks.md",
        "references/brand-execution-contract.md",
        "references/brand-output-eval.md",
        "references/direct-handoff-channels.md",
        "references/drafter-instructions.md",
        "references/examples/README.md",
        "references/examples/aeko_shop-fixture.html",
        "references/examples/aeko_shop-fixture.md",
        "references/examples/aeko_shop-fixture.meta.json",
        "references/examples/blog-example.md",
        "references/examples/context-reviews-fixture.md",
        "references/examples/in-store-content-example.md",
        "references/examples/instagram-post-example.md",
        "references/examples/press-release-example.md",
        "references/recipes/editorial-html-jsonld.md",
        "references/recipes/instagram.md",
        "references/recipes/magazine.md",
        "references/recipes/naver_blog.md",
        "references/recipes/press_release.md",
        "references/recipes/reddit.md",
        "references/recipes/tiktok.md",
        "references/recipes/tistory.md",
        "references/recipes/youtube.md",
        "references/style/voice-overrides.md",
    ),
    "aeko-create-loop": (
        "SKILL.md",
        "references/brand-execution-contract.md",
    ),
    "aeko-fix-technical": (
        "SKILL.md",
        "references/brand-execution-contract.md",
        "references/brand-output-eval.md",
        "references/examples/README.md",
        "references/examples/deploy-notes-example.md",
        "references/examples/json-ld-example.json",
        "references/examples/llms-txt-example.txt",
        "references/examples/robots-txt-additions-example.txt",
        "references/recipes/deploy-checklist.md",
        "references/recipes/json-ld.md",
        "references/recipes/llms-txt.md",
        "references/recipes/robots-txt-patch.md",
        "references/style/voice-overrides.md",
    ),
    "aeko-ga4": (
        "SKILL.md",
        "references/arow-contract.md",
        "references/brand-execution-contract.md",
        "references/brand-output-eval.md",
    ),
    "aeko-manage-prompts": (
        "SKILL.md",
        "references/brand-execution-contract.md",
        "references/context-curation.md",
        "references/discover-track.md",
        "references/review-suggestions.md",
        "references/review-untrack.md",
    ),
    "aeko-message-audit": (
        "SKILL.md",
        "references/brand-execution-contract.md",
        "references/brand-output-eval.md",
        "references/evidence-vocabulary.md",
        "references/render-contract.md",
        "scripts/fetch_evidence.py",
    ),
    "aeko-openai-ads-reporting": (
        "SKILL.md",
        "references/brand-execution-contract.md",
        "references/brand-output-eval.md",
    ),
    "aeko-openai-budget-shift": ("SKILL.md",),
    "aeko-openai-compose-ads": (
        "SKILL.md",
        "references/brand-execution-contract.md",
        "references/brand-output-eval.md",
    ),
    "aeko-openai-guardrails": (
        "SKILL.md",
        "references/brand-execution-contract.md",
        "references/brand-output-eval.md",
    ),
    "aeko-pdp-audit": (
        "SKILL.md",
        "references/arow-contract.md",
        "references/severity.md",
        "references/status-bands.md",
        "scripts/fetch_evidence.py",
    ),
    "aeko-pdp-build": (
        "SKILL.md",
        "references/brand-execution-contract.md",
        "references/brand-output-eval.md",
        "scripts/fetch_evidence.py",
    ),
    "aeko-publish-content": (
        "SKILL.md",
        "references/brand-execution-contract.md",
        "references/brand-output-eval.md",
    ),
    "aeko-run-loop": (
        "SKILL.md",
        "references/brand-execution-contract.md",
    ),
    "aeko-site-audit": (
        "SKILL.md",
        "references/arow-contract.md",
        "references/severity.md",
        "scripts/fetch_evidence.py",
    ),
    "aeko-source-analysis": (
        "SKILL.md",
        "references/aeo-frameworks.md",
        "references/brand-execution-contract.md",
        "references/brand-output-eval.md",
        "references/cited-page-mode.md",
        "references/prompt-mode.md",
    ),
    "aeko-start": (
        "SKILL.md",
        "references/customization-contract.md",
    ),
    "aeko-store": (
        "SKILL.md",
        "references/review-intake-mode.md",
        "references/setup-mode.md",
    ),
    "aeko-update-pdp": (
        "SKILL.md",
        "references/brand-execution-contract.md",
        "references/brand-output-eval.md",
        "references/browser-review.md",
        "references/examples/README.md",
        "references/examples/json-ld-preferences.json",
        "references/examples/pdp-html-example.html",
        "references/prompts/verification-prompts.md",
        "references/recipes/json-ld-schemas.md",
        "references/recipes/pdp-scaffold.md",
        "references/recipes/responsive-html-contract.md",
        "references/refresh-mode.md",
        "references/style/voice-overrides.md",
    ),
    "aeko-weekly-report": (
        "SKILL.md",
        "references/arow-contract.md",
        "references/brand-execution-contract.md",
        "references/brand-output-eval.md",
    ),
}

LEGACY_BACKEND_DOCUMENTS = (
    ("skill:context_extract:default", "skill", "context_extract", "default"),
    ("eval:context_quality:default", "eval", "context_quality", "default"),
    ("skill:ad_copy:situation_question", "skill", "ad_copy", "situation_question"),
    ("skill:ad_copy:conversational", "skill", "ad_copy", "conversational"),
    ("eval:ad_brand:default", "eval", "ad_brand", "default"),
    ("eval:ad_skill:situation_question", "eval", "ad_skill", "situation_question"),
    ("eval:ad_skill:conversational", "eval", "ad_skill", "conversational"),
    ("skill:ad_copy:general", "skill", "ad_copy", "general"),
    ("eval:ad_skill:general", "eval", "ad_skill", "general"),
)

LEGACY_RELATIONSHIPS = {
    "aeko-store": (
        "skill:context_extract:default",
        "eval:context_quality:default",
    ),
    "aeko-openai-compose-ads": tuple(
        value[0] for value in LEGACY_BACKEND_DOCUMENTS[2:]
    ),
}

# Selection metadata is part of the reviewed artifact rather than inferred from
# descriptions or model output. Only the explicitly mapped commands below are valid generic
# feedback targets; the remaining commands still carry a stable category and an
# empty dependency closure for catalog discovery.
COMMAND_CATEGORIES = {
    "aeko-create-ad-copy": "advertising",
    "aeko-action-center": "router",
    "aeko-ads-review": "reporting",
    "aeko-ai-visibility": "reporting",
    "aeko-competitor-analysis": "analysis",
    "aeko-connect": "connection",
    "aeko-content-ideas": "content",
    "aeko-create-content": "content",
    "aeko-create-loop": "orchestration",
    "aeko-fix-technical": "optimization",
    "aeko-ga4": "reporting",
    "aeko-manage-prompts": "prompts",
    "aeko-message-audit": "analysis",
    "aeko-openai-ads-reporting": "reporting",
    "aeko-openai-budget-shift": "advertising",
    "aeko-openai-compose-ads": "advertising",
    "aeko-openai-guardrails": "advertising",
    "aeko-pdp-audit": "analysis",
    "aeko-pdp-build": "content",
    "aeko-publish-content": "content",
    "aeko-run-loop": "orchestration",
    "aeko-site-audit": "analysis",
    "aeko-source-analysis": "analysis",
    "aeko-start": "router",
    "aeko-store": "connection",
    "aeko-update-pdp": "optimization",
    "aeko-weekly-report": "reporting",
}

FEEDBACK_SELECTION = {
    "aeko-create-ad-copy": {
        "subject_kind": "automation_output",
        "execution_classes": [],
        "requires_knowledge": ["voice/brand-voice", "products/product-facts", "markets/market-guidance"],
    },
    "aeko-create-content": {
        "subject_kind": "content",
        "execution_classes": ["local_content_artifact"],
        "requires_knowledge": [
            "identity/positioning",
            "audience/customer-context",
            "voice/brand-voice",
            "products/product-facts",
            "markets/market-guidance",
        ],
    },
    "aeko-fix-technical": {
        "subject_kind": "content",
        "execution_classes": ["technical_artifact"],
        "requires_knowledge": [
            "identity/positioning",
            "products/product-facts",
            "markets/market-guidance",
        ],
    },
    "aeko-manage-prompts": {
        "subject_kind": "prompt",
        "execution_classes": [],
        "requires_knowledge": [
            "audience/customer-context",
            "products/product-facts",
            "markets/market-guidance",
            "perception/ai-observations",
        ],
    },
    "aeko-update-pdp": {
        "subject_kind": "content",
        "execution_classes": ["store_write_artifact"],
        "requires_knowledge": [
            "identity/positioning",
            "audience/customer-context",
            "voice/brand-voice",
            "products/product-facts",
            "markets/market-guidance",
        ],
    },
}


def _version() -> str:
    payload = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text("utf-8"))
    value = payload.get("version")
    if not isinstance(value, str) or not value:
        raise ValueError("The Claude plugin manifest has no usable version.")
    return value


def _frontmatter_value(text: str, key: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("SKILL.md must start with YAML frontmatter.")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise ValueError("SKILL.md frontmatter is not closed.") from None
    prefix = f"{key}:"
    for index, line in enumerate(lines[1:end], start=1):
        if not line.startswith(prefix):
            continue
        value = line[len(prefix) :].strip()
        if value in {">", "|"}:
            folded = []
            for continuation in lines[index + 1 : end]:
                if continuation and not continuation[0].isspace():
                    break
                if continuation.strip():
                    folded.append(continuation.strip())
            return " ".join(folded)
        return value.strip("'\"")
    raise ValueError(f"SKILL.md frontmatter is missing {key}.")


def _safe_file(skill_slug: str, relative: str) -> tuple[str, bytes]:
    path = PurePosixPath(relative)
    if (
        path.is_absolute()
        or not path.parts
        or any(
            part in {"", ".", ".."} or part in FORBIDDEN_PARTS for part in path.parts
        )
        or any(part.endswith("-workspace") for part in path.parts)
    ):
        raise ValueError(f"Unsafe allowlisted path: {skill_slug}/{relative}")
    source_relative = PurePosixPath("skills", skill_slug, *path.parts).as_posix()
    source = ROOT.joinpath(*PurePosixPath(source_relative).parts)
    if source.is_symlink() or not source.is_file():
        raise ValueError(
            f"Allowlisted source is missing or is a symlink: {source_relative}"
        )
    raw = source.read_bytes()
    if len(raw) > MAX_FILE_BYTES:
        raise ValueError(f"Allowlisted source exceeds 256 KiB: {source_relative}")
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError(
            f"Allowlisted source is not UTF-8: {source_relative}"
        ) from None
    if b"\x00" in raw:
        raise ValueError(f"Allowlisted source contains NUL: {source_relative}")
    return source_relative, raw


def _validate_inventory(skill_slug: str, allowed: tuple[str, ...]) -> None:
    skill_root = ROOT / "skills" / skill_slug
    actual = {
        path.relative_to(skill_root).as_posix()
        for path in skill_root.rglob("*")
        if path.is_file() or path.is_symlink()
    }
    expected = set(allowed)
    if actual != expected:
        missing = sorted(expected - actual)
        unlisted = sorted(actual - expected)
        raise ValueError(
            f"Trusted file inventory mismatch for {skill_slug}; "
            f"missing={missing}, unlisted={unlisted}"
        )


def _file_record(path: str, source_path: str, raw: bytes, *, editable: bool) -> dict:
    return {
        "path": path,
        "source_path": source_path,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "size_bytes": len(raw),
        "editable": editable,
        "content": raw.decode("utf-8"),
    }


def _package_digest(records: list[dict]) -> str:
    digest = hashlib.sha256(b"aeko-trusted-upstream-package-v1\x00")
    for record in sorted(records, key=lambda value: value["path"]):
        for value in (
            record["path"],
            record["sha256"],
            str(record["size_bytes"]),
        ):
            encoded = value.encode("utf-8")
            digest.update(len(encoded).to_bytes(4, "big"))
            digest.update(encoded)
    return digest.hexdigest()


def _normalized_link(source_path: str, target: str) -> str:
    stack = list(PurePosixPath(source_path).parent.parts)
    for part in PurePosixPath(target).parts:
        if part in {"", "."}:
            continue
        if part == "..":
            if not stack:
                raise ValueError(
                    f"Local Markdown link escapes its package: {source_path} -> {target}"
                )
            stack.pop()
        else:
            stack.append(part)
    return PurePosixPath(*stack).as_posix()


def _validate_local_links(slug: str, records: list[dict]) -> None:
    allowed = {record["path"] for record in records}
    for record in records:
        if not record["path"].lower().endswith(".md"):
            continue
        for match in MARKDOWN_LINK.finditer(record["content"]):
            target = match.group(1).strip().split()[0].strip("<>").split("#", 1)[0]
            if (
                not target
                or target in {"src", "url"}
                or "://" in target
                or target.startswith(("mailto:", "/"))
            ):
                continue
            resolved = _normalized_link(record["path"], target)
            if resolved not in allowed:
                raise ValueError(
                    f"Unresolved local Markdown link in {slug}: "
                    f"{record['path']} -> {target}"
                )


def build_catalog() -> dict:
    if len(PACKAGE_ALLOWLIST) != 27 or len(PACKAGE_ALLOWLIST) > MAX_DOCUMENTS:
        raise ValueError(
            "The trusted catalog must contain exactly 27 bounded entrypoints."
        )
    if set(COMMAND_CATEGORIES) != set(PACKAGE_ALLOWLIST):
        raise ValueError("Every canonical command requires one stable category.")
    if not set(FEEDBACK_SELECTION) <= set(PACKAGE_ALLOWLIST):
        raise ValueError("Feedback selection names an unknown canonical command.")
    documents = []
    source_bytes = 0
    source_files = 0
    for slug, allowed in sorted(PACKAGE_ALLOWLIST.items()):
        if not slug.startswith("aeko-") or len(set(allowed)) != len(allowed):
            raise ValueError(f"Invalid or duplicate allowlist entries for {slug}.")
        if (
            not allowed
            or allowed[0] != "SKILL.md"
            or len(allowed) > MAX_FILES_PER_DOCUMENT
        ):
            raise ValueError(f"Invalid bounded package allowlist for {slug}.")
        _validate_inventory(slug, allowed)
        records = []
        for relative in allowed:
            source_path, raw = _safe_file(slug, relative)
            if relative == "SKILL.md" and len(raw) > MAX_SKILL_BYTES:
                raise ValueError(f"SKILL.md exceeds 128 KiB: {source_path}")
            records.append(
                _file_record(
                    relative,
                    source_path,
                    raw,
                    editable=relative.lower().endswith(".md"),
                )
            )
            source_bytes += len(raw)
            source_files += 1
        skill_text = records[0]["content"]
        if _frontmatter_value(skill_text, "name") != slug:
            raise ValueError(f"Canonical slug/frontmatter mismatch for {slug}.")
        _validate_local_links(slug, records)
        related = list(LEGACY_RELATIONSHIPS.get(slug, ()))
        selection = {
            "category": COMMAND_CATEGORIES[slug],
            "feedback": FEEDBACK_SELECTION.get(slug),
            "requires_commands": [],
        }
        documents.append(
            {
                "kind": "skill",
                "subkind": "customer_plugin",
                "key": slug,
                "package_slug": slug,
                "command": f"/{slug}",
                "name": slug,
                "description": _frontmatter_value(skill_text, "description"),
                "source_package_sha256": _package_digest(records),
                "legacy_backend_relationship": (
                    "related_runtime_components_only" if related else "none"
                ),
                "legacy_backend_document_keys": related,
                "selection": selection,
                "skill_md": records[0],
                "support_files": records[1:],
            }
        )
    if source_bytes > MAX_TOTAL_SOURCE_BYTES:
        raise ValueError("The trusted catalog exceeds its 4 MiB source-byte limit.")

    content_digest = hashlib.sha256(b"aeko-trusted-upstream-catalog-v1\x00")
    for document in documents:
        for value in (
            document["package_slug"],
            document["source_package_sha256"],
            json.dumps(
                document["selection"],
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
        ):
            encoded = value.encode("utf-8")
            content_digest.update(len(encoded).to_bytes(4, "big"))
            content_digest.update(encoded)
    return {
        "schema": SCHEMA,
        "source": {
            "repository": "https://github.com/AEKO-Intelligence/aeko-plugin",
            "plugin_version": _version(),
            "selection": "explicit-public-file-allowlist",
            "network_fetch": False,
        },
        "limits": {
            "max_documents": MAX_DOCUMENTS,
            "max_files_per_document": MAX_FILES_PER_DOCUMENT,
            "max_skill_bytes": MAX_SKILL_BYTES,
            "max_file_bytes": MAX_FILE_BYTES,
            "max_total_source_bytes": MAX_TOTAL_SOURCE_BYTES,
        },
        "counts": {
            "canonical_entrypoints": len(documents),
            "legacy_backend_documents": len(LEGACY_BACKEND_DOCUMENTS),
            "source_files": source_files,
            "source_bytes": source_bytes,
        },
        "content_sha256": content_digest.hexdigest(),
        "relationship_note": (
            "The nine legacy backend skill/eval documents are runtime prompt components, "
            "not the 27 customer-plugin command entrypoints. Related entries below are "
            "workflow associations only and are not one-to-one imports."
        ),
        "legacy_backend_documents": [
            {"identity": identity, "kind": kind, "subkind": subkind, "key": key}
            for identity, kind, subkind, key in LEGACY_BACKEND_DOCUMENTS
        ],
        "documents": documents,
    }


def _encoded(catalog: dict) -> bytes:
    return (
        json.dumps(catalog, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = _encoded(build_catalog())
    output = args.output.resolve()
    if args.check:
        if not output.is_file() or output.read_bytes() != expected:
            print(f"Trusted upstream catalog is stale: {output}")
            return 1
        payload = json.loads(expected)
        print(
            "Trusted upstream catalog passes "
            f"({payload['counts']['canonical_entrypoints']} entrypoints; "
            f"{payload['counts']['source_files']} explicitly allowlisted files; "
            f"{payload['counts']['source_bytes']} source bytes)."
        )
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    handle, temp_name = tempfile.mkstemp(prefix=f".{output.name}.", dir=output.parent)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(expected)
        os.chmod(temp_name, 0o644)
        os.replace(temp_name, output)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
