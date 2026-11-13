"""Validate ecosystem.yaml, generate the map and AGENTS.md, compare dependencies.

Usage:
    uv run scripts/ecosystem.py validate
    uv run scripts/ecosystem.py map            # write docs/ECOSYSTEM_MAP.md
    uv run scripts/ecosystem.py map --check    # exit 4 when the map is stale
    uv run scripts/ecosystem.py agents         # write AGENTS.md (HUB-4.3)
    uv run scripts/ecosystem.py agents --check # exit 4 when AGENTS.md is stale
    uv run scripts/ecosystem.py deps           # third-party ranges across checkouts
    uv run scripts/ecosystem.py deps --installed   # also versions in each .venv
    uv run scripts/ecosystem.py drift          # pins against tags; copies of Nogat
    uv run scripts/ecosystem.py standard       # IDs, links, budgets, copies
    uv run scripts/ecosystem.py standard --write   # regenerate blocks, then check
    uv run scripts/ecosystem.py set check      # consumers' pins against the release set
    uv run scripts/ecosystem.py set apply --project P [--path DIR]  # pin P to the set
    uv run scripts/ecosystem.py set bump P [--rev REF]  # move P in the set
    uv run scripts/ecosystem.py set readme [--check]    # the set's README.md

Checkouts are resolved as siblings of Nogat or under NOGAT_WORKSPACE (HUB §3).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tomllib
from collections.abc import Callable, Sequence
from pathlib import Path, PurePosixPath
from typing import Any, NoReturn
from urllib.parse import urlsplit

import guide
import jsonschema
import standard
import terms
import yaml
from packaging.requirements import InvalidRequirement, Requirement
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name
from packaging.version import InvalidVersion, Version

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "ecosystem.yaml"
SCHEMA = ROOT / "schemas" / "ecosystem.schema.json"
ERROR_SCHEMA = ROOT / "schemas" / "agent" / "error-1.schema.json"
MAP = ROOT / "docs" / "ECOSYSTEM_MAP.md"
AGENTS = ROOT / "AGENTS.md"
RELEASE_SETS = ROOT / "release-sets"
CANDIDATE = re.compile(r"^candidate-(\d+)$")
FULL_COMMIT = re.compile(r"^[0-9a-f]{40}$")

LOCAL_PATH = re.compile(r"(^|\s)(/home/|/Users/|~/|[A-Za-z]:\\)")
COMMIT = re.compile(r"^[0-9a-f]{7,40}$")
STANDARDS = ROOT / "standards"
README_VERSION = re.compile(r"^Standard (\d+\.\d+)\b", re.MULTILINE)
TOPIC_VERSION = re.compile(r"^Part of standard (\S+)", re.MULTILINE)
VERSIONLESS = {"README.md", "DECISIONS.md"}
INCLUDE = re.compile(r"^(-r|--requirement)(\s+|=)(?P<path>\S+)")
OPTION = re.compile(r"\s+--?[A-Za-z]")
# What projects copy of Nogat (DEV-15.6): files, and directories filtered by
# `nogat_sources`.
COPIED_PATHS = (
    "schemas/agent",
    "schemas/exchange",
    "standards/error_registry.json",
    "design/tokens.css",
    "design/marks",
    "design/kit",
)
COPY_HEADER = re.compile(rb"\A/\*.*?\*/(\r?\n)?", re.DOTALL)


class Failure(Exception):
    """An outcome reported as a registry error (ERR §2, ECO-044)."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        hint: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.hint = hint
        self.details = details or {}


class RegistryError(Failure):
    """A file the tooling reads is missing or malformed; the message names it."""

    def __init__(self, message: str, code: str = "data_error") -> None:
        super().__init__(code, message)


def _os_code(error: OSError) -> str:
    return "not_found" if isinstance(error, FileNotFoundError) else "io_error"


def _shown(path: Path) -> str:
    """Path for messages, relative to Nogat (siblings appear as `../<Project>`)."""
    return os.path.relpath(path, ROOT)


def _read(path: Path) -> str:
    """Text of a UTF-8 file; RegistryError names the file when it cannot be read."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as e:
        raise RegistryError(f"{_shown(path)}: cannot read: {e}", _os_code(e)) from e
    except UnicodeDecodeError as e:
        raise RegistryError(f"{_shown(path)}: not UTF-8: {e}") from e


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
        raise RegistryError(
            f"{REGISTRY.name}: cannot read: {e.strerror}", _os_code(e)
        ) from e
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
    DECISIONS.md is a versionless log.
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

    problems.extend(guide.route_problems(registry))

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


def checkout(project: dict[str, Any]) -> Path:
    """Return a project's checkout: the workspace directory named like its repository.

    The directory is the last segment of `repo` (HUB-3.1), which may differ
    from the registry `name` while the repository keeps an older name.
    """
    repo: str = project["repo"]
    path = urlsplit(repo).path.strip("/").removesuffix(".git")
    return workspace() / (path.rpartition("/")[2] or project["name"])


def _names_repo(req: Requirement, sources: list[dict[str, Any]], repo: str) -> bool:
    """Whether the requirement's URL or one of its uv sources is the repository."""
    urls = [req.url or "", *(str(s.get("git") or s.get("url") or "") for s in sources)]
    return any(repo.lower() in url.lower() for url in urls)


def _toml(path: Path, read: Callable[[Path], str] = _read) -> dict[str, Any]:
    """Parse a TOML file; RegistryError names the file when it is not valid TOML."""
    try:
        return tomllib.loads(read(path))
    except tomllib.TOMLDecodeError as e:
        raise RegistryError(f"{_shown(path)}: not valid TOML: {e}") from e


def _uv_sources(
    path: Path, read: Callable[[Path], str] = _read
) -> dict[str, list[dict[str, Any]]]:
    """`[tool.uv.sources]` of a pyproject.toml by package name; {} for other files.

    uv installs a dependency named there from its source, whatever the
    requirement says; a name may list several sources chosen by markers.
    Raises RegistryError when the file cannot be read or parsed.
    """
    if path.suffix != ".toml":
        return {}
    sources = _toml(path, read).get("tool", {}).get("uv", {}).get("sources") or {}
    return {
        canonicalize_name(name): entry if isinstance(entry, list) else [entry]
        for name, entry in sources.items()
    }


def _requirement_lines(
    path: Path,
    seen: frozenset[Path] = frozenset(),
    read: Callable[[Path], str] = _read,
) -> list[str]:
    r"""Return the requirement strings of a pyproject.toml or requirements file.

    pyproject.toml contributes dependencies, extras and dependency groups. A
    requirements file is read as pip reads it: `\` continues a line, options
    after a requirement (`--hash=…`) and comments are dropped, `-r` includes
    are followed and other option lines (`-e`, `-c`, `--index-url`) skipped.
    `read` returns a file's text (the disk by default, a git ref in `set check`).
    Raises RegistryError when a file cannot be read or parsed.
    """
    if path.suffix == ".toml":
        data = _toml(path, read)
        project = data.get("project", {})
        lines = list(project.get("dependencies") or [])
        for extra in (project.get("optional-dependencies") or {}).values():
            lines += extra
        for group in (data.get("dependency-groups") or {}).values():
            lines += [item for item in group if isinstance(item, str)]
        return lines
    text = read(path)
    lines = []
    seen = seen | {Path(os.path.normpath(path))}
    for raw in text.replace("\\\n", " ").splitlines():
        line = raw.split(" #")[0].strip()
        if not line or line.startswith("#"):
            continue
        include = INCLUDE.match(line)
        if include:
            target = Path(os.path.normpath(path.parent / include["path"]))
            if target not in seen:
                lines += _requirement_lines(target, seen, read)
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
        checkout_dir = checkout(p)
        if manifests and not checkout_dir.is_dir():
            notes.append(f"{p['name']}: no checkout at {checkout_dir}")
            continue
        for manifest in manifests:
            path = checkout_dir / manifest
            if not path.is_file():
                notes.append(f"{p['name']}: {manifest} missing")
                continue
            try:
                lines = _requirement_lines(path)
                sources = _uv_sources(path)
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
                if (
                    name in ecosystem
                    or req.url
                    or any(
                        _names_repo(req, sources.get(name, []), q["repo"])
                        for q in registry["projects"]
                    )
                ):
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
        base = (checkout(p) / manifests[0]).parent
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
    """Print third-party ranges shared by projects; Failure when some cannot agree."""
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
    if conflicts:
        raise Failure(
            "conflict",
            f"{len(conflicts)} package(s) have ranges no single version satisfies",
            hint="align the ranges before preparing a release set (REL-6.4)",
            details={"reason": "range_conflict", "packages": sorted(conflicts)},
        )
    return 0


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


def _matches(
    req: Requirement, sources: list[dict[str, Any]], producer: dict[str, Any]
) -> bool:
    """Whether a requirement names the producer.

    A match is the import name, the PyPI name, `nogat-<project>` or the
    producer's repository URL in the requirement or in its uv `sources`.
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
    return _names_repo(req, sources, producer["repo"])


def _pin(req: Requirement) -> tuple[str, str]:
    """Classify a requirement as (kind, value): tag, commit, branch, range, path, none.

    For a VCS URL the ref is what follows the last `@` of the URL path, so
    refs containing `/` (`release/0.8`) are kept whole; a commit is kept as
    written.
    """
    if req.url:
        if req.url.startswith("file:") or "://" not in req.url:
            return "path", req.url
        path = urlsplit(req.url.removeprefix("git+")).path
        ref = path.rpartition("@")[2] if "@" in path else ""
        if not ref:
            return "none", ""
        if COMMIT.match(ref):
            return "commit", ref
        if re.match(r"^v?\d", ref):
            return "tag", ref
        return "branch", ref
    if req.specifier:
        return "range", str(req.specifier)
    return "none", ""


def _source_pin(source: dict[str, Any]) -> tuple[str, str] | None:
    """Classify a `[tool.uv.sources]` entry as `_pin` does a requirement.

    None for a source that keeps the requirement's own pin (`index`,
    `workspace`).
    """
    if "git" in source:
        if "tag" in source:
            return "tag", source["tag"]
        if "branch" in source:
            return "branch", source["branch"]
        if "rev" not in source:
            return "none", ""
        return _pin(Requirement(f"source @ git+{source['git']}@{source['rev']}"))
    if "path" in source:
        return "path", source["path"]
    if "url" in source:
        return _pin(Requirement(f"source @ {source['url']}"))
    return None


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


def _declared_pins(
    lines: list[str], sources: dict[str, list[dict[str, Any]]], producer: dict[str, Any]
) -> list[tuple[str, str, str]]:
    """Pins of the producer among a manifest's requirements: (kind, value, form).

    A requirement with `[tool.uv.sources]` entries is pinned by them (form
    `tool.uv.sources`), otherwise by itself (form ""). [] when no requirement
    names the producer.
    """
    pins: list[tuple[str, str, str]] = []
    for line in lines:
        try:
            req = Requirement(line)
        except InvalidRequirement:
            continue
        entries = sources.get(canonicalize_name(req.name), [])
        if not _matches(req, entries, producer):
            continue
        own = [p for e in entries if (p := _source_pin(e)) is not None]
        if own:
            pins += [(kind, value, "tool.uv.sources") for kind, value in own]
        else:
            pins.append((*_pin(req), ""))
    return pins


def nogat_sources(root: Path) -> list[str]:
    """Nogat's files that projects copy, tracked at HEAD of `root` (DEV-15.6).

    Agent and exchange schemas, the error registry, the tokens, the marks
    and every file of the kit; paths relative to `root`, sorted.
    """
    listed = _git(
        root, "ls-tree", "-r", "-z", "--name-only", "HEAD", "--", *COPIED_PATHS
    )
    sources = []
    for path in listed.split("\0"):
        parent, suffix = (
            PurePosixPath(path).parent.as_posix(),
            PurePosixPath(path).suffix,
        )
        if (
            path in COPIED_PATHS
            or path.startswith("design/kit/")
            or (parent in ("schemas/agent", "schemas/exchange") and suffix == ".json")
            or (parent == "design/marks" and suffix == ".svg")
        ):
            sources.append(path)
    return sorted(sources)


def _blob_hashes(root: Path, names: list[str]) -> dict[str, str]:
    """SHA-256 of each `commit:path` blob of `root`; names git lacks are left out.

    One `git cat-file --batch` reads every blob; a blob met again under
    another name is not hashed twice.
    """
    out = _git_bytes(
        root, "cat-file", "--batch", stdin="".join(f"{n}\n" for n in names).encode()
    )
    by_blob: dict[str, str] = {}
    hashes: dict[str, str] = {}
    at = 0
    for name in names:
        end = out.index(b"\n", at)
        header = out[at:end].decode("utf-8").split()
        at = end + 1
        if len(header) != 3:  # `<name> missing`: the path is absent at that commit
            continue
        blob, kind, size = header[0], header[1], int(header[2])
        if kind == "blob":
            if blob not in by_blob:
                by_blob[blob] = hashlib.sha256(out[at : at + size]).hexdigest()
            hashes[name] = by_blob[blob]
        at += size + 1
    return hashes


def source_versions(root: Path, sources: list[str]) -> dict[str, dict[str, str]]:
    """Per source, the newest commit on HEAD's history holding each SHA-256."""
    history = {
        s: _git(root, "log", "--format=%H", "HEAD", "--", s).split() for s in sources
    }
    names = [f"{c}:{s}" for s in sources for c in history[s]]
    hashes = _blob_hashes(root, names)
    versions: dict[str, dict[str, str]] = {}
    for source in sources:
        found = versions.setdefault(source, {})
        for commit in history[source]:  # newest first: the first commit wins
            digest = hashes.get(f"{commit}:{source}")
            if digest is not None:
                found.setdefault(digest, commit)
    return versions


def without_copy_header(data: bytes) -> bytes:
    """Drop a leading `/* ... */` that names Nogat as the origin (DEV-15.3)."""
    match = COPY_HEADER.match(data)
    if match and b"Copied from Nogat" in match[0]:
        return data[match.end() :]
    return data


def _sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def copy_rows(registry: dict[str, Any], root: Path) -> list[tuple[str, ...]]:
    """(project, copy, source, state) of each project's copy of a Nogat file (D9).

    A copy is a file tracked in the project's checkout named like a source;
    its working-tree bytes, without a leading `Copied from Nogat` comment,
    are `current` when they equal Nogat's working tree, `behind <commit>`
    when they equal an older version on Nogat's HEAD, else `modified`.
    """
    sources = nogat_sources(root)
    versions = source_versions(root, sources)
    current = {s: _sha256(root / s) for s in sources}
    by_name: dict[str, list[str]] = {}
    for source in sources:
        by_name.setdefault(PurePosixPath(source).name, []).append(source)
    rows: list[tuple[str, ...]] = []
    for project in registry["projects"]:
        if "hub" in project["profiles"]:
            continue
        directory = checkout(project)
        if not (directory / ".git").exists():
            rows.append((project["name"], "—", "—", "no checkout"))
            continue
        tracked = _git(directory, "ls-files", "-z").split("\0")
        for path in sorted(p for p in tracked if PurePosixPath(p).name in by_name):
            try:
                data = without_copy_header((directory / path).read_bytes())
            except OSError:
                continue  # tracked but deleted or unreadable in the working tree
            digest = hashlib.sha256(data).hexdigest()
            for source in by_name[PurePosixPath(path).name]:
                if digest == current[source]:
                    state = "current"
                elif digest in versions[source]:
                    state = f"behind {versions[source][digest][:7]}"
                else:
                    state = "modified"
                rows.append((project["name"], path, source, state))
    return rows


def report_drift(registry: dict[str, Any]) -> int:
    """Print each active runtime or optional dependency's pin against latest tag.

    A second table states each project's copies of Nogat's files (D9).
    """
    by_name = {p["name"]: p for p in registry["projects"]}
    rows: list[tuple[str, str, str, str, str]] = []
    for consumer in registry["projects"]:
        consumer_dir = checkout(consumer)
        for dep in consumer["depends_on"]:
            if dep["status"] != "active" or dep["kind"] not in ("runtime", "optional"):
                continue
            producer = by_name[dep["project"]]
            who = (consumer["name"], producer["name"])
            producer_checkout = checkout(producer)
            latest = (
                _latest_tag(producer_checkout) if producer_checkout.is_dir() else None
            )
            if not consumer_dir.is_dir():
                rows.append((*who, "—", latest or "—", "no checkout"))
                continue
            manifests = consumer.get("python_manifests") or []
            if not manifests:
                rows.append((*who, "—", latest or "—", "no manifest"))
                continue
            found = False
            for manifest in manifests:
                path = consumer_dir / manifest
                if not path.is_file():
                    continue
                try:
                    lines = _requirement_lines(path)
                    sources = _uv_sources(path)
                except RegistryError as e:
                    rows.append((*who, "—", latest or "—", f"unreadable: {e}"))
                    found = True
                    continue
                pins = _declared_pins(lines, sources, producer)
                found = found or bool(pins)
                for kind, value, form in pins:
                    where = f"{manifest}, {form}" if form else manifest
                    shown = value[:7] if kind == "commit" else value
                    pin = f"{kind} {shown} ({where})" if value else f"{kind} ({where})"
                    state = (
                        "no tags"
                        if kind in ("tag", "range") and latest is None
                        else _state(kind, value, latest)
                    )
                    rows.append((*who, pin, latest or "—", state))
            if not found:
                rows.append((*who, "—", latest or "—", "not declared"))
    _table(("consumer", "producer", "pin", "latest tag", "state"), rows)
    print()
    _table(("project", "copy", "source", "state"), copy_rows(registry, ROOT))
    return 0


def _table(header: tuple[str, ...], rows: Sequence[tuple[str, ...]]) -> None:
    """Print rows as columns padded to their widest cell."""
    widths = [max(len(r[i]) for r in [header, *rows]) for i in range(len(header))]
    for row in [header, *rows]:
        print("  ".join(c.ljust(w) for c, w in zip(row, widths, strict=True)).rstrip())


def candidate() -> Path:
    """Directory of the current candidate: `candidate-<N>` with the highest N."""
    numbered = [
        (int(m[1]), path)
        for path in (RELEASE_SETS.iterdir() if RELEASE_SETS.is_dir() else [])
        if path.is_dir() and (m := CANDIDATE.match(path.name))
    ]
    if not numbered:
        raise Failure(
            "not_found",
            f"{_shown(RELEASE_SETS)}: no candidate-<N> directory (REL-6.4)",
            hint="create release-sets/candidate-1/, then run: "
            "uv run scripts/ecosystem.py set bump <Project>",
            details={"reason": "no_candidate"},
        )
    return max(numbered)[1]


def members(registry: dict[str, Any], directory: Path) -> dict[str, str]:
    """Commit of each member in the candidate's members.toml, in registry order.

    Raises RegistryError when the file is missing, names a project the
    registry lacks or gives anything but `commit = "<40 hex>"`.
    """
    path = directory / "members.toml"
    data = _toml(path)
    order = [p["name"] for p in registry["projects"]]
    problems = []
    for name, table in data.items():
        if name not in order:
            problems.append(f"{name}: not a project of ecosystem.yaml")
        elif (
            not isinstance(table, dict)
            or set(table) != {"commit"}
            or not FULL_COMMIT.match(str(table["commit"]))
        ):
            problems.append(f'{name}: needs exactly commit = "<40 hex>"')
    if problems:
        raise RegistryError(f"{_shown(path)}: " + "; ".join(problems))
    return {name: data[name]["commit"] for name in order if name in data}


def render_members(directory: Path, commits: dict[str, str]) -> str:
    """Text of a candidate's members.toml."""
    out = [
        f"# Release set {directory.name} (REL-6.4): the commit of each member.",
        "# Moved by `uv run scripts/ecosystem.py set bump <Project>`; README.md is",
        "# generated from this file (`set readme`).",
    ]
    for name, commit in commits.items():
        out += ["", f"[{name}]", f'commit = "{commit}"']
    return "\n".join(out) + "\n"


def render_set_readme(
    registry: dict[str, Any], directory: Path, commits: dict[str, str]
) -> str:
    """Text of a candidate's README.md, generated from members.toml."""
    repos = {p["name"]: p["repo"] for p in registry["projects"]}
    out = [
        f"# Release set {directory.name}",
        "",
        "<!-- Generated from members.toml by "
        "`uv run scripts/ecosystem.py set readme`; do not edit. -->",
        "",
        "A candidate, not yet released (REL-6.4): every consumer pins each member",
        "at the commit below. `uv run scripts/ecosystem.py set check` compares the",
        "consumers' pins with it, `set apply --project <P>` writes them into a",
        "consumer and `set bump <P>` moves a member.",
        "",
        "| Member | Commit |",
        "|---|---|",
    ]
    for name, commit in commits.items():
        out.append(f"| {name} | [`{commit}`]({repos[name]}/commit/{commit}) |")
    return "\n".join(out) + "\n"


def integration_ref(project: dict[str, Any]) -> str:
    """Remote branch holding a project's code: registry `branch`, else develop."""
    return f"origin/{project.get('branch') or 'develop'}"


def _git_bytes(
    directory: Path, *args: str, code: str = "not_found", stdin: bytes | None = None
) -> bytes:
    """Stdout of `git -C directory args` fed `stdin`; Failure `code` names a failure."""
    try:
        done = subprocess.run(
            ["git", "-C", str(directory), *args],
            input=stdin,
            capture_output=True,
            check=False,
        )
    except OSError as e:
        raise Failure("missing_dependency", f"git: {e.strerror}") from e
    if done.returncode:
        stderr = done.stderr.decode("utf-8", "replace")
        why = stderr.strip().splitlines()[-1:] or [f"exit {done.returncode}"]
        raise Failure(
            code,
            f"{_shown(directory)}: git {' '.join(args)}: {why[0]}",
            details={"reason": "git_failed"},
        )
    return done.stdout


def _git(directory: Path, *args: str, code: str = "not_found") -> str:
    """Stdout of `git -C directory args` as text; Failure `code` names a failure."""
    return _git_bytes(directory, *args, code=code).decode("utf-8")


def _reader_at(directory: Path, ref: str) -> Callable[[Path], str]:
    """Return a `read` for the manifest readers: files of `directory` at `ref`."""

    def read(path: Path) -> str:
        try:
            relative = path.relative_to(directory).as_posix()
        except ValueError as e:
            raise RegistryError(f"{path}: outside {_shown(directory)}") from e
        return _git(directory, "show", f"{ref}:{relative}")

    return read


def _set_state(kind: str, value: str, commit: str | None) -> str:
    """Compare a consumer's pin with the set's commit of its producer."""
    if commit is None:
        return "not in set"
    if kind != "commit":
        return "not a commit pin"
    return "ok" if commit.startswith(value.lower()) else "differs"


def check_set(registry: dict[str, Any], directory: Path) -> int:
    """Print every consumer's pin of a producer against the set (D2).

    Manifests are read at each consumer's integration ref after `git fetch`.
    A consumer is compared with every member and with the producers of its
    active runtime and optional dependencies; such a dependency that the
    manifests do not declare is listed as `not declared`. Failure `conflict`
    when a pin differs from the set, is no commit or names a producer outside
    it; `not_found` when a consumer cannot be read.
    """
    commits = members(registry, directory)
    print(
        f"{_shown(directory)}: "
        + ", ".join(f"{name} {commit[:7]}" for name, commit in commits.items())
    )
    rows: list[tuple[str, str, str, str, str, str]] = []
    for consumer in registry["projects"]:
        manifests = consumer.get("python_manifests") or []
        if not manifests:
            continue
        name = consumer["name"]
        edges = {
            dep["project"]
            for dep in consumer["depends_on"]
            if dep["status"] == "active" and dep["kind"] in ("runtime", "optional")
        }
        repo = checkout(consumer)
        ref = integration_ref(consumer)
        try:
            if not repo.is_dir():
                raise Failure("not_found", f"no checkout at {_shown(repo)}")
            _git(repo, "fetch", "--quiet", "origin", code="source_unavailable")
            read = _reader_at(repo, ref)
            parsed = [
                (
                    m,
                    _requirement_lines(repo / m, read=read),
                    _uv_sources(repo / m, read),
                )
                for m in manifests
            ]
        except Failure as e:
            rows.append((name, "—", ref, "—", "—", f"unreadable: {e.message}"))
            continue
        for producer in registry["projects"]:
            if producer["name"] == name or not (
                producer["name"] in edges or producer["name"] in commits
            ):
                continue
            commit = commits.get(producer["name"])
            who = (name, producer["name"])
            found = False
            for manifest, lines, sources in parsed:
                for kind, value, form in _declared_pins(lines, sources, producer):
                    found = True
                    where = f"{ref}:{manifest}" + (f", {form}" if form else "")
                    pinned = value[:7] if kind == "commit" else f"{kind} {value}"
                    state = _set_state(kind, value, commit)
                    rows.append((*who, where, (commit or "—")[:7], pinned, state))
            if not found and producer["name"] in edges:
                rows.append((*who, ref, (commit or "—")[:7], "—", "not declared"))
    _table(("consumer", "producer", "manifest", "set", "pinned", "state"), rows)
    unreadable = sorted({r[0] for r in rows if r[5].startswith("unreadable")})
    wrong = sorted(
        {r[0] for r in rows if r[5] not in ("ok", "not declared")} - set(unreadable)
    )
    if wrong:
        raise Failure(
            "conflict",
            f"pins differ from {_shown(directory)} in {', '.join(wrong)}",
            hint="run: uv run scripts/ecosystem.py set apply --project <Consumer>, "
            "then uv lock and the consumer's gate",
            details={"reason": "pin_mismatch", "consumers": wrong},
        )
    if unreadable:
        raise Failure(
            "not_found",
            "cannot read the manifests of " + ", ".join(unreadable),
            hint="clone the missing checkouts (HUB §3) or fetch their branches",
            details={"reason": "unreadable_consumer", "consumers": unreadable},
        )
    return 0


def _with_ref(line: str, url: str, commit: str) -> str:
    """Point the VCS URL of a requirement line at `commit`; change nothing else."""
    base, mark, fragment = url.partition("#")
    if "@" in urlsplit(base.removeprefix("git+")).path:
        base = base[: base.rindex("@")]
    return line.replace(url, f"{base}@{commit}{mark}{fragment}", 1)


def _pinned_text(
    path: Path, text: str, producers: list[dict[str, Any]], commits: dict[str, str]
) -> str:
    """Return a manifest's text with each pin of a set member at its commit (D3).

    A `[tool.uv.sources]` entry has its `rev` replaced; a requirement without
    one has the ref of its `git+` URL replaced or added. Tag and branch
    sources, ranges and paths are left for the author.
    """
    sources = _uv_sources(path)
    for line in _requirement_lines(path):
        try:
            req = Requirement(line)
        except InvalidRequirement:
            continue
        entries = sources.get(canonicalize_name(req.name), [])
        producer = next((p for p in producers if _matches(req, entries, p)), None)
        if producer is None:
            continue
        commit = commits[producer["name"]]
        if entries:
            for entry in entries:
                rev = entry.get("rev")
                if "git" in entry and isinstance(rev, str):
                    text = re.sub(
                        rf"(\brev\s*=\s*)([\"']){re.escape(rev)}\2",
                        rf"\g<1>\g<2>{commit}\g<2>",
                        text,
                    )
        elif req.url and req.url.startswith("git+"):
            text = text.replace(line, _with_ref(line, req.url, commit))
    return text


def apply_set(
    registry: dict[str, Any], commits: dict[str, str], name: str, directory: Path
) -> list[Path]:
    """Rewrite a consumer's pins of the set's members in place; changed files."""
    project = _project(registry, name)
    manifests = project.get("python_manifests") or []
    if not manifests:
        raise Failure(
            "not_found",
            f"{name} has no python_manifests in ecosystem.yaml",
            details={"reason": "no_manifest"},
        )
    producers = [
        p for p in registry["projects"] if p["name"] in commits and p["name"] != name
    ]
    changed = []
    for manifest in manifests:
        path = directory / manifest
        text = _read(path)
        pinned = _pinned_text(path, text, producers, commits)
        if pinned != text:
            path.write_text(pinned, encoding="utf-8")
            changed.append(path)
    return changed


def _project(registry: dict[str, Any], name: str) -> dict[str, Any]:
    """Return the registry entry named `name`; `validation_error` when none is."""
    for project in registry["projects"]:
        if project["name"] == name:
            found: dict[str, Any] = project
            return found
    raise Failure(
        "validation_error",
        f"unknown project {name!r}",
        hint="use a project name from ecosystem.yaml",
        details={"reason": "unknown_project"},
    )


def bump(registry: dict[str, Any], directory: Path, name: str, rev: str | None) -> int:
    """Set a member's commit to `rev` resolved in its checkout, then the README (D4).

    The checkout is fetched first; `rev` defaults to the project's
    integration ref. members.toml is created when the candidate has none.
    """
    project = _project(registry, name)
    repo = checkout(project)
    if not repo.is_dir():
        raise Failure(
            "not_found",
            f"{name}: no checkout at {_shown(repo)}",
            details={"reason": "no_checkout"},
        )
    _git(repo, "fetch", "--quiet", "origin", code="source_unavailable")
    ref = rev or integration_ref(project)
    commit = _git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}").strip()
    path = directory / "members.toml"
    commits = members(registry, directory) if path.exists() else {}
    old = commits.get(name)
    commits[name] = commit
    commits = {
        p["name"]: commits[p["name"]]
        for p in registry["projects"]
        if p["name"] in commits
    }
    path.write_text(render_members(directory, commits), encoding="utf-8")
    print(f"{name}: {old[:7] if old else '—'} -> {commit} ({ref})")
    readme = render_set_readme(registry, directory, commits)
    return _generated(directory / "README.md", readme, False, "set readme")


def check_standard(registry: dict[str, Any], write: bool) -> int:
    """Run the checks of scripts/standard.py; Failure when any finds a problem.

    Generated outputs: the error tables of ERROR_REGISTRY.md and
    schemas/agent/error-1.schema.json, both from error_registry.json, and
    the kit's terms page design/kit/nogat-terms.html from nogat-terms.md.
    """
    path = STANDARDS / "ERROR_REGISTRY.md"
    errors = _read_json(STANDARDS / "error_registry.json")
    blocks = standard.error_tables(errors)
    schema = standard.error_schema(errors)
    page = terms.build(_read(terms.SOURCE))
    if write:
        text = _read(path)
        fresh = standard.regenerate(text, blocks)
        if fresh != text:
            path.write_text(fresh, encoding="utf-8")
            print(f"wrote {_shown(path)}")
        for target, content in ((ERROR_SCHEMA, schema), (terms.PAGE, page)):
            if not target.is_file() or _read(target) != content:
                target.write_text(content, encoding="utf-8")
                print(f"wrote {_shown(target)}")
    stale = [
        *standard.generated_problems(path, blocks, _shown(path)),
        *standard.file_problems(ERROR_SCHEMA, schema, _shown(ERROR_SCHEMA)),
        *standard.file_problems(terms.PAGE, page, _shown(terms.PAGE)),
    ]
    problems = [
        *standard.id_problems(ROOT),
        *standard.link_problems(ROOT),
        *standard.budget_problems(ROOT),
        *standard.project_list_problems(ROOT, registry),
        *standard.marker_problems(ROOT, registry),
    ]
    for problem in [*problems, *stale]:
        print(problem, file=sys.stderr)
    if problems:
        raise Failure(
            "data_error",
            f"the standard has {len(problems + stale)} problem(s)",
            hint="fix the lines listed above",
            details={"reason": "standard_inconsistent", "count": len(problems)},
        )
    if stale:
        raise Failure(
            "conflict",
            "generated outputs of the standard are stale",
            hint="run: uv run scripts/ecosystem.py standard --write",
            details={"reason": "stale_generated_file", "count": len(stale)},
        )
    print("standard: IDs, links, budgets, generated outputs and project lists agree")
    return 0


def _generated(path: Path, text: str, check: bool, command: str) -> int:
    """Write a generated file, or with `check` fail when it is stale (HUB-4.5)."""
    shown = _shown(path)
    if not check:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {shown}")
        return 0
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        raise Failure(
            "conflict",
            f"{shown} is stale",
            hint=f"run: uv run scripts/ecosystem.py {command}",
            details={"reason": "stale_generated_file", "path": shown},
        )
    print(f"{shown} is up to date")
    return 0


def check_map(registry: dict[str, Any], check: bool) -> int:
    """Write docs/ECOSYSTEM_MAP.md, or with `check` fail when it is stale."""
    return _generated(MAP, render(registry), check, "map")


def check_agents(registry: dict[str, Any], check: bool) -> int:
    """Write AGENTS.md (HUB-4.3), or with `check` fail when it is stale."""
    return _generated(AGENTS, guide.render(registry), check, "agents")


class _Parser(argparse.ArgumentParser):
    """Argument parser that reports usage errors as `validation_error`."""

    def error(self, message: str) -> NoReturn:
        raise Failure(
            "validation_error",
            message,
            hint=f"run: uv run scripts/{self.prog} --help",
        )


def _parser() -> argparse.ArgumentParser:
    parser = _Parser(prog="ecosystem.py", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="validate ecosystem.yaml")
    map_cmd = sub.add_parser("map", help="generate docs/ECOSYSTEM_MAP.md")
    map_cmd.add_argument(
        "--check", action="store_true", help="fail when the map is stale"
    )
    agents_cmd = sub.add_parser("agents", help="generate AGENTS.md, the routing table")
    agents_cmd.add_argument(
        "--check", action="store_true", help="fail when AGENTS.md is stale"
    )
    deps_cmd = sub.add_parser(
        "deps", help="compare third-party dependencies across checkouts"
    )
    deps_cmd.add_argument(
        "--installed", action="store_true", help="also compare each checkout's .venv"
    )
    sub.add_parser(
        "drift",
        help="compare consumers' pins with producers' latest tags, and copies of "
        "Nogat's files with Nogat",
    )
    standard_cmd = sub.add_parser(
        "standard", help="check the standard's IDs, links, budgets and copies"
    )
    standard_cmd.add_argument(
        "--write", action="store_true", help="regenerate generated blocks first"
    )
    set_cmd = sub.add_parser(
        "set", help="the release set candidate: pins of every consumer (REL-6.4)"
    )
    set_sub = set_cmd.add_subparsers(dest="set_command", required=True)
    set_sub.add_parser(
        "check", help="compare consumers' pins at their integration refs with the set"
    )
    apply_cmd = set_sub.add_parser(
        "apply", help="rewrite a consumer's pins to the set's commits"
    )
    apply_cmd.add_argument("--project", required=True, help="consumer to rewrite")
    apply_cmd.add_argument(
        "--path", type=Path, help="its checkout (default: the workspace's)"
    )
    bump_cmd = set_sub.add_parser("bump", help="move a member to another commit")
    bump_cmd.add_argument("project", help="member to move")
    bump_cmd.add_argument(
        "--rev", help="commit, tag or branch (default: its integration ref)"
    )
    readme_cmd = set_sub.add_parser(
        "readme", help="generate the candidate's README.md from members.toml"
    )
    readme_cmd.add_argument(
        "--check", action="store_true", help="fail when README.md is stale"
    )
    return parser


def run_set(registry: dict[str, Any], args: argparse.Namespace) -> int:
    """Run a `set` subcommand on the current candidate."""
    directory = candidate()
    if args.set_command == "bump":
        return bump(registry, directory, args.project, args.rev)
    if args.set_command == "apply":
        path = args.path or checkout(_project(registry, args.project))
        commits = members(registry, directory)
        for changed in apply_set(registry, commits, args.project, path):
            print(changed)
        return 0
    if args.set_command == "check":
        return check_set(registry, directory)
    readme = render_set_readme(registry, directory, members(registry, directory))
    return _generated(directory / "README.md", readme, args.check, "set readme")


def run(args: argparse.Namespace) -> int:
    """Run the parsed command; Failure reports an outcome that is an error."""
    registry = load()
    problems = validate(registry)
    if problems:
        for problem in problems:
            print(f"ecosystem.yaml: {problem}", file=sys.stderr)
        raise Failure(
            "data_error",
            f"ecosystem.yaml has {len(problems)} problem(s)",
            hint="fix the lines listed above",
            details={"reason": "invalid_registry", "count": len(problems)},
        )
    if args.command == "validate":
        print(f"ecosystem.yaml: {len(registry['projects'])} projects, valid")
        return 0
    if args.command == "deps":
        return report_deps(registry, args.installed)
    if args.command == "drift":
        return report_drift(registry)
    if args.command == "set":
        return run_set(registry, args)
    if args.command == "standard":
        return check_standard(registry, args.write)
    if args.command == "agents":
        return check_agents(registry, args.check)
    return check_map(registry, args.check)


def error_document(failure: Failure, command: str | None) -> dict[str, Any]:
    """Return the `nogat-error/1` document of a failure (AGI-4.3, ERR-4).

    Title and exit code come from standards/error_registry.json; when that
    file cannot be read, the code stands in for the title and the exit code
    is that of `internal_error`.
    """
    try:
        entries = _read_json(STANDARDS / "error_registry.json")["errors"]
        entry = next(e for e in entries if e["code"] == failure.code)
    except (Failure, KeyError, StopIteration):
        entry = {"title_en": failure.code, "exit_code": 1}
    document: dict[str, Any] = {
        "schema": "nogat-error/1",
        "code": failure.code,
        "title": entry["title_en"],
        "message": failure.message,
        "details": failure.details,
        "exit_code": entry["exit_code"],
    }
    if failure.hint:
        document["hint"] = failure.hint
    if command:
        document["command"] = command
    return document


def main(argv: list[str] | None = None) -> int:
    """Run the command line; on an error the last stderr line is its document."""
    command = None
    try:
        args = _parser().parse_args(argv)
        # `ecosystem <verb>`, the form of `nogat ecosystem <verb>` (HUB-7.3).
        command = " ".join(
            [
                "ecosystem",
                args.command,
                *([args.set_command] if args.command == "set" else []),
            ]
        )
        return run(args)
    except Failure as failure:
        document = error_document(failure, command)
    except Exception as e:  # any defect becomes internal_error (ERR §2)
        document = error_document(
            Failure("internal_error", f"{type(e).__name__}: {e}"), command
        )
    print(f"ecosystem: {document['message']}", file=sys.stderr)
    print(json.dumps(document, ensure_ascii=False), file=sys.stderr)
    return int(document["exit_code"])


if __name__ == "__main__":
    sys.exit(main())
