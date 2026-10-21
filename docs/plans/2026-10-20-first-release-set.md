# Plan: first release set

Status: proposed. Requirements: REL §6, REL-2.1, REL-5.3, HUB-5.2, ECO-025,
ECO-037. Details phase 5 of the
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

Option B. The members (REL-6.1) are Kartograf, IMGWTools, Hydrolog, Retman and
Archiwista. Hydrograf is an app without a package and Hydraulik is research;
they follow in their own sessions (REL-5.4). Version numbers are written in
the release pull requests (REL-2.1), after a candidate passed; this plan names
none.

## Steps

1. **Start clean.** Adoption phases 1 to 4 are done, and every member's tree
   is clean with its branches pushed. A candidate built earlier finds problems
   early but is never released: the history rewrite changes its commits.
2. **Migrate consumers against producer heads**, each in its own session and
   repository (DEV-3.4). A member that cannot run on a producer's development
   head migrates on a topic branch whose pull request pins the producer's
   commit (REL-5.3) and passes the member's own CI. Retman and Archiwista need
   no code change; the candidate overrides their pins.
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
   `uv tool install git+https://github.com/Daldek/Nogat@vX.Y.Z` (HUB-7.1).
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

Candidates: none yet.
