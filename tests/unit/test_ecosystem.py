"""Unit tests of scripts/ecosystem.py: parsing, range checks, pins, tags."""

from __future__ import annotations

import subprocess
from pathlib import Path

import ecosystem
import pytest
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet


@pytest.mark.parametrize(
    "ranges",
    [
        ("<3", ">2.5"),
        (">1.0", "<1.1"),
        ("<2", ">1,!=1.5"),
        (">=2.1,<3", ">=2.0.2"),
        ("==1.4.*", ">1.4.9"),
        ("~=2.2", "<2.3"),
        ("!=1.0", "!=2.0"),
    ],
)
def test_range_conflicts_overlapping_ranges_agree(ranges: tuple[str, str]) -> None:
    specs = {f"P{i}": SpecifierSet(r) for i, r in enumerate(ranges)}
    assert ecosystem.range_conflicts(specs) is None


@pytest.mark.parametrize(
    "ranges",
    [
        ("<2", ">=2"),
        (">=1.5,<2", "<1.5"),
        ("==1.4.*", ">=1.5"),
        ("==2.0", "!=2.0"),
    ],
)
def test_range_conflicts_disjoint_ranges_reported(ranges: tuple[str, str]) -> None:
    specs = {f"P{i}": SpecifierSet(r) for i, r in enumerate(ranges)}
    why = ecosystem.range_conflicts(specs)
    assert why is not None
    assert why.startswith("no version satisfies")


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        (
            "kartograf @ git+https://github.com/Daldek/Kartograf.git@release/0.8",
            ("branch", "release/0.8"),
        ),
        (
            "kartograf @ git+https://github.com/Daldek/Kartograf.git@feature/x#egg=k",
            ("branch", "feature/x"),
        ),
        (
            "kartograf @ git+https://github.com/Daldek/Kartograf.git@v0.7.2",
            ("tag", "v0.7.2"),
        ),
        (
            "kartograf @ git+https://github.com/Daldek/Kartograf.git"
            "@8e9bcbb0123456789abcdef0123456789abcdef0",
            ("commit", "8e9bcbb"),
        ),
        (
            "kartograf @ git+ssh://git@github.com/Daldek/Kartograf.git",
            ("none", ""),
        ),
        ("kartograf @ file:///src/kartograf", ("path", "file:///src/kartograf")),
        ("kartograf>=0.8.0,<0.9", ("range", "<0.9,>=0.8.0")),
        ("kartograf", ("none", "")),
    ],
)
def test_pin_classifies_requirement(line: str, expected: tuple[str, str]) -> None:
    assert ecosystem._pin(Requirement(line)) == expected


def test_requirement_lines_reads_requirements_like_pip(tmp_path: Path) -> None:
    (tmp_path / "base.txt").write_text("numpy>=1.26  # arrays\n", encoding="utf-8")
    (tmp_path / "requirements.txt").write_text(
        "# runtime\n"
        "-r base.txt\n"
        "--index-url https://example.org/simple\n"
        "-e .\n"
        "fastapi==0.1 \\\n"
        "    --hash=sha256:abc \\\n"
        "    --hash=sha256:def\n"
        "pydantic>=2.5 ; python_version >= '3.12'\n",
        encoding="utf-8",
    )
    lines = ecosystem._requirement_lines(tmp_path / "requirements.txt")
    assert lines == [
        "numpy>=1.26",
        "fastapi==0.1",
        "pydantic>=2.5 ; python_version >= '3.12'",
    ]


def test_requirement_lines_include_cycle_terminates(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("-r b.txt\nalpha\n", encoding="utf-8")
    (tmp_path / "b.txt").write_text("-r a.txt\nbeta\n", encoding="utf-8")
    assert ecosystem._requirement_lines(tmp_path / "a.txt") == ["beta", "alpha"]


def test_requirement_lines_reads_pyproject_sections(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\n"
        'dependencies = ["httpx>=0.27"]\n'
        "[project.optional-dependencies]\n"
        'mcp = ["mcp>=1.0"]\n'
        "[dependency-groups]\n"
        'dev = ["pytest>=8", {include-group = "lint"}]\n'
        'lint = ["ruff"]\n',
        encoding="utf-8",
    )
    lines = ecosystem._requirement_lines(tmp_path / "pyproject.toml")
    assert lines == ["httpx>=0.27", "mcp>=1.0", "pytest>=8", "ruff"]


@pytest.mark.parametrize(
    ("name", "text", "fragment"),
    [
        ("pyproject.toml", "[project\n", "not valid TOML"),
        ("requirements.txt", None, "cannot read"),
    ],
)
def test_requirement_lines_bad_manifest_raises_registry_error(
    tmp_path: Path, name: str, text: str | None, fragment: str
) -> None:
    path = tmp_path / name
    if text is not None:
        path.write_text(text, encoding="utf-8")
    with pytest.raises(ecosystem.RegistryError, match=fragment):
        ecosystem._requirement_lines(path)


def _git_repo_with_tags(path: Path, tags: list[str]) -> Path:
    env = {
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@example.org",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@example.org",
        "PATH": "/usr/bin:/bin",
    }
    subprocess.run(["git", "init", "-q", str(path)], check=True, env=env)
    subprocess.run(
        ["git", "-C", str(path), "commit", "-q", "--allow-empty", "-m", "x"],
        check=True,
        env=env,
    )
    for tag in tags:
        subprocess.run(["git", "-C", str(path), "tag", tag], check=True, env=env)
    return path


@pytest.mark.parametrize(
    ("tags", "latest"),
    [
        (["v1.0.0", "v1.0.0-rc1", "v0.9.0"], "v1.0.0"),
        (["v1.0.0", "v1.1.0rc1"], "v1.0.0"),
        (["v0.2.0rc1", "v0.1.0rc1"], "v0.2.0rc1"),
        (["v0.10.0", "v0.9.0", "vnext"], "v0.10.0"),
        ([], None),
    ],
)
def test_latest_tag_prefers_newest_final_release(
    tmp_path: Path, tags: list[str], latest: str | None
) -> None:
    assert ecosystem._latest_tag(_git_repo_with_tags(tmp_path / "r", tags)) == latest


def test_latest_tag_outside_git_is_none(tmp_path: Path) -> None:
    assert ecosystem._latest_tag(tmp_path) is None


@pytest.mark.parametrize(
    ("kind", "value", "latest", "state"),
    [
        ("tag", "v0.7.0", "v0.7.2", "behind"),
        ("tag", "v0.7.2", "v0.7.2", "current"),
        ("tag", "v0.8.0", "v0.7.2", "ahead"),
        ("range", ">=0.8.0,<0.9", "v0.7.2", "range excludes latest"),
        ("range", ">=0.7", "v0.7.2", "range ok"),
        ("tag", "vnext", "v0.7.2", "not comparable"),
        ("commit", "8e9bcbb", "v0.7.2", "commit pin"),
    ],
)
def test_state_compares_pin_with_latest(
    kind: str, value: str, latest: str, state: str
) -> None:
    assert ecosystem._state(kind, value, latest) == state
