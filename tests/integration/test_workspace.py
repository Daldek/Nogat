"""Registry commands against a throwaway workspace of checkouts."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

import ecosystem
import guide
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
    _write(
        workspace / "Web" / "backend" / "pyproject.toml",
        '[project]\ndependencies = ["producer>=0.8.0.dev0,<0.9"]\n'
        "[tool.uv.sources]\nproducer = { git = "
        '"https://github.com/Daldek/Producer.git", '
        'rev = "26ee45924b719b4f357ab02c88cda58aa806843f" }\n',
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
                "Web",
                python_manifests=["backend/pyproject.toml"],
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
    pins, copies = capsys.readouterr().out.split("\n\n")
    rows = {line.split()[0]: line for line in pins.splitlines()[1:]}
    assert "branch release/0.8" in rows["App"]
    assert "branch pin" in rows["App"]
    assert "commit 26ee459 (backend/pyproject.toml, tool.uv.sources)" in rows["Web"]
    assert rows["Web"].endswith("commit pin")
    assert "unreadable" in rows["Broken"]
    assert "not valid TOML" in rows["Broken"]
    assert rows["Bare"].endswith("no manifest")
    assert rows["Absent"].endswith("no checkout")
    # None of the checkouts is a git repository: no copy is read.
    assert copies.split()[:4] == ["project", "copy", "source", "state"]
    assert [line.split()[0] for line in copies.splitlines()[1:]] == [
        "Producer",
        "App",
        "Web",
        "Broken",
        "Bare",
        "Absent",
    ]
    assert all(line.endswith("no checkout") for line in copies.splitlines()[1:])


def test_renamed_project_is_read_from_its_repository_directory(
    workspace: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The registry name changed, the repository and its checkout did not
    # (ECO-057); the consumer still requires the old distribution name.
    _write(
        workspace / "OldTools" / "pyproject.toml",
        '[project]\ndependencies = ["pandas>=2"]\n',
    )
    _write(
        workspace / "App" / "pyproject.toml",
        '[project]\ndependencies = ["oldtools>=3.0.0.dev0,<4", "pandas>=2.1"]\n'
        "[tool.uv.sources]\noldtools = { git = "
        '"https://github.com/Daldek/OldTools.git", '
        'rev = "71bae778a6573019a0b8da6498b4429f0e03ddfb" }\n',
    )
    registry = {
        "projects": [
            _project(
                "Renamed",
                repo="https://github.com/Daldek/OldTools",
                distribution={"pypi": "renamed", "import_name": "renamed"},
                python_manifests=["pyproject.toml"],
            ),
            _project(
                "App",
                python_manifests=["pyproject.toml"],
                depends_on=[_dep("Renamed")],
            ),
        ]
    }
    assert ecosystem.report_drift(registry) == 0
    pins = capsys.readouterr().out.split("\n\n")[0]
    rows = {line.split()[0]: line for line in pins.splitlines()[1:]}
    assert rows["App"].split()[1] == "Renamed"
    assert "commit 71bae77 (pyproject.toml, tool.uv.sources)" in rows["App"]

    specs, notes = ecosystem.declared(registry)
    assert notes == []
    assert set(specs) == {"pandas"}
    assert set(specs["pandas"]) == {"Renamed", "App"}


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
    assert document["command"] == "ecosystem validate"
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


@pytest.mark.parametrize("content", [None, "# old\n"])
def test_agents_check_detects_a_missing_or_stale_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    content: str | None,
) -> None:
    target = tmp_path / "AGENTS.md"
    if content is not None:
        target.write_text(content, encoding="utf-8")
    monkeypatch.setattr(ecosystem, "AGENTS", target)
    monkeypatch.setattr(ecosystem, "ROOT", tmp_path)
    assert ecosystem.main(["agents", "--check"]) == 4
    document = _error(capsys.readouterr().err)
    assert document["details"]["reason"] == "stale_generated_file"
    assert document["hint"] == "run: uv run scripts/ecosystem.py agents"
    assert ecosystem.main(["agents"]) == 0
    assert ecosystem.main(["agents", "--check"]) == 0
    assert "is up to date" in capsys.readouterr().out
    assert target.read_text(encoding="utf-8") == guide.render(ecosystem.load())


SET = "26ee45924b719b4f357ab02c88cda58aa806843f"
OLD = "8cd6844c493d27e6a8792c29dfc64528d68a2998"
GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.org",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.org",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
}


def _git(repo: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        env=GIT_ENV,
    )
    return done.stdout.strip()


def _commit(seed: Path, files: dict[str, str], branch: str) -> str:
    """Commit `files` in the seed repository and push them to its origin."""
    for name, text in files.items():
        _write(seed / name, text)
    _git(seed, "add", "-A")
    _git(seed, "commit", "-q", "--allow-empty", "-m", "x")
    _git(seed, "push", "-q", "origin", f"HEAD:{branch}")
    return _git(seed, "rev-parse", "HEAD")


def _published(
    workspace: Path, name: str, files: dict[str, str], branch: str = "develop"
) -> Path:
    """Return the seed of `name`: its files are on origin's `branch`, cloned."""
    origin = workspace / "_origins" / f"{name}.git"
    seed = workspace / "_seeds" / name
    _git(workspace, "init", "-q", "--bare", str(origin))
    _git(workspace, "init", "-q", "-b", branch, str(seed))
    _git(seed, "remote", "add", "origin", str(origin))
    _commit(seed, files, branch)
    _git(workspace, "clone", "-q", "-b", branch, str(origin), name)
    return seed


def _set(tmp_path: Path, commits: dict[str, str]) -> Path:
    directory = tmp_path / "release-sets" / "candidate-1"
    _write(directory / "members.toml", ecosystem.render_members(directory, commits))
    return directory


def _pyproject(*requirements: str, sources: str = "") -> dict[str, str]:
    listed = ", ".join(f'"{r}"' for r in requirements)
    text = f'[project]\nname = "x"\ndependencies = [{listed}]\n'
    if sources:
        text += f"[tool.uv.sources]\n{sources}\n"
    return {"pyproject.toml": text}


def _rows(out: str) -> set[tuple[str, str, str]]:
    """(consumer, producer, state) of each row `set check` printed."""
    cells = [re.split(r"\s{2,}", line) for line in out.splitlines()[2:]]
    return {(c[0], c[1], c[-1]) for c in cells}


def test_set_check_compares_both_pin_forms_at_the_integration_ref(
    workspace: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    url = "https://github.com/Daldek/Producer"
    _published(workspace, "Pep", _pyproject(f"producer @ git+{url}@{SET[:7]}"))
    _published(
        workspace,
        "Uv",
        _pyproject(
            "producer>=0.1",
            sources=f'producer = {{ git = "{url}.git", rev = "{OLD}" }}',
        ),
        branch="feature/x",
    )
    # The working tree differs from what the integration ref holds.
    _write(
        workspace / "Uv" / "pyproject.toml",
        _pyproject(f"producer @ git+{url}@{SET}")["pyproject.toml"],
    )
    _published(workspace, "Ranged", _pyproject("producer>=0.1"))
    _published(workspace, "Silent", _pyproject("numpy>=1.26"))
    _published(workspace, "Later", _pyproject(f"producer @ git+{url}@{OLD}"))
    consumers: dict[str, dict[str, Any]] = {
        "Pep": {},
        "Uv": {"branch": "feature/x"},
        "Ranged": {},
        "Silent": {},
        "Later": {},
    }
    registry = {
        "projects": [
            _project("Producer"),
            *(
                _project(
                    name,
                    python_manifests=["pyproject.toml"],
                    depends_on=[] if name == "Later" else [_dep("Producer")],
                    **fields,
                )
                for name, fields in consumers.items()
            ),
        ]
    }
    directory = _set(workspace, {"Producer": SET})
    with pytest.raises(ecosystem.Failure) as caught:
        ecosystem.check_set(registry, directory)
    assert caught.value.code == "conflict"
    assert caught.value.details["consumers"] == ["Later", "Ranged", "Uv"]
    assert _rows(capsys.readouterr().out) == {
        ("Pep", "Producer", "ok"),
        ("Uv", "Producer", "differs"),
        ("Ranged", "Producer", "not a commit pin"),
        ("Silent", "Producer", "not declared"),
        ("Later", "Producer", "differs"),
    }

    registry["projects"] = [
        p for p in registry["projects"] if p["name"] in ("Producer", "Pep", "Silent")
    ]
    assert ecosystem.check_set(registry, directory) == 0


def test_set_check_reports_a_consumer_it_cannot_read(
    workspace: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _published(workspace, "Pep", _pyproject("numpy"), branch="main")
    registry = {
        "projects": [
            _project("Producer"),
            _project("Pep", python_manifests=["pyproject.toml"]),
            _project("Gone", python_manifests=["pyproject.toml"]),
        ]
    }
    with pytest.raises(ecosystem.Failure) as caught:
        ecosystem.check_set(registry, _set(workspace, {"Producer": SET}))
    assert caught.value.code == "not_found"
    assert caught.value.details["consumers"] == ["Gone", "Pep"]
    assert "origin/develop" in capsys.readouterr().out


def test_set_apply_rewrites_both_forms_and_nothing_else(tmp_path: Path) -> None:
    pyproject = (
        "[project]\n"
        'name = "app"\n'
        "dependencies = [\n"
        '    "producer @ git+https://github.com/Daldek/Producer@v0.1.0",  # tag\n'
        '    "stranger @ git+https://github.com/Daldek/Stranger@1234567",\n'
        '    "numpy>=1.26",\n'
        "]\n"
        "[project.optional-dependencies]\n"
        "store = [\"other[store]>=1 ; python_version >= '3.12'\"]\n"
        "[tool.uv.sources]\n"
        f"other = {{ git = \"https://github.com/Daldek/Other.git\", rev = '{OLD}' }}\n"
    )
    requirements = (
        "producer @ git+https://github.com/Daldek/Producer.git#egg=producer\n"
    )
    _write(tmp_path / "pyproject.toml", pyproject)
    _write(tmp_path / "requirements.txt", requirements)
    other = "fedcba9876543210fedcba9876543210fedcba98"
    registry = {
        "projects": [
            _project("Producer"),
            _project("Other"),
            _project("Stranger"),
            _project("App", python_manifests=["pyproject.toml", "requirements.txt"]),
        ]
    }
    commits = {"Producer": SET, "Other": other}

    changed = ecosystem.apply_set(registry, commits, "App", tmp_path)

    assert changed == [tmp_path / "pyproject.toml", tmp_path / "requirements.txt"]
    assert (tmp_path / "pyproject.toml").read_text(encoding="utf-8") == (
        pyproject.replace("Producer@v0.1.0", f"Producer@{SET}").replace(OLD, other)
    )
    assert (tmp_path / "requirements.txt").read_text(encoding="utf-8") == (
        requirements.replace(".git#", f".git@{SET}#")
    )
    assert ecosystem.apply_set(registry, commits, "App", tmp_path) == []


def test_set_bump_resolves_the_ref_and_regenerates_the_readme(
    workspace: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seed = _published(workspace, "Producer", {"a.txt": "1\n"})
    first = _git(seed, "rev-parse", "HEAD")
    registry = {"projects": [_project("Consumer"), _project("Producer")]}
    directory = workspace / "release-sets" / "candidate-2"
    directory.mkdir(parents=True)
    (workspace / "release-sets" / "candidate-1").mkdir()
    monkeypatch.setattr(ecosystem, "RELEASE_SETS", workspace / "release-sets")
    readme = argparse.Namespace(set_command="readme", check=True)

    assert ecosystem.bump(registry, directory, "Producer", None) == 0
    assert ecosystem.members(registry, directory) == {"Producer": first}
    second = _commit(seed, {"a.txt": "2\n"}, "develop")
    ecosystem.bump(registry, directory, "Producer", None)
    assert ecosystem.members(registry, directory) == {"Producer": second}
    assert ecosystem.run_set(registry, readme) == 0
    ecosystem.bump(registry, directory, "Producer", first[:7])
    assert ecosystem.members(registry, directory) == {"Producer": first}
    assert first in (directory / "README.md").read_text(encoding="utf-8")

    _write(
        directory / "members.toml",
        ecosystem.render_members(directory, {"Producer": second}),
    )
    with pytest.raises(ecosystem.Failure) as caught:
        ecosystem.run_set(registry, readme)
    assert caught.value.code == "conflict"


@pytest.mark.parametrize(
    "text",
    [
        f'[Unknown]\ncommit = "{SET}"\n',
        f'[Producer]\ncommit = "{SET[:7]}"\n',
        f'[Producer]\ncommit = "{SET}"\nbranch = "develop"\n',
    ],
)
def test_members_rejects_anything_but_full_commits_of_projects(
    tmp_path: Path, text: str
) -> None:
    _write(tmp_path / "members.toml", text)
    with pytest.raises(ecosystem.RegistryError) as caught:
        ecosystem.members({"projects": [_project("Producer")]}, tmp_path)
    assert caught.value.code == "data_error"


def _repository(directory: Path, files: dict[str, str]) -> str:
    """Commit `files` in the repository `directory`, made when missing; the commit."""
    if not (directory / ".git").exists():
        _git(directory.parent, "init", "-q", str(directory))
    for name, text in files.items():
        _write(directory / name, text)
    _git(directory, "add", "-A")
    _git(directory, "commit", "-q", "--allow-empty", "-m", "x")
    return _git(directory, "rev-parse", "HEAD")


HANDOFF = "schemas/exchange/handoff-1.schema.json"
TOKENS = ":root { --nogat-ink: #102030; }\n"
HEADER = (
    "/* Copied from Nogat design/tokens.css at commit 29e7e1c (DEV-15.3). "
    "Do not edit here:\n   change Nogat, then copy again. */\n"
)


def test_copies_of_nogat_files_are_current_behind_or_modified(
    workspace: Path,
) -> None:
    nogat = workspace / "_nogat"
    _repository(
        nogat,
        {
            HANDOFF: '{"v": 1}\n',
            "schemas/agent/result-1.schema.json": '{"r": 1}\n',
            "design/tokens.css": TOKENS,
            "design/README.md": "not copied\n",
        },
    )
    second = _repository(nogat, {HANDOFF: '{"v": 2}\n'})
    restored = _repository(nogat, {HANDOFF: '{"v": 1}\n'})
    _repository(nogat, {HANDOFF: '{"v": 3}\n'})
    _repository(
        workspace / "Alpha",
        {
            "schemas/nogat/handoff-1.schema.json": '{"v": 1}\n',
            "web/tokens.css": HEADER + TOKENS,
            "docs/result-1.schema.json": '{"r": "edited"}\n',
            "README.md": "Alpha\n",
        },
    )
    _write(workspace / "Alpha" / "untracked" / "handoff-1.schema.json", "{}\n")
    _repository(
        workspace / "Beta",
        {
            "a/handoff-1.schema.json": '{"v": 3}\n',
            "b/handoff-1.schema.json": '{"v": 2}\n',
            # A comment that does not name Nogat stays part of the copy.
            "tokens.css": "/* Our tokens. */\n" + TOKENS,
        },
    )
    (workspace / "Plain").mkdir()
    registry = {
        "projects": [
            _project("Nogat", profiles=["hub"]),
            _project("Alpha"),
            _project("Beta"),
            _project("Plain"),
            _project("Absent"),
        ]
    }
    assert ecosystem.copy_rows(registry, nogat) == [
        (
            "Alpha",
            "docs/result-1.schema.json",
            "schemas/agent/result-1.schema.json",
            "modified",
        ),
        (
            "Alpha",
            "schemas/nogat/handoff-1.schema.json",
            HANDOFF,
            f"behind {restored[:7]}",
        ),
        ("Alpha", "web/tokens.css", "design/tokens.css", "current"),
        ("Beta", "a/handoff-1.schema.json", HANDOFF, "current"),
        ("Beta", "b/handoff-1.schema.json", HANDOFF, f"behind {second[:7]}"),
        ("Beta", "tokens.css", "design/tokens.css", "modified"),
        ("Plain", "—", "—", "no checkout"),
        ("Absent", "—", "—", "no checkout"),
    ]
