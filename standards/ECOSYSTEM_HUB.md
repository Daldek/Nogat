# Ecosystem hub (Nogat)

Part of standard 2.1 · IDs `HUB-…`

Requirements for Nogat as the hub of the ecosystem (ECO-001, ECO-002).

---

## 1. Role

**HUB-1.1** Nogat holds:
1. this standard (`standards/`);
2. the project registry (`ecosystem.yaml`);
3. tooling that reads the registry (drift report, workspace sync, MCP
   configuration, routing table for agents, checks of this standard);
4. the user package `nogat`, which installs the whole ecosystem with one
   command (HUB §7, ECO-026).

**HUB-1.2** Nogat does not contain code of other projects, as submodules,
copies or vendored packages; the `nogat` package depends on their releases.
*Why:* submodules pin commits and conflict with active development and
history rewrites; the registry references repositories instead.

## 2. Registry `ecosystem.yaml`

**HUB-2.1** The registry records structure only: what only Nogat knows. Its
fields are those of `schemas/ecosystem.schema.json`, shown below;
`python_manifests` and, in a dependency, `uses` and `note` are optional.

```yaml
schema: nogat-ecosystem/1
standard_version: "2.1"       # HUB-6.1
data_sources:                 # HUB-2.7
  - {id: gugik, name: GUGiK, country: PL, url: https://www.geoportal.gov.pl, licence: "…"}
projects:
  - name: Retman
    summary: Polish natural-language command layer over the ecosystem tools.   # budget DOC-1.7
    profiles: [tool]          # tool | app | hub
    status: active            # active | research | paused | archived
    repo: https://github.com/Daldek/Retman
    python_manifests: [pyproject.toml]   # HUB-2.8
    visibility: public        # public | private
    distribution:
      pypi: null              # null until published
      import_name: retman
    interfaces:
      cli: retman
      mcp: null
      rest: null
      python: retman
    data_sources: []          # ids from top-level data_sources accessed directly
    provides: []              # HUB-2.5: {id, kind, summary} offered to other projects
    depends_on:
      - project: Kartograf
        kind: optional        # runtime | optional | dev | data   (data = reads another project's files or store)
        status: active        # active | planned
        via: [library]        # library | cli | mcp | rest | service | store | file
        exchange: [kartograf-catalog/1, kartograf-download/1]   # ids from Kartograf provides
        uses: [symbol]        # optional: public symbols used
        note: free text       # optional
```

*Why:* ECO-034; versions, pins and release tags are read from the
repositories (HUB-4.1).

**HUB-2.3** The registry is validated by a JSON Schema in the gate
(`schemas/ecosystem.schema.json`, `uv run scripts/ecosystem.py validate`).

**HUB-2.4** No local paths in `ecosystem.yaml`.

**HUB-2.5** Each project lists what it offers to other projects in
`provides` (`id`, `kind`, `summary`). `kind` is one of `dataset`, `sidecar`,
`store`, `manifest`, `document`, `catalog`, `library`, `service`, `contract`.
Versioned document kinds keep their own id (`kartograf-meta/1`).

**HUB-2.6** Each `depends_on` entry records `status`, `via` and `exchange`,
the ids from the producer's `provides` that cross the boundary; entries MAY
add `uses` (public symbols) and `note`. Exchanges without a package
dependency (reading exported files or another project's store markers) use
kind `data`.
*Why:* the dependency graph alone does not tell which formats a producer
must keep stable or which consumer breaks when a document kind changes.

**HUB-2.7** External data sources are defined once in top-level
`data_sources` (`id`, `name`, `country`, `url`, `licence`); projects list the
ids they access directly.

**HUB-2.8** Projects with Python code list their committed dependency files
in `python_manifests` (repository-relative, for example `pyproject.toml`,
`backend/requirements.txt`); the drift and dependency reports read them
(HUB-4.1, HUB-4.6).

## 3. Local workspace

**HUB-3.1** By default, repositories are resolved as siblings of Nogat, in a
directory named like the project's registry `name`.

**HUB-3.2** A different layout is set with `NOGAT_WORKSPACE`, the directory
that holds the checkouts.

**HUB-3.3** `nogat workspace sync` clones missing repositories into the
workspace and reports dirty trees, unpushed commits and branches that do not
follow DEV-3.1. It never pulls or modifies a dirty repository.
*Why:* users of the tools need no clones; they install packages (REL §3).

## 4. Generated outputs

**HUB-4.1** `uv run scripts/ecosystem.py drift` (`nogat ecosystem drift` once
the package exists, HUB-7.3) reads the checkouts (HUB §3) and prints, for each
active runtime or optional dependency, the consumer's pin from its
`python_manifests` against the producer's latest `v*` tag, and states whether
it is current, behind, a commit or branch pin, or a range that excludes the
latest tag.

**HUB-4.2** `nogat mcp config --client claude|cursor|codex|vscode` prints a
configuration with every ecosystem MCP server, from registry data.

**HUB-4.3** Nogat `AGENTS.md` is generated from the registry: a routing
table (task → tool → entry command) with a link to each tool's AGENTS.md;
the tools' blocks (AGI-8.2) are not inlined, and the budget of DOC-1.7
applies.
*Why:* an agent working from Nogat needs to know which tool covers a task
without opening every repository; inlining every block would exceed the
budget (ECO-048).

**HUB-4.5** `docs/ECOSYSTEM_MAP.md` is generated from the registry
(`uv run scripts/ecosystem.py map`): data-flow diagram, project table,
dependency table (kind, route, exchanged ids), what each project provides and
who consumes it, external data sources. It shows structure only: no versions
and no pins. `map --check` fails with `conflict` when the file is stale; the
gate runs it.
*Why:* people and agents need one view of which tool feeds which and what
breaks when a format changes.

**HUB-4.6** `uv run scripts/ecosystem.py deps` compares third-party
requirements across the checkouts: ranges declared by two or more projects,
and ranges no single version satisfies (`conflict`). `--installed` adds the
Python version and package versions of each checkout's `.venv` and lists
packages that differ. It prepares a candidate (REL-6.4).

**HUB-4.7** `uv run scripts/ecosystem.py standard` checks the standard: every
cited requirement ID, section and decision exists, IDs are defined once in
their document, relative links resolve, Nogat's files keep the budgets of
DOC-1.7, project lists in prose match the registry, and generated tables are
fresh (`--write` regenerates them). The gate runs it.

**HUB-4.8** Nogat's scripts report failures by the registry: a malformed
input is `data_error`, a missing one `not_found`, a stale generated file or
incompatible ranges `conflict`, a wrong call `validation_error`, a defect
`internal_error`; the last stderr line is the `nogat-error/1` document
(AGI-4.3).
*Why:* agents handle the hub's tools like any other tool (ECO-044).

## 5. Agents operating from Nogat

**HUB-5.2** A cross-project change starts with a plan in Nogat (DEV-17.4)
that lists the affected projects and the order, producers first.

## 6. Standard versioning

**HUB-6.1** The version of the standard (MAJOR.MINOR) is in
`standards/README.md`; `ecosystem.yaml` carries it as `standard_version`.
Changes on `develop` accumulate under the next version, listed in the
changelog of `standards/README.md`; when they reach `main`, the merge commit
is tagged `std-X.Y`, and the next change starts version X.(Y+1). Projects
cite requirement IDs, not versions, and record deviations as DEV-1.2 says.
`uv run scripts/ecosystem.py validate` (`nogat ecosystem validate` once the
package exists) checks that `standard_version`, the version line of
`standards/README.md`, `standard_version` in `error_registry.json` and the
`Part of standard X.Y` header of every topic document agree.
*Why:* a tag marks what projects can copy (ERR-3); unpublished drafts need
none (ECO-046).

## 7. The `nogat` package

**HUB-7.1** Nogat is published as `nogat`. One command installs every
ecosystem tool and all their Python dependencies at the versions of one
release set:

```
uv tool install nogat
```

Until every member is on PyPI, a `nogat` release is a git tag, installed with
`uv tool install git+https://github.com/Daldek/Nogat@vX.Y.Z`; `nogat` goes to
PyPI once all members are there. uv is the only documented installer. System
components are not installed but checked by `nogat doctor`: Docker, the
SFINCS engine, PostgreSQL with PostGIS, GPU drivers and the model server used
by Retman.
*Why:* ECO-026; users get one consistent working environment instead of
separate installations with different versions of the same libraries.

**HUB-7.2** A `nogat` release is a release set (REL §6). Its `pyproject.toml`
depends on every member at an exact version (a direct reference to the
member's tag until the member is on PyPI, REL-5.1) and on every third-party
package of the set's `uv.lock` at an exact version, with environment markers.
The dependency list is generated from the lock, and the gate fails when it is
stale. `nogat` is therefore installed in its own environment (`uv tool`), not
added to projects with their own dependencies; a project that needs one tool
depends on `nogat-<project>` with a range (REL-5.2).
*Why:* a wheel cannot carry a lock file; exact dependencies are the only way
one install command reproduces the verified set.

**HUB-7.3** The package exposes each member's commands (`<tool>`,
`<tool>-mcp`) through `[project.scripts]` entries pointing at the members'
entry functions, so one install puts them on `PATH`. The `nogat` command has
two groups, is exempt from the command shape of AGI §3 and reports errors as
HUB-4.8 says:
- for users: `nogat init` (writes `nogat.toml` and creates the data and cache
  directories, checking that hard links work; DEV-18.1, DEV-18.2),
  `nogat doctor` (installed versions against the set; settings and their
  sources, credentials present or missing and store sizes, from
  `<tool> config show --json` of each member with profile `tool`, DEV-18.6;
  the external prerequisites of HUB-7.1), `nogat mcp config` (HUB-4.2),
  `nogat guide` (routing table, HUB-4.3);
- for maintenance, run in a Nogat checkout: `nogat ecosystem validate | map |
  deps | drift | standard` (replacing `scripts/ecosystem.py`),
  `nogat workspace sync` (HUB-3.3).

The package includes `ecosystem.yaml` as package data, read by `nogat mcp
config`, `nogat guide` and the maintenance commands; DEV-5.4 applies (a test
proves the file is in the built wheel).

**HUB-7.4** The `nogat` bump is the largest bump of any member since the
previous `nogat` release, where a minor bump of a `0.y` member and a removed
member count as major and an added member as minor; raising the minimum
Python is major; third-party and development-tool updates alone are minor,
because the set is tested, except a security fix between sets, which is a
patch (REL-6.6).
*Why:* ECO-026; the number tells users whether an upgrade may break their
scripts.
