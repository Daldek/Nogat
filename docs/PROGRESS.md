# Progress

Audited on 2026-10-28: local branches, worktrees, recent commits, manifests,
project progress documents and `git ls-remote --heads --tags origin` (tags
checked for Nogat). No tests or gates were run; earlier gate results below
are historical evidence, not verification of the current heads.

## Status

| Component | State | Note |
|---|---|---|
| Standard 2.1 | in progress | not yet published to `main`; tagged `std-2.1` when it is (HUB-6.1) |
| Registry and schema | done | `ecosystem.yaml`, `schemas/ecosystem.schema.json`; follows the branches of Kartograf, IMGWTools, Hydrolog and Hydraulik since 2026-10-25 (CHANGELOG); `routes` name the commands of those branches, of Retman and of Archiwista |
| `validate`, `map`, `agents`, `deps`, `drift` | done | `scripts/ecosystem.py`, errors by the registry (HUB-4.8) |
| Hub gate and CI | done | `scripts/gate.sh` on `uv.lock`, tests in `tests/` |
| Standard checks | done | `uv run scripts/ecosystem.py standard`, in the gate |
| Contradictions in standard 2.1 | done | ECO-042 to ECO-049 and consistency fixes |
| Canonical agent-interface schemas | done | `schemas/agent/`, contract tests (ECO-050) |
| Data-output convention (ECO-051) | done in Nogat | DEV §19 and AGI-3.4 and related rules, store markers in the registry, plan `docs/plans/2026-10-24-data-output.md` with the state of every project (Results, 2026-10-25) |
| Integration dry run | done 2026-10-25 | historical baseline: six heads, four cross-tool flows and eight failures with owners (`docs/plans/2026-10-25-integration-dry-run.md`). The later final integration plan records the fixes and the pending post-fix repeat |
| Final integration run | initial run done 2026-10-25; repeat pending | F1 to F8 have owners and fixing commits; all but F6 (the author's history rewrite) are fixed and pushed (`docs/plans/2026-10-25-final-integration.md`, Fixes). Retman, Hydraulik, Hydrograf and Archiwista are re-pinned and pushed, with their gates recorded (Next 3 of that plan). Hydrograf (`affine<3` until pyflwdir 0.5.13, its ADR-062) and Archiwista (`affine>=3`) remain incompatible in one environment; the repeat must run them apart |
| Generated `AGENTS.md` (HUB-4.3) | done | `uv run scripts/ecosystem.py agents` from the `routes` of the registry (HUB-2.9, ECO-052), `agents --check` in the gate; the guide links name `main`, so they resolve once each project is merged there (IMGWTools after the rename of `master`) |
| `nogat` package (HUB §7) | planned | |
| Adoption in the projects | in progress | current branch evidence is listed below; the 2026-10-25 adoption and data-output snapshots are historical, not current waiting lists. The post-fix integration repeat and first release set remain open |

### Project evidence on 2026-10-28

Heads below were compared with `origin`; a topic branch being published does
not mean it is merged or released. Sources are each branch's
`docs/PROGRESS.md`, recent commits and dependency manifests.

| Project | Audited branch and head | Progress and remaining work |
|---|---|---|
| Nogat | `feature/data-output`, `2ccea34` before this audit | Latest commit adds the GUI visual-identity backlog. Standard 2.1 remains off `main`; `origin` has no tags. Contribution files and v1 template replacement remain open |
| Kartograf | `feature/data-output`, `745e8b18` | Plain mode is implemented at library and command-layer level; its own Next 4 still leaves a real-CLI subprocess smoke and plain-mode prose open. Later commits add `store_state`, shared task arguments for `project add`, project-lock reasons, report-cache reuse and PL-2000 sheet outlines. Message-catalog migration is closed; `kartograf mcp` and domain JSON Schemas remain open |
| IMGWTools | `feature/data-output`, `e28fbcd` | Data-output migration, MCP stdout fix, `parse_command`/`format_command` and catalog examples are recorded as done. Live plain-mode smoke, English documentation and release work remain open |
| Hydrolog | `feature/routing-schematic`, `5fa22b3` (routing worktree) | `hydrolog.testing` exists (introduced at `0719c41`); network objects, rainfall/runoff and SVG schematics are implemented on stacked routing branches. The main checkout remains at `chore/nogat-2.1`, `d4f7282`; inspecting that checkout alone misses this work. Merge, CLA, notebook translations and release remain open |
| Retman | `feature/kartograf-data-output`, `cc6d1ee` | Both producer migrations are done on the branch. Manifest pins Kartograf `c31ca04c` and IMGWTools `6bd35a4`, not their latest heads. The Status table's older pins and “nothing is pushed” statement are stale; Next 2 has the matching pins. Documentation translations and the evaluation on the 630-command set remain open |
| Archiwista | `feature/kartograf-data-output`, `b7775bb`; `feature/v0.4-team`, `815c8b2`; `feature/v0.4-review`, `8118c33` | Data output, English documentation and the message catalog are done on the branches. v0.3 actions and station comparison (I8, `b7775bb`) progressed beyond the integration baseline. The data-output manifest now pins Kartograf `745e8b18`, but IMGWTools stays at `6bd35a4`. v0.4 team/shared/review work is separate; D7 refusal/sign-in auditing is done at `815c8b2`, not the whole security checklist or T12 |
| Hydrograf | `feature/producer-heads`, `9dfa3a8` | Producer migrations, quality tooling and contribution files are implemented; CLA, translation/REST gaps and history work remain open. Pins remain Kartograf `c31ca04c`, IMGWTools `6bd35a4`, Hydrolog `5fa22b3`; `affine<3` is retained. The checkout is on older `feature/kartograf-wykorzystanie`, `bc0b438`; the running Docker image is not evidence of the newer branch being deployed |
| Hydraulik | `feature/sfincs-swmm`, `91559e0` | Extracted SFINCS/SWMM implementation and Hydrolog hand-off are committed; pins are Hydrolog `5fa22b3` and IMGWTools `6bd35a4`. Contract tests using `hydrolog.testing` are present, not run in this audit. The old claim that Kartograf has no plain mode is stale; the live terrain flow still needs verification. The older uncommitted PoC and documents stay local by the author's choice in this audit |

DEV-10.6 follow-up: `hydrolog.testing` is no longer missing, but the Nogat
registry still lacks `hydrolog-testing` and its file-exchange edges.
`kartograf.testing` already builds a GeoTIFF as part of its fixture store;
`imgwtools.testing` exports store fixtures, not a dedicated PMAXTP builder.
Do not treat the remaining file-contract work as uniformly absent or done.

### Changes on 2026-10-29 and 2026-10-30

These rows supersede the Archiwista and Hydrograf rows above where they
differ. Gate results named here were run in this session.

| Project | Branch and head | Change |
|---|---|---|
| Archiwista | `feature/v0.4-team`, `df7e71e`, pushed | Plan v0.4 complete: T12 (three-person acceptance, every C9 route called by each role against the matrix, ASVS checklist, LAN runbook) and review defects D6 and D10. Full gate green on `54cded3` (2556 passed, coverage 93.53%) after four fixes it found (`c8d4b5e`, `bbe223d`, `96ddda8`, `54cded3`; the last a real Esc race in the web shell). Decided by the author's delegated approval: the five checklist deviations are accepted for LAN use; v0.3 and v0.4 are released separately, v0.3 first, after the first release set. Open: the author's three-computer run of the runbook. Git: `feature/v0.4-review` and `feature/v0.4-shared` deleted locally (both contained in `v0.4-team`, still on `origin`), their worktree removed, every branch tracks its own `origin` branch, `feat/mockup` pushed as a backup |
| Hydrograf | `feature/logowanie-testow`, `1d81694`, pushed | Request logging and rotation, nginx bound to loopback, the tester guide; the test service runs this branch (Kartograf 0.7.0, IMGWTools 2.1.0, Hydrolog 0.6.3), not `feature/producer-heads`. Merging it into `producer-heads` conflicts in `README.md`, `backend/api/main.py`, `docs/CHANGELOG.md` and `docs/PROGRESS.md`. A Kaczawa bootstrap (183M cells) was OOM-killed twice; a smaller area (66M cells) succeeded and is served. Memory plan F1–F7 (~19 GB → ~9 GB, results identical) and clipping of shown data to the analysis boundary (high priority) are backlog items in its `docs/PROGRESS.md` and `docs/TECHNICAL_DEBT.md`. Before its first push the branch history (`develop..`) was rewritten to replace a share path and a LAN address with placeholders |

Git hygiene audit (2026-10-29, after `git fetch`): Hydraulik has uncommitted
documents on `develop` and an unpushed PoC worktree branch; IMGWTools has two
stashes (one is REST C5 work in progress) and `fix/archiwista-compat`, most
likely superseded by `fix/archiwista-compat-2`; Hydrolog's
`feature/v1-catalog-mcp-hsg` is merged and can be deleted; local
`backup/*` branches in Hydrograf and IMGWTools have no `origin` copy.

## Next

1. Close the remaining data-output documentation and CLI smoke in Kartograf,
   the live plain-mode smoke in IMGWTools, and the file-contract/registry
   follow-ups above (each project in its own session, DEV-3.4).
   Reconcile consumers' stale progress text with their manifests; newer
   producer commits do not automatically replace reviewed pins. Prepare
   the first release set only after the remaining integration work.
   When a tool renames a command, change its `routes` and run `agents`
   (CLAUDE.md).
2. Repeat the final integration run at explicitly recorded heads, including
   the changes after 2026-10-25 in Kartograf, IMGWTools and Archiwista,
   with Hydrograf and Archiwista apart and the two flows of F2. Record the
   outcome in the data-output plan; no repeat was performed in this audit.
3. Publish 2.1 to `main` with the author (ADOPTION_PLAN 0.3, 0.4).
4. Prepare a coherent visual identity for Hydrograf, Archiwista and every
   other ecosystem tool that has or will have a GUI (user request, 2026-10-28).
   Define shared visual guidelines and reusable design assets, with room for
   each tool's identity. Backlog only: on 2026-10-29 no design work existed in
   any repository or on this machine; start with a plan in `docs/plans/`
   linked to `2026-10-20-unified-gui.md`.
5. Archiwista's release (decision D2 of the projects plan, 2026-10-31,
   replacing the separate v0.3 and v0.4 of 2026-10-29): one release holding
   v0.3, v0.4 and the projects, after step 5 of that plan, outside the first
   release set (D3, REL-5.4).
6. Projects move to Archiwista (ECO-054): plan
   `docs/plans/2026-10-31-archiwista-projects.md`, approved 2026-10-31 with
   D1 to D7 as recommended; steps 1 to 5 are done and pushed on
   `feature/archiwista-projects` in Kartograf, IMGWTools, Retman and
   Archiwista (the plan's Results). Open: the release (step 6); the branches
   are not merged. Follow-ups seen on the way: Kartograf's LAZ sidecars carry
   no survey work, so Archiwista's "pobrane" badge never matches LAZ (a
   `request` issue for Kartograf, not filed: no `gh` on this machine);
   Archiwista's "U źródła" offers only nmt, nmpt and laz, so BDOT10k and
   orthophoto are downloaded by pasting a Kartograf command; Archiwista's
   `test_doctor_refused_store_shows_the_fix_the_producer_gave` fails while
   port 8090 is taken (the test is not hermetic).

## Open questions

- F6 of the final integration run remains open: the author owns the history
  rewrite of Hydrograf's `develop` and IMGWTools. The recorded Hydrograf gate
  uses `GATE_COMMIT_RANGE=develop..HEAD`; IMGWTools' commit step checks only
  one commit. Passing gates do not close this item.
- Hydrograf must lift its `affine<3` cap when pyflwdir 0.5.13 permits it
  (ADR-062); until then keep it and Archiwista in separate environments.
- Hydraulik's code is committed on `feature/sfincs-swmm` (worktree
  `Hydraulik-sfincs`, not merged), and its registry entry lists that branch's
  `pyproject.toml`, which the `Hydraulik` checkout on `develop` lacks until the
  merge (`deps` notes it). Keep `status: research` until the author merges the
  branch and settles the proof of concept, or mark it `active` now?
- The Hydraulik entry has no data source, because the branch has no
  OpenStreetMap access (its roads come from BDOT10k), but its README still
  names OpenStreetMap and ODbL in the data and licensing paragraph: which is
  right?
- Publishing 2.1 to `main` (and its tag) and replacing the v1 `templates/`
  and `configs/` (root-owned files).
- The plans in `docs/plans/` predate DEV-17.4's `Approved:` line: add it to
  the ones the author approved.
- Contribution files (`SECURITY.md`, `CONTRIBUTING.md`, `docs/CLA.md`,
  `CONTRIBUTORS.md`, DEV-13.7, DEV-16.2) are listed under Deviations in
  `CLAUDE.md`, but they are a gap, not a deliberate deviation: move the entry
  here (ADOPTION_PLAN 0.6), or adapt Archiwista's files and write
  `SECURITY.md` (CLA text needs the author's approval; private vulnerability
  reporting is a GitHub setting)?
- Merge order into `develop`: `fix/hub-gaps` first, then `feature/data-output`
  (cut from `fix/hub-gaps`); `develop` lacks the 2.1 fixes, the standard
  checks and this file. Both merges need the author's approval (DEV-3.3).
