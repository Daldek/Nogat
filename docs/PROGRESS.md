# Progress

Audited on 2026-11-14 against Nogat's `develop` (`6e4e71b`) and the `origin/develop` of the
projects after `git fetch`; release-set pins by `set check`. History is the git log, the
CHANGELOG and each plan's Results (DOC-6.1). IMGWTools is called Obserwator from v3.0.0
(ECO-057); its local checkout may still be the directory `IMGWTools`.

## Status

| Component | State | Note |
|---|---|---|
| Standard 1.0 | in progress | not yet published to `main`; tagged `std-1.0` when it is (HUB-6.1); the drafts called 2.0 and 2.1 on `develop` are 1.0 (ECO-056) |
| Registry and schema | done | `ecosystem.yaml`, `schemas/ecosystem.schema.json`; `routes` name the commands of every tool's integration branch (HUB-2.9) |
| `validate`, `map`, `agents`, `deps`, `drift`, `standard`, `set` | done | `scripts/ecosystem.py`, errors by the registry (HUB-4.8); `drift` also reports the projects' copies of the schemas, the error registry, `nogat_logging.py`, the tokens, the marks and the kit (HUB-4.1, DEV-15.6) |
| Hub gate and CI | done | `scripts/gate.sh` on `uv.lock`, tests in `tests/` (unit, integration, contract, browser) |
| Canonical agent-interface schemas | done | `schemas/agent/`, contract tests (ECO-050) |
| Hand-off schema `nogat-handoff/1` | done | `schemas/exchange/handoff-1.schema.json`, with `node_provenance` (2026-11-10) and the optional `attribution` and `terms_notice` (ECO-060) |
| Data-output convention (ECO-051) | done in Nogat | DEV §19, AGI-3.4; plan `docs/plans/2026-10-24-data-output.md` |
| Generated `AGENTS.md` (HUB-4.3) | done | from the `routes` of the registry, `agents --check` in the gate; the guide links name `main`, so they resolve once each project is merged there |
| Visual identity and GUI kit (DEV §15) | done in Nogat | `design/`: tokens, marks, specimen, mockups; kit 0.7.0 (app menu, sources strip, hand-off, regulamin, admin panel); Hydrograf, Hydrolog, Obserwator and Archiwista ship a copy of the kit |
| Provider attribution and regulamin (DEV §20, ECO-060 to ECO-065, ECO-068) | done | regulamin 1.0, corrected in place (kit 0.6.2), republished 2026-11-14 (`terms_effective` 2026-11-14) by Hydrograf, Hydrolog and Obserwator; one `<nogat-sources>` strip per view in the four GUIs; plans `2026-11-13-provider-attribution.md`, `2026-11-13-gui-terms.md` (its „For the author” items), `2026-11-13-compact-attribution.md`, `2026-11-13-terms-fix.md` |
| Unified logging (DEV-12.4 to DEV-12.9, ECO-066) | in progress | Nogat, Hydrograf, Hydrolog and Obserwator (GUI, REST server) merged; Archiwista (step 6) open; plan `2026-11-13-unified-logging.md` |
| Admin panel (DEV-15.13, ECO-067) | done | at `/admin/` in Hydrograf, Hydrolog, Obserwator and Archiwista, deployed 2026-11-14; Cloudflare Access per path is the author's step; plan `2026-11-13-admin-panel.md` |
| Info texts (DEV-15.14, ECO-069) | done in Nogat | merged 2026-11-14 (`6e4e71b`); the GUIs revise their texts (Next 1) |
| Regulamin link without a footer (DEV-15.7, DEV-15.8, ECO-070) | in progress | Nogat on branch `feat/no-footer` (2026-11-14); Hydrograf, Hydrolog and Obserwator move the link to the rail's foot (Next 14); plan `2026-11-14-no-footer.md` |
| One set of pins (HUB-4.9, REL-6.4) | in progress | `release-sets/candidate-3/`: Kartograf `d0990c8`, Obserwator `f9f4ee7`, Hydrolog `930915d`, Retman `320a7d6`. `set check` on 2026-11-14: Hydrograf and Archiwista match; Retman and Hydraulik pin Hydrolog `759d7ef` (candidate-2), Hydraulik declares no Kartograf pin. `verify-candidate` (REL-6.5) does not exist yet |
| Final integration run | in progress | the run of 2026-10-25 found F1 to F8, all fixed (`docs/plans/2026-10-25-final-integration.md`); the repeat is pending and must run Hydrograf (`affine<3` until pyflwdir 0.5.13, its ADR-062) and Archiwista (`affine>=3`) apart |
| `nogat` package (HUB §7) | planned | |

## Next

1. Info texts of a GUI (ECO-069, DEV-15.14, example in `design/README.md`):
   Hydrograf, Hydrolog, Obserwator and Archiwista revise their „(i)” texts,
   help popovers and „Objaśnienie metod” to it, method detail beyond about
   400 characters moving to their guides.
2. Unified logging, step 6: Archiwista copies `nogat_logging.py` (plan
   `docs/plans/2026-11-13-unified-logging.md`). Deleting `claude-agent`'s
   user journal, with the mockup's 673 lines of client addresses, waits for
   the author's one root step (the plan's „Journal entries written before
   the migration”).
3. Admin panel, step 6: the author sets Cloudflare Access on `/admin`,
   `/admin/*` and `/api/admin/*` of hydrograf-test, hydrolog-test and
   obserwator-test (`docs/plans/2026-11-13-admin-panel.md`).
4. Station data and analyses (ECO-059, plan
   `docs/plans/2026-11-12-station-data-and-analyses.md`, approved
   2026-11-13): N1 done; next Hydrolog's H1 to H4 under its own plan, then
   R1, O1 to O4 and Obserwator's GUI plan. Open: IMGW-PIB's terms
   (question 4).
5. Release set: Retman and Hydraulik apply candidate-3 (`set apply
   --project <P>`), or a next candidate takes a newer Hydrolog (Open
   questions). Hydrolog v1.0.0 waits for Obserwator 3.0.0's tag (producers
   first, HUB-5.2), `verify-candidate` and the author's versions. Plan
   `docs/plans/2026-11-03-one-pin-set.md`.
6. Repeat the final integration run at explicitly recorded heads, with
   Hydrograf and Archiwista apart and the two flows of F2; record the
   outcome in the data-output plan. Before the first release set, reconcile
   consumers' progress text with their manifests and close the data-output
   documentation and CLI smoke in Kartograf and the live plain-mode smoke in
   Obserwator (each project in its own session, DEV-3.4). When a tool
   renames a command, change its `routes` and run `agents` (CLAUDE.md).
7. Publish 1.0 to `main` with the author (ADOPTION_PLAN 0.3, 0.4). Numbers
   count from `main` (ECO-056, plan
   `docs/plans/2026-11-03-numbering-from-main.md`): steps 1 (Nogat) and 2
   (Kartograf) done; steps 3 to 5 change the projects' references before
   their next merge into `main` (Archiwista's `archiwista-state/2` back to
   `/1`); step 6 is this publication.
8. Releases (DEV-3.3), all the author's: no project has been tagged or
   merged into `main` since 2026-10-17. Hydrograf's `develop` carries
   `0.5.0.dev0` for v0.5.0, Kartograf's is frozen for 0.8.0 (its
   `docs/PROGRESS.md`); Obserwator's v3.0.0 is its `develop`, still
   untagged (its `docs/PROGRESS.md`); Hydraulik's code is on
   `feature/sfincs-swmm`.
9. Archiwista's release (decision D2 of
   `docs/plans/2026-10-31-archiwista-projects.md`): one release holding
   v0.3, v0.4 and the projects, outside the first release set (D3, REL-5.4).
   Open: the author's three-computer run of its v0.4 LAN runbook. Gaps found
   in use: Kartograf KD-3/KD-4 (Archiwista's „U źródła” offers only nmt, nmpt
   and laz) and KH (plans show no size); Kartograf's LAZ sidecars carry no
   survey work, so Archiwista's „pobrane” badge never matches LAZ (a
   `request` issue for Kartograf, not filed).
10. Archiwista's sets as Hydrograf's only Kartograf input
    (`docs/plans/2026-11-02-archiwista-sets-for-hydrograf.md`): A1 to A3 and
    H1 done; A4 (Kaczawa moved to `projects/kaczawa`) and A5 (the set built
    and closed) wait for the author; H2 and S5 follow Hydrograf v0.5.0.
11. Visual identity (`docs/plans/2026-11-01-visual-identity.md`): step 5,
    Archiwista's copy of `tokens.css`, is not on its `develop` (it ships the
    kit). GUI platform stage 2, the GUI hub,
    `docs/plans/2026-11-01-nogat-gui-platform.md` (`Approved: pending`).
12. Retman's evaluation rows of the operations added for Kartograf,
    Obserwator and Hydrolog are unmeasured: no model server on this machine.
13. Hydrograf without IMGW-PIB, a to-do after the first joint release: draft
    plan `docs/plans/2026-11-14-independence-from-imgw.md` (`Approved:
    pending`) with the research
    `2026-11-14-independence-from-imgw/era5-instead-of-pmaxtp.md`; the
    author's decisions of 2026-11-14: non-commercial today, so PMAXTP stays;
    then D (user rainfall), R (ERA5/CERRA × published coefficients from
    IMGW-PIB HVD gauges), A as its check, C only on demand; a written
    question to IMGW-PIB before any commercial start.
14. Regulamin link without a footer (ECO-070, plan
    `docs/plans/2026-11-14-no-footer.md`): Hydrograf, Hydrolog and
    Obserwator drop the footer statement and link „Regulamin” from the app
    menu, the rail's foot and their welcome window.

Ports of the local GUIs: 8000 IMGWTools, 8060 Obserwator, 8070 Hydrolog
(`hydrolog gui serve`), 8080 Hydrograf, 8090 Archiwista; the
`nogat-specimen` container keeps 8765 and serves the mockups from the shared
checkout's `feature/hydrolog-gui-mockup`. Hydrograf's other instance:
Hydroni 8081. Public hosts: `hydrograf-test`, `hydrolog-test`,
`archiwista-test` and `obserwator-test.debever.pl`.

## Open questions

- Publishing 1.0 to `main` (tag `std-1.0`, Next 7) and replacing the legacy
  `standards/templates/` and `standards/configs/` (ADOPTION_PLAN 0.1, 0.4):
  the author's step, because those files are owned by root and the agents
  here have no root.
- `docs/CLA.md` (DEV-16.2): its text needs the author's approval, then the
  pull-request template's CLA box (DEV-16.4); until then no external pull
  request is merged. Private vulnerability reporting (DEV-13.7) is the
  author's GitHub setting; GitHub's API reported it off on 2026-11-09.
- No record of approval, so no `Approved:` line (DEV-17.4):
  `2026-10-20-first-release-set.md` (proposed) and `2026-10-20-unified-gui.md`
  (an idea).
- Watch: Hydrograf keeps `affine<3` until pyflwdir 0.5.13 (ADR-062); until
  then Hydrograf and Archiwista run in separate environments.
- The author's decisions: the final versions, with no tags in any project
  until they are decided (Hydrolog v1.0.0 included); candidate-3 by Retman
  and Hydraulik, or a next candidate with a newer Hydrolog; Windows as a
  blocking CI job in Hydrolog; Hydroni on Hydrograf's current `develop`.
- Hydrograf's network method (ADR-080), recorded with proposals in its
  `docs/PROGRESS.md`, no work until the author asks („na razie nic nie
  rób”): a large unpointed tributary entering mid-reach stays in the
  przyrzecze, routed nowhere; reach lengths by D8 4–7 % longer than BDOT10k;
  reach slopes from end-point elevations noisy on short or flat reaches; the
  50 m mouth tolerance is arbitrary (reaches of 50–200 m get a notice and a
  button only); elements over 250 km² lie beyond SCS-CN's validity (a notice
  only).
