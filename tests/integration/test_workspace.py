"""Registry commands against a throwaway workspace of checkouts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import ecosystem
import pytest


def _project(name: str, **fields: Any) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "name": name,
        "summary": f"{name} test project.",
        "profiles": ["tool"],
        "status": "active",
        "repo": f"https://github.com/Daldek/{name}",
        "visibility": "public",
        "distribution": {"pypi": None, "import_name": name.lower()},
        "interfaces": {"cli": None, "mcp": None, "rest": None, "python": None},
        "data_sources": [],
        "provides": [],
        "depends_on": [],
    }
    entry.update(fields)
    return entry


def _dep(project: str) -> dict[str, Any]:
    return {
        "project": project,
        "kind": "runtime",
        "status": "active",
        "via": ["library"],
        "exchange": [],
    }


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("NOGAT_WORKSPACE", str(tmp_path))
    return tmp_path


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_drift_reports_each_consumer_state(
    workspace: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write(
        workspace / "App" / "pyproject.toml",
        "[project]\ndependencies = ["
        '"producer @ git+https://github.com/Daldek/Producer.git@release/0.8"]\n',
    )
    _write(workspace / "Broken" / "pyproject.toml", "[project\n")
    (workspace / "Bare").mkdir()
    (workspace / "Producer").mkdir()
    registry = {
        "projects": [
            _project("Producer"),
            _project(
                "App",
                python_manifests=["pyproject.toml"],
                depends_on=[_dep("Producer")],
            ),
            _project(
                "Broken",
                python_manifests=["pyproject.toml"],
                depends_on=[_dep("Producer")],
            ),
            _project("Bare", depends_on=[_dep("Producer")]),
            _project("Absent", depends_on=[_dep("Producer")]),
        ]
    }
    assert ecosystem.report_drift(registry) == 0
    rows = {line.split()[0]: line for line in capsys.readouterr().out.splitlines()[1:]}
    assert "branch release/0.8" in rows["App"]
    assert "branch pin" in rows["App"]
    assert "unreadable" in rows["Broken"]
    assert "not valid TOML" in rows["Broken"]
    assert rows["Bare"].endswith("no manifest")
    assert rows["Absent"].endswith("no checkout")


def test_deps_flags_only_real_conflicts(
    workspace: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write(
        workspace / "A" / "pyproject.toml",
        '[project]\ndependencies = ["numpy<3", "shapely<2"]\n',
    )
    _write(workspace / "B" / "requirements.txt", "numpy>2.5\nshapely>=2.0.2\n")
    registry = {
        "projects": [
            _project("A", python_manifests=["pyproject.toml"]),
            _project("B", python_manifests=["requirements.txt"]),
        ]
    }
    with pytest.raises(ecosystem.Failure) as raised:
        ecosystem.report_deps(registry, with_installed=False)
    assert raised.value.code == "conflict"
    assert raised.value.details["packages"] == ["shapely"]
    out = capsys.readouterr().out
    numpy = next(line for line in out.splitlines() if "numpy" in line)
    shapely = next(line for line in out.splitlines() if "shapely" in line)
    assert "CONFLICT" not in numpy
    assert "CONFLICT" in shapely


def test_deps_notes_unreadable_manifest(
    workspace: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write(workspace / "A" / "pyproject.toml", "[project\n")
    registry = {"projects": [_project("A", python_manifests=["pyproject.toml"])]}
    assert ecosystem.report_deps(registry, with_installed=False) == 0
    assert "not valid TOML" in capsys.readouterr().err


def _error(err: str) -> dict[str, Any]:
    document: dict[str, Any] = json.loads(err.strip().splitlines()[-1])
    assert document["schema"] == "nogat-error/1"
    return document


@pytest.mark.parametrize(
    ("content", "message", "code", "exit_code"),
    [
        (None, "ecosystem.yaml: cannot read", "not_found", 3),
        ("projects: [\n", "ecosystem.yaml: not valid YAML", "data_error", 7),
        ("- a\n", "ecosystem.yaml: top level must be a mapping", "data_error", 7),
        ("schema: nogat-ecosystem/1\n", "ecosystem.yaml has", "data_error", 7),
    ],
)
def test_main_bad_registry_error_document(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    content: str | None,
    message: str,
    code: str,
    exit_code: int,
) -> None:
    registry = tmp_path / "ecosystem.yaml"
    if content is not None:
        registry.write_text(content, encoding="utf-8")
    monkeypatch.setattr(ecosystem, "REGISTRY", registry)
    assert ecosystem.main(["validate"]) == exit_code
    err = capsys.readouterr().err
    assert "Traceback" not in err
    document = _error(err)
    assert document["code"] == code
    assert document["exit_code"] == exit_code
    assert document["command"] == "validate"
    assert message in document["message"]


def test_main_usage_error_is_validation_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert ecosystem.main(["map", "--chek"]) == 2
    document = _error(capsys.readouterr().err)
    assert document["code"] == "validation_error"
    assert document["hint"] == "run: uv run scripts/ecosystem.py --help"


def test_main_defect_is_internal_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def broken(registry: dict[str, Any]) -> list[str]:
        raise KeyError("projects")

    monkeypatch.setattr(ecosystem, "validate", broken)
    assert ecosystem.main(["validate"]) == 1
    assert _error(capsys.readouterr().err)["code"] == "internal_error"


def test_validate_missing_topic_header_reported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    standards = tmp_path / "standards"
    standards.mkdir()
    for path in ecosystem.STANDARDS.glob("*.md"):
        (standards / path.name).write_text(path.read_text(encoding="utf-8"))
    (standards / "error_registry.json").write_text(
        (ecosystem.STANDARDS / "error_registry.json").read_text(encoding="utf-8")
    )
    topic = standards / "AGENT_INTERFACE.md"
    lines = topic.read_text(encoding="utf-8").splitlines(keepends=True)
    topic.write_text("".join(line for line in lines if "Part of standard" not in line))
    monkeypatch.setattr(ecosystem, "STANDARDS", standards)
    problems = ecosystem.validate(ecosystem.load())
    assert problems == ["standards/AGENT_INTERFACE.md: no 'Part of standard X.Y' line"]


def test_map_check_detects_stale_map(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    stale = tmp_path / "ECOSYSTEM_MAP.md"
    stale.write_text("# old\n", encoding="utf-8")
    monkeypatch.setattr(ecosystem, "MAP", stale)
    monkeypatch.setattr(ecosystem, "ROOT", tmp_path)
    assert ecosystem.main(["map", "--check"]) == 4
    assert _error(capsys.readouterr().err)["details"]["reason"] == (
        "stale_generated_file"
    )
    assert ecosystem.main(["map"]) == 0
    assert ecosystem.main(["map", "--check"]) == 0
    assert "is up to date" in capsys.readouterr().out
