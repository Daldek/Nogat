"""Validate ecosystem.yaml, generate docs/ECOSYSTEM_MAP.md, compare dependencies.

Usage:
    uv run scripts/ecosystem.py validate
    uv run scripts/ecosystem.py map            # write docs/ECOSYSTEM_MAP.md
    uv run scripts/ecosystem.py map --check    # exit 1 when the map is stale
    uv run scripts/ecosystem.py deps           # third-party ranges across checkouts
    uv run scripts/ecosystem.py deps --installed   # also versions in each .venv
    uv run scripts/ecosystem.py drift          # consumers' pins against producers' tags
    uv run scripts/ecosystem.py standard       # IDs, links, budgets, copies
    uv run scripts/ecosystem.py standard --write   # regenerate blocks, then check

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
from urllib.parse import urlsplit

import jsonschema
import standard
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
VERSIONLESS = {"README.md", "DECISIONS.md"}
INCLUDE = re.compile(r"^(-r|--requirement)(\s+|=)(?P<path>\S+)")
OPTION = re.compile(r"\s+--?[A-Za-z]")


class RegistryError(Exception):
    """A file the tooling reads is missing or malformed; the message names it."""


def _shown(path: Path) -> str:
    """Path for messages, relative to Nogat (siblings appear as `../<Project>`)."""
    return os.path.relpath(path, ROOT)


def _read(path: Path) -> str:
    """Text of a UTF-8 file; RegistryError names the file when it cannot be read."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise RegistryError(f"{_shown(path)}: cannot read: {e}") from e


def _read_json(path: Path) -> Any:
    """Parse a JSON file; RegistryError names the file when it is not valid JSON."""
    try:
        return json.loads(_read(path))
    except json.JSONDecodeError as e:
        raise RegistryError(f"{_shown(path)}: not valid JSON: {e}") from e


def load() -> dict[str, Any]:
    """Read ecosystem.yaml; raise RegistryError when it cannot be read as a mapping."""
    try:
        with REGISTRY.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except OSError as e:
        raise RegistryError(f"{REGISTRY.name}: cannot read: {e.strerror}") from e
    except yaml.YAMLError as e:
        raise RegistryError(f"{REGISTRY.name}: not valid YAML: {e}") from e
    if not isinstance(data, dict):
        raise RegistryError(f"{REGISTRY.name}: top level must be a mapping")
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
    """Check that every statement of the standard version agrees (HUB-6.1).

    Every topic document in `standards/` carries a "Part of standard X.Y"
    line near the top; README.md has the "Standard X.Y" line instead and
    DECISIONS.md is a versionless log (2.x).
    """
    problems: list[str] = []
    readme = _read(STANDARDS / "README.md")
    found = README_VERSION.search(readme)
    if found is None:
        problems.append("standards/README.md: no 'Standard X.Y' version line")
    elif found.group(1) != version:
        problems.append(
            f"standards/README.md: version {found.group(1)} "
            f"!= standard_version {version}"
        )
    registry = _read_json(STANDARDS / "error_registry.json")
    if registry.get("standard_version") != version:
        problems.append(
            f"standards/error_registry.json: standard_version "
            f"{registry.get('standard_version')!r} != {version}"
        )
    for path in sorted(STANDARDS.glob("*.md")):
        if path.name in VERSIONLESS:
            continue
        head = "\n".join(_read(path).splitlines()[:5])
        header = TOPIC_VERSION.search(head)
        if header is None:
            problems.append(f"standards/{path.name}: no 'Part of standard X.Y' line")
        elif header.group(1) != version:
            problems.append(
                f"standards/{path.name}: "
                f"'Part of standard {header.group(1)}' != {version}"
            )
    return problems


def validate(registry: dict[str, Any]) -> list[str]:
    """Return problems: schema violations first, then cross-reference errors."""
    schema = _read_json(SCHEMA)
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
                    f"{p['name']}: provides id {item['id']!r} "
                    f"already provided by {owner}"
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
    """Return docs/ECOSYSTEM_MAP.md generated from the registry (HUB-4.5)."""
    projects = registry["projects"]
    sources = {s["id"]: s for s in registry["data_sources"]}
    edges = [(p, d) for p in projects for d in p["depends_on"]]

    out: list[str] = [
        "# Ecosystem map",
        "",
        "<!-- Generated by `uv run scripts/ecosystem.py map` from ecosystem.yaml."
        " Do not edit. -->",
        "",
        "Projects, dependencies and data exchanged between them. Source of truth:",
        "[`ecosystem.yaml`](../ecosystem.yaml) (standard",
        f"{registry['standard_version']}, "
        "[ECOSYSTEM_HUB](../standards/ECOSYSTEM_HUB.md)).",
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
            f"| [{p['name']}]({p['repo']}) | {', '.join(p['profiles'])} "
            f"| {p['status']} | {_cell(p['summary'])} |"
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
            f"| {consumer['name']} | {dep['project']} | {dep['kind']} "
            f"| {dep['status']} | {', '.join(dep['via'])} "
            f"| {_code(dep['exchange'])} |"
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
    """Directory holding the project checkouts (HUB §3)."""
    return Path(os.environ.get("NOGAT_WORKSPACE") or ROOT.parent)


def _requirement_lines(path: Path, seen: frozenset[Path] = frozenset()) -> list[str]:
    r"""Return the requirement strings of a pyproject.toml or requirements file.

    pyproject.toml contributes dependencies, extras and dependency groups. A
    requirements file is read as pip reads it: `\` continues a line, options
    after a requirement (`--hash=…`) and comments are dropped, `-r` includes
    are followed and other option lines (`-e`, `-c`, `--index-url`) skipped.
    Raises RegistryError when a file cannot be read or parsed.
    """
    text = _read(path)
    if path.suffix == ".toml":
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError as e:
            raise RegistryError(f"{_shown(path)}: not valid TOML: {e}") from e
        project = data.get("project", {})
        lines = list(project.get("dependencies") or [])
        for extra in (project.get("optional-dependencies") or {}).values():
            lines += extra
        for group in (data.get("dependency-groups") or {}).values():
            lines += [item for item in group if isinstance(item, str)]
        return lines
    lines = []
    seen = seen | {path.resolve()}
    for raw in text.replace("\\\n", " ").splitlines():
        line = raw.split(" #")[0].strip()
        if not line or line.startswith("#"):
            continue
        include = INCLUDE.match(line)
        if include:
            target = (path.parent / include["path"]).resolve()
            if target not in seen:
                lines += _requirement_lines(target, seen)
            continue
        if line.startswith("-"):
            continue
        lines.append(OPTION.split(line, maxsplit=1)[0].strip())
    return lines


def declared(
    registry: dict[str, Any],
) -> tuple[dict[str, dict[str, SpecifierSet]], list[str]]:
    """Third-party requirements per package and project, plus notes on skips."""
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
            try:
                lines = _requirement_lines(path)
            except RegistryError as e:
                notes.append(f"{p['name']}: {e}")
                continue
            for line in lines:
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


def _just_above(version: Version) -> Version:
    """Return a release above `version`, below every release sorting after it."""
    release = (*version.release, *[0] * 8, 1)
    return Version(".".join(map(str, release)))


def range_conflicts(specs: dict[str, SpecifierSet]) -> str | None:
    """Describe why the declared ranges cannot share one version, or None.

    The versions that satisfy every range form intervals bounded by the
    versions the ranges name. Each bound and the release just above it, plus
    version 0, are tried; an empty intersection has no such candidate.
    """
    candidates: set[Version] = {Version("0")}
    for spec in specs.values():
        for s in spec:
            try:
                bound = Version(s.version.removesuffix(".*"))
            except InvalidVersion:
                continue
            candidates |= {bound, _just_above(bound)}
    if any(
        all(spec.contains(v, prereleases=True) for spec in specs.values())
        for v in candidates
    ):
        return None
    return "no version satisfies " + "; ".join(f"{p} {s}" for p, s in specs.items())


def installed(
    registry: dict[str, Any],
) -> tuple[dict[str, tuple[str, dict[str, str]]], list[str]]:
    """Python and package versions of each checkout's .venv, plus notes on skips.

    The environment is the .venv next to the project's first manifest.
    """
    found: dict[str, tuple[str, dict[str, str]]] = {}
    notes: list[str] = []
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
        try:
            listed = subprocess.run(
                ["uv", "pip", "list", "--format", "json", "--python", str(python)],
                capture_output=True,
                text=True,
                check=True,
            )
            version = subprocess.run(
                [str(python), "-V"], capture_output=True, text=True, check=True
            )
            packages = json.loads(listed.stdout)
        except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as e:
            notes.append(f"{p['name']}: cannot list {python}: {e}")
            continue
        found[p["name"]] = (
            version.stdout.split()[-1],
            {canonicalize_name(x["name"]): x["version"] for x in packages},
        )
    return found, notes


def report_deps(registry: dict[str, Any], with_installed: bool) -> int:
    """Print third-party ranges shared by projects; 1 when some cannot agree."""
    specs, notes = declared(registry)
    shared = {name: s for name, s in sorted(specs.items()) if len(s) > 1}
    conflicts = {name: why for name, s in shared.items() if (why := range_conflicts(s))}
    print(
        f"Declared third-party ranges: {len(specs)} packages, "
        f"{len(shared)} declared by two or more projects"
    )
    print()
    for name, per_project in shared.items():
        flag = f"  CONFLICT: {conflicts[name]}" if name in conflicts else ""
        ranges = "; ".join(f"{p} {s or '*'}" for p, s in per_project.items())
        print(f"  {name}: {ranges}{flag}")
    if with_installed:
        envs, env_notes = installed(registry)
        notes += env_notes
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
    """Newest `v*` release tag of a checkout, or None without tags or git.

    Tags are ordered as versions; a pre-release tag is the latest only when
    the checkout has no final release tag.
    """
    try:
        done = subprocess.run(
            ["git", "-C", str(checkout), "tag", "--list", "v*"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    versions: list[tuple[bool, Version, str]] = []
    for tag in done.stdout.split():
        try:
            version = Version(tag.removeprefix("v"))
        except InvalidVersion:
            continue
        versions.append((not version.is_prerelease, version, tag))
    return max(versions)[2] if versions else None


def _matches(req: Requirement, producer: dict[str, Any]) -> bool:
    """Whether a requirement names the producer.

    A match is the import name, the PyPI name, `nogat-<project>` or the
    producer's repository URL.
    """
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
    """Classify a requirement as (kind, value): tag, commit, branch, range, path, none.

    For a VCS URL the ref is what follows the last `@` of the URL path, so
    refs containing `/` (`release/0.8`) are kept whole.
    """
    if req.url:
        if req.url.startswith("file:") or "://" not in req.url:
            return "path", req.url
        path = urlsplit(req.url.removeprefix("git+")).path
        ref = path.rpartition("@")[2] if "@" in path else ""
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
    """Compare a pin of `kind` and `value` with the producer's latest tag."""
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
    """Print each active runtime or optional dependency: pin against latest tag."""
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
            manifests = consumer.get("python_manifests") or []
            if not manifests:
                rows.append((*who, "—", latest or "—", "no manifest"))
                continue
            found = False
            for manifest in manifests:
                path = checkout / manifest
                if not path.is_file():
                    continue
                try:
                    lines = _requirement_lines(path)
                except RegistryError as e:
                    rows.append((*who, "—", latest or "—", f"unreadable: {e}"))
                    found = True
                    continue
                for line in lines:
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


def check_standard(registry: dict[str, Any], write: bool) -> int:
    """Run the checks of scripts/standard.py; print problems, return 1 if any."""
    path = STANDARDS / "ERROR_REGISTRY.md"
    blocks = standard.error_tables(_read_json(STANDARDS / "error_registry.json"))
    if write:
        text = _read(path)
        fresh = standard.regenerate(text, blocks)
        if fresh != text:
            path.write_text(fresh, encoding="utf-8")
            print(f"wrote {_shown(path)}")
    problems = [
        *standard.id_problems(ROOT),
        *standard.link_problems(ROOT),
        *standard.budget_problems(ROOT),
        *standard.generated_problems(path, blocks, _shown(path)),
        *standard.project_list_problems(ROOT, registry),
    ]
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        return 1
    print("standard: IDs, links, budgets, generated blocks and project lists agree")
    return 0


def main() -> int:
    """Run the command named on the command line; return the exit status."""
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
    standard_cmd = sub.add_parser(
        "standard", help="check the standard's IDs, links, budgets and copies"
    )
    standard_cmd.add_argument(
        "--write", action="store_true", help="regenerate generated blocks first"
    )
    args = parser.parse_args()

    try:
        registry = load()
        problems = validate(registry)
    except RegistryError as e:
        print(f"ecosystem: {e}", file=sys.stderr)
        return 1
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
    if args.command == "standard":
        return check_standard(registry, args.write)

    text = render(registry)
    if args.check:
        if not MAP.exists() or MAP.read_text(encoding="utf-8") != text:
            print(
                f"{MAP.relative_to(ROOT)} is stale; "
                "run: uv run scripts/ecosystem.py map",
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
