# Progress

Audited on 2026-11-15 against Nogat's `develop` (`c9a0516`) and the `origin/develop` of the
projects after `git fetch`; release-set pins by `set check`. History is the git log, the
CHANGELOG and each plan's Results (DOC-6.1). IMGWTools is called Obserwator from v3.0.0
(ECO-057); its local checkout may still be the directory `IMGWTools`.

## Deployment and storage (author's decision 2026-11-15)

- **Archiwista store `agent-tmp`** ("Magazyn agent-tmp") on NAS: CIFS mount at /mnt/magazyn/agent-tmp (//magazyn.local/agent-tmp), holds:
  - kartograf = /mnt/magazyn/agent-tmp/hydroni/kartograf (kartograf-store/1)
  - obserwator raw = /mnt/magazyn/agent-tmp/obserwator (2825 archives, moved from ~/data/obserwator-target/raw)
  - project kaczawa = /mnt/magazyn/agent-tmp/hydroni/projekty/kaczawa (area 792 km², set 2026-1: 194 NMT sheets, 10 BDOT10k counties, 1 HSG raster)
  - BDOT10k counties and unpinned data also held
  - NAS usage: 66 GB of 300 GB
- **Obserwator data** (processed, local, served fast) = /home/claude-agent/data/obserwator-target/data
- **Obserwator service** (obserwator-public.service) deployed at 3816b3c with OBSERWATOR_RAW_ROOT=/mnt/magazyn/agent-tmp/obserwator
- **Hydrograf** instances: :8080 live (cache removed), :8081 Hydroni test; admin-panel store re-processing deferred to after the first joint release
- **Archiwista deployed** at 7a11c76 on :8090; project h07 rebound to agent-tmp (2909 pins)
- **Deleted** in cleanup: test stores and e2e outputs; Hydrograf cache (12 GB old layout); data/nmt.pre-recut
- **Backups** retained: ~/data/archiwista-public/backup-2026-11-14-v1/ and earlier ROLLBACK.txt


## Status

| Component | State | Note |
|---|---|---|
| Long jobs (DEV-17.6, ECO-073) | done | merged 2026-11-15 (`c0a9f36`); long-running tasks run as user systemd units outside the agent's session |
| Standard 1.0 | in progress | not yet published to `main`; tagged `std-1.0` when it is (HUB-6.1); the drafts called 2.0 and 2.1 on `develop` are 1.0 (ECO-056) |
| Registry and schema | done | `ecosystem.yaml`, `schemas/ecosystem.schema.json`; `routes` name the commands of every tool's integration branch (HUB-2.9) |
| `validate`, `map`, `agents`, `deps`, `drift`, `standard`, `set` | done | `scripts/ecosystem.py`, errors by the registry (HUB-4.8); `drift` also reports the projects' copies of the schemas, the error registry, `nogat_logging.py`, the tokens, the marks and the kit (HUB-4.1, DEV-15.6) |
| Hub gate and CI | done | `scripts/gate.sh` on `uv.lock`, tests in `tests/` (unit, integration, contract, browser) |
| Canonical agent-interface schemas | done | `schemas/agent/`, contract tests (ECO-050) |
| Hand-off schema `nogat-handoff/1` | done | `schemas/exchange/handoff-1.schema.json`, with `node_provenance` (2026-11-10) and the optional `attribution` and `terms_notice` (ECO-060) |
| Data-output convention (ECO-051) | done in Nogat | DEV §19, AGI-3.4; plan `docs/plans/2026-10-24-data-output.md` |
| Generated `AGENTS.md` (HUB-4.3) | done | from the `routes` of the registry, `agents --check` in the gate; the guide links name `main`, so they resolve once each project is merged there |
| Visual identity and GUI kit (DEV §15) | done | `design/`: tokens, marks, specimen, mockups; kit 1.0.0 (app menu, sources strip, hand-off, regulamin, admin panel), which stays 1.0.0 until the author decides (REL-1.4); the copies of the kit, the marks and the tokens in Hydrograf, Hydrolog, Obserwator and Archiwista match Nogat's at their `origin/develop` of 2026-11-15 (SHA-256, the tokens apart from their DEV-15.3 header) |
| Provider attribution and regulamin (DEV §20, ECO-060 to ECO-065, ECO-068, ECO-071) | done in Nogat | CP is exactly „Dane ČHMÚ zostały przetworzone”; old CP lines with details count as CP. Regulamin 1.0, corrected in place (ECO-068, ECO-071; kit 1.0.0) and republished 2026-11-14 (`terms_effective` 2026-11-14) by Hydrograf, Hydrolog and Obserwator; only the author raises its version. One `<nogat-sources>` strip per view in the four GUIs; plans `2026-11-13-provider-attribution.md`, `2026-11-13-gui-terms.md`, `2026-11-13-compact-attribution.md`, `2026-11-13-terms-fix.md` |
| Unified logging (DEV-12.4 to DEV-12.9, ECO-066) | done | Nogat, Hydrograf, Hydrolog, Obserwator (GUI, REST server) and Archiwista (step 6, its A-ADR-057, `8573a93`) merged; deleting the journal entries written before the migration waits for the author's root step; plan `2026-11-13-unified-logging.md` |
| Admin panel (DEV-15.13, ECO-067) | done | at `/admin/` in Hydrograf, Hydrolog and Obserwator, deployed 2026-11-14; Archiwista has no `/admin/` page: its view „Zgłoszenia” uses `/api/v1/admin/feedback` with its sign-in and `feedback.manage` (step 5 of the plan; a deviation in its CLAUDE.md since `5aced6c`, on branch `chore/release-prep-2026-11-15`); Cloudflare Access per path is the author's step; plan `2026-11-13-admin-panel.md` |
| Info texts (DEV-15.14, ECO-069) | done in Nogat | merged 2026-11-14 (`6e4e71b`); the GUIs revise their texts (Next 2) |
| Regulamin link without a footer (DEV-15.7, DEV-15.8, ECO-070) | done | merged 2026-11-14 (`3a161ca`); Hydrograf, Hydrolog and Obserwator merged and deployed the same day; plan `2026-11-14-no-footer.md` |
| One set of pins (HUB-4.9, REL-6.4) | in progress | **candidate-5** (2026-11-15), the members of the first joint release (ECO-074): Kartograf `e14bc78`, Obserwator `f4f6a8d`, Hydrolog `3ce7ee8` (develop `d82982a`, v0.8.0.dev0), Hydrograf `939b55f` (a sheet missing at 5 m from the set's 1 m NMT, its ADR-087, found by the scenario test of 2026-11-15), Archiwista `800231c` (project files group-readable, its A-ADR-058, found by the scenario test), each gate green before its merge. `set check`: every pin between the members matches; Retman and Hydraulik differ until they apply the set in their own sessions (a later set) |
| Final integration run | in progress | the run of 2026-10-25 found F1 to F8, all fixed (`docs/plans/2026-10-25-final-integration.md`); the repeat is pending and must run Hydrograf (`affine<3` until pyflwdir 0.5.13, its ADR-062) and Archiwista (`affine>=3`) apart |
| `nogat` package (HUB §7) | planned | |

## Next

1. CP without detail (ECO-071): producers use the fixed line once and treat
   old parenthetical CP as CP on read (regulamin 1.0 corrected in place, no
   new `terms_effective`); the four GUIs carry kit 1.0.0 on their `develop`
   (2026-11-15).
2. Info texts of a GUI (ECO-069, DEV-15.14, example in `design/README.md`):
   Hydrograf, Hydrolog, Obserwator and Archiwista revise their „(i)” texts,
   help popovers and „Objaśnienie metod” to it, method detail beyond about
   400 characters moving to their guides.
3. Unified logging: deleting `claude-agent`'s user journal, with the
   mockup's 673 lines of client addresses, waits for the author's one root
   step (`docs/plans/2026-11-13-unified-logging.md`, „Journal entries
   written before the migration”).
4. Admin panel, step 6: the author sets Cloudflare Access on `/admin`,
   `/admin/*` and `/api/admin/*` of hydrograf-test, hydrolog-test and
   obserwator-test (`docs/plans/2026-11-13-admin-panel.md`).
5. Station data and analyses (ECO-059, plan
   `docs/plans/2026-11-12-station-data-and-analyses.md`, approved
   2026-11-13): N1 done; next Hydrolog's H1 to H4 under its own plan, then
   R1, O1 to O4 and Obserwator's GUI plan. Open: IMGW-PIB's terms
   (question 4).
6. Release set and deployment (2026-11-15): **candidate-5** holds the members of the
   first joint release (2026-11-15): Nogat, Kartograf, Hydrograf, Hydrolog, Obserwator and
   Archiwista (ECO-074); Retman and Hydraulik join a later set.
   Deployment state, members' heads and the pins that differ: Status.
   **Hydrograf admin-panel store re-processing** deferred to after the first joint release
   (author's decision 2026-11-15). Before the tags: the candidate's `pyproject.toml` and
   `uv.lock` (REL-6.4) and `verify-candidate` (REL-6.5), neither of which exists yet;
   the author's versions, Hydrolog's next release being 0.8.0 (ECO-074),
   producers first (HUB-5.2, REL-6.6). Plan `docs/plans/2026-11-03-one-pin-set.md`.
7. Repeat the final integration run at explicitly recorded heads, with
   Hydrograf and Archiwista apart and the two flows of F2; record the
   outcome in the data-output plan. Before the first release set, reconcile
   consumers' progress text with their manifests and close the data-output
   documentation and CLI smoke in Kartograf and the live plain-mode smoke in
   Obserwator (each project in its own session, DEV-3.4). When a tool
   renames a command, change its `routes` and run `agents` (CLAUDE.md).
8. Publish 1.0 to `main` with the author (ADOPTION_PLAN 0.3, 0.4). Numbers
   count from `main` (ECO-056, plan
   `docs/plans/2026-11-03-numbering-from-main.md`): steps 1 (Nogat) and 2
   (Kartograf) done; steps 3 to 5 change the projects' references before
   their next merge into `main` (Archiwista's `archiwista-state/2` back to
   `/1`); step 6 is this publication.
9. Releases (DEV-3.3), all the author's: no project has been tagged or
   merged into `main` since 2026-10-17. Hydrograf's `develop` carries
   `0.5.0.dev0` for v0.5.0, Kartograf's is frozen for 0.8.0 (its
   `docs/PROGRESS.md`); Obserwator's v3.0.0 is its `develop`, still
   untagged (its `docs/PROGRESS.md`); Hydraulik's code is on
   `feature/sfincs-swmm`.
10. Archiwista's release (decision D2 of
   `docs/plans/2026-10-31-archiwista-projects.md`): one release holding
   v0.3, v0.4 and the projects, in the first joint release by the author's
   scope of 2026-11-15 (D3 had kept it outside).
   Open: the author's three-computer run of its v0.4 LAN runbook. Gaps found
   in use: Kartograf KD-3/KD-4 (Archiwista's „U źródła” offers only nmt, nmpt
   and laz) and KH (plans show no size); Kartograf's LAZ sidecars carry no
   survey work, so Archiwista's „pobrane” badge never matches LAZ (a
   `request` issue for Kartograf, not filed).
11. Archiwista's sets as Hydrograf's only Kartograf input
    (`docs/plans/2026-11-02-archiwista-sets-for-hydrograf.md`): A1 to A3 and
    H1 done; A4 (Kaczawa moved to `projects/kaczawa`) and A5 (the set built
    and closed) wait for the author; H2 and S5 follow Hydrograf v0.5.0.
12. Visual identity (`docs/plans/2026-11-01-visual-identity.md`): step 5,
    Archiwista's copy of `tokens.css`, is not on its `develop` (it ships the
    kit). GUI platform stage 2, the GUI hub,
    `docs/plans/2026-11-01-nogat-gui-platform.md` (`Approved: pending`).
13. Retman's evaluation rows of the operations added for Kartograf,
    Obserwator and Hydrolog are unmeasured: no model server on this machine.
14. Hydrograf without IMGW-PIB, a to-do after the first joint release: draft
    plan `docs/plans/2026-11-14-independence-from-imgw.md` (`Approved:
    pending`) with the research
    `2026-11-14-independence-from-imgw/era5-instead-of-pmaxtp.md`; the
    author's decisions of 2026-11-14: non-commercial today, so PMAXTP stays;
    then D (user rainfall), R (ERA5/CERRA × published coefficients from
    IMGW-PIB HVD gauges), A as its check, C only on demand; a written
    question to IMGW-PIB before any commercial start.
15. Large basins in one Hydrograf instance: draft plan
    `docs/plans/2026-11-16-large-basins.md` (`Approved: pending`, branch
    `plan/large-basins`, not merged) from the scenario test of 2026-11-15
    (E7-08, E7-09) and the author's two rounds of 2026-11-16: JCWP parts
    within a fixed cell budget under the 8 GB cap, joined at BDOT10k inlets
    in topological order, one database for several basins (the Barycz and
    the Bóbr in one instance), Archiwista unchanged; gauges and Czechia are
    later extensions. Hydrograf's `feature/large-basins` (worktree
    `~/workspace/wt/hydrograf-large-basins`) has no code until `Approved:`
    and merges after the first joint release. Open: the memory measurement
    with Hydroni stopped, mixed cell sizes, format additions after the release.

Ports of the local GUIs: 8000 IMGWTools, 8060 Obserwator, 8070 Hydrolog
(`hydrolog gui serve`), 8080 Hydrograf, 8090 Archiwista; the
`nogat-specimen` container keeps 8765 and serves `design/` of the shared
checkout, on `develop` since 2026-11-15 (the container had exited when
checked that day). Hydrograf's other instance:
Hydroni 8081. Public hosts: `hydrograf-test`, `hydrolog-test`,
`archiwista-test` and `obserwator-test.debever.pl`.

## Open questions

- Publishing 1.0 to `main` (tag `std-1.0`, Next 8) and replacing the legacy
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
  until they are decided; Windows as a
  blocking CI job in Hydrolog; Hydroni on Hydrograf's current `develop`.
- Hydrograf's network method (ADR-080), recorded with proposals in its
  `docs/PROGRESS.md`, no work until the author asks („na razie nic nie
  rób”): a large unpointed tributary entering mid-reach stays in the
  przyrzecze, routed nowhere; reach lengths by D8 4–7 % longer than BDOT10k;
  reach slopes from end-point elevations noisy on short or flat reaches; the
  50 m mouth tolerance is arbitrary (reaches of 50–200 m get a notice and a
  button only); elements over 250 km² lie beyond SCS-CN's validity (a notice
  only).
