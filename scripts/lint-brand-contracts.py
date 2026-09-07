#!/usr/bin/env python3
"""Local release invariants; never loads private corpora or executes MCP tools."""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ADOPTERS = (
    "aeko-openai-compose-ads", "aeko-create-content", "aeko-publish-content",
    "aeko-update-pdp", "aeko-fix-technical", "aeko-create-loop", "aeko-run-loop",
    "aeko-weekly-report", "aeko-pdp-build", "aeko-message-audit", "aeko-source-analysis",
    "aeko-competitor-analysis", "aeko-ai-visibility", "aeko-ads-review", "aeko-ga4",
    "aeko-openai-ads-reporting", "aeko-openai-guardrails",
)
EVAL_ADOPTERS = ADOPTERS[:5] + ADOPTERS[7:]
SUPPORT_ADOPTERS = (
    ("arow-contract.md", "skills/aeko-weekly-report/references/arow-contract.md",
     ("aeko-site-audit", "aeko-pdp-audit", "aeko-ads-review", "aeko-ga4",
      "aeko-ai-visibility", "aeko-action-center")),
    ("aeo-frameworks.md", "skills/aeko-create-content/references/aeo-frameworks.md",
     ("aeko-source-analysis", "aeko-competitor-analysis", "aeko-ai-visibility")),
    ("action-item-contract.md", "docs/contracts/action-item-contract.md", ("aeko-action-center",)),
)


def check(root: Path, mcp_source: Path | None = None) -> list[str]:
    errors: list[str] = []
    for relative in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
                     ".codex-plugin/plugin.json", ".codex-plugin/marketplace.json",
                     "gemini-extension.json"):
        try:
            json.loads((root / relative).read_text())
        except (OSError, ValueError) as exc:
            errors.append(f"{relative}: invalid manifest: {exc}")

    skills = sorted(p for p in (root / "skills").glob("*/SKILL.md")
                    if not p.parent.name.endswith("-workspace"))
    if len(skills) != 26:
        errors.append(f"Expected 26 canonical skills, found {len(skills)}")
    tools: set[str] = set()
    for path in skills:
        source = path.read_text()
        if not source.startswith("---\n") or "\n---\n" not in source[4:]:
            errors.append(f"{path.relative_to(root)}: missing frontmatter")
            continue
        header = source.split("---", 2)[1]
        name = re.search(r"^name:\s*(\S+)\s*$", header, re.M)
        if not name or name[1] != path.parent.name:
            errors.append(f"{path.relative_to(root)}: canonical slug mismatch")
        allowed = re.search(r"^allowed-tools:\s*(.+)$", header, re.M)
        if allowed:
            tools.update(re.findall(r"\baeko_[a-z0-9_]+\b", allowed[1]))

    for slug in ADOPTERS:
        path = root / "skills" / slug
        for filename, canonical in (
            ("brand-execution-contract.md", "docs/contracts/brand-execution-contract.md"),
            *((("brand-output-eval.md", "evals/brand-output.md"),) if slug in EVAL_ADOPTERS else ()),
        ):
            copy = path / "references" / filename
            if copy.is_symlink() or not copy.is_file() or copy.read_bytes() != (root / canonical).read_bytes():
                errors.append(f"{slug}: {filename} must be an identical in-package file")
            if f"references/{filename}" not in (path / "SKILL.md").read_text():
                errors.append(f"{slug}: missing discoverable reference to {filename}")

    for filename, canonical, slugs in SUPPORT_ADOPTERS:
        for slug in slugs:
            copy = root / "skills" / slug / "references" / filename
            if copy.is_symlink() or not copy.is_file() or copy.read_bytes() != (root / canonical).read_bytes():
                errors.append(f"{slug}: {filename} must be an identical in-package file")

    # Inspect tracked path names only: never read original outputs or ignored eval workspaces.
    tracked = subprocess.run(["git", "ls-files", "-z"], cwd=root, check=True,
                             capture_output=True).stdout.decode().split("\0")
    for path in filter(None, tracked):
        parts = Path(path).parts
        if "outputs" in parts or any(p.endswith("-workspace") for p in parts):
            errors.append(f"Private/scratch path is tracked: {path}")

    if mcp_source is not None:
        defined: set[str] = set()
        for path in sorted((mcp_source / "aeko_mcp/tools").glob("*.py")):
            for node in ast.parse(path.read_text()).body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    defined.add(node.name)
        if not defined:
            errors.append(f"No MCP tool source found at {mcp_source}")
        elif tools - defined:
            errors.append("Unknown allowed MCP tools: " + ", ".join(sorted(tools - defined)))
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp-source", type=Path, help="Optional read-only sibling MCP checkout")
    args = parser.parse_args()
    failures = check(ROOT, args.mcp_source)
    if failures:
        raise SystemExit("\n".join(f"ERROR: {failure}" for failure in failures))
    print("Brand release contracts pass (26 skills; self-contained shared refs; private paths excluded).")
