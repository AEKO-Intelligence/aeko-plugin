from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build-trusted-upstream-catalog.py"
SPEC = importlib.util.spec_from_file_location("trusted_catalog_builder", SCRIPT)
builder = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(builder)


def _record(path: str, content: bytes) -> dict:
    return {
        "path": path,
        "sha256": hashlib.sha256(content).hexdigest(),
        "size_bytes": len(content),
    }


def test_per_command_digest_changes_for_same_size_content_or_path():
    original = builder._package_digest([_record("references/a.md", b"alpha")])
    changed_content = builder._package_digest([_record("references/a.md", b"bravo")])
    changed_path = builder._package_digest([_record("references/b.md", b"alpha")])

    assert original != changed_content
    assert original != changed_path
