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
