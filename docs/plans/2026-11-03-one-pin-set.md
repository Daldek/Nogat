# Plan: one set of pins, kept by Nogat

Approved: 2026-11-03 (the author: every dependency between projects points
at the same commits and Nogat steers them); the decisions below by
delegated approval.

Requirements: REL-5.3, REL-6.1, REL-6.4, HUB-3.1, HUB-5.2.

## Goal

Every consumer pins each producer at the same commit, the one in Nogat's
current candidate (REL-6.4). Nogat checks the pins, writes them into the
consumers and moves them forward; a session can end with "pin the next
commits" as one command per project.

## Facts (2026-11-03)

- Pins differ: Kartograf `eab8612` (Hydrograf, Archiwista), `dbcfe5b`
  (Retman); Obserwator `71bae77` (Hydrograf), `8cd6844` (Archiwista,
  Retman), `651d4d7` (Hydraulik); Hydrolog `1708a09` (Hydrograf), `2a5ba1a`
  (Hydraulik). Two forms: a PEP 508 direct reference `pkg @ git+URL@<sha>`
  (Archiwista, Retman) and `[tool.uv.sources] pkg = { git = URL, rev =
  "<sha>" }` (Hydrograf, Hydraulik).
- `scripts/ecosystem.py drift` reads both forms from the workspace
  checkouts, which may lag `origin` or sit on another branch (Hydraulik's
  code lives on `feature/sfincs-swmm`).
- REL-6.4 already names `release-sets/candidate-<N>/` with "a README with the
  commit of each member"; no candidate exists yet.

## Decisions

| # | Decision |
|---|---|
| D1 | `release-sets/candidate-1/members.toml` is the source of truth: `[<Project>] commit = "<40 hex>"` for every project that another one pins and every member of REL-6.1. Its `README.md` is generated from it (gate: `--check`). |
| D2 | `ecosystem.py set check` reads each consumer's manifests at its integration ref (`origin/develop`, or the registry's new optional `branch` for a project whose code lives elsewhere, Hydraulik `feature/sfincs-swmm`) and reports every pin of a producer that differs from the set; it fails with `conflict` (exit 4, HUB-4.8) when one differs. It does not run in the gate (it needs the workspace and the network state); it runs before every merge that changes a pin. |
| D3 | `ecosystem.py set apply --project P [--path DIR]` rewrites P's pins in place to the set's commits, both forms, full 40-hex SHAs, nothing else; then the consumer runs `uv lock` and its gate. |
| D4 | `ecosystem.py set bump P [--rev REF]` sets P's commit to `REF` (default: `origin/develop` of P's checkout, after `git fetch`) as a full SHA and regenerates the README. A bump is committed to Nogat `develop` before consumers apply it. |
| D5 | Hydrograf is included: the author's instruction covers every dependency; moving its pins (and the import rename `imgwtools` → `obserwator`) is admitted under its freeze as the API break of a producer. Production keeps the deployed image until the author redeploys. |
| D6 | Out of scope now: the set's `pyproject.toml` and universal `uv.lock` of REL-6.1 and `verify-candidate` (REL-6.5); Hydrograf's `affine<3` still separates it from Archiwista. |

## Steps

| # | Change | Verified by |
|---|---|---|
| 1 | Nogat: D1–D4 in `scripts/ecosystem.py` with tests; HUB/REL text; candidate-1 at the heads of `origin/develop` (Kartograf, Obserwator, Hydrolog) | Nogat gate |
| 2 | each consumer: `set apply`, `uv lock`, code follow-ups, its gate | `set check` exit 0 (`conflict`, exit 4, while a pin differs) |
| 3 | Retman: knows every tool at the set's commits and runs their basic functions | Retman's tests and a live smoke |

## Results

- Step 1 (2026-11-03, branch `feature/pin-set`, gate OK): HUB-4.9 and
  REL-6.4; candidate-1 is Kartograf `9deaa31`, Obserwator `ea158dc`, Hydrolog
  `38855a1`. `set check` then: Retman's Kartograf pin matches; Hydrograf (3),
  Hydraulik (2), Retman (Obserwator) and Archiwista (2) differ; Hydraulik
  does not declare Kartograf (it calls its CLI).
- Step 2 (2026-11-03/04): every consumer applies candidate-1 (Hydrograf
  `e1b06dd`, Hydraulik `51204b8`, Retman `30691e6`, Archiwista `e479219`);
  Hydrolog moved to `2eb8bd0` by `set bump`; `set check` exit 0, with
  Hydraulik's Kartograf "not declared" (it calls the CLI).
- Step 3 (2026-11-04): Retman offers every basic route of Kartograf,
  Obserwator and Hydrolog (38 operations, Hydrolog edge active in the
  registry); a smoke of all of them with the real tools at the set's commits
  planned 43 cases, ran 41, skipped 2 large downloads, none failed.

### candidate-2 (2026-11-10)

`set bump` of each member at its `origin/develop` after a fetch (Nogat branch
`chore/candidate-2`); `candidate-1` stays as it was. Retman is recorded too:
the set holds each member (D1, REL-6.4), and the members of the first release
set are Kartograf, Obserwator, Hydrolog and Retman (decision D3 of
`2026-10-31-archiwista-projects.md`; Archiwista follows in its own session).
Like candidate-1 it has no `pyproject.toml` or `uv.lock` (D6), and
`verify-candidate` does not exist yet (REL-6.5, ADOPTION_PLAN 5.2).

| Member | Commit | Date | Since candidate-1 (first-parent / all commits) |
|---|---|---|---|
| Kartograf | `d0990c89da88e73b9081fe33a151ba9d27b4f820` | 2026-11-10 | `9deaa31`: 9 / 27 |
| Obserwator | `f9f4ee7927ba520d3e82d3e289872090ae24e2ec` | 2026-11-10 | `1ee5457`: 4 / 8 |
| Hydrolog | `3b84db6ec7e45c2b2f25c67e2ea20c51f7f54169` | 2026-11-10 | `1ffcd6b`: 24 / 86 |
| Retman | `a9c04ad933555d442fe1bf8cf082bf7b5bf1b0cc` | 2026-11-10 | new member |

The consumers that are not members, the same day: Hydrograf `develop`
`894810c0`, Hydraulik `feature/sfincs-swmm` `d467f763`, Archiwista `develop`
`0d1907fe`. `set check` then: `conflict` (exit 4) in Archiwista, Hydraulik,
Hydrograf, Hydrolog and Retman, each still on candidate-1's commits except
Hydrograf's Hydrolog; every pinned commit is on its producer's `develop`, and
each lock file holds the commit its manifest pins.

| Consumer | Producer | Pinned (date) | Behind the set (first-parent / all) |
|---|---|---|---|
| Hydrolog | Obserwator | `1ee5457` (2026-11-04) | 4 / 8 |
| Hydrograf | Kartograf | `9deaa31` (2026-11-03) | 9 / 27 |
| Hydrograf | Obserwator | `1ee5457` | 4 / 8 |
| Hydrograf | Hydrolog | `4fad769` (2026-11-09) | 3 / 7 |
| Hydraulik | Obserwator | `1ee5457` | 4 / 8 |
| Hydraulik | Hydrolog | `1ffcd6b` (2026-11-05) | 24 / 86 |
| Hydraulik | Kartograf | not declared (calls the CLI) | — |
| Retman | Kartograf | `9deaa31` | 9 / 27 |
| Retman | Obserwator | `1ee5457` | 4 / 8 |
| Retman | Hydrolog | `1ffcd6b` | 24 / 86 |
| Archiwista | Kartograf | `9deaa31` | 9 / 27 |
| Archiwista | Obserwator | `1ee5457` | 4 / 8 |

Moving them, each consumer in its own session (DEV-3.4): `set apply
--project P`, `uv lock`, its gate, the merge into its integration branch.
`set apply` on copies of the five manifests rewrote exactly these pins.

1. Hydrolog first, then `set bump Hydrolog`. uv reads the
   `[tool.uv.sources]` of a git dependency, so Hydrolog's own Obserwator pin
   travels with its extras `pmaxtp`, `gui` and `all`: a throwaway lock of the
   four members (uv 0.13.0, Linux, macOS and Windows) fails on conflicting
   Obserwator URLs with `hydrolog[all]` at `3b84db6` and Obserwator `f9f4ee7`,
   resolves 80 packages with Obserwator at `1ee5457`, and 73 without
   Hydrolog's extras. No consumer asks for those extras today.
2. Hydrograf, Retman and Hydraulik then take the set's Hydrolog; Archiwista,
   which pins no Hydrolog, at any time. Hydrograf follows its own rules for
   pins and production (D5); the HSG of the least permeable layer, open in
   its `docs/PROGRESS.md`, needs the new Kartograf. Archiwista's gate takes
   about an hour.
3. `set bump Retman` after Retman's merge, then `set check` exit 0.

What the gates meet in the lag, by the producers' CHANGELOGs:

- Obserwator: CHANGELOG wording and the text of the MCP agent guide; no API
  change.
- Kartograf: `soil hsg --depth-rule least-permeable` (its ADR-061;
  `--depth` is no longer `required` in the catalog, one of the group
  `depth`), NMT/NMPT sheets whose cell size differs from their index refused
  as `ResolutionMismatchError` (`data_error`, exit 7, its ADR-060), PGW data
  in `hydro download --product pgw` (its ADR-059) with `kartograf.testing`
  builders, size probes without a content coding.
- Hydrolog after `1ffcd6b` (Retman, Hydraulik): **Breaking** values, the CN
  of `water` is 98, not 100; `stats flood-frequency` fits by `l_moments` by
  default, not `mle`; new `stats homogeneity`, `--fit-method`, TR-55 rows,
  the series hand-off. After `4fad769` (Hydrograf): the descriptions of
  `residential_low` and `residential_medium` only.
- Comments that name candidate-1 (Hydrolog's and Retman's `pyproject.toml`)
  and the consumers' integration documents follow in the same sessions.
