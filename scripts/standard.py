"""Checks of the standard itself: IDs, links, budgets and copies of registry data.

`uv run scripts/ecosystem.py standard` runs every check and exits 1 on a
problem; `--write` first regenerates the blocks this module owns (the error
registry tables in standards/ERROR_REGISTRY.md).
"""

from __future__ import annotations

import json
import re
import tomllib
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

PREFIXES = ("DEV", "DOC", "AGI", "ERR", "REL", "HUB")
_P = "|".join(PREFIXES)
DEFINITION = re.compile(rf"^\*\*(?P<id>(?:{_P})-\d+(?:\.\d+)?)\*\*", re.MULTILINE)
CITED_ID = re.compile(rf"(?<![\w-])(?P<id>(?:{_P})-\d+(?:\.\d+)?)(?!\w)")
CITED_SECTION = re.compile(rf"(?<![\w-])(?P<prefix>{_P}) §(?P<n>\d+)")
CITED_ECO = re.compile(r"(?<![\w-])(?P<id>ECO-\d{3})(?!\d)")
DOC_PREFIX = re.compile(rf"IDs `(?P<prefix>{_P})-…`")
SECTION = re.compile(r"^## (?P<n>\d+)\. ", re.MULTILINE)
ECO_HEADING = re.compile(r"^## (?P<id>ECO-\d{3}) ", re.MULTILINE)
LINK = re.compile(r"(?<!!)\[[^\]\n]*\]\((?P<target>[^)\s]+)\)")
HEADING = re.compile(r"^#{1,6} (?P<text>.+?)\s*#*\s*$", re.MULTILINE)
FENCE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)
INLINE_CODE = re.compile(r"`[^`\n]*`")
HTML_ID = re.compile(r'<a id="([^"]+)"></a>')
BUDGET_ROW = re.compile(
    r"^\| `(?P<path>[^`]+)` \| (?P<lines>[\d,]+) lines(?: and (?P<kib>\d+) KiB)? \|",
    re.MULTILINE,
)
DESCRIPTION_ROW = re.compile(
    r"^\| Description ladder: `pyproject` `description` \| (?P<chars>[\d,]+) "
    r"characters \|",
    re.MULTILINE,
)
GENERATED = re.compile(
    r"(?P<open><!-- generated: (?P<name>[\w-]+) .*?-->\n)(?P<body>.*?)"
    r"(?P<close><!-- end generated -->)",
    re.DOTALL,
)
MARKERS = re.compile(r"The markers are (?P<names>[^;]+);")

# Directories with v1 files kept verbatim until replaced (DOC-11.1).
V1 = ("standards/legacy/", "standards/templates/", "standards/configs/")
CITING_SUFFIXES = {".md", ".py", ".sh", ".yml", ".yaml", ".json", ".toml"}


def _files(root: Path, suffixes: set[str]) -> list[Path]:
    """Return Nogat's own files with the given suffixes.

    Skipped: the v1 directories, hidden directories other than `.github`,
    and uv.lock.
    """
    found = []
    for path in sorted(root.rglob("*")):
        parts = path.relative_to(root).parts
        rel = "/".join(parts)
        if (
            not path.is_file()
            or path.suffix not in suffixes
            or rel.startswith(V1)
            or any(p.startswith(".") and p != ".github" for p in parts)
            or rel == "uv.lock"
        ):
            continue
        found.append(path)
    return found


def _strip_code(text: str) -> str:
    """Blank fenced blocks and inline code so examples are not read as links."""
    text = FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    return INLINE_CODE.sub("``", text)


def _without_changelog(path: Path, text: str) -> str:
    """Drop the changelog of standards/README.md: it lists retired IDs."""
    if path.as_posix().endswith("standards/README.md"):
        return text.split("\n## Changelog", 1)[0]
    return text


def id_problems(root: Path) -> list[str]:
    """Check that IDs are defined once, in their document, and every citation resolves.

    Definitions are `**PREFIX-n.m**` at the start of a line in the topic
    document whose header names the prefix; sections are `## n.` headings of
    that document; decisions are `## ECO-nnn` headings of DECISIONS.md. The
    changelog of standards/README.md is history and is not checked.
    """
    problems: list[str] = []
    standards = root / "standards"
    defined: Counter[str] = Counter()
    sections: set[tuple[str, str]] = set()
    for path in sorted(standards.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        header = DOC_PREFIX.search("\n".join(text.splitlines()[:5]))
        for m in DEFINITION.finditer(text):
            defined[m["id"]] += 1
            if header is None or not m["id"].startswith(header["prefix"] + "-"):
                problems.append(f"standards/{path.name}: {m['id']} defined here")
        if header is not None:
            sections |= {(header["prefix"], m["n"]) for m in SECTION.finditer(text)}
    problems += [f"{i} defined {n} times" for i, n in sorted(defined.items()) if n > 1]
    decisions = (standards / "DECISIONS.md").read_text(encoding="utf-8")
    ecos = Counter(m["id"] for m in ECO_HEADING.finditer(decisions))
    problems += [f"{i} defined {n} times" for i, n in sorted(ecos.items()) if n > 1]

    for path in _files(root, CITING_SUFFIXES):
        rel = path.relative_to(root).as_posix()
        if rel.startswith("tests/"):
            continue
        text = _without_changelog(path, path.read_text(encoding="utf-8"))
        for number, line in enumerate(text.splitlines(), 1):
            for m in CITED_ID.finditer(line):
                if m["id"] not in defined:
                    problems.append(f"{rel}:{number}: {m['id']} is not defined")
            for m in CITED_SECTION.finditer(line):
                if (m["prefix"], m["n"]) not in sections:
                    problems.append(
                        f"{rel}:{number}: {m['prefix']} §{m['n']} is not a section"
                    )
            for m in CITED_ECO.finditer(line):
                if m["id"] not in ecos:
                    problems.append(f"{rel}:{number}: {m['id']} is not a decision")
    return problems


def slug(heading: str) -> str:
    """Return GitHub's anchor for a Markdown heading."""
    text = INLINE_CODE.sub(lambda m: m.group(0).strip("`"), heading).lower()
    kept = "".join(c for c in text if c in " -_" or unicodedata.category(c)[0] in "LN")
    return kept.replace(" ", "-")


def anchors(text: str) -> set[str]:
    """Return the anchors of a Markdown text.

    Headings get GitHub's slugs, with duplicates numbered as GitHub numbers
    them; `<a id="…">` elements add their ids.
    """
    seen: Counter[str] = Counter()
    found = set(HTML_ID.findall(text))
    for m in HEADING.finditer(FENCE.sub("", text)):
        base = slug(m["text"])
        found.add(f"{base}-{seen[base]}" if seen[base] else base)
        seen[base] += 1
    return found


def link_problems(root: Path) -> list[str]:
    """Check that relative links in Nogat's Markdown reach a file and heading."""
    problems = []
    for path in _files(root, {".md"}):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        for number, line in enumerate(_strip_code(text).splitlines(), 1):
            for m in LINK.finditer(line):
                target = m["target"]
                if re.match(r"^[a-z][a-z+.-]*:", target):
                    continue
                file_part, _, anchor = target.partition("#")
                dest = (path.parent / file_part).resolve() if file_part else path
                if not dest.exists():
                    problems.append(f"{rel}:{number}: {target} does not exist")
                    continue
                if (
                    anchor
                    and dest.suffix == ".md"
                    and anchor not in anchors(dest.read_text(encoding="utf-8"))
                ):
                    problems.append(f"{rel}:{number}: no heading for #{anchor}")
    return problems


def budget_problems(root: Path) -> list[str]:
    """Check Nogat's own files against the budgets of DOC-1.7.

    Rows of the DOC-1.7 table that name a file with a line budget apply to
    that file in Nogat when it exists; the `pyproject` description row
    applies to pyproject.toml.
    """
    table = (root / "standards" / "DOCUMENTATION_STANDARDS.md").read_text(
        encoding="utf-8"
    )
    problems = []
    for m in BUDGET_ROW.finditer(table):
        path = root / m["path"]
        if not path.is_file():
            continue
        data = path.read_bytes()
        lines = data.count(b"\n")
        limit = int(m["lines"].replace(",", ""))
        if lines > limit:
            problems.append(f"{m['path']}: {lines} lines, budget {limit} (DOC-1.7)")
        if m["kib"] and len(data) > int(m["kib"]) * 1024:
            problems.append(f"{m['path']}: {len(data)} bytes, budget {m['kib']} KiB")
    description = DESCRIPTION_ROW.search(table)
    pyproject = root / "pyproject.toml"
    if description and pyproject.is_file():
        text = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        chars = len(text.get("project", {}).get("description", ""))
        limit = int(description["chars"].replace(",", ""))
        if chars > limit:
            problems.append(
                f"pyproject.toml: description {chars} characters, budget {limit}"
            )
    return problems


def _dash(value: object) -> str:
    return "–" if value is None else str(value)


def error_tables(registry: dict[str, Any]) -> dict[str, str]:
    """Return the Markdown tables generated from error_registry.json, by block name."""
    outcomes = ["| Status | Exit | Meaning |", "|---|---|---|"]
    outcomes += [
        f"| `{o['status']}` | {o['exit_code']} | {o['meaning']} |"
        for o in registry["outcomes"]
    ]
    errors = ["| Code | Exit | HTTP | Meaning |", "|---|---|---|---|"]
    errors += [
        f'| <a id="{e["code"]}"></a>`{e["code"]}` | {_dash(e["exit_code"])} '
        f"| {_dash(e['http_status'])} "
        f"| {e['meaning']} |"
        for e in registry["errors"]
    ]
    return {
        "error-outcomes": "\n".join(outcomes) + "\n",
        "error-codes": "\n".join(errors) + "\n",
    }


def regenerate(text: str, blocks: dict[str, str]) -> str:
    """Return `text` with every known generated block replaced by its content."""

    def replace(m: re.Match[str]) -> str:
        body = blocks.get(m["name"], m["body"])
        return m["open"] + body + m["close"]

    return GENERATED.sub(replace, text)


def generated_problems(path: Path, blocks: dict[str, str], shown: str) -> list[str]:
    """Check that every expected generated block exists in `path` and is fresh."""
    text = path.read_text(encoding="utf-8")
    present = {m["name"] for m in GENERATED.finditer(text)}
    problems = [
        f"{shown}: no generated block {n!r}" for n in blocks if n not in present
    ]
    if regenerate(text, blocks) != text:
        problems.append(
            f"{shown}: generated blocks are stale; "
            "run: uv run scripts/ecosystem.py standard --write"
        )
    return problems


def error_schema(registry: dict[str, Any]) -> str:
    """Return schemas/agent/error-1.schema.json, generated from error_registry.json.

    The codes, and the exit code each one fixes, come from the registry; the
    rest of the document is AGI-4.3.
    """
    codes = [e["code"] for e in registry["errors"]]
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://github.com/Daldek/Nogat/schemas/agent/error-1.schema.json",
        "title": "<tool>-error/1",
        "description": (
            "Error document (AGI-4.3, ERR-4). Generated from "
            "standards/error_registry.json by `uv run scripts/ecosystem.py "
            "standard --write`; do not edit. Unknown fields are allowed (AGI-4.1)."
        ),
        "type": "object",
        "required": ["schema", "code", "title", "message", "details", "exit_code"],
        "properties": {
            "schema": {"type": "string", "pattern": "^[a-z][a-z0-9]*-error/1$"},
            "code": {"$ref": "#/$defs/code"},
            "title": {"type": "string", "minLength": 1},
            "message": {"type": "string", "minLength": 1},
            "hint": {"type": "string", "minLength": 1},
            "details": {
                "type": "object",
                "properties": {"reason": {"$ref": "#/$defs/reason"}},
            },
            "exit_code": {"type": ["integer", "null"]},
            "command": {"$ref": "commands-1.schema.json#/$defs/command_name"},
        },
        "allOf": [
            {
                "if": {"properties": {"code": {"const": e["code"]}}},
                "then": {"properties": {"exit_code": {"const": e["exit_code"]}}},
            }
            for e in registry["errors"]
        ],
        "$defs": {
            "code": {"enum": codes},
            "reason": {"type": "string", "pattern": "^[a-z][a-z0-9_]*$"},
        },
    }
    return json.dumps(schema, indent=2, ensure_ascii=False) + "\n"


def file_problems(path: Path, expected: str, shown: str) -> list[str]:
    """Check that a generated file exists and equals its generator's output."""
    if not path.is_file() or path.read_text(encoding="utf-8") != expected:
        return [f"{shown}: stale; run: uv run scripts/ecosystem.py standard --write"]
    return []


def _names(text: str) -> set[str]:
    """Return the names of a prose list: `a, b, c and d`, backticks ignored."""
    parts = re.split(r",|\band\b|\s+", text.replace("`", ""))
    return {p.strip() for p in parts if p.strip()}


def project_list_problems(root: Path, registry: dict[str, Any]) -> list[str]:
    """Check the lists of projects typed in prose against the registry."""
    projects = registry["projects"]
    members = {p["name"] for p in projects if "hub" not in p["profiles"]}
    lower = {n.lower() for n in members}
    clis = {p["interfaces"]["cli"] for p in projects if p["interfaces"]["cli"]}
    checks: list[tuple[str, str, set[str]]] = [
        (
            "README.md",
            r"Poland and Czechia:\s*(?P<names>[^.]+)\.",
            members,
        ),
        (
            "standards/README.md",
            r"`<project>`:[^:]*:\s*(?P<names>[a-z,\s]+);",
            lower,
        ),
        (
            "standards/README.md",
            r"`<tool>`:[^:]*:\s*(?P<names>[a-z,\s]+);",
            clis,
        ),
        (
            "standards/README.md",
            r"Shared rules for (?P<names>[^.]+?) and Nogat\.",
            members,
        ),
        (
            "standards/ci/ci.yml",
            r"for p in (?P<names>[a-z ]+); do",
            lower,
        ),
        (
            "standards/ci/README.md",
            r"distributions \((?P<names>[`a-z,\s]+?) and their",
            lower,
        ),
    ]
    problems = []
    for rel, pattern, expected in checks:
        text = (root / rel).read_text(encoding="utf-8")
        m = re.search(pattern, text)
        if m is None:
            problems.append(f"{rel}: project list not found ({pattern})")
            continue
        found = _names(m["names"].replace("\n", " "))
        if found != expected:
            problems.append(
                f"{rel}: project list differs from ecosystem.yaml: "
                f"missing {sorted(expected - found)}, extra {sorted(found - expected)}"
            )

    dev = (root / "standards" / "DEVELOPMENT_STANDARDS.md").read_text(encoding="utf-8")
    for profile in ("tool", "app", "hub"):
        m = re.search(rf"^\| `{profile}` \| [^|]+\| (?P<names>[^|]+)\|", dev, re.M)
        expected = {p["name"] for p in projects if profile in p["profiles"]}
        found = _names(re.sub(r"\([^)]*\)", "", m["names"])) if m else set()
        if found != expected:
            problems.append(
                f"standards/DEVELOPMENT_STANDARDS.md: DEV §1 `{profile}` lists "
                f"{sorted(found)}, ecosystem.yaml has {sorted(expected)}"
            )
    return problems


def marker_problems(root: Path, registry: dict[str, Any]) -> list[str]:
    """Check the store markers listed in DEV-19.12 against the registry.

    Every project that provides a `store` has the marker `<tool>-store.json`,
    `<tool>` being its CLI; the sentence "The markers are …;" must name exactly
    those files.
    """
    problems: list[str] = []
    expected: set[str] = set()
    for project in registry["projects"]:
        if not any(item["kind"] == "store" for item in project["provides"]):
            continue
        cli = project["interfaces"]["cli"]
        if cli is None:
            problems.append(
                f"{project['name']}: provides a store but has no CLI, so no "
                "marker name (DEV-19.12)"
            )
        else:
            expected.add(f"{cli}-store.json")
    rel = "standards/DEVELOPMENT_STANDARDS.md"
    m = MARKERS.search((root / rel).read_text(encoding="utf-8"))
    if m is None:
        return [*problems, f"{rel}: marker list not found ({MARKERS.pattern})"]
    found = _names(m["names"])
    if found != expected:
        problems.append(
            f"{rel}: DEV-19.12 lists markers {sorted(found)}, the registry's "
            f"stores have {sorted(expected)}"
        )
    return problems
