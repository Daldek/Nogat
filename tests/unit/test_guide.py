"""Unit tests of scripts/guide.py: the routing table of Nogat's AGENTS.md."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

import guide
import pytest

RAW = "https://raw.githubusercontent.com/Daldek"


def _project(name: str, **fields: Any) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "name": name,
        "summary": f"{name} test project.",
        "profiles": ["tool"],
        "status": "active",
        "repo": f"https://github.com/Daldek/{name}",
        "visibility": "public",
        "distribution": {"pypi": None, "import_name": name.lower()},
        "interfaces": {"cli": name.lower(), "mcp": None, "rest": None, "python": None},
        "routes": [{"task": f"Run {name}", "command": f"{name.lower()} run"}],
        "data_sources": [],
        "provides": [],
        "depends_on": [],
    }
    entry.update(fields)
    return entry


def _registry() -> dict[str, Any]:
    hub = _project("Hub", profiles=["hub"])
    del hub["routes"]
    hub["interfaces"]["cli"] = None
    alpha_routes = [
        {"task": "Fetch the alpha data", "command": "alpha fetch"},
        {"task": "Read the alpha data", "command": "alpha read"},
    ]
    beta = _project(
        "Beta",
        profiles=["app"],
        status="research",
        interfaces={"cli": None, "mcp": None, "rest": "/api", "python": None},
        routes=[{"task": "Ask beta", "command": "POST /api/ask"}],
    )
    return {"projects": [hub, _project("Alpha", routes=alpha_routes), beta]}


def _section(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    start = lines.index(f"## {heading}") + 1
    stop = next((i for i in range(start, len(lines)) if lines[i][:3] == "## "), None)
    return lines[start:stop]


def _table(text: str, heading: str) -> list[list[str]]:
    """Return the data rows of the table under a heading, as lists of cells."""
    rows = [r for r in _section(text, heading) if r.startswith("| ")]
    return [
        [c.strip() for c in re.split(r"(?<!\\)\|", row.strip())[1:-1]]
        for row in rows[1:]
    ]


@pytest.mark.parametrize(
    "repo",
    [
        "https://github.com/Daldek/Alpha",
        "https://github.com/Daldek/Alpha/",
        "https://github.com/Daldek/Alpha.git",
    ],
)
@pytest.mark.parametrize(
    ("profiles", "cli", "document"),
    [
        (["tool"], "alpha", "AGENTS.md"),
        (["tool", "app"], "alpha", "AGENTS.md"),
        (["app"], "alpha", "README.md"),
        (["tool"], None, "README.md"),
    ],
)
def test_guide_url_names_the_document_an_agent_reads_first(
    repo: str, profiles: list[str], cli: str | None, document: str
) -> None:
    project = _project("Alpha", repo=repo, profiles=profiles)
    project["interfaces"]["cli"] = cli
    assert guide.guide_url(project) == f"{RAW}/Alpha/main/{document}"


def test_guide_url_refuses_a_repository_that_is_not_on_github() -> None:
    project = _project("Alpha", repo="https://gitlab.com/Daldek/Alpha")
    with pytest.raises(ValueError, match="github.com"):
        guide.guide_url(project)


def test_render_has_one_row_per_route_in_registry_order() -> None:
    rows = _table(guide.render(_registry()), "Routing table")
    assert [(row[0], row[2]) for row in rows] == [
        ("Fetch the alpha data", "`alpha fetch`"),
        ("Read the alpha data", "`alpha read`"),
        ("Ask beta", "`POST /api/ask`"),
    ]


def test_render_links_each_tool_by_reference_and_marks_one_that_is_not_active() -> None:
    text = guide.render(_registry())
    assert [row[1] for row in _table(text, "Routing table")] == [
        "[Alpha][alpha]",
        "[Alpha][alpha]",
        "[Beta][beta] (research)",
    ]
    definitions = [line for line in text.splitlines() if re.match(r"\[\w+\]: ", line)]
    assert definitions == [
        f"[alpha]: {RAW}/Alpha/main/AGENTS.md",
        f"[beta]: {RAW}/Beta/main/README.md",
    ]


def test_render_keeps_a_pipe_of_a_task_inside_its_cell() -> None:
    registry = _registry()
    registry["projects"][1]["routes"][0]["task"] = "Choose a | b"
    rows = _table(guide.render(registry), "Routing table")
    assert rows[0] == ["Choose a \\| b", "[Alpha][alpha]", "`alpha fetch`"]


def test_render_leaves_out_a_project_without_routes_and_the_hub() -> None:
    registry = _registry()
    del registry["projects"][2]["routes"]
    text = guide.render(registry)
    assert [row[0] for row in _table(text, "Routing table")] == [
        "Fetch the alpha data",
        "Read the alpha data",
    ]
    assert "[beta]:" not in text
    assert [row[0] for row in _table(text, "Tools")] == ["Alpha", "Beta"]


@pytest.mark.parametrize(
    ("provides", "named"),
    [
        ([{"id": "alpha-store/1", "kind": "store", "summary": "A store."}], True),
        ([{"id": "alpha-meta/1", "kind": "sidecar", "summary": "A sidecar."}], False),
    ],
)
def test_render_names_the_root_option_only_for_tools_with_a_store(
    provides: list[dict[str, str]], named: bool
) -> None:
    registry = _registry()
    registry["projects"][1]["provides"] = provides
    lines = [line for line in guide.render(registry).splitlines() if "--root" in line]
    assert bool(lines) is named
    assert all("Alpha" in line for line in lines)


def test_render_ends_with_the_pointer_to_claude_md_and_one_newline() -> None:
    text = guide.render(_registry())
    assert text.splitlines()[-1] == "Developing this repository? Read CLAUDE.md."
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_route_problems_clean_registry_has_none() -> None:
    assert guide.route_problems(_registry()) == []


def _drop_routes(registry: dict[str, Any]) -> None:
    del registry["projects"][1]["routes"]


def _foreign_cli(registry: dict[str, Any]) -> None:
    registry["projects"][1]["routes"][0]["command"] = "other fetch"


def _longer_cli_name(registry: dict[str, Any]) -> None:
    registry["projects"][1]["routes"][0]["command"] = "alphabet fetch"


def _request_without_rest(registry: dict[str, Any]) -> None:
    registry["projects"][1]["routes"][0]["command"] = "GET /api/alpha"


def _command_without_cli(registry: dict[str, Any]) -> None:
    registry["projects"][2]["routes"][0]["command"] = "beta ask"


def _task_of_another_tool(registry: dict[str, Any]) -> None:
    registry["projects"][2]["routes"][0]["task"] = "FETCH THE ALPHA DATA"


def _task_twice(registry: dict[str, Any]) -> None:
    registry["projects"][1]["routes"][1]["task"] = "Fetch the alpha data"


def _not_on_github(registry: dict[str, Any]) -> None:
    registry["projects"][1]["repo"] = "https://gitlab.com/Daldek/Alpha"


def _no_hub(registry: dict[str, Any]) -> None:
    del registry["projects"][0]


@pytest.mark.parametrize(
    ("change", "problem"),
    [
        (_drop_routes, "Alpha: no routes"),
        (_foreign_cli, "Alpha: route 'other fetch' starts with neither its CLI"),
        (_longer_cli_name, "Alpha: route 'alphabet fetch' starts with neither"),
        (_request_without_rest, "Alpha: route 'GET /api/alpha' is an HTTP request"),
        (_command_without_cli, "Beta: route 'beta ask' starts with neither"),
        (_task_of_another_tool, "Beta: task 'FETCH THE ALPHA DATA' is already routed"),
        (_task_twice, "Alpha: task 'Fetch the alpha data' is already routed by Alpha"),
        (_not_on_github, "Alpha: repo is not a github.com/<owner>/<name> URL"),
        (_no_hub, "one project must have the hub profile, found 0"),
    ],
)
def test_route_problems_reports(
    change: Callable[[dict[str, Any]], None], problem: str
) -> None:
    registry = _registry()
    change(registry)
    assert any(problem in found for found in guide.route_problems(registry))
