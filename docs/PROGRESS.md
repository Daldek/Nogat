# Progress

Audited on 2026-11-15 against Nogat's `develop` (`c9a0516`), updated 2026-11-16 by the
candidate's lock, `verify-candidate`, the integration run, the members' releases, Nogat's
release `v0.1.0` with standard 1.0 (`std-1.0`, 2026-11-17), the closed set `kaczawa`/`2026-1`
and the `origin/develop` of the projects after `git fetch`, and on 2026-11-22 for Nogat
`v0.2.0` with standard 1.1 (`std-1.1`); release-set pins by `set check`.
History is the git log, the CHANGELOG and each plan's Results (DOC-6.1). IMGWTools is
called Obserwator from v3.0.0 (ECO-057); its local checkout may still be the directory
`IMGWTools`.

## Deployment and storage (author's decision 2026-11-15)

- **Archiwista store `agent-tmp`** ("Magazyn agent-tmp") on NAS: CIFS mount at /mnt/magazyn/agent-tmp (//magazyn.local/agent-tmp), holds:
  - kartograf = /mnt/magazyn/agent-tmp/hydroni/kartograf (kartograf-store/1)
  - obserwator raw = /mnt/magazyn/agent-tmp/obserwator (2825 archives, moved from ~/data/obserwator-target/raw)
  - project kaczawa = /mnt/magazyn/agent-tmp/hydroni/projekty/kaczawa (area 792 km², set 2026-1 closed 2026-11-15T00:00:04Z: 194 NMT sheets, 10 BDOT10k counties, 1 HSG raster, no PGW units file)
  - BDOT10k counties and unpinned data also held
  - NAS usage: 66 GB of 300 GB
- **Obserwator data** (processed, local, served fast) = ~/data/obserwator-310/data (Obserwator 3.1.0 layout, since 2026-11-23; the 3.0 root moved to `/data/nmt/deploy-backup-2026-11-22/obserwator-target-data`)
- **Patch releases deployed 2026-11-18** (the author's approval; as on 2026-11-16: checkouts detached at the tags, venvs `uv sync --locked --all-extras --reinstall-package <pkg>`, then the unit restarted; each smoke-checked on 127.0.0.1 and its public host):
  - Hydrolog `v0.8.1` (`hydrolog-gui.service`, worktree `~/workspace/Hydrolog-gui`, was `v0.8.0`), with Obserwator 3.0.1 as its extra; Obserwator's analyses call this venv's `hydrolog`; the SCS unit hydrograph of a daily step keeps its volume (0.998 mm)
  - Obserwator `v3.0.1` (`obserwator-public.service`, `~/data/obserwator-public/app-target`, was `v3.0.0`), OBSERWATOR_RAW_ROOT=/mnt/magazyn/agent-tmp/obserwator; the series `cz.chmi.meteo_daily` built (`2026-09-04_0303d027`, 1,535 stations; the analyses of 2026-11-17 had used a 10-station version); `analyses build` of both providers with Hydrolog 0.8.1 runs as the unit `obserwator-analyses-2026-11-18` (IMGW-PIB 3,240 and ČHMÚ 2,321 stations, none carried forward)
  - Archiwista `v0.3.1` (`archiwista-public.service`, `~/data/archiwista-public/app`, was `v0.3.0`) with Kartograf 0.8.1 and Obserwator 3.0.1 (`archiwista doctor`: 0 errors); no index or state migration
  - Hydrograf `v0.5.1` on :8080 (`~/workspace/Hydrograf` detached at the tag; image `hydrograf-api:latest` rebuilt with Kartograf 0.8.1, Obserwator 3.0.1, Hydrolog 0.8.1; no migration, no new variables); the hydrograph of a daily step gives the Polish notice `uh_substeps`; Hydroni :8081 unchanged. Production keeps the data of Archiwista's set `kaczawa/2026-2` it took on 2026-11-17 (backup in `/data/nmt/hydrograf-backup-2026-11-17/`); the staging instance `hgstaging` that cut it was removed on 2026-11-18 (the author's decision: containers, volume `hgstaging_postgres_data`, worktree `~/workspace/Hydrograf-staging`, `~/data/hydrograf-staging`), and its README, cut scripts and logs are kept in `/mnt/magazyn/agent-tmp/archiwum-2026-11-18/hydrograf-staging/`
- **The round's releases deployed 2026-11-22/23** (the author's approval „Jeżeli wszystko przejdzie, to masz zgodę na wdrożenie na produkcję”; rollback commands in `~/data/deploy-2026-11-22/ROLLBACK.md`, backups in `/data/nmt/deploy-backup-2026-11-22/`):
  - Hydrolog `v0.9.0` (`hydrolog-gui.service`, `~/workspace/Hydrolog-gui`, was `v0.8.1`); a GUI computation answers `formula_versions`
  - Hydrograf `v0.6.0` (image rebuilt, was `v0.5.1`; image `hydrograf-api:rollback-2026-11-22`, `hydro_db` dump; no migration). Production's `hydro_api` runs `docker-compose.yml` + `docker-compose.override.yml` (`./backend` bind-mounted, `--reload`), not the prod overlay, which needs `secrets/db_password.txt` absent here: a checkout reloads the old image at once (about 10 min unhealthy on 2026-11-22), so check out and recreate together. A 137 km² hydrograph takes about 150 s, beyond nginx's 120 s (504 through the GUI), the same on `v0.5.1`: Hydrograf's backlog
  - Obserwator `v3.1.0` in a parallel install: `obserwator-public.service` from `~/data/obserwator-public/app-310` with Hydrolog `v0.9.0` in `~/data/obserwator-public/hydrolog-090` (`OBSERWATOR_HYDROLOG_COMMAND`); the data root built from the raw root by `~/data/obserwator-310/build.sh` (7 series, catalogs IMGW 3,811 and CHMU 2,486 stations, analyses of 3,240 + 2,321 stations, 0 problems; 9.5 h, 4.2 GB). `app-target` and `~/workspace/Hydrolog-obs` are no longer used; only 3.1.0 runs `store sync` on the raw root
  - Archiwista `v0.3.3` (`~/data/archiwista-public/app`, was `v0.3.1`) with Kartograf 0.8.2 and Obserwator 3.1.0; `obserwator_data` points at the new root; `reindex --store agent-tmp` 1,645 s, the 27 versions of the old root marked missing, none pinned (all 3,336 pins are Kartograf's)
- **Deleted** in cleanup: test stores and e2e outputs; Hydrograf cache (12 GB old layout); data/nmt.pre-recut. On 2026-11-18 `/` was full (0 B free, the meteo series build failed): the pytest temporary data of the gates, the venvs of `release-sets/*`, the checkouts of `set verify` and Docker's unused build cache were deleted, the scratch of 2026-11-01 to 2026-11-15 in `~/data/tmp`, the gates' logs, `~/tmp/nogat-run-2026-11-16`, `~/tmp/release-2026-11-16` and `~/workspace/archiwista-scratch` moved to `/mnt/magazyn/agent-tmp/archiwum-2026-11-18/` (the share keeps no symbolic links); 46 GB free after. Left in `~/data/tmp` because their copy is incomplete: `arch-tidy`, `h1-smoke`, `kclean`, `o1`, `o2` and two Firefox profiles (about 3 GB)
- **Backups** retained: `/data/nmt/deploy-backup-2026-11-22/` (before the deployment of the round: `hydro_db`, Archiwista's index, state and settings, the old Obserwator data root), image `hydrograf-api:rollback-2026-11-22`; `/data/nmt/deploy-backup-2026-11-18/`, image `hydrograf-api:rollback-2026-11-18`; `/data/nmt/deploy-backup-2026-11-16/`, image `hydrograf-api:rollback-2026-11-16`; ~/data/archiwista-public/backup-2026-11-14-v1/ and earlier ROLLBACK.txt

## Status

| Component | State | Note |
|---|---|---|
| Long jobs (DEV-17.6, ECO-073) | done | merged 2026-11-15 (`c0a9f36`); long-running tasks run as user systemd units outside the agent's session |
| Standard 1.0 | done 2026-11-17 | published to `main` with `v0.1.0`, its merge commit tagged `std-1.0` (HUB-6.1, ADOPTION_PLAN 0.4); the drafts called 2.0 and 2.1 on `develop` are 1.0 (ECO-056); the root-owned legacy `standards/templates/` and `standards/configs/` reached `main` unchanged (ADOPTION_PLAN 0.1, a known deviation) |
| Standard 1.1 | done, in 0.2.0 | published to `main` with `v0.2.0`, its merge commit tagged `std-1.1` (HUB-6.1): COMPUTATIONS.md (CMP, ECO-078), the operator's instance (ECO-079), the strip folded on a phone (ECO-080), kit 1.1.0 (ECO-081), providers by national acronyms (DEV-2.5, ECO-082) and one pattern of file names (DEV-19.21, ECO-083); the changelog of `standards/README.md` lists them |
| Registry and schema | done | `ecosystem.yaml`, `schemas/ecosystem.schema.json`; `routes` name the commands of every tool's integration branch (HUB-2.9) |
| `validate`, `map`, `agents`, `deps`, `drift`, `standard`, `set` | done | `scripts/ecosystem.py`, errors by the registry (HUB-4.8); `drift` also reports the projects' copies of the schemas, the error registry, `nogat_logging.py`, `nogat_formulas.py`, the tokens, the marks and the kit (HUB-4.1, DEV-15.6) |
| Hub gate and CI | done | `scripts/gate.sh` on `uv.lock`, tests in `tests/` (unit, integration, contract, browser) |
| Canonical agent-interface schemas | done | `schemas/agent/`, contract tests (ECO-050) |
| Hand-off schema `nogat-handoff/1` | done | `schemas/exchange/handoff-1.schema.json`, with `node_provenance` (2026-11-10) and the optional `attribution` and `terms_notice` (ECO-060) |
| Data-output convention (ECO-051) | done in Nogat | DEV §19, AGI-3.4; plan `docs/plans/2026-10-24-data-output.md` |
| Generated `AGENTS.md` (HUB-4.3) | done | from the `routes` of the registry, `agents --check` in the gate; the guide links name `main`: they resolve for Nogat and the members of `v0.1.0`, and for Retman and Hydraulik once each is merged there |
| Visual identity and GUI kit (DEV §15) | done | `design/`: tokens, marks, specimen, mockups; kit 1.1.0 in 0.2.0 (app menu, sources strip, hand-off, regulamin and its draft for operators, admin panel; ECO-081) and 1.2.0 on `develop` (`screen-lines`, the blocks `camels-pl` and `e-obs`; ECO-086, ECO-087), whose version moves only with the author's consent (REL-1.4); the kit manifests of Hydrograf, Hydrolog, Obserwator and Archiwista equal 1.1.0 in their releases of `v0.2.0` |
| Provider attribution and regulamin (DEV §20, ECO-060 to ECO-065, ECO-068, ECO-071, ECO-080, ECO-086, ECO-087) | done in Nogat | CP is exactly „Dane ČHMÚ zostały przetworzone”; old CP lines with details count as CP. DEV §20 is one table of provider lines that DEV-20.4 orders (ECO-087), with CAMELS-PL's, E-OBS's and G2DC-PL+'s lines (ECO-086) on `develop`. Regulamin 1.0, corrected in place (ECO-068, ECO-071; kit 1.0.0) and republished 2026-11-14 (`terms_effective` 2026-11-14) by Hydrograf, Hydrolog and Obserwator; only the author raises its version. One `<nogat-sources>` strip per view in the four GUIs, folded to one line on a phone (ECO-080) in their releases of `v0.2.0`; plans `2026-11-13-provider-attribution.md`, `2026-11-13-gui-terms.md`, `2026-11-13-compact-attribution.md`, `2026-11-13-terms-fix.md`, `2026-11-21-phone-sources-strip.md` |
| Unified logging (DEV-12.4 to DEV-12.9, ECO-066) | done | Nogat, Hydrograf, Hydrolog, Obserwator (GUI, REST server) and Archiwista (step 6, its A-ADR-057, `8573a93`) merged; deleting the journal entries written before the migration waits for the author's root step; plan `2026-11-13-unified-logging.md` |
| Formula reference module (CMP-8.1, standard 1.1) | done, in 0.2.0 | `standards/reference/nogat_formulas.py` and `schemas/formula/card-1.schema.json`, tested against right and wrong toy formulas (CMP-8.2); step 2 of plan `2026-11-18-computation-standard.md`; Hydrolog 0.9.0 copies it |
| Admin panel (DEV-15.13, ECO-067) | done | at `/admin/` in Hydrograf, Hydrolog and Obserwator, deployed 2026-11-14; Archiwista has no `/admin/` page: its view „Zgłoszenia” uses `/api/v1/admin/feedback` with its sign-in and `feedback.manage` (step 5 of the plan; a deviation in its CLAUDE.md since `5aced6c`, released in `v0.3.0`); Cloudflare Access per path set by the author on 2026-11-23; plan `2026-11-13-admin-panel.md` |
| Info texts (DEV-15.14, ECO-069) | done in Nogat | merged 2026-11-14 (`6e4e71b`); the GUIs revise their texts (Next 2) |
| Regulamin link without a footer (DEV-15.7, DEV-15.8, ECO-070) | done | merged 2026-11-14 (`3a161ca`); Hydrograf, Hydrolog and Obserwator merged and deployed the same day; plan `2026-11-14-no-footer.md` |
| One set of pins (HUB-4.9, REL-6.4) | done for the members | `v0.2.0`: the round's candidate, verified by `verify-candidate`, at the tags Kartograf `v0.8.2`, Obserwator `v3.1.0`, Hydrolog `v0.9.0`, Hydrograf `v0.6.0` and Archiwista `v0.3.3`. Before it candidate-6 became `v0.1.0` and candidate-10 `v0.1.1`. Retman and Hydraulik differ until they apply a later set |
| Members' releases (REL-2.1, REL-6.6) | done | tags on `main`: Kartograf `v0.8.0`, Obserwator `v3.0.0`, Hydrolog `v0.8.0`, Hydrograf `v0.5.0`, Archiwista `v0.3.0` on 2026-11-16 (`docs/plans/2026-11-16-candidate-5-integration.md`, „candidate-6 and the releases”; merged locally without pull requests, `gh` is not installed, with the author's approval); the patches of Next 7; the round of 2026-11-21 (Next 16): Obserwator `v3.1.0`, Hydrolog `v0.9.0`, Hydrograf `v0.6.0`, Archiwista `v0.3.3`; 2026-11-23 (Next 17): Obserwator `v3.2.0` and Archiwista `v0.4.0` outside a release set (REL-6.6 deviation: the author's decision that Nogat's release waits; the next set carries them) |
| `verify-candidate` (REL-6.5, ECO-077) | done | `set verify` and `.github/workflows/verify-candidate.yml`, on `main` since `v0.1.0`; it verified candidate-7 (after its releases), candidate-10 (`v0.1.1`) and the round's candidate (`v0.2.0`) on the three runners; candidate-6 was verified only on this machine by `set verify` (REL-6.5 deviation) |
| Final integration run | done 2026-11-16 | at candidate-5 (`docs/plans/2026-11-16-candidate-5-integration.md`): every member passes in the candidate's environment and on its own lock except the known failures C1 to C6, and C7 came up in the gate of Obserwator's release commit; all are left to the next releases by the author's decision (Kartograf: `obserwator-data.json` not a store; Archiwista: a umask-dependent test and two Firefox 159 crashes with the set's Playwright 1.65.2; Obserwator: a test that depends on the length of `TMPDIR`) |
| Nogat's version (ECO-076) | done, 0.2.0 | `v0.2.0` with `std-1.1`, the release set `release-sets/v0.2.0/` (REL-6.6); `v0.1.1` (`a973bf0`) 2026-11-20, the patch release set from `main` (REL-2.4), merged back into `develop`; `v0.1.0` 2026-11-17; `1.0.0` only by the author's decision (HUB-7.4) |
| `nogat` package (HUB §7) | planned | not in `v0.2.0`: the set installs as an environment, `uv sync --locked --no-dev --python 3.12` in `release-sets/v0.2.0/`, not with `uv tool install` (ADOPTION_PLAN 5.4; a deviation from HUB-7.1, HUB-7.2 and REL-6.1, CLAUDE.md) |

## Next

1. CP without detail (ECO-071): producers use the fixed line once and treat
   old parenthetical CP as CP on read (regulamin 1.0 corrected in place, no
   new `terms_effective`); the four GUIs carry the kit, 1.1.0 in their
   releases of `v0.2.0`.
2. Info texts of a GUI (ECO-069, DEV-15.14, example in `design/README.md`):
   Hydrograf, Hydrolog, Obserwator and Archiwista revise their „(i)” texts,
   help popovers and „Objaśnienie metod” to it, method detail beyond about
   400 characters moving to their guides.
3. Unified logging: deleting `claude-agent`'s user journal, with the
   mockup's 673 lines of client addresses, waits for the author's one root
   step (`docs/plans/2026-11-13-unified-logging.md`, „Journal entries
   written before the migration”).
4. Admin panel, step 6: done 2026-11-23 — the author set Cloudflare Access on `/admin`, `/admin/*` and `/api/admin/*` of hydrograf-test, hydrolog-test and obserwator-test (`docs/plans/2026-11-13-admin-panel.md`).
5. Station data and analyses (ECO-059, plan
   `docs/plans/2026-11-12-station-data-and-analyses.md`, approved
   2026-11-13): N1 done; next Hydrolog's H1 to H4 under its own plan, then
   R1, O1 to O4 and Obserwator's GUI plan. Open: IMGW-PIB's terms
   (question 4).
6. Follow-ups of `v0.1.0`, owned by the members, each in its own session:
   - Hydrograf re-processes its production from Archiwista's project
     `kaczawa` (H2 and S5 of 11; the admin-panel store re-processing the
     author deferred on 2026-11-15 to after the first joint release). Its
     set `2026-2` was built in the web interface by the plan's A5 and
     closed by `piotr` on 2026-11-17 (an agent's session on the author's
     request): four calls, 222 pins, the inputs of `2026-1` with the PGW
     units of the area (`hydro/pl_pgw`, 2023-09-15). The bootstrap has no
     cut to the area (`--units` is ADR-071's processing, the same results):
     the staging instance `hgstaging` (127.0.0.1:8083, v0.5.0; its README
     in `~/data/hydrograf-staging/`) gave 981.5 km² at 10 000 m² with 594
     outlets. Cut on 2026-11-17 by the runbook's scripts as production was
     (kaczawa2's K3–K12, adapted: the project's area as the boundary, and
     the 10 km² outlet segment cut to it because it runs on past the
     outlet), it equals production: the stream tables per threshold
     (792.009 km², one outlet), the land cover, `bdot_streams`, the
     depressions and every probe point. It differs in the soil groups
     (B 90.98 / C 8.66 % against 90.78 / 8.86 %, the set's raster) and the
     PMAXTP grid of the mosaic's box (depths up to about 0.75 % higher).
     Production took these data on 2026-11-17 (Deployment and storage);
     the cut belongs in Hydrograf (S5), so a later re-processing needs no
     hand-run scripts.
   - Obserwator: the user unit `chmi-night` (2026-11-16/17,
     `~/tmp/chmi-night/`) downloaded the daily archives of the 2,474 ČHMÚ
     stations into the raw root (41,271 files, none failed), built
     `cz.chmi.hydro_daily` and rebuilt the analyses with Hydrolog 0.8.0;
     the defects it found went into Obserwator `v3.0.1` and Hydrolog
     `v0.8.1` (Next 7), and `cz.chmi.meteo_daily` was built on 2026-11-21
     (Deployment and storage). Obserwator's copies in `schemas/nogat/` are
     those of `std-1.1` (its D6,
     `docs/plans/2026-11-04-obserwator-agent-contracts.md`).
7. The members' next releases fix the known failures C1 to C7 and the
   findings of the scenario test of 2026-11-15/16 (Barycz, Bóbr) (the
   author's decision of 2026-11-16); each member opens its next cycle
   (`X.Y.(Z+1).dev0`) with its next change. When a tool renames a command,
   change its `routes` and run `agents` (CLAUDE.md). The patch scope, defects
   only, approved by the author on 2026-11-17, producers first:
   - Obserwator 3.0.1: done on `fix/3.0.1` (Next 6); released with the
     others (the author's decision of 2026-11-17), and the features planned
     on 2026-11-14 as its 3.0.1 move to 3.1.0.
   - Kartograf 0.8.1: done on `fix/0.8.1` (C1, its part of C5, E5a-01: a
     repeated `--sheet` is refused); full gate passed (8,664 tests). GEO-02
     stays (a convention; a fix would break callers), E2-04 is a feature and
     moves to a minor.
   - Hydrolog 0.8.1: its part of E5b-08, E5b-07 (at least a notice), the
     per-period `OverflowError` of `hydrometrics rating-curve`, the rating
     curve fit that does not converge (to be examined), the threshold of 0
     or below 0 of `low_flow_sequences`, and its GUI report #1 (the
     horizontal axis of „Obliczenia składowe” shows absurdly small values),
     and a notice and an unreliable mark on a physically implausible
     rating curve or period (e.g. IMGW 150170070 Głuchołazy: b 6.5 and
     h0 −88 cm in 1981–1990, b 6.6 and h0 −179 cm in 2001–2010, periods
     that mix the stage shifts of 1998–1999 and 2008; the author's decision
     of 2026-11-17).
     Done on `fix/0.8.1` (ADR-0041 for the implausible-curve mark); E5b-07
     computes the SCS hydrograph in sub-steps, which changes the e2e
     reference to 72.23 m³/s and 1,046,077 m³; full gate passed (8,891
     tests).
     The 50 reports of the GUIs (Hydrograf 30, Hydrolog 12, Obserwator 8)
     were reviewed and marked read on 2026-11-17; no replies are prepared
     (the author's decision).
   - Hydrograf 0.5.1, after Hydrolog: E3-04, E5b-05, E5b-06, E5b-09,
     E5b-01, E5b-08, E4-02, E4-03, HG-E2E-01 to 03, its PROGRESS Next 17,
     the `dem_mosaic.vrt` a bootstrap leaves; from the external test report
     of 2026-11-02 (author's copy in `~/tmp/feedback/`): A2 (Snyder's Lc
     only in the advanced mode, the Tc method not disabled for Snyder), B2
     (= G05-1) and B3 (Esc both hides and clears). Its M2 (touch has no
     hover) and M3 (profile and sheets overlap on a phone), once confirmed,
     go to 0.6.0; U3, the „Logowanie” link to `/admin/` in the rail, stays
     (the author: accounts may come later).
     Done on `fix/0.5.1`, E5b-06 by Hydrolog's catalog notices; full gate
     passed (2,404 tests). Left: E3-04 (needs the author's amendment of
     ADR-083) and Next 17 (a feature).
   - Archiwista 0.3.1: done on `fix/0.3.1` (E7-01 with A-ADR-049 erratum 9,
     E2-06, C2, C6; C3 marked as known under Playwright 1.65.2); full gate
     passed (3,029 tests). E2-05 is left: it needs a geometry-countries API
     of Kartograf (a minor). The e2e success path of the map's „Ustaw jako
     obszar projektu…” is no longer exercised.
   - **Released 2026-11-18** with the author's approval from candidate-7
     (REL-6.5 deviation: `verify-candidate` ran afterwards): Kartograf
     `v0.8.1`, Obserwator `v3.0.1`, Hydrolog `v0.8.1`, Hydrograf `v0.5.1`,
     Archiwista `v0.3.1`; deployed the same day (Deployment and storage);
     Kartograf `v0.8.2` followed as a hotfix outside the round.
   - Each patch is made in a new worktree of its repository on a topic
     branch `fix/<topic>` from `origin/develop` (DEV-3.1), as Obserwator's
     `fix/3.0.1`.
   - **Nogat 0.1.1 released 2026-11-20** from candidate-10 (run 44775327473):
     Kartograf `v0.8.2`, Obserwator `v3.0.1`, Hydrolog `v0.8.1`, Hydrograf
     `v0.5.2`, Archiwista `v0.3.2`; standard 1.1 stays on `develop`. Flaky
     in the first attempt, passed on the
     rerun: Hydrolog's `test_leaving_or_reloading_the_page_ends_its_session`
     (macOS, Python 3.15) and Archiwista's
     `test_verify_runs_offline_and_marks_each_pin_while_network_jobs_say_why[firefox]`
     (Ubuntu, Python 3.12; „Stylesheet not loaded” of the map view while
     the test ends, 1 in 55 local runs), both for their next releases.
     Minor releases with a plan: S5 (the cut to the area), large basins, E3-03,
     E5b-02, E5b-04 (Hydrograf 0.6.0), E2-09/KH (Kartograf), E2-10 and
     E7-02 (Archiwista), E3-02 and the features planned as Obserwator's
     3.0.1 (3.1.0, the author's decision of 2026-11-17). From the check of
     150170070 (the author, 2026-11-17):
     Hydrolog's rating-curve periods from detected stage shifts at a
     steady discharge instead of fixed decades, with gauge-zero changes the
     user may give (Obserwator's report #3), since IMGW-PIB publishes no
     history of gauge zeros (checked 2026-11-17: the daily, monthly and
     half-year archives, `lista_zmian_hydro.txt`, `lista_stacji_hydro.csv`,
     the API and hydro.imgw.pl give only the current zero, e.g. 279.88 m
     EVRF2007 at 150170070; the hydrological yearbooks 2018–2025 give each
     year's P.z. of their stations only, with no remark code for a change;
     IMGW re-computes archived Q after a change of the stage–discharge
     relation, so its H is raw and its Q is homogenised); Obserwator shows
     or hides the unreliable periodic curves with a warning, and its station
     card says that IMGW's daily Q are derived from IMGW's own rating
     curves, not measured.
8. The round without a Nogat release (the author's decision of 2026-11-23): no Nogat release and no
   `std-*` tag; standard 1.2 accumulates on `develop` (HUB-6.1): ECO-084, ECO-085, DEV-20.8, the `forbidden`
   reasons, ECO-086 (CAMELS-PL, step 1 of its plan), ECO-087 (P9's table of provider lines; `screen-lines`
   for Obserwator's provider fed by files, I13) and kit `1.2.0`. On the members' `develop` (not pushed, not
   released), 2026-11-23: Kartograf `0.9.0.dev0` (CAMELS-PL step 2, its ADR-062), Hydrolog `0.10.0.dev0`
   (step 5, its ADR-0073; CAMELS-PL's BFI uses another filter, recorded, not matched), Obserwator
   `3.3.0.dev0` (the provider fed by files, its ADR-033, kit `1.2.0`). Open for the author: whether the
   terms line RD goes with what CAMELS-PL took from IMGW-PIB (DEV-20.7 vs DEV-20.12). Deleting
   `feature/verify-candidate` and `chore/candidate-6` is the author's.
9. Retman and Hydraulik join a later set (ECO-074): each applies its pins
   and does step 4 of `docs/plans/2026-11-03-numbering-from-main.md`
   (references and the emitted `standard_version`; Hydraulik's
   `feature/sfincs-swmm` still copies `standard_version` 2.1) before its
   next merge into `main`; Hydraulik's code is on `feature/sfincs-swmm`.
   The plan's other steps are done: 1 to 5 for Nogat and the members of
   `v0.1.0`, 6 with `std-1.0`.
10. Archiwista `v0.3.0`, released 2026-11-16 in the first joint release,
   holds v0.3, v0.4 and the projects (decision D2 of
   `docs/plans/2026-10-31-archiwista-projects.md`).
   Open: the author's three-computer run of its v0.4 LAN runbook. Gaps found
   in use: Kartograf KD-3/KD-4 (Archiwista's „U źródła” offers only nmt, nmpt
   and laz) and KH (plans show no size); Kartograf's LAZ sidecars carry no
   survey work, so Archiwista's „pobrane” badge never matches LAZ (a
   `request` issue for Kartograf, not filed).
11. Archiwista's sets as Hydrograf's only Kartograf input
    (`docs/plans/2026-11-02-archiwista-sets-for-hydrograf.md`): A1 to A5 and
    H1 done; A4 and A5 as the project `kaczawa` and its set `2026-1`, closed
    2026-11-15 (Deployment and storage). H2 and S5 are next: the staging
    re-processing of 6.
12. Visual identity (`docs/plans/2026-11-01-visual-identity.md`): step 5,
    Archiwista's copy of `tokens.css`, is not on its `develop` (it ships the
    kit). GUI platform stage 2, the GUI hub, is Latarnik (the author, 2026-11-24):
    plan `docs/plans/2026-11-24-latarnik.md` (`plan/latarnik`), approved 2026-11-24.
13. Retman's evaluation rows of the operations added for Kartograf,
    Obserwator and Hydrolog are unmeasured: no model server on this machine.
14. Hydrograf without IMGW-PIB, a to-do that the first joint release
    unblocks; no code before the plan's `Approved:` line (DEV-17.4): draft
    plan `docs/plans/2026-11-14-independence-from-imgw.md` (`Approved:
    pending`) with the research
    `2026-11-14-independence-from-imgw/era5-instead-of-pmaxtp.md`; the
    author's decisions of 2026-11-14: non-commercial today, so PMAXTP stays;
    then D (user rainfall), R (ERA5/CERRA × published coefficients from
    IMGW-PIB HVD gauges), A as its check, C only on demand; a written
    question to IMGW-PIB before any commercial start.
15. Operator's instance (`2026-11-21-obserwator-instance.md`, approved):
    steps 1–5 in Obserwator `3.1.0` and Nogat `0.2.0` (ECO-079, Obserwator
    ADR-025; kit `1.1.0`); step 6, the provider fed by files, is Obserwator
    `v3.3.0` (the author, 2026-11-22). The lawyer's review of the operator's
    draft regulamin waits for an actual deployment at a client (the author,
    2026-11-23) and blocks no release.
16. Release round of 2026-11-21, released as the set `v0.2.0` (candidate-12,
    run 45048681845; CI of every `main` passed): Obserwator `3.1.0`, Hydrolog
    `0.9.0`, Hydrograf `0.6.0`, Archiwista `0.3.3`, Kartograf `0.8.2`
    unchanged, Nogat `0.2.0` with `std-1.1`; deployed 2026-11-22/23
    (Deployment and storage). No member has a publish workflow (REL-2.1
    step 5), as in the earlier releases. Next: Archiwista `0.3.4` (the race
    of `test_worker_logs_warnings_and_errors_as_app_records_and_deletes_nothing`),
    Obserwator `v3.2.0` (Next 17), Hydrograf `0.7.0`, steps 7 and 10 of the
    computation standard. The plans `2026-11-20-hydromet-providers.md` and
    `2026-11-16-operational-series.md` were reviewed and approved by Fable for
    the author on 2026-11-23 (Next 17); CAMELS-PL (`2026-11-22-camels-pl.md`)
    is approved, Obserwator `v3.4.0`.
17. Obserwator `v3.2.0` and Archiwista `v0.4.0`, released 2026-11-23 outside a
    release set (Members' releases): the plans `2026-11-16-operational-series.md`
    and `2026-11-20-hydromet-providers.md` (approved by Fable for the author,
    review `~/workspace/wt/logs/fable-obserwator-3.2.0.md`), their Results.
    Production (D1) is the author's: Archiwista `0.4.0` first, then Obserwator
    `3.2.0`, `[obserwator.capture]`, the first backup, the timers, the backfill.
    Next in the members (Next 8): Obserwator `v3.3.0` (the provider fed by
    files; Gdańskie Wody waits for its terms), Kartograf's CAMELS-PL product,
    Hydrolog `0.10.0`; CAMELS-PL `v3.4.0`. `plan/large-basins` takes Next 18.
19. Interval estimation beside point estimation (Obserwator feedback #13): plan `docs/plans/2026-11-24-interval-estimation.md`, approved by the author on 2026-11-24 with the answers to its questions 1 to 6, reviewed by Fable on 2026-11-24 (`~/workspace/wt/logs/fable-interval-estimation.md`): Hydrolog computes the intervals of the flood, precipitation and low-flow quantiles (a parametric bootstrap of the L-moments fits, KZGW 2017's delta method of the maximum-likelihood fits) at 95 % and 68 %, Obserwator stores both and shows them, selectable, as bands and „[dolna–górna]”; N1 first, then Hydrolog `0.10.0`, then Obserwator (`v3.4.0` or `v3.5.0`, whichever first runs Hydrolog `0.10.0`), one `analyses build` after both.
20. Approved by the author on 2026-11-24 after Fable's reviews (`~/workspace/wt/logs/fable-{unified-charts,qgis-plugin,latarnik,shared-base-maps}.md`), merged into `develop`: `docs/plans/2026-11-24-unified-charts.md` (one chart module in the kit, Obserwator feedback #9), `2026-11-24-qgis-plugin.md` (Goniec, feedback #11; Obserwator `v3.6.0`), `2026-11-24-latarnik.md` (item 12) and `2026-11-24-shared-base-maps.md` (answers 1–9; Hydrograf's MapLibre move is its own plan); Kartograf's GUI is its own plan (Kartograf `plan/kartograf-gui`).

Ports of the local GUIs: 8000 IMGWTools, 8060 Obserwator, 8070 Hydrolog
(`hydrolog gui serve`), 8080 Hydrograf, 8090 Archiwista; the
`nogat-specimen` container keeps 8765 and serves `design/` of the shared
checkout, on `develop` since 2026-11-15 (the container had exited when
checked that day). Hydrograf's other instance:
Hydroni 8081. Public hosts: `hydrograf-test`, `hydrolog-test`,
`archiwista-test` and `obserwator-test.debever.pl`.

## Open questions

- Replacing the legacy `standards/templates/` and `standards/configs/`
  (ADOPTION_PLAN 0.1): the author's step, because those files are owned by
  root and the agents here have no root; they reached `main` unchanged with
  `std-1.0`, a known deviation.
- `docs/CLA.md` (DEV-16.2): its text needs the author's approval, then the
  pull-request template's CLA box (DEV-16.4); until then no external pull
  request is merged. Private vulnerability reporting (DEV-13.7) is the
  author's GitHub setting; GitHub's API reported it off on 2026-11-09.
- No record of approval, so no `Approved:` line (DEV-17.4):
  `2026-10-20-unified-gui.md` (an idea).
- Watch: Hydrograf keeps `affine<3` until pyflwdir 0.5.13 (ADR-062); until
  then Hydrograf and Archiwista run in separate environments.
- The author's decisions: Windows as a blocking CI job in Hydrolog; Hydroni
  on Hydrograf's current `develop`.
- Hydrograf's network method (ADR-080), recorded with proposals in its
  `docs/PROGRESS.md`, no work until the author asks („na razie nic nie
  rób”): a large unpointed tributary entering mid-reach stays in the
  przyrzecze, routed nowhere; reach lengths by D8 4–7 % longer than BDOT10k;
  reach slopes from end-point elevations noisy on short or flat reaches; the
  50 m mouth tolerance is arbitrary (reaches of 50–200 m get a notice and a
  button only); elements over 250 km² lie beyond SCS-CN's validity (a notice
  only).
