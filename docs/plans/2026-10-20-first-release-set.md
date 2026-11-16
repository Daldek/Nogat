# Plan: first release set

Approved: 2026-11-16 (the author: build the candidate's `pyproject.toml`, its
`uv.lock` and `verify-candidate`, then run the integration run; the first
`nogat` release is `0.1.0`, ECO-076). Requirements: REL §6, REL-2.1,
REL-5.3, HUB-5.2, ECO-025, ECO-037. Details phase 5 of the
[adoption plan](../../standards/ADOPTION_PLAN.md).

## Goal

Release the ecosystem tools as one tested combination, the first `nogat`
release. Nothing is tagged until a candidate has passed `verify-candidate` on
the three CI runners.

## Options

| Option | Verdict |
|---|---|
| A. Tag each member when it is ready; publish `nogat` from the latest tags | Rejected: the combination is never tested and third-party versions keep drifting (ECO-025) |
| B. Verify a candidate built from the members' development heads, then release the members and `nogat` | Chosen (ECO-037) |
| C. Pin exact third-party versions in every member | Rejected: unsolvable environments for library users (ECO-025, REL-5.2) |
| D. Verify by hand on the author's machines | Rejected: hand-written records, while the CI runners are the same three platforms (ECO-037) |

## Decision

Option B. The members (REL-6.1) are Kartograf, IMGWTools, Hydrolog and
Retman. Archiwista left the set on 2026-10-31 (ECO-054, decision D3 of the
[projects plan](2026-10-31-archiwista-projects.md)): the producers' tags do
not wait for its project work, and it follows in its own session like
Hydrograf, an app without a package, and Hydraulik, research (REL-5.4).
Version numbers are written in the release pull requests (REL-2.1), after a
candidate passed; this plan names none.

Superseded on 2026-11-15 by ECO-074: the author names the members, and the
first set is Kartograf, Hydrograf, Hydrolog, Obserwator and Archiwista;
Retman and Hydraulik join a later set.

## Steps

1. **Start clean.** Adoption phases 1 to 4 are done, and every member's tree
   is clean with its branches pushed. A candidate built earlier finds problems
   early but is never released: the history rewrite changes its commits.
2. **Migrate consumers against producer heads**, each in its own session and
   repository (DEV-3.4). A member that cannot run on a producer's development
   head migrates on a topic branch whose pull request pins the producer's
   commit (REL-5.3) and passes the member's own CI. Retman drops its
   IMGWTools project module (projects plan, step 4); the candidate overrides
   its pins.
3. **Build the candidate** on a topic branch of Nogat:
   `release-sets/candidate-<N>/` with a `pyproject.toml` installing every
   member at its commit (pins between members overridden, test dependencies of
   all members in a `dev` group), a `uv.lock` universal for Linux, macOS and
   Windows (`[tool.uv] environments`), and a README with each member's commit.
4. **Verify** with `verify-candidate` (REL-6.5), dispatched against the
   candidate branch; the workflow file is on `main`, because GitHub runs
   `workflow_dispatch` only for workflows on the default branch. The run URL
   goes into the README. The author MAY add runs on their own machines for
   what CI cannot test, such as network shares.
5. **Fix and repeat.** A failure is fixed in its member (own session, branch,
   pull request into `develop`); the next candidate records the new commits
   and reruns the workflow.
6. **Release the members** (REL-2.1, REL-6.6), producers first, in the
   dependency order of `ecosystem.yaml`: for each, the release pull request,
   the pull request `develop` → `main` and the author's tag. Between the
   passing candidate and the tag only the release pull request is merged into
   the member's `develop`; any other merge means a new candidate. The author
   confirms the version numbers in the release pull requests.
7. **Release `nogat`** (REL-6.6, HUB-7.2) after every member has its tag: its
   release pull request puts the candidate's set in place with each member's
   commit replaced by its tag and the dependency list regenerated from the
   lock; then `develop` → `main` and the author's tag. The candidate branch is
   deleted. Users install with
   `uv tool install git+https://github.com/Daldek/Nogat@vX.Y.Z` (HUB-7.1)
   once the `nogat` package exists; `v0.1.0` is released without it
   (Results).
8. **Upgrade the consumers outside the set** in their own sessions (REL-5.4).
   Hydrograf pins the new tags. On 2026-10-20 Kartograf's development head no
   longer exports `LandCoverManager` and `HSGCalculator`; the Kartograf
   CHANGELOG gives the replacements (`download_landcover`, `check_landcover`,
   `download_soil`, `calculate_hsg`, `hsg_statistics`). Files to change:
   `backend/core/cn_calculator.py`, `backend/scripts/download_landcover.py`,
   `backend/scripts/bootstrap.py`. The Hydrolog and IMGWTools heads keep the
   symbols Hydrograf imports.

## Results

Baseline, 2026-10-20 (`uv run scripts/ecosystem.py deps --installed`): 18
packages are declared by two or more projects with no conflicting ranges. The
environments mix two Python minor versions, 59 packages differ between them
(majors included) and only two projects have a lock file. One environment
built from all checkouts resolves on Linux (188 packages with Hydraulik, 117
without), so no third-party conflict blocks a candidate.

| Project | State on 2026-10-20 |
|---|---|
| Kartograf | `develop`; one commit not pushed |
| IMGWTools | `fix/archiwista-compat-2`, four commits beyond `slave`; one stash |
| Hydrolog | `develop`; catalog, MCP and HSG merged |
| Retman | `develop`; Kartograf and IMGWTools pinned by commit |
| Archiwista | `develop`; Kartograf installed editable |
| Hydrograf | pins release tags older than the heads of Kartograf, Hydrolog and IMGWTools; does not run on Kartograf `develop` |
| Hydraulik | uncommitted proof of concept |

Candidates: candidate-1 to candidate-4 held members' commits only (the pins
plan, `2026-11-03-one-pin-set.md`). candidate-5 (2026-11-16) is the first
with step 3: its `pyproject.toml` installs Kartograf `[mcp]`, Obserwator
`[full]`, Hydrolog `[all]` and Archiwista `[obserwator]` at the set's commits
with the union of their `dev` groups, and its `uv.lock` resolves 127 packages
for the three platforms, one version each. The pins between members equal
the set's commits (`set check`), so none is overridden. Hydrograf, an app,
is verified on its own lock (ECO-077). Step 4's workflow is
`.github/workflows/verify-candidate.yml`, which runs `set verify`; it can
be dispatched once it is on `main`. The local run of the same command, the
members' own gates and the flows are in
[the integration run of candidate-5](2026-11-16-candidate-5-integration.md).

Members' releases (step 6, 2026-11-16), producers first, from candidate-6:
Kartograf `v0.8.0`, Obserwator `v3.0.0`, Hydrolog `v0.8.0`, Hydrograf
`v0.5.0` and Archiwista `v0.3.0`, each an annotated tag on the merge commit
of its `main`; the release commits and gates are in
[the integration run of candidate-5](2026-11-16-candidate-5-integration.md),
„candidate-6 and the releases”. With the author's approval the merges ran
locally without pull requests (`gh` is not installed), and candidate-6 was
verified only on this machine by `set verify`, not by the workflow
(REL-6.5 deviation).

Nogat's release (step 7, 2026-11-17): `v0.1.0`. Its release commit
`78e0149` sets `0.1.0` and adds `release-sets/v0.1.0/`, candidate-6 with
each member's commit replaced by its tag (the same 127 packages);
`develop` → `main` is merged locally without a pull request, with the
author's approval, and the merge commit carries the tags `v0.1.0` and
`std-1.0`. The `nogat` package (HUB §7, ADOPTION_PLAN 5.4) does not exist
yet, so the set has no generated dependency list and no `uv tool install`:
it is installed as an environment, `uv sync --locked --no-dev` in
`release-sets/v0.1.0/`. The workflow `verify-candidate` is on `main` from
this release and verifies the next candidate. The topic branches
`chore/candidate-6` and `feature/verify-candidate` are merged into
`develop`; deleting them is the author's.
