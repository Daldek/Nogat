# Plan: integration dry run at the data-output heads

Status: done 2026-10-25. A dry run: no candidate exists, and nothing is pinned,
tagged or pushed.

Requirements: ECO-051, DEV-10.6, REL-5.3, REL-6.2, REL-6.4, REL-6.5. Step 7 of
the [data-output plan](2026-10-24-data-output.md), run before its producers are
complete, and a rehearsal of steps 3 and 4 of the
[first release set](2026-10-20-first-release-set.md).

## Goal

Find out, before a candidate exists, whether the members work together at the
heads of their working branches: whether one environment resolves, whether each
member's offline suite passes in it, and whether the flows that cross two tools
run. A failure is fixed in its own project (own session and branch, DEV-3.4),
so each one is listed with its cause and its owner.

## Options

| Option | Verdict |
|---|---|
| A. One environment; each member installed as a wheel from a detached checkout of its branch head; the pins between members overridden; each suite run from its checkout | Chosen: it is what `verify-candidate` does (REL-6.5) |
| B. The live trees, installed editable | Rejected: sessions edit the live trees, so the heads move during the run, and an editable install hides every test that finds its files through the package path |
| C. Each member's own environment from its own lock | Rejected: that is each member's own gate and shows nothing about the combination |

## Decision

Option A. The environment, the checkouts and the output of every run stay
outside every repository and are removed afterwards; nothing is committed
(REL-5.3).

## Steps

1. **Heads.** One `git worktree add --detach` checkout per member, at the head
   its branch had when the run began. Two heads moved while it lasted:
   Kartograf's, by `252d632f` (`--output-dir` in every data command) and a
   commit of documents, and Archiwista's, by a commit that changes only its
   PROGRESS. The first pass ran at Kartograf's older head `4c99f53a`; its
   checkout was then moved to the new head, and Kartograf's suite, Retman's
   suite and the flows of Kartograf were run again. Archiwista's suite was not
   (its failures are `init_project(root=)` and the version, both unchanged), and
   neither was Hydraulik's (it runs a fake Kartograf). The table names the
   heads the results belong to.

   | Project | Branch | Head | Version |
   |---|---|---|---|
   | IMGWTools | `feature/data-output` | `a304521` | 3.0.0 |
   | Kartograf | `feature/data-output` | `40455e5e` (first pass `4c99f53a`) | 0.8.0.dev0 |
   | Hydrolog | `feature/routing-network` | `6c9ba5a` | 1.0.0.dev0 |
   | Retman | `feature/imgwtools-data-output` | `932d2cf` | 0.1.0.dev0 |
   | Archiwista | `chore/nogat-2.1` | `093ea8c` (now `b2ae7ce`, PROGRESS only) | 0.3.0.dev0 |
   | Hydraulik | `feature/sfincs-swmm` | `793002a` | 0.1.0.dev0 |

   During the first pass Kartograf's working tree held uncommitted catalog and
   CLI changes; only committed heads were tested.
2. **Environment.** A throwaway uv project on Python 3.12 with the six members
   as direct dependencies on their checkouts, every extra the gates install
   (`kartograf[mcp]`, `imgwtools` with `api,cli,mcp,pandas,store`,
   `hydrolog[all]`, `hydraulik[all]`), the union of the members' `dev` groups
   as its `dev` group, and a lock universal for Linux, macOS and Windows. The
   pins between members are replaced by the checkouts:

   ```toml
   [tool.uv]
   environments = ["sys_platform == 'linux'", "sys_platform == 'darwin'", "sys_platform == 'win32'"]
   override-dependencies = ["kartograf[mcp]", "imgwtools[api,cli,mcp,pandas,store]", "hydrolog[all]"]

   [tool.uv.sources]
   kartograf = { path = "<checkout>" }   # likewise the other five members
   ```

3. **Suites.** Each member's offline suite, `pytest tests` with the marker
   expression of its own gate (`not live`; for Archiwista `not live and not
   perf and not smb`), run from its checkout with all six members installed
   from the checkouts. The user data, configuration and cache directories
   pointed into the throwaway area, so no suite touched a user directory.
4. **Smoke flows** across two tools. Every flow was run with connections
   refused (a proxy on a closed port), so that none depends on a server, except
   the two plans of Kartograf's plain mode, which ask the real servers
   (read-only requests, nothing is downloaded).

## Results

### Environment

The lock resolves: 138 packages (131 third-party, the six members and the
root), 135 installed on Linux, no third-party conflict. `uv run
scripts/ecosystem.py deps --installed` over the six checkouts lists 40
third-party packages, 16 of them declared by two or more projects, and flags no
conflicting range.

The pins between members do conflict, which is why they are overridden. The
first one uv reports without the overrides is `kartograf`: the checkout against
Archiwista's commit `8e9bcbb`. The IMGWTools pins (a commit in Retman, a tag in
Hydraulik) and the Hydrolog pin (a tag in Hydraulik) are of the same kind.

| Consumer | Producer | Pin overridden |
|---|---|---|
| Retman (`tools` group) | Kartograf | commit `8e9bcbb`, 46 commits behind the head tested, version `0.8.0` |
| Retman (`tools` group) | IMGWTools | commit `a304521`, the head tested |
| Archiwista | Kartograf | commit `8e9bcbb` |
| Hydraulik (`rainfall` extra) | Hydrolog, IMGWTools | tags `v0.7.0`, `v2.1.1` |

A trap for step 3 of the release set: `override-dependencies` replaces every
requirement on the package, extras included, and also the self-reference inside
its own extras (`imgwtools[full]` is declared as `imgwtools[api,cli,mcp,...]`).
An override `imgwtools[full]` made the lock drop all of those extras (125
packages, no `pyarrow`, `typer` or `rich`) without an error. Name the extras in
the override and look for a package of each extra in the lock.

### Suites

| Project | Passed | Failed | Skipped | Not run (`live`) | Note |
|---|---|---|---|---|---|
| IMGWTools | 2330 | 0 | 0 | 80 | |
| Kartograf | 8425 | 4 | 0 | 18 | F4; at `4c99f53a`: 8384 passed, the same 4 failed |
| Hydrolog | 5095 | 0 | 17 | 0 | |
| Hydraulik | 812 | 0 | 1 | 17 | the skip is an empty parameter set |
| Retman | 3036 | 29 | 6 | 7 | F1, F2; the 6 skips are Kartograf checks that F2 hides; at `4c99f53a`: 2983 passed, 82 failed |
| Archiwista | 762 | 179, and 265 errors | 0 | 47 | F2, F3; run with its own `src/` first on the path, as a wheel it stops at collection (F4) |

### Smoke flows

| Flow | Result |
|---|---|
| Hydrolog `route network` to six CSV tables, then Hydraulik `swmm run --check` on `OUT.csv` | Passes. The plan writes `network.inp` and `network.rpt`, applies 299,026.5 m3 as the inflow of the node `J1`, no blocker. Hydrolog's head reproduces the tables Hydraulik recorded for its own fixture network byte for byte (five files). |
| Retman `plan run --check` for IMGW archives, its decisions scripted, the real IMGWTools behind it | Passes. A complete plan of 24 archives; the call Retman builds, `imgw datasets download --dataset pl.imgw.hydro_daily --years 2019,2020 --output-dir <results>`, validates, and the tool's own `--check` lists 24 `write` targets and creates nothing. |
| Hydraulik `terrain download --check` on Kartograf's head | At `4c99f53a`, refused as expected: exit 0 with the blocker `engine_incompatible`, "kartograf 0.8.0.dev0 runs, but `elevation download` has no --output-dir"; `engines check` reported the command unavailable and the live test skipped with the same text (F5). At `40455e5e`, passes: three `write` targets (the elevation GeoTIFF, the BDOT10k package of the county, the soil GeoTIFF), no conflict, no blocker, and `engines check` finds "--output-dir writes plain files". Kartograf's plan asks the real servers, so with connections refused the command fails with `source_unavailable` (exit 5). |
| Archiwista `doctor` with a Kartograf store built by Kartograf's `testing` module and IMGWTools installed beside it; again with an `imgw` store entry | Exit 10 both times. The Kartograf plugin is incompatible (F2); the doctor lists no IMGWTools source, and `imgw` is an unknown setting (F6). |
| `store init` in both producers | Passes. An empty root gets its marker; a root with the layout and no marker is verified and gets it. The sidecars of both fixture stores carry every field of DEV-19.16 except `dataset_key`, which neither stores. |
| IMGWTools writes into a Kartograf store | `-o` inside it: `--check` lists `conflict`, `output_in_store`; the run exits 4 and names every path in `details.paths`. `--root` inside it: the run exits 4, `nested_store`, before any request; `--check` plans the download (F7). |
| Kartograf writes into an IMGWTools store | `--root` inside or at it: `--check` exits 4, `nested_store`. `--output-dir` inside it (`40455e5e`; the CLI had no such option at `4c99f53a`): `--check` lists `conflict`, `output_in_store`, and nothing is written. The runs of either option ask the WFS first, so their refusal was not shown offline. |

### Failures across members

| # | Where it shows | Cause | Owner |
|---|---|---|---|
| F1 | Retman: 29 failures at `40455e5e`, 82 at `4c99f53a`, all in the Kartograf half | The Kartograf half still calls the Kartograf of its pin. At `4c99f53a` its `output_dir=` (for `root=`) was refused in `validate_command`, `run_command`, `check_command` and the command line (56 tests). At `40455e5e` `output_dir` is Kartograf's option for plain files, so the same calls pass validation with another meaning; what they would write was not run. Still failing: `VersionedFile` built without the new `size_bytes` (9); eight tests that compare Kartograf's validation error with `invalid_input` and find `validation_error`; the codes `no_coverage` and `download_failed` for `no_data` and `source_unavailable` (3); and, hidden by F2, six conformance tests that read `kartograf.get_catalog`, removed for `list_commands()` and `command_schema()`. The other nine are F2. | Retman, step 5 of the plan, which waited for Kartograf's `root`; not a defect of the head |
| F2 | Retman: nine tests fail (the version gate, the table of capabilities, three `eval` runs, four README examples), six Kartograf checks are skipped, and every start warns that no Kartograf operation is offered. Archiwista: `doctor` exits 10, and 156 of its 444 failures and errors name the incompatible source or need its pinned coordinate operations | Both consumers accept Kartograf `>=0.8.0,<0.9`. Develop carries `0.8.0.dev0` (REL-1.1), which PEP 440 puts below `0.8.0`, so both refuse the head. Commit `8e9bcbb` still said `0.8.0`, so it went unseen. The 24 Archiwista tests that do not name it pass once the head's version is reported as `0.8.0`, and so do the five Retman tests that failed for no other reason at `4c99f53a`. | Retman (`supported_versions`) and Archiwista (`SUPPORTED_VERSIONS`); the author decides how a consumer range treats an untagged producer (REL-5.3) |
| F3 | Archiwista: 288 of the 444, almost all errors in fixtures | `tests/fixtures/make_store.py` calls Kartograf's `init_project(output_dir=...)` and the contract test pins the `output_dir` of `list_segments`, `list_partitions` and `iter_store`; all are `root` now | Archiwista, step 4, not started |
| F4 | Kartograf: 4 tests of `test_version.py`, at both heads. Archiwista: `test_package_data.py` fails at collection and stops the whole run | Both find the repository through the path of the installed package. That works in an editable install and not in a wheel, which is how REL-2.3 and REL-6.5 install a member. The four Kartograf tests pass when it is imported from its checkout (17 of 17 in the file, checked at `4c99f53a`). | Kartograf, Archiwista; or the author decides that `verify-candidate` installs the member under test editable |
| F5 | Hydraulik `terrain download`; no plain mode on Kartograf's CLI at `4c99f53a` | The catalog of that head had `--root` and no `--output-dir`; the option group was uncommitted in its working tree (step 2). Hydraulik refused correctly (its ADR-0006). `252d632f` fixed it: at `40455e5e` the catalog has `output_dir` (`path_role: output`) and `root` in one group, and the flow passes. | Kartograf, step 2 (done for the CLI) |
| F6 | Archiwista `doctor` | Archiwista has no IMGWTools source yet: its branch `feature/imgw-source` holds plans and the sidecar core and no adapter, so the `imgw` store entry of SPEC 5.5 is unknown and "both producers" cannot be run | Archiwista |
| F7 | IMGWTools `datasets download --root` | `--check` plans a download into a root inside another store, and only the run refuses (`nested_store`). Plain mode refuses in both. | IMGWTools, minor |
| F8 | DEV-10.6 | Only Retman's IMGWTools half builds its stores with a producer's `testing` module. Archiwista writes Kartograf stores by hand, Retman's Kartograf half and Hydraulik use no `testing` module of Kartograf (Hydraulik runs a fake program), and Hydrolog has no `hydrolog.testing` | Archiwista, Retman, Hydraulik, Hydrolog |

What crosses a boundary and passes: IMGWTools with Retman's IMGWTools half
(all its tests), Hydrolog's tables with Hydraulik (byte for byte), the heads of
Hydrolog and IMGWTools behind Hydraulik's `rainfall` extra (all its tests), and
the markers and the nested-store refusals of both producers.

### What the run does not show

- Kartograf's plain mode against the real servers beyond its plans: nothing was
  downloaded.
- Anything on macOS or Windows (the lock resolves for them, nothing ran there)
  or on Python 3.13.
- A run against the real servers: IMGWTools has no `live` test of plain mode.
- Retman with a real model server; its decisions were scripted.
- Timing-sensitive Archiwista tests: other sessions kept the load average above
  10 while it ran.

## Next

1. The failures fall into two groups, each for its own session: Retman step 5
   and Archiwista step 4 (F1, F3), which the plan orders after Kartograf's
   step 2, and whose size this run measured (29 tests in Retman, 288 in
   Archiwista); a decision on consumer ranges and on how `verify-candidate`
   installs a member (F2, F4). F5 is closed by Kartograf's `252d632f`.
2. Repeat the run when Kartograf's step 2 is complete and record it in the
   Results of the data-output plan: that is the integration check of step 7.
