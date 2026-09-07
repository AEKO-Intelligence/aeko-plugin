#!/usr/bin/env python3
"""Exercise a supplied backend canonical serializer using synthetic brand packages only.

Usage: python scripts/check-portable-package-examples.py --backend-packages /path/to/packages.py
No network, database, model calls, or writes to the backend checkout.
"""
from __future__ import annotations

import argparse
import importlib.util
import io
from pathlib import Path
import sys
import zipfile


def main(path: Path) -> None:
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("canonical_package_examples", path)
    if spec is None or spec.loader is None:
        raise ValueError("Cannot load the supplied package serializer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    def package(brand: str, rule: str):
        metadata = dict(name=f"synthetic-{brand}", description="Synthetic brand regression package",
                        kind="skill", subkind="ad_copy", applies_to=None, declared_inputs=[])
        files = [module.SupportFile("references/brand-rules.md", rule),
                 module.SupportFile("references/evals.md", f"Evaluate only {brand}: {rule}"),
                 module.SupportFile("references/examples.md", "Synthetic acceptable: A quiet evening light.")]
        return module.validate_package(text="Read references/brand-rules.md and references/evals.md.\n",
                                       canonical=metadata, support_files=files)

    upstream = package("upstream", "Ground every factual claim.")
    a1 = package("brand-a", "Ground every factual claim.")
    b1 = package("brand-b", "Ground every factual claim.")
    frozen = {"upstream": upstream.zip_bytes(), "a1": a1.zip_bytes(), "b1": b1.zip_bytes()}
    a2 = package("brand-a", 'Ground every factual claim. Do not claim "the best" for brand-a.')
    assert a1.digest != a2.digest, "A rule edit must change the package digest"
    assert a1.zip_bytes() == frozen["a1"], "Old A version must remain immutable"
    assert upstream.zip_bytes() == frozen["upstream"] and b1.zip_bytes() == frozen["b1"]
    for value in (upstream, a1, b1, a2):
        assert value.zip_bytes() == value.zip_bytes(), "Export must be deterministic"
        with zipfile.ZipFile(io.BytesIO(value.zip_bytes())) as archive:
            actual = {name.split("/", 1)[1]: archive.read(name) for name in archive.namelist()}
        assert actual == dict(value.entries), "Hosted projected bytes and ZIP bytes must match"
        assert set(actual) == {"SKILL.md", "references/brand-rules.md", "references/evals.md", "references/examples.md"}
        assert actual["SKILL.md"].startswith(b"---\nname:"), "Export must have canonical frontmatter"
    assert b'the best' not in dict(b1.entries)["references/brand-rules.md"]
    assert b'the best' in dict(a2.entries)["references/evals.md"], "A's eval must travel with A's rule"

    rejected = 0
    for unsafe in ("../other-brand.md", "/private-corpus.md", "references/SKILL.md", "references/code.py"):
        try:
            module.validate_package(text="Synthetic test", canonical=a1.metadata,
                                    support_files=[module.SupportFile(unsafe, "synthetic")])
        except module.PackageValidationError:
            rejected += 1
        else:
            raise AssertionError(f"Unsafe brand-editor support path was accepted: {unsafe}")
    print(f"Synthetic package checks pass: two brands, retained versions, export parity, {rejected} rejected paths.")
    print("No runner generation, updater activation, or model-based behavior was tested.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend-packages", type=Path, required=True)
    main(parser.parse_args().backend_packages.resolve())
