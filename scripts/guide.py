"""Nogat's AGENTS.md, generated from ecosystem.yaml (HUB-4.3, ECO-048, ECO-052).

A routing table (task, tool, entry command) built from the `routes` of every
project, each row linking the tool's guide for agents; the tools' own blocks
(AGI-8.2) are not inlined. `uv run scripts/ecosystem.py agents` writes the
file and `agents --check` fails when it is stale. The budget of DOC-1.7 is
checked by `standard`, like that of every other file of Nogat.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

# Guides are read raw (DOC-1.4, DOC-5.2) on the branch every repository
# releases from (DEV-3.1).
RAW = "https://raw.githubusercontent.com"
BRANCH = "main"
HTTP_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE")
INTERFACES = (("cli", "CLI"), ("mcp", "MCP"), ("rest", "REST"), ("python", "Python"))
LAST_LINE = "Developing this repository? Read CLAUDE.md."  # DOC-4.2


def _github_path(repo: str) -> str | None:
    """Return `<owner>/<name>` of a github.com repository URL, else None."""
    url = urlsplit(repo)
    path = url.path.strip("/").removesuffix(".git")
    if url.netloc != "github.com" or path.count("/") != 1:
        return None
    return path


def _raw(project: dict[str, Any], path: str) -> str:
    """Raw URL of a file of a project's repository."""
    owner_name = _github_path(project["repo"])
    if owner_name is None:
        raise ValueError(f"{project['name']}: repo is not a github.com repository URL")
    return f"{RAW}/{owner_name}/{BRANCH}/{path}"


def guide_url(project: dict[str, Any]) -> str:
    """Return the raw URL of the document an agent reads first about a project.

    A tool with a CLI has a generated AGENTS.md; an app has none (DOC-1.1), so
    its README stands in.
    """
    has_agents_md = "tool" in project["profiles"] and project["interfaces"]["cli"]
    return _raw(project, "AGENTS.md" if has_agents_md else "README.md")


def route_problems(registry: dict[str, Any]) -> list[str]:
    """Check the routes against the interfaces of their projects (HUB-2.9).

    Every project but the hub needs a route, so that the table reaches its
    guide; a route starts with the project's CLI or is an HTTP request to a
    project with a REST interface; a task is routed once; the repositories
    are on GitHub, where the guides are linked.
    """
    projects = registry["projects"]
    problems: list[str] = []
    hubs = [p["name"] for p in projects if "hub" in p["profiles"]]
    if len(hubs) != 1:
        problems.append(f"one project must have the hub profile, found {len(hubs)}")
    routed: dict[str, str] = {}
    for project in projects:
        name = project["name"]
        routes = project.get("routes", [])
        if "hub" not in project["profiles"] and not routes:
            problems.append(f"{name}: no routes, so the routing table skips it")
        if _github_path(project["repo"]) is None:
            problems.append(f"{name}: repo is not a github.com/<owner>/<name> URL")
        cli = project["interfaces"]["cli"]
        for route in routes:
            command = route["command"]
            if command.split(" ", 1)[0] in HTTP_METHODS:
                if project["interfaces"]["rest"] is None:
                    problems.append(
                        f"{name}: route {command!r} is an HTTP request, "
                        "but the project has no REST interface"
                    )
            elif cli is None or not command.startswith(f"{cli} "):
                problems.append(
                    f"{name}: route {command!r} starts with neither its CLI "
                    f"({cli}) nor an HTTP method"
                )
            task = route["task"].casefold()
            if task in routed:
                problems.append(
                    f"{name}: task {route['task']!r} is already routed by "
                    f"{routed[task]}"
                )
            routed.setdefault(task, name)
    return problems


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _and(names: list[str]) -> str:
    if len(names) < 2:
        return "".join(names)
    return f"{', '.join(names[:-1])} and {names[-1]}"


def _interfaces(project: dict[str, Any]) -> str:
    found = [
        f"{label} `{project['interfaces'][key]}`"
        for key, label in INTERFACES
        if project["interfaces"][key]
    ]
    return ", ".join(found) or "none"


def render(registry: dict[str, Any]) -> str:
    """Return Nogat's AGENTS.md generated from the registry (HUB-4.3)."""
    projects = registry["projects"]
    hub = next(p for p in projects if "hub" in p["profiles"])
    members = [p for p in projects if "hub" not in p["profiles"]]
    routed = [p for p in members if p.get("routes")]
    stores = [
        p["name"]
        for p in members
        if any(item["kind"] == "store" for item in p["provides"])
    ]
    root = (
        f"; `--root` writes the versioned store of {_and(stores)}"
        " (default `<data_dir>/<tool>`)"
        if stores
        else ""
    )
    out: list[str] = [
        "# Nogat - guide for agents",
        "",
        "> Generated from `ecosystem.yaml`: `uv run scripts/ecosystem.py agents`."
        " Do not edit it by hand.",
        "",
        "## Purpose and scope",
        "",
        "Nogat is the hub of an ecosystem of tools for hydrology, meteorology and"
        f" geodata in Poland and Czechia: {_and([p['name'] for p in members])}."
        " It holds the shared standard, the project registry and the map of what"
        " feeds what. It downloads and computes nothing itself.",
        "",
        "Use it to find the tool for a task and the command to start with, then"
        " read that tool's guide, linked in the table; and to plan a change that"
        " spans projects: a plan in `docs/plans/` comes first, producers before"
        " consumers.",
        "",
        "Not for running a task: call the tool. Its guide gives its options,"
        " flows and error codes.",
        "",
        "## Routing table",
        "",
        "One row per task. A tool that is not `active` is marked in its row; an"
        " app has no AGENTS.md, so its link is its README.",
        "",
        "| Task | Tool | Entry command |",
        "|---|---|---|",
    ]
    for project in routed:
        state = "" if project["status"] == "active" else f" ({project['status']})"
        tool = f"[{project['name']}][{project['name'].lower()}]{state}"
        for route in project["routes"]:
            out.append(f"| {_cell(route['task'])} | {tool} | `{route['command']}` |")
    out.append("")
    out += [f"[{p['name'].lower()}]: {guide_url(p)}" for p in routed]

    out += [
        "",
        "## Tools",
        "",
        "| Tool | Status | Interfaces | What it is |",
        "|---|---|---|---|",
    ]
    for project in members:
        out.append(
            f"| {project['name']} | {project['status']} | {_interfaces(project)} "
            f"| {_cell(project['summary'])} |"
        )

    out += [
        "",
        "## Calling a tool",
        "",
        "Every tool (profile `tool`) is called the same way:",
        "",
        "1. **Discover, do not guess:** `<tool> commands list` lists the commands;"
        ' `<tool> commands schema --command "<group> <verb>"` gives the options'
        " of one, with values and examples.",
        "2. **Check, then run:** a command that writes has `--check`, which plans"
        " without effects; run the plan first.",
        "3. **Read the result:** `status` of the envelope is `ok`, `partial` or"
        " `failed` (exit 0, 10, 11); `partial` and `failed` are results, not"
        " errors: read `items` and retry only the failed units.",
        "4. **Decide by code:** an error is a document on the last line of stderr;"
        " its `code` and exit code come from the shared error registry (below).",
        "5. **Know where data goes:** `--output-dir` (`-o`) writes plain files and"
        f" `--output` one file{root}; `--force` replaces existing files and"
        " nothing else is overwritten; an `--output-dir` inside a store is"
        " refused with `conflict`.",
        "",
        "## More",
        "",
        f"- [Ecosystem map]({_raw(hub, 'docs/ECOSYSTEM_MAP.md')}): data flow, what"
        " each project provides and who consumes it",
        f"- [Registry]({_raw(hub, 'ecosystem.yaml')}): the projects, their"
        " interfaces, routes and exchanged data",
        f"- [Error registry]({_raw(hub, 'standards/ERROR_REGISTRY.md')}): the codes"
        " and exit codes of every tool",
        f"- [Agent interface standard]({_raw(hub, 'standards/AGENT_INTERFACE.md')}):"
        " the catalog, CLI, result and error documents every tool follows",
        "",
        LAST_LINE,
    ]
    return "\n".join(out) + "\n"
