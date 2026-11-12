"""The GUI kit's manifest, design/kit/nogat-kit.json (DEV-15.6).

A GUI copies the kit byte for byte; the manifest's version and hashes are
what a copy is compared with, so they must describe the files Nogat ships.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

KIT = Path(__file__).resolve().parents[2] / "design" / "kit"
MANIFEST = json.loads((KIT / "nogat-kit.json").read_text(encoding="utf-8"))


def test_manifest_lists_every_kit_file_with_its_hash() -> None:
    shipped = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in KIT.iterdir()
        if p.is_file() and p.name != "nogat-kit.json"
    }
    assert MANIFEST["files"] == shipped, (
        "design/kit/nogat-kit.json is stale: update the hashes and the version"
    )


def test_kit_files_carry_the_nogat_prefix_and_a_semver_version() -> None:
    assert all(name.startswith("nogat-") for name in MANIFEST["files"])
    assert re.fullmatch(
        r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", MANIFEST["version"]
    )
