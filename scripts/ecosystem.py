# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6,<7", "jsonschema>=4.23,<5", "packaging>=24"]
# ///
"""Validate ecosystem.yaml, generate docs/ECOSYSTEM_MAP.md, compare dependencies.

Usage:
    uv run scripts/ecosystem.py validate
    uv run scripts/ecosystem.py map            # write docs/ECOSYSTEM_MAP.md
    uv run scripts/ecosystem.py map --check    # exit 1 when the map is stale
    uv run scripts/ecosystem.py deps           # third-party ranges across checkouts
    uv run scripts/ecosystem.py deps --installed   # also versions in each .venv
    uv run scripts/ecosystem.py drift          # consumers' pins against producers' tags

Checkouts are resolved as siblings of Nogat or under NOGAT_WORKSPACE (HUB §3).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

import jsonschema
import yaml
from packaging.requirements import InvalidRequirement, Requirement
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name
from packaging.version import InvalidVersion, Version

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "ecosystem.yaml"
SCHEMA = ROOT / "schemas" / "ecosystem.schema.json"
MAP = ROOT / "docs" / "ECOSYSTEM_MAP.md"

LOCAL_PATH = re.compile(r"(^|\s)(/home/|/Users/|~/|[A-Za-z]:\\)")
COMMIT = re.compile(r"^[0-9a-f]{7,40}$")
STANDARDS = ROOT / "standards"
README_VERSION = re.compile(r"^Standard (\d+\.\d+)\b", re.MULTILINE)
TOPIC_VERSION = re.compile(r"^Part of standard (\S+)", re.MULTILINE)


def load() -> dict[str, Any]:
    with REGISTRY.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise SystemExit(f"{REGISTRY.name}: top level must be a mapping")
    return data


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [s for v in value.values() for s in _strings(v)]
    if isinstance(value, list):
        return [s for v in value for s in _strings(v)]
    return []


def standard_version_problems(version: str) -> list[str]:
    """Check that every statement of the standard version agrees (HUB-6.1)."""
    problems: list[str] = []
    readme = (STANDARDS / "README.md").read_text(encoding="utf-8")
    found = README_VERSION.search(readme)
    if found is None:
        problems.append("standards/README.md: no 'Standard X.Y' version line")
    elif found.group(1) != version:
        problems.append(
            f"standards/README.md: version {found.group(1)} != standard_version {version}"
        )
    registry = json.loads(
        (STANDARDS / "error_registry.json").read_text(encoding="utf-8")
    )
    if registry.get("standard_version") != version:
        problems.append(
            f"standards/error_registry.json: standard_version "
            f"{registry.get('standard_version')!r} != {version}"
        )
    for path in sorted(STANDARDS.glob("*.md")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:5])
        header = TOPIC_VERSION.search(head)
        if header is not None and header.group(1) != version:
            problems.append(
                f"standards/{path.name}: 'Part of standard {header.group(1)}' != {version}"
            )
    return problems


def validate(registry: dict[str, Any]) -> list[str]:
    """Return problems: schema violations first, then cross-reference errors."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    problems = [
        f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
        for e in sorted(
            validator.iter_errors(registry),
            key=lambda e: list(map(str, e.absolute_path)),
        )
    ]
    if problems:
        return problems

    sources = {s["id"] for s in registry["data_sources"]}
    projects = {p["name"]: p for p in registry["projects"]}
    if len(projects) != len(registry["projects"]):
        problems.append("project names are not unique")

    provided: dict[str, str] = {}
    for p in registry["projects"]:
        for item in p["provides"]:
            owner = provided.setdefault(item["id"], p["name"])
            if owner != p["name"]:
                problems.append(
                    f"{p['name']}: provides id {item['id']!r} already provided by {owner}"
                )

    for p in registry["projects"]:
        name = p["name"]
        for source in p["data_sources"]:
            if source not in sources:
                problems.append(f"{name}: unknown data source {source!r}")
        for dep in p["depends_on"]:
            producer = dep["project"]
            if producer == name:
                problems.append(f"{name}: depends on itself")
                continue
            if producer not in projects:
                problems.append(f"{name}: depends on unknown project {producer!r}")
                continue
            own = {i["id"] for i in projects[producer]["provides"]}
            for fmt in dep["exchange"]:
                if fmt not in own:
                    problems.append(
                        f"{name} -> {producer}: {fmt!r} is not in {producer}.provides"
                    )

    for s in _strings(registry):
        if LOCAL_PATH.search(s):
            problems.append(f"local path in registry (HUB-2.4): {s!r}")
    problems.extend(standard_version_problems(registry["standard_version"]))
    return problems


def _cell(text: str) -> str:
    return (
        text.replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("|", "\\|")
        .replace("\n", " ")
    )


def _code(items: list[str]) -> str:
    return ", ".join(f"`{i}`" for i in items) if items else "—"


def _node(name: str) -> str:
    return re.sub(r"\W", "_", name)


def render(registry: dict[str, Any]) -> str:
    projects = registry["projects"]
    sources = {s["id"]: s for s in registry["data_sources"]}
    edges = [(p, d) for p in projects for d in p["depends_on"]]

    out: list[str] = [
        "# Ecosystem map",
        "",
        "<!-- Generated by `uv run scripts/ecosystem.py map` from ecosystem.yaml. Do not edit. -->",
        "",
        "Projects, dependencies and data exchanged between them. Source of truth:",
        "[`ecosystem.yaml`](../ecosystem.yaml) (standard",
        f"{registry['standard_version']}, [ECOSYSTEM_HUB](../standards/ECOSYSTEM_HUB.md)).",
        "",
        "## Data flow",
        "",
        "Arrows run from producer to consumer and carry the transport. Dotted",
        "arrows are planned dependencies or file and store exchanges without a",
        "package dependency (labelled).",
        "",
        "```mermaid",
        "flowchart LR",
    ]
    for p in projects:
        label = f"{p['name']}<br/>{p['status']}"
        out.append(f'  {_node(p["name"])}["{label}"]')
    out.append("  subgraph external[External data sources]")
    for s in registry["data_sources"]:
        out.append(f'    src_{_node(s["id"])}(["{s["id"]}"])')
    out.append("  end")
    for p in projects:
        for s in p["data_sources"]:
            out.append(f"  src_{_node(s)} --> {_node(p['name'])}")
    for consumer, dep in edges:
        label = "/".join(dep["via"])
        if dep["status"] == "planned":
            arrow = f"-. planned: {label} .->"
        elif dep["kind"] == "data":
            arrow = f"-. {label}, no package .->"
        else:
            arrow = f"-- {label} -->"
        out.append(f"  {_node(dep['project'])} {arrow} {_node(consumer['name'])}")
    out += ["```", ""]

    out += [
        "## Projects",
        "",
        "| Project | Profiles | Status | Summary |",
        "|---|---|---|---|",
    ]
    for p in projects:
        out.append(
            f"| [{p['name']}]({p['repo']}) | {', '.join(p['profiles'])} | {p['status']} "
            f"| {_cell(p['summary'])} |"
        )
    out.append("")

    out += [
        "## Dependencies and exchanged data",
        "",
        "| Consumer | Producer | Kind | Status | Via | Exchanged data |",
        "|---|---|---|---|---|---|",
    ]
    for consumer, dep in edges:
        out.append(
            f"| {consumer['name']} | {dep['project']} | {dep['kind']} | {dep['status']} "
            f"| {', '.join(dep['via'])} | {_code(dep['exchange'])} |"
        )
    out.append("")

    notes = [(c, d) for c, d in edges if d.get("note") or d.get("uses")]
    if notes:
        out += ["### Details", ""]
        for consumer, dep in notes:
            parts = []
            if dep.get("uses"):
                parts.append(f"uses {_code(dep['uses'])}")
            if dep.get("note"):
                parts.append(dep["note"])
            out.append(
                f"- **{consumer['name']} → {dep['project']}**: " + "; ".join(parts)
            )
        out.append("")

    out += ["## What each project provides", ""]
    for p in projects:
        if not p["provides"]:
            continue
        out += [
            f"### {p['name']}",
            "",
            "| Id | Kind | Consumers | Description |",
            "|---|---|---|---|",
        ]
        for item in p["provides"]:
            consumers = [
                c["name"] + (" (planned)" if d["status"] == "planned" else "")
                for c, d in edges
                if d["project"] == p["name"] and item["id"] in d["exchange"]
            ]
            out.append(
                f"| `{item['id']}` | {item['kind']} | {', '.join(consumers) or '—'} "
                f"| {_cell(item['summary'])} |"
            )
        out.append("")

    out += [
        "## External data sources",
        "",
        "Direct access only; data obtained through another project is shown in the",
        "data-flow diagram.",
        "",
        "| Source | Country | Licence | Accessed directly by |",
        "|---|---|---|---|",
    ]
    for sid, s in sources.items():
        users = [p["name"] for p in projects if sid in p["data_sources"]]
        out.append(
            f"| [{s['name']}]({s['url']}) | {s['country']} | {_cell(s['licence'])} "
            f"| {', '.join(users) or '—'} |"
        )
    out.append("")
    return "\n".join(out)


def workspace() -> Path:
    return Path(os.environ.get("NOGAT_WORKSPACE") or ROOT.parent)


def _requirement_lines(path: Path) -> list[str]:
    if path.suffix == ".toml":
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        project = data.get("project", {})
        lines = list(project.get("dependencies") or [])
        for extra in (project.get("optional-dependencies") or {}).values():
            lines += extra
        for group in (data.get("dependency-groups") or {}).values():
            lines += [item for item in group if isinstance(item, str)]
        return lines
    return [
        line.split(" #")[0].strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith(("#", "-"))
    ]


def declared(
    registry: dict[str, Any],
) -> tuple[dict[str, dict[str, SpecifierSet]], list[str]]:
    """Third-party requirements per package and project, plus notes on skipped checkouts."""
    ecosystem = {canonicalize_name(p["name"]) for p in registry["projects"]}
    ecosystem |= {
        canonicalize_name(n)
        for p in registry["projects"]
        for n in p["distribution"].values()
        if n
    }
    result: dict[str, dict[str, SpecifierSet]] = {}
    notes: list[str] = []
    for p in registry["projects"]:
        manifests = p.get("python_manifests") or []
        checkout = workspace() / p["name"]
        if manifests and not checkout.is_dir():
            notes.append(f"{p['name']}: no checkout at {checkout}")
            continue
        for manifest in manifests:
            path = checkout / manifest
            if not path.is_file():
                notes.append(f"{p['name']}: {manifest} missing")
                continue
            for line in _requirement_lines(path):
                try:
                    req = Requirement(line)
                except InvalidRequirement:
                    notes.append(f"{p['name']}: cannot parse {line!r} in {manifest}")
                    continue
                name = canonicalize_name(req.name)
                if name in ecosystem or req.url:
                    continue
                specs = result.setdefault(name, {})
                specs[p["name"]] = specs.get(p["name"], SpecifierSet()) & req.specifier
    return result, notes


def range_conflicts(specs: dict[str, SpecifierSet]) -> str | None:
    """Describe why the declared ranges cannot share one version, or None.

    Candidates are the versions named by the ranges themselves; ranges that
    admit none of them in common are reported.
    """
    candidates: set[Version] = set()
    for spec in specs.values():
        for s in spec:
            try:
                candidates.add(Version(s.version.removesuffix(".*")))
            except InvalidVersion:
                continue
    if not candidates:
        return None
    if any(
        all(spec.contains(v, prereleases=True) for spec in specs.values())
        for v in candidates
    ):
        return None
    return "no version satisfies " + "; ".join(f"{p} {s}" for p, s in specs.items())


def installed(registry: dict[str, Any]) -> dict[str, tuple[str, dict[str, str]]]:
    """Python version and package versions of each checkout's .venv next to its first manifest."""
    found: dict[str, tuple[str, dict[str, str]]] = {}
    for p in registry["projects"]:
        manifests = p.get("python_manifests") or []
        if not manifests:
            continue
        base = (workspace() / p["name"] / manifests[0]).parent
        python = next(
            (
                c
                for c in (
                    base / ".venv" / "bin" / "python",
                    base / ".venv" / "Scripts" / "python.exe",
                )
                if c.exists()
            ),
            None,
        )
        if python is None:
            continue
        listed = subprocess.run(
            ["uv", "pip", "list", "--format", "json", "--python", str(python)],
            capture_output=True,
            text=True,
            check=True,
        )
        version = subprocess.run(
            [str(python), "-V"], capture_output=True, text=True, check=True
        )
        found[p["name"]] = (
            version.stdout.split()[-1],
            {
                canonicalize_name(x["name"]): x["version"]
                for x in json.loads(listed.stdout)
            },
        )
    return found


def report_deps(registry: dict[str, Any], with_installed: bool) -> int:
    specs, notes = declared(registry)
    shared = {name: s for name, s in sorted(specs.items()) if len(s) > 1}
    conflicts = {name: why for name, s in shared.items() if (why := range_conflicts(s))}
    print(
        f"Declared third-party ranges: {len(specs)} packages, {len(shared)} declared by two or more projects"
    )
    print()
    for name, per_project in shared.items():
        flag = f"  CONFLICT: {conflicts[name]}" if name in conflicts else ""
        ranges = "; ".join(f"{p} {s or '*'}" for p, s in per_project.items())
        print(f"  {name}: {ranges}{flag}")
    if with_installed:
        envs = installed(registry)
        print()
        print(
            "Installed environments: "
            + ", ".join(f"{p} (Python {v})" for p, (v, _) in envs.items())
        )
        names = sorted({n for _, pkgs in envs.values() for n in pkgs})
        differing = []
        for n in names:
            versions = {p: pkgs[n] for p, (_, pkgs) in envs.items() if n in pkgs}
            if len(set(versions.values())) > 1:
                differing.append((n, versions))
        print(f"Packages with different versions across environments: {len(differing)}")
        for n, versions in differing:
            print(f"  {n}: " + "; ".join(f"{p} {v}" for p, v in versions.items()))
    for note in notes:
        print(f"note: {note}", file=sys.stderr)
    return 1 if conflicts else 0


def _latest_tag(checkout: Path) -> str | None:
    """Newest `v*` tag of a checkout, or None without tags or git."""
    try:
        done = subprocess.run(
            ["git", "-C", str(checkout), "tag", "--list", "v*", "--sort=-v:refname"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    tags = done.stdout.split()
    return tags[0] if tags else None


def _matches(req: Requirement, producer: dict[str, Any]) -> bool:
    """Whether a requirement names the producer: import name, PyPI name, nogat-<project> or repo URL."""
    names = {
        canonicalize_name(n)
        for n in (
            producer["distribution"]["import_name"],
            producer["distribution"]["pypi"],
            f"nogat-{producer['name']}",
        )
        if n
    }
    if canonicalize_name(req.name) in names:
        return True
    return bool(req.url) and producer["repo"].lower() in (req.url or "").lower()


def _pin(req: Requirement) -> tuple[str, str]:
    """Classify a requirement as (kind, value): tag, commit, branch, range, path or none."""
    if req.url:
        if req.url.startswith("file:") or "://" not in req.url:
            return "path", req.url
        last = req.url.split("#")[0].split("?")[0].rstrip("/").rpartition("/")[2]
        ref = last.partition("@")[2]
        if not ref:
            return "none", ""
        if COMMIT.match(ref):
            return "commit", ref[:7]
        if re.match(r"^v?\d", ref):
            return "tag", ref
        return "branch", ref
    if req.specifier:
        return "range", str(req.specifier)
    return "none", ""


def _state(kind: str, value: str, latest: str | None) -> str:
    if kind == "commit":
        return "commit pin"
    if kind == "branch":
        return "branch pin"
    if kind == "path":
        return "path"
    if kind == "none":
        return "not pinned"
    if latest is None:
        return "no tags"
    try:
        newest = Version(latest.lstrip("v"))
        if kind == "tag":
            pinned = Version(value.lstrip("v"))
            return (
                "current"
                if pinned == newest
                else "behind"
                if pinned < newest
                else "ahead"
            )
        return (
            "range ok"
            if SpecifierSet(value).contains(newest, prereleases=True)
            else "range excludes latest"
        )
    except InvalidVersion:
        return "not comparable"


def report_drift(registry: dict[str, Any]) -> int:
    """Print each active runtime or optional dependency: consumer pin against producer tag."""
    by_name = {p["name"]: p for p in registry["projects"]}
    rows: list[tuple[str, str, str, str, str]] = []
    for consumer in registry["projects"]:
        checkout = workspace() / consumer["name"]
        for dep in consumer["depends_on"]:
            if dep["status"] != "active" or dep["kind"] not in ("runtime", "optional"):
                continue
            producer = by_name[dep["project"]]
            who = (consumer["name"], producer["name"])
            producer_checkout = workspace() / producer["name"]
            latest = (
                _latest_tag(producer_checkout) if producer_checkout.is_dir() else None
            )
            if not checkout.is_dir():
                rows.append((*who, "—", latest or "—", "no checkout"))
                continue
            found = False
            for manifest in consumer.get("python_manifests") or []:
                path = checkout / manifest
                if not path.is_file():
                    continue
                for line in _requirement_lines(path):
                    try:
                        req = Requirement(line)
                    except InvalidRequirement:
                        continue
                    if not _matches(req, producer):
                        continue
                    found = True
                    kind, value = _pin(req)
                    pin = (
                        f"{kind} {value} ({manifest})"
                        if value
                        else f"{kind} ({manifest})"
                    )
                    state = (
                        "no tags"
                        if kind in ("tag", "range") and latest is None
                        else _state(kind, value, latest)
                    )
                    rows.append((*who, pin, latest or "—", state))
            if not found:
                rows.append((*who, "—", latest or "—", "not declared"))
    header = ("consumer", "producer", "pin", "latest tag", "state")
    widths = [max(len(r[i]) for r in [header, *rows]) for i in range(5)]
    for row in [header, *rows]:
        print("  ".join(c.ljust(w) for c, w in zip(row, widths, strict=True)).rstrip())
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="validate ecosystem.yaml")
    map_cmd = sub.add_parser("map", help="generate docs/ECOSYSTEM_MAP.md")
    map_cmd.add_argument(
        "--check", action="store_true", help="fail when the map is stale"
    )
    deps_cmd = sub.add_parser(
        "deps", help="compare third-party dependencies across checkouts"
    )
    deps_cmd.add_argument(
        "--installed", action="store_true", help="also compare each checkout's .venv"
    )
    sub.add_parser("drift", help="compare consumers' pins with producers' latest tags")
    args = parser.parse_args()

    registry = load()
    problems = validate(registry)
    if problems:
        for problem in problems:
            print(f"ecosystem.yaml: {problem}", file=sys.stderr)
        return 1
    if args.command == "validate":
        print(f"ecosystem.yaml: {len(registry['projects'])} projects, valid")
        return 0
    if args.command == "deps":
        return report_deps(registry, args.installed)
    if args.command == "drift":
        return report_drift(registry)

    text = render(registry)
    if args.check:
        if not MAP.exists() or MAP.read_text(encoding="utf-8") != text:
            print(
                f"{MAP.relative_to(ROOT)} is stale; run: uv run scripts/ecosystem.py map",
                file=sys.stderr,
            )
            return 1
        print(f"{MAP.relative_to(ROOT)} is up to date")
        return 0
    MAP.parent.mkdir(parents=True, exist_ok=True)
    MAP.write_text(text, encoding="utf-8")
    print(f"wrote {MAP.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
