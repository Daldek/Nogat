"""Unit tests of scripts/standard.py on small throwaway trees."""

from __future__ import annotations

from pathlib import Path

import pytest
import standard


def _tree(root: Path, files: dict[str, str]) -> Path:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


BASE = {
    "standards/README.md": "# Standard\n\n## Changelog\n\n- Deleted IDs: DEV-9.9.\n",
    "standards/DEVELOPMENT_STANDARDS.md": (
        "# Dev\n\nPart of standard 2.1 · IDs `DEV-…`\n\n## 1. Profiles\n\n"
        "**DEV-1.1** Rule.\n\n**DEV-1.2** See DEV-1.1 and DOC §2.\n"
    ),
    "standards/DOCUMENTATION_STANDARDS.md": (
        "# Doc\n\nPart of standard 2.1 · IDs `DOC-…`\n\n## 2. README\n\n"
        "**DOC-2.1** Rule, ECO-001.\n\n"
        "| Text | Budget | Enforced by |\n|---|---|---|\n"
        "| `CLAUDE.md` | 3 lines | review |\n"
        "| `AGENTS.md` | 200 lines and 1 KiB | contract test |\n"
        "| Description ladder: `pyproject` `description` | 10 characters | review |\n"
    ),
    "standards/DECISIONS.md": "# Decisions\n\n## ECO-001 First\n\nText.\n",
}


def test_id_problems_clean_tree_has_none(tmp_path: Path) -> None:
    assert standard.id_problems(_tree(tmp_path, BASE)) == []


@pytest.mark.parametrize(
    ("extra", "problem"),
    [
        ({"docs/plan.md": "Uses DEV-1.3.\n"}, "docs/plan.md:1: DEV-1.3 is not defined"),
        ({"docs/plan.md": "See DEV §4.\n"}, "docs/plan.md:1: DEV §4 is not a section"),
        (
            {"docs/plan.md": "Per ECO-002.\n"},
            "docs/plan.md:1: ECO-002 is not a decision",
        ),
        ({"scripts/x.sh": "# DOC-7.1\n"}, "scripts/x.sh:1: DOC-7.1 is not defined"),
        (
            {"standards/RELEASE.md": "# R\n\nIDs `REL-…`\n\n**DEV-1.1** Copy.\n"},
            "DEV-1.1 defined 2 times",
        ),
        (
            {"standards/RELEASE.md": "# R\n\nIDs `REL-…`\n\n**DEV-5.1** Here.\n"},
            "standards/RELEASE.md: DEV-5.1 defined here",
        ),
    ],
)
def test_id_problems_reports(
    tmp_path: Path, extra: dict[str, str], problem: str
) -> None:
    assert problem in standard.id_problems(_tree(tmp_path, {**BASE, **extra}))


def test_id_problems_ignores_changelog_and_v1(tmp_path: Path) -> None:
    extra = {"standards/legacy/v1.0/OLD.md": "DEV-42.1\n"}
    assert standard.id_problems(_tree(tmp_path, {**BASE, **extra})) == []


@pytest.mark.parametrize(
    ("heading", "anchor"),
    [
        (
            "ECO-002 Machine-readable registry `ecosystem.yaml`",
            "eco-002-machine-readable-registry-ecosystemyaml",
        ),
        ("2. Registry `ecosystem.yaml`", "2-registry-ecosystemyaml"),
        ("Zen of Nogat", "zen-of-nogat"),
        ("ČÚZK: źródła (PL/CZ)", "čúzk-źródła-plcz"),
    ],
)
def test_slug_matches_github(heading: str, anchor: str) -> None:
    assert standard.slug(heading) == anchor


def test_anchors_number_duplicates() -> None:
    text = "# A\n## Notes\n```\n# not a heading\n```\n## Notes\n"
    assert standard.anchors(text) == {"a", "notes", "notes-1"}


def test_link_problems(tmp_path: Path) -> None:
    root = _tree(
        tmp_path,
        {
            "a.md": "# Top\n\n## Part two\n",
            "docs/b.md": (
                "[ok](../a.md#part-two) [self](#local) [web](https://x.org/y.md)\n"
                "[gone](../c.md) [bad](../a.md#part-three)\n"
                "`[code](nowhere.md)`\n"
                "```\n[fenced](nowhere.md)\n```\n"
                "## Local\n"
            ),
        },
    )
    assert standard.link_problems(root) == [
        "docs/b.md:2: ../c.md does not exist",
        "docs/b.md:2: no heading for #part-three",
    ]


def test_budget_problems(tmp_path: Path) -> None:
    root = _tree(
        tmp_path,
        {
            **BASE,
            "CLAUDE.md": "1\n2\n3\n4\n",
            "AGENTS.md": "x" * 2000 + "\n",
            "pyproject.toml": '[project]\ndescription = "eleven char"\n',
        },
    )
    assert standard.budget_problems(root) == [
        "CLAUDE.md: 4 lines, budget 3 (DOC-1.7)",
        "AGENTS.md: 2001 bytes, budget 1 KiB",
        "pyproject.toml: description 11 characters, budget 10",
    ]


REGISTRY = {
    "outcomes": [{"status": "ok", "exit_code": 0, "meaning": "Done."}],
    "errors": [
        {
            "code": "rate_limited",
            "exit_code": None,
            "http_status": 429,
            "meaning": "Slow down.",
        }
    ],
}


def test_generated_blocks_regenerate_and_check(tmp_path: Path) -> None:
    path = tmp_path / "ERR.md"
    path.write_text(
        "Intro\n<!-- generated: error-outcomes from json; do not edit -->\nold\n"
        "<!-- end generated -->\n<!-- generated: error-codes x -->\n"
        "<!-- end generated -->\nOutro\n",
        encoding="utf-8",
    )
    blocks = standard.error_tables(REGISTRY)
    assert standard.generated_problems(path, blocks, "ERR.md") == [
        "ERR.md: generated blocks are stale; "
        "run: uv run scripts/ecosystem.py standard --write"
    ]
    path.write_text(standard.regenerate(path.read_text(), blocks), encoding="utf-8")
    text = path.read_text()
    assert "| `ok` | 0 | Done. |" in text
    assert '| <a id="rate_limited"></a>`rate_limited` | – | 429 | Slow down. |' in text
    assert "rate_limited" in standard.anchors(text)
    assert text.startswith("Intro\n") and text.endswith("Outro\n")
    assert standard.generated_problems(path, blocks, "ERR.md") == []


def test_generated_problems_missing_block(tmp_path: Path) -> None:
    path = tmp_path / "ERR.md"
    path.write_text("no blocks\n", encoding="utf-8")
    problems = standard.generated_problems(path, standard.error_tables(REGISTRY), "E")
    assert problems == [
        "E: no generated block 'error-outcomes'",
        "E: no generated block 'error-codes'",
    ]
