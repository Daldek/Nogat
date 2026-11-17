# Progress

Audited on 2026-11-15 against Nogat's `develop` (`c9a0516`), updated 2026-11-16 by the
candidate's lock, `verify-candidate`, the integration run, the members' releases, Nogat's
release `v0.1.0` with standard 1.0 (`std-1.0`, 2026-11-17), the closed set `kaczawa`/`2026-1`
and the `origin/develop` of the projects after `git fetch`; release-set pins by `set check`.
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
- **Obserwator data** (processed, local, served fast) = ~/data/obserwator-target/data
- **Released versions deployed 2026-11-16** (checkouts detached at the tags, venvs `uv sync --locked --all-extras --reinstall-package <pkg>`, then the unit restarted; each smoke-checked on 127.0.0.1 and its public host):
  - Hydrolog `v0.8.0` (`hydrolog-gui.service`, worktree `~/workspace/Hydrolog-gui`, was `e5df06d`), with Obserwator 3.0.0 as its extra; Obserwator's analyses call this venv's `hydrolog`
  - Obserwator `v3.0.0` (`obserwator-public.service`, `~/data/obserwator-public/app-target`, was `3816b3c`; code unchanged but the version), OBSERWATOR_RAW_ROOT=/mnt/magazyn/agent-tmp/obserwator; its stored analyses are those of 2026-11-15 (Hydrolog 0.8.0.dev0), not rebuilt (Next 6)
  - Archiwista `v0.3.0` (`archiwista-public.service`, `~/data/archiwista-public/app`, was `7a11c76`) with Kartograf 0.8.0 and Obserwator 3.0.0; no index or state migration
  - Hydrograf `v0.5.0` on :8080 (`~/workspace/Hydrograf` detached at the tag, was local `develop` `1577dbc`; image `hydrograf-api:latest` rebuilt with Kartograf 0.8.0, Obserwator 3.0.0, Hydrolog 0.8.0; alembic `007`, no migration); Hydroni :8081 unchanged. On 2026-11-17 17:05–17:10 (the author's decision) production took its data from Archiwista's set `kaczawa/2026-2`, cut in the staging instance `hgstaging` (Next 6): the seven data tables restored data-only (feedback kept), the rasters, `hydro_merged.gpkg`, the boundary, `frontend/data` (its `results/` kept) and the tiles copied; every probe point equals staging; backup and rollback in `/data/nmt/hydrograf-backup-2026-11-17/` and `~/data/hydrograf-staging/README`
- **Deleted** in cleanup: test stores and e2e outputs; Hydrograf cache (12 GB old layout); data/nmt.pre-recut
- **Backups** retained: `/data/nmt/deploy-backup-2026-11-16/` (before the deployment of the releases: `hydrograf-hydro_db.dump`, `hydrograf.env`, Archiwista state and index, Hydrolog's feedback, `~/.local/share/nogat` and `~/.local/state/nogat`, the user units, `deployed-before.txt`), image `hydrograf-api:rollback-2026-11-16`; ~/data/archiwista-public/backup-2026-11-14-v1/ and earlier ROLLBACK.txt


## Status

| Component | State | Note |
|---|---|---|
| Long jobs (DEV-17.6, ECO-073) | done | merged 2026-11-15 (`c0a9f36`); long-running tasks run as user systemd units outside the agent's session |
| Standard 1.0 | done 2026-11-17 | published to `main` with `v0.1.0`, its merge commit tagged `std-1.0` (HUB-6.1, ADOPTION_PLAN 0.4); the drafts called 2.0 and 2.1 on `develop` are 1.0 (ECO-056); the root-owned legacy `standards/templates/` and `standards/configs/` reached `main` unchanged (ADOPTION_PLAN 0.1, a known deviation) |
| Registry and schema | done | `ecosystem.yaml`, `schemas/ecosystem.schema.json`; `routes` name the commands of every tool's integration branch (HUB-2.9) |
| `validate`, `map`, `agents`, `deps`, `drift`, `standard`, `set` | done | `scripts/ecosystem.py`, errors by the registry (HUB-4.8); `drift` also reports the projects' copies of the schemas, the error registry, `nogat_logging.py`, the tokens, the marks and the kit (HUB-4.1, DEV-15.6) |
| Hub gate and CI | done | `scripts/gate.sh` on `uv.lock`, tests in `tests/` (unit, integration, contract, browser) |
| Canonical agent-interface schemas | done | `schemas/agent/`, contract tests (ECO-050) |
| Hand-off schema `nogat-handoff/1` | done | `schemas/exchange/handoff-1.schema.json`, with `node_provenance` (2026-11-10) and the optional `attribution` and `terms_notice` (ECO-060) |
| Data-output convention (ECO-051) | done in Nogat | DEV §19, AGI-3.4; plan `docs/plans/2026-10-24-data-output.md` |
| Generated `AGENTS.md` (HUB-4.3) | done | from the `routes` of the registry, `agents --check` in the gate; the guide links name `main`: they resolve for Nogat and the members of `v0.1.0`, and for Retman and Hydraulik once each is merged there |
| Visual identity and GUI kit (DEV §15) | done | `design/`: tokens, marks, specimen, mockups; kit 1.0.0 (app menu, sources strip, hand-off, regulamin, admin panel), which stays 1.0.0 until the author decides (REL-1.4); the copies of the kit, the marks and the tokens in Hydrograf, Hydrolog, Obserwator and Archiwista match Nogat's at their `origin/develop` of 2026-11-15 (SHA-256, the tokens apart from their DEV-15.3 header) |
| Provider attribution and regulamin (DEV §20, ECO-060 to ECO-065, ECO-068, ECO-071) | done in Nogat | CP is exactly „Dane ČHMÚ zostały przetworzone”; old CP lines with details count as CP. Regulamin 1.0, corrected in place (ECO-068, ECO-071; kit 1.0.0) and republished 2026-11-14 (`terms_effective` 2026-11-14) by Hydrograf, Hydrolog and Obserwator; only the author raises its version. One `<nogat-sources>` strip per view in the four GUIs; plans `2026-11-13-provider-attribution.md`, `2026-11-13-gui-terms.md`, `2026-11-13-compact-attribution.md`, `2026-11-13-terms-fix.md` |
| Unified logging (DEV-12.4 to DEV-12.9, ECO-066) | done | Nogat, Hydrograf, Hydrolog, Obserwator (GUI, REST server) and Archiwista (step 6, its A-ADR-057, `8573a93`) merged; deleting the journal entries written before the migration waits for the author's root step; plan `2026-11-13-unified-logging.md` |
| Admin panel (DEV-15.13, ECO-067) | done | at `/admin/` in Hydrograf, Hydrolog and Obserwator, deployed 2026-11-14; Archiwista has no `/admin/` page: its view „Zgłoszenia” uses `/api/v1/admin/feedback` with its sign-in and `feedback.manage` (step 5 of the plan; a deviation in its CLAUDE.md since `5aced6c`, released in `v0.3.0`); Cloudflare Access per path is the author's step; plan `2026-11-13-admin-panel.md` |
| Info texts (DEV-15.14, ECO-069) | done in Nogat | merged 2026-11-14 (`6e4e71b`); the GUIs revise their texts (Next 2) |
| Regulamin link without a footer (DEV-15.7, DEV-15.8, ECO-070) | done | merged 2026-11-14 (`3a161ca`); Hydrograf, Hydrolog and Obserwator merged and deployed the same day; plan `2026-11-14-no-footer.md` |
| One set of pins (HUB-4.9, REL-6.4) | done for the members | **candidate-6** (2026-11-16): Kartograf `7a1eb11`, Obserwator `11eedea`, Hydrolog `1be867d`, Hydrograf `1aa66f1`, Archiwista `95b0540`, the members after their release documentation; `set check`: every pin between the members matches; `set verify` on this machine: all pass except the known C2 and C3; released as `release-sets/v0.1.0/` with the members' tags. Retman and Hydraulik differ until they apply a later set |
| Members' releases (REL-2.1, REL-6.6) | done 2026-11-16 | tags on `main`: Kartograf `v0.8.0`, Obserwator `v3.0.0`, Hydrolog `v0.8.0`, Hydrograf `v0.5.0`, Archiwista `v0.3.0` (`docs/plans/2026-11-16-candidate-5-integration.md`, „candidate-6 and the releases”); merged locally without pull requests (`gh` is not installed), with the author's approval; verified locally only (REL-6.5 deviation: the workflow reached Nogat's `main` only with `v0.1.0`) |
| `verify-candidate` (REL-6.5, ECO-077) | done 2026-11-17 | `set verify` and `.github/workflows/verify-candidate.yml`, on `main` with `v0.1.0` and dispatchable from there; not run yet: candidate-6 was verified only on this machine by `set verify` (REL-6.5 deviation) |
| Final integration run | done 2026-11-16 | at candidate-5 (`docs/plans/2026-11-16-candidate-5-integration.md`): every member passes in the candidate's environment and on its own lock except the known failures C1 to C6, and C7 came up in the gate of Obserwator's release commit; all are left to the next releases by the author's decision (Kartograf: `obserwator-data.json` not a store; Archiwista: a umask-dependent test and two Firefox 159 crashes with the set's Playwright 1.65.2; Obserwator: a test that depends on the length of `TMPDIR`) |
| Nogat's version (ECO-076) | done 2026-11-17 | `v0.1.0`, the release set `release-sets/v0.1.0/` (REL-6.6, HUB-7.2); `pyproject.toml` and `uv.lock` carry `0.1.0`; merged into `main` locally without a pull request, with the author's approval; `1.0.0` only by the author's decision (HUB-7.4) |
| `nogat` package (HUB §7) | planned | not in `v0.1.0`: the set installs as an environment, `uv sync --locked --no-dev --python 3.12` in `release-sets/v0.1.0/`, not with `uv tool install` (ADOPTION_PLAN 5.4; a deviation from HUB-7.1, HUB-7.2 and REL-6.1, CLAUDE.md) |

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
   - Obserwator: the user unit `chmi-night` (2026-11-16 23:05 to
     2026-11-17 08:07, `~/tmp/chmi-night/`) downloaded the daily archives
     of the 2,474 Czech ČHMÚ stations of the catalog into the raw root, one
     station per call (41,271 files, none failed; about 2,800 meteo files
     are not published and 75 hydro stations have none), built the series
     `cz.chmi.hydro_daily` (20 min) and rebuilt the analyses of every
     station with Hydrolog 0.8.0 (6 h 9 min; the service shows them):
     IMGW-PIB 3,240 stations, 83,704 analyses ok and 1,000 failed at 201
     stations (the 2026-11-15 build with 0.8.0.dev0: 2,093 at 1,066); ČHMÚ
     796 stations (23 before), 31,971 ok and 265 failed at 55. Almost all
     failures are series too short for the method (Mann–Kendall, flood and
     low-flow frequency, homogeneity and precipitation quantiles with 0 to 2
     years against the 3 needed; incomplete months or years); defects for
     Hydrolog 0.8.1: `hydrometrics rating-curve` per period ends in an
     `OverflowError` (8 stations: `_level_at` inverts a curve whose `b` is
     near zero, `operations/hydrometrics.py:276`), its fit does not converge
     at 5 stations, and `low_flow_sequences` refuses a threshold of 0 (Q)
     or below 0 (H) instead of a notice. The series
     `cz.chmi.meteo_daily` fails: Obserwator
     3.0.0 refuses the whole build at a row whose `TIMEFUNC` is an old
     observation term (85 of 3,351 files). Fixed on Obserwator's branch
     `fix/3.0.1` (ADR-003 erratum of 2026-11-17: a daily value at any
     observation term is that day's), with C4, its part of C5, C7 and
     E3-06; its full gate passed (3,446 tests). The release of 3.0.1 waits
     for the author's approval; the meteo series is built after it.
     Obserwator also refreshes its copies in `schemas/nogat/` from
     `std-1.0` (its D6, `docs/plans/2026-11-04-obserwator-agent-contracts.md`).
7. The members' next releases fix the known failures C1 to C7 and the
   findings of the scenario test of 2026-11-15/16 (Barycz, Bóbr) (the
   author's decision of 2026-11-16); each member opens its next cycle
   (`X.Y.(Z+1).dev0`) with its next change. When a tool renames a command,
   change its `routes` and run `agents` (CLAUDE.md). The patch scope, defects
   only, approved by the author on 2026-11-17, producers first:
   - Obserwator 3.0.1: done on `fix/3.0.1` (Next 6); not released yet, by
     the author's decision.
   - Kartograf 0.8.1: C1, its part of C5, E5a-01, GEO-02 (to be checked),
     E2-04.
   - Hydrolog 0.8.1: its part of E5b-08, E5b-07 (at least a notice), the
     per-period `OverflowError` of `hydrometrics rating-curve`, the rating
     curve fit that does not converge (to be examined), the threshold of 0
     or below 0 of `low_flow_sequences`, and its GUI report #1 (the
     horizontal axis of „Obliczenia składowe” shows absurdly small values).
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
   - Archiwista 0.3.1: E7-01, E2-06, E2-05, the tests C2, C3, C6.
   - Each patch is made in a new worktree of its repository on a topic
     branch `fix/<topic>` from `origin/develop` (DEV-3.1), as Obserwator's
     `fix/3.0.1`.
   - Then a new candidate and Nogat 0.1.1. Minor releases with a plan: S5
     (the cut to the area), large basins, E3-03, E5b-02, E5b-04 (Hydrograf
     0.6.0), E2-09/KH (Kartograf), E2-10 and E7-02 (Archiwista), E3-02 and
     the features of Obserwator's „Release 3.0.1” (3.1.0, waits for the
     author).
8. Nogat after `v0.1.0`: `develop` opens its next cycle (`0.y.z.dev0`,
   REL-1.1) with its next change, and the standard's next version on
   `develop` is 1.1 (HUB-6.1); the next candidate is the first that the
   workflow `verify-candidate` verifies from `main` on the three runners
   (REL-6.5); deleting the merged topic branches `feature/verify-candidate`
   and `chore/candidate-6` is the author's (step 7 of
   `docs/plans/2026-10-20-first-release-set.md`).
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
    kit). GUI platform stage 2, the GUI hub,
    `docs/plans/2026-11-01-nogat-gui-platform.md` (`Approved: pending`).
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
