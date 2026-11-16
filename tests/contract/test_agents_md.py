"""Nogat's AGENTS.md against its generator and the rules for the file (DEV-10.4).

AGENTS.md is generated from ecosystem.yaml and never edited by hand (DOC-4.1);
these tests pin what an agent relies on: the file is fresh, within the budget
of DOC-1.7, links the guide of every tool with absolute URLs (DOC-1.4, HUB-4.3)
and ends with the pointer of DOC-4.2.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import ecosystem
import guide
import pytest
import standard

ROOT = Path(__file__).resolve().parents[2]
AGENTS = ROOT / "AGENTS.md"


@pytest.fixture(scope="module")
def registry() -> dict[str, Any]:
    return ecosystem.load()


def test_agents_md_equals_the_generator_output(registry: dict[str, Any]) -> None:
    assert AGENTS.read_text(encoding="utf-8") == guide.render(registry)


def test_generated_agents_md_fits_the_budget_of_doc_1_7(
    registry: dict[str, Any],
) -> None:
    table = (ROOT / "standards" / "DOCUMENTATION_STANDARDS.md").read_text("utf-8")
    budgets = {m["path"]: m for m in standard.BUDGET_ROW.finditer(table)}
    data = guide.render(registry).encode("utf-8")
    assert data.count(b"\n") <= int(budgets["AGENTS.md"]["lines"])
    assert len(data) <= int(budgets["AGENTS.md"]["kib"]) * 1024


def test_every_link_of_agents_md_is_an_absolute_url() -> None:
    text = AGENTS.read_text(encoding="utf-8")
    inline = re.findall(r"\]\(([^)\s]*)\)", text)
    reference = re.findall(r"^\[[^\]]+\]:\s*(\S*)", text, re.MULTILINE)
    assert inline or reference
    assert all(t.startswith("https://") for t in [*inline, *reference])


def test_agents_md_links_the_guide_of_every_tool(registry: dict[str, Any]) -> None:
    text = AGENTS.read_text(encoding="utf-8")
    tools = [p for p in registry["projects"] if "hub" not in p["profiles"]]
    assert tools
    for project in tools:
        assert guide.guide_url(project) in text, project["name"]


def test_agents_md_ends_with_the_pointer_to_claude_md() -> None:
    lines = AGENTS.read_text(encoding="utf-8").splitlines()
    assert lines[-1] == "Developing this repository? Read CLAUDE.md."
