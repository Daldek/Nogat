# Plan: projects belong to Archiwista

Approved: 2026-10-31

Requirements: HUB-5.2, DEV-17.4, DEV-19.18, REL-5.3, REL-5.4, ECO-020,
ECO-054. Changes the members of the
[first release set](2026-10-20-first-release-set.md) before their tags.

## Goal

One notion of a project, owned by one tool. Kartograf and IMGWTools only
download data and keep the versioned store; Archiwista alone keeps projects.
A project records the work on one task (the author's words, 2026-10-31): the
area it covers, the store versions it uses, the activity on it, and the
exports for further work in QGIS or Hydrograf. Data already in the store is
pinned to a project without asking the source; only new data goes through the
check at the source and the plan window. Many projects may pin the same
version.

## Where it starts

Neither producer has released projects: Kartograf's last tag is `v0.7.2`
(projects are in the untagged 0.8.0), IMGWTools' last tag is `v2.1.1`
(projects are in the untagged 3.0.0). Removing them breaks no released user
(ECO-020); after the tags it would be a breaking change of released versions.

Today the notion is split in three:

| Piece | Owner | What it holds |
|---|---|---|
| `kartograf-project.json` (`kartograf-project/1`) | Kartograf, `src/kartograf/project/` and `cli/project_cmd.py`, about 3,000 lines, CLI and MCP `project init/add/remove/download/status/verify` | tasks (a data command and its options) and their pins (`version`, `sha256`); one store |
| `imgw-project.json` (`imgw-project/1`) | IMGWTools, `src/imgwtools/project.py`, about 3,100 lines, CLI `imgw project …` | the same shape for archives, series and station catalogs, with `content_sha256` matching for ČHMÚ |
| A project in Archiwista | Archiwista: discovery of both manifests, owner and sharing in the state database, own data and snapshots (A-ADR-027), project jobs (A-ADR-039, A-ADR-040, A-ADR-042), and the planned "Zestaw" (SPEC 8.4, v1.1) | everything else: access, own data, the interface, and the set as a separate notion |

The producers' model makes a pin a result of running its task's command: a
pin exists only inside a task and only after a full run. Data already in the
store can be pinned only by adding a command whose run finds it there
(Kartograf's live run of 2026-10-15, scenario 2: three index requests, no data
downloaded). No producer pins a stored version as it is, and neither has a
project area, an activity record or an export.

Consumers of the producers' projects: Archiwista (`ProjectActionAdapter`,
`adapter/kartograf/actions.py`, the IMGW adapter), Retman (the module
`imgw_projects`: `src/retman/tools/imgwtools/{projects,calls_projects,describe_projects,ops_projects,preview_projects}.py`).
Hydrolog, Hydrograf and Hydraulik use neither (checked in their code).

## Options

| Option | Verdict |
|---|---|
| A. Keep the producers' manifests; Archiwista shows one "Projekt" over them, adds the area, the activity view and the export, and asks each producer for a "pin what the store holds" operation | Rejected: the split stays under the surface, every new project feature crosses three repositories, and a version is pinned only through a producer's task |
| B. Projects only in Archiwista; producers keep download, check, the store and one new function each that gives the command of a stored version | Chosen: one owner, one file, pins of any producer, and the producers lose about 6,000 lines of code and their tests |
| C. A shared project library imported by every tool | Rejected: a new dependency between all projects for a notion only Archiwista presents (as ECO-051 option C) |
| D. Release with the producers' projects now and move them later | Rejected: the release would publish an interface only to break it in the next one |

## Decision

Option B, on the author's request of 2026-10-31, recorded as ECO-054 in
`standards/DECISIONS.md`.

**What a producer keeps.** Download and check (`run_command`,
`check_command`, the plan document), the store and its read API, the sidecar,
`kartograf.testing` and `imgwtools.testing` without project builders. It gains
one read-only function: the command of a stored version, from its sidecar,
as a `CommandCall` (Kartograf's request KB-6 `command_for_file`, and its
IMGWTools counterpart). A version whose command cannot be rebuilt (see the
families below) answers with a coded refusal, not a guess.

**What Archiwista owns.** A project is a directory with
`archiwista-project.json` (`archiwista-project/1`), written only by
Archiwista under a lock `.archiwista-project.lock`; access (owner,
visibility, groups) stays in the state database as today (A-ADR-029). The
file holds:

- name, description, created at and by;
- the area: a geometry file in the project's `obszary/` with its SHA-256;
- the stores: per producer, the store root as written (relative or absolute,
  matched by path or alias as today, SPEC 4.7);
- groups of pins, each with a name, its origin (`plan` with the producer's
  `CommandCall`, or `local` with the selection that chose it) and its pins:
  producer, `version` (store-relative path), `sha256`, `content_sha256` when
  the sidecar has one, `size_bytes`, unit, label, pinned at and by.

Own data (`dane/`) and snapshots (`.wersje/`) stay as they are. The activity
of a project is the action log (A-ADR-047) filtered by the project, shown on
its card. Exports (the former "Zestaw", SPEC 8.4) become the project's
exports in `zestawy/<name>/`, generated from its pins.

**Operations in Archiwista.**

| Operation | Network | How |
|---|---|---|
| Pin local data | no | from "Stan lokalny" (area, product, year, variant), a Katalog selection or a file card: the chosen versions and their `sha256` from the index into a group with origin `local` |
| Add new data | yes | the plan window: the download job's `files[]` (DEV-19.19) become a group with origin `plan` and the call |
| Verify | no | Archiwista hashes the pinned versions; `content_sha256` decides when a version's bytes changed but its content did not |
| Check for updates | yes | the producer's check of the group's call (origin `plan`) or of the call of each pinned version (origin `local`, the new producer function); a version without a call is reported as not checkable, with the reason |
| Re-pin | yes | the call run in update mode, the group's pins replaced by the result after its full success |
| Restore missing | yes | the call run in default mode; a pin whose `sha256` (or `content_sha256`) returns is kept, otherwise the restore fails for that pin |
| Export | no | QGIS `.qgz`, `pliki.csv`, `pliki.txt` (for Hydrograf), `ATRYBUCJE.txt`, `polecenia.sh` from the calls, `projekt.json` (SPEC 8.4 adapted) |

## Steps

Producers before consumers (HUB-5.2). Each step runs in its own repository's
session (DEV-3.4) on a topic branch, one commit per step with the project's
gate green, an ADR, CHANGELOG (**Breaking** in the producers) and PROGRESS;
no aliases or deprecated paths (ECO-020). File references are those of
2026-10-31 and only locate the work. Sizes are estimates in sessions.

1. **Nogat** (0.5). The new ECO decision; DEV-19.18 loses "a `project` command" from its
   examples; `ecosystem.yaml`: remove `kartograf-project/1` and
   `imgw-project/1` from `provides` and from every `exchange`, add
   `archiwista-project/1` to Archiwista, update the `kartograf-testing`
   summary; `map` and `agents` regenerated; the first-release-set plan
   updated by decision D3; PROGRESS and CHANGELOG.

2. **Kartograf** (2 to 3), parallel with step 3.
   - Remove `src/kartograf/project/`, `cli/project_cmd.py`,
     `catalog/commands/project.py`, the MCP project tools and the `--project`
     handling in `mcp_server.py` and `commands.py`, `ProjectLockedError`,
     `messages/project.py`, `PROJECT_GEOMETRY_CHANGED`, the project names of
     `__all__`, the project builders of `kartograf.testing`, the project tests
     (`tests/unit/test_project_manifest.py`, `tests/integration/test_project_*.py`)
     and the project chapters of USAGE, SCOPE and README. The command
     registry's `project_task` flag and `task_command` go with them; nothing
     outside projects needs them (verify with a grep and the gate).
   - Add `command_for_file(sidecar) -> CommandCall` (KB-6) for the families
     whose `request` rebuilds the call: elevation and imagery by sheet or
     box, LAZ, cutouts, units by TERYT. Refuse with a code for the others:
     land cover and collections chosen by a box (the units behind the box are
     not in the sidecar), CZ collections by a box, and derived `soil hsg`
     (its SoilGrids inputs are not recorded; decision D5).
   - ADR-040 and its spec get "superseded by <new ADR>"; the new ADR records
     the removal and KB-6.

3. **IMGWTools** (1.5 to 2), parallel with step 2.
   - Remove `src/imgwtools/project.py`, the `project` command group, its
     catalog entries (`_TASK_COMMANDS`, `_PROJECT_FUNCTIONS`, the project
     commands), the project types of `store/types.py`, `messages/project.py`,
     the `imgw-project/1` contract schema, the exports, the project builders
     of `imgwtools.testing`, `tests/unit/test_project.py`,
     `tests/unit/test_project_chmi.py`, `tests/contract/test_project_contract.py`
     and the project chapters (versioned-store spec §10.1, ADR-001 and
     ADR-003 D14 to D18 marked superseded where they speak of projects).
   - Keep `content_sha256` and `content_form` in the archive sidecars: they
     are the store's facts that Archiwista matches on.
   - Add the command of a stored archive or series version
     (`command_for_version`), refusing with a code where the metadata does not
     rebuild the call.

4. **Retman** (0.5). Remove the module `imgw_projects` (five files listed
   above), its tests and its rows in README and ARCHITECTURE; re-pin
   Kartograf and IMGWTools at the commits of steps 2 and 3.

5. **Archiwista** (6 to 8), after steps 2 and 3 are pushed.
   - P1, ADR and SPEC. A new ADR supersedes A-ADR-039, A-ADR-040 and the
     project parts of A-ADR-023, A-ADR-032 decision 14 and A-ADR-042; SPEC
     glossary (Project, Project job, Pin, Set), 4.7, 8.4, UC-06, UC-07, UC-10
     and 13; SCOPE. `ProjectActionAdapter` is removed; the source protocol
     gains `command_for_version`.
   - P2, the project file. `archiwista-project/1` (schema, reader, writer,
     lock), discovery by that file instead of the producers' manifests, the
     index tables of projects and pins fed from it, `POST /projects` and
     `archiwista project-init` writing it. Owner and sharing unchanged.
   - P3, pinning. Local pins (from "Stan lokalny", the Katalog and the file
     card, a new "Dodaj do projektu…" there) and pins from the plan window
     ("Dodaj jako zadanie projektu" becomes "Dodaj do projektu", fed by the
     download's `files[]`). Routes, CLI (`archiwista project-pin`,
     `project-unpin`), action-log names.
   - P4, the jobs. `project_verify`, `project_check`, `project_repin` and
     `project_restore` (the former `project_download`) over the producers'
     `check_command`, `run_command` and `command_for_version`.
   - P5, the interface. The project card: area on the map, groups and pins
     with their state, actions, the project's activity from the action log;
     the guide's slide on projects.
   - P6, exports: the former SPEC 8.4 under the project, `pliki.txt` first
     (decision D6).
   - Fix first, as its own commit before P3: the store badge of the
     availability rows never matches real data, because `held_units`
     (`index/queries.py`) filters on the report's survey-work ids while the
     index keeps the sidecar's numeric campaign id
     (`adapter/kartograf/adapter.py:853`); "pobrane" must be right before
     people pin by it.

6. **Release** (Nogat, by the first-release-set plan). A candidate with the
   new heads, the integration run repeated, then the tags, producers first.

## Decisions of the author

Settled on 2026-10-31: the author left them to the session, which took the
recommended option of each.

| ID | Question | Options | Chosen |
|---|---|---|---|
| D1 | Where the project lives | a) `archiwista-project.json` in the project directory, access in the state database; b) everything in the state database | a): it travels with the directory and the share, survives a lost state database, and other tools can read it |
| D2 | Archiwista's releases | a) one release after step 5 holding v0.3, v0.4 and the projects; b) v0.3 and v0.4 separately as decided on 2026-10-29, the project work backported to v0.3 | a): v0.3's project actions (A7, A8, A13) are rewritten by step 5, and v0.4 is built on top of v0.3 |
| D3 | The first release set | a) Kartograf, IMGWTools, Hydrolog and Retman after steps 2 to 4; Archiwista follows in its own session (REL-5.4); b) wait for step 5 | a): the producers' tags no longer wait for Archiwista's largest step |
| D4 | Existing producer manifests | a) none migrated (ECO-020; projects were never released); b) a one-off import into `archiwista-project/1` | a) |
| D5 | Versions whose command cannot be rebuilt | a) pinnable, with "check" and "restore" disabled with the reason; b) not pinnable | a); a later sidecar field recording the inputs of derived data (`soil hsg`) lifts it per family |
| D6 | Exports in this plan | a) `pliki.txt` and `ATRYBUCJE.txt` in P6, the QGIS export later (v1.1); b) the whole SPEC 8.4 in P6 | a) |
| D7 | A project's activity | a) the action log filtered by project; b) also a history file in the project directory | a); b) only if projects must carry their history to another installation |

## Risks

| Risk | Effect | Mitigation |
|---|---|---|
| A pin's store is written by another process, which replaces a current path | the pin still names its version path and `sha256`; nothing changes for it | pins never name current paths |
| Reproducibility without Archiwista is lost: `kartograf project download` no longer exists | a project cannot be rebuilt with the producer's CLI alone | `polecenia.sh` in the export and `archiwista project-restore` |
| The command of a local version may select more or different data than the version (a newer campaign, another height system) | "check" compares unlike things | the check compares by unit and `sha256`, never by count; a mismatch is reported, not re-pinned |
| Steps 2 and 3 land while Archiwista is still on the old pins | Archiwista's build breaks on a re-pin | Archiwista keeps its current pins until step 5 replaces the adapter calls |
| The author's earlier decisions change: MVP projects through the availability result (2026-10-18), Zestaw as a v1.1 notion, v0.3 and v0.4 released separately (2026-10-29) | plans and SCOPE disagree | step 1 and P1 update them; this plan lists them |

## Results

| Step | Repository and branch | Result |
|---|---|---|
| 1 | Nogat, `plan/archiwista-projects` | ECO-054; DEV-19.18 without the `project` example; registry: `archiwista-project/1` added, `kartograf-project/1` and `imgw-project/1` removed with their edges, `command_for_file` and `command_for_version` in the store read APIs; map and AGENTS.md regenerated; first-release set without Archiwista (D3) |
| 2 | Kartograf, `feature/archiwista-projects`, pushed at `8ad55ab6` | `5590bf67` removes projects (ADR-057 supersedes ADR-040; the data-command table `task_command` stays as `kartograf.data_commands.DATA_COMMANDS`, since `validate_command`, `run_command` and `check_command` call every data command through it); `2bbaec9c` fixes a wrapped fact line the removal exposed; `8ad55ab6` adds `command_for_file(sidecar)` (KB-6) with `CommandNotRebuildableError` (`unsupported`, `command_not_rebuildable`) for files chosen by an area, `soil hsg`, reprojected PL WCS cutouts and sidecars without a needed field. Gate green: 8544 passed |
| 3 | IMGWTools, `feature/archiwista-projects`, pushed at `4bf8bb0d` | `79ebec2` removes projects (ADR-008; `content_sha256` and `content_form` stay in the sidecars); `4bf8bb0` adds `command_for_version(version, *, root=None)` for archives, station lists and catalogs, series and PMAXTP, with the registry code `unsupported` added to its error module. Gate green: 2471 passed |
| 4 | Retman, `feature/archiwista-projects`, pushed at `5c3be44` | `668e578` removes the `imgw_projects` module and pins IMGWTools `4bf8bb0d`; `5c3be44` pins Kartograf `8ad55ab6` and removes the nested option path and the `identifier` extractor, which only project tasks used. Gate green: 3162 passed |
| 5 | Archiwista, `feature/archiwista-projects` (from `feature/v0.4-team`) | `0509143` fixes the store badge (survey work, not campaign id); `28bcadb` A-ADR-049 and Archiwista's plan of P2 to P6; P2 `494fc06`, `b5a3b05`, `b439e3a` (the file `archiwista-project/1`, discovery by it alone, index, routes, CLI, views); P6 `8ba6cc0`; P3 `af237cd`, `f1d6790`, `21b4c4c` (pins from the store and from the plan window); P4 `642fbd0` (re-pin of Kartograf `8ad55ab6` and IMGWTools `4bf8bb0d`, `command_for_version`), `84c6b08` (verify, check, re-pin, restore); P5 `937080d`, `d09156b` (activity, the card's actions, the guide); `07f8c71` four defects of a review. Gate at `07f8c71`: 2654 passed, one failure that needs port 8090 free (taken by the author's running instance), pushed. On the author's clarification of 2026-10-31 a group is shown to people as a „Zestaw” (a complete set of input data for one purpose, e.g. one year), and the export became flat: `eksport/<name>/` with one folder per category (`NMT`, `BDOT`, `ORTO`, …) holding copies of the files in their original formats and one `README.txt`, optionally a ZIP (`c2f9cdf`, `3414727`, `04d0378`, `8a117ed`, `7a8dfcd`; A-ADR-049 decision 13, erratum 1). A use case walked through in the real interface with live GUGiK downloads is outside the repository (`archiwista-scenario/SCENARIUSZ.md`) |
