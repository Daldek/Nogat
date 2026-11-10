# Progress

Audited on 2026-10-28: local branches, worktrees, recent commits, manifests, project progress
documents and `git ls-remote --heads --tags origin` (tags checked for Nogat). No tests or gates
were run; earlier gate results below are historical evidence, not verification of the current
heads. Items 4, 6, 7, 8 and 9 of Next and the changes from 2026-11-01 to 2026-11-03 are current
as of 2026-11-03 and supersede the project rows below where they differ. IMGWTools is called
Obserwator from v3.0.0 (ECO-057); dated sections keep the old name.

## Status

| Component | State | Note |
|---|---|---|
| Standard 1.0 | in progress | not yet published to `main`; tagged `std-1.0` when it is (HUB-6.1); the drafts called 2.0 and 2.1 on `develop` are 1.0 (ECO-056) |
| Registry and schema | done | `ecosystem.yaml`, `schemas/ecosystem.schema.json`; follows the branches of Kartograf, Obserwator, Hydrolog and Hydraulik since 2026-10-25 (CHANGELOG); `routes` name the commands of those branches, of Retman and of Archiwista; Obserwator's checkout is the directory `IMGWTools`, its repository's name (HUB-3.1) |
| `validate`, `map`, `agents`, `deps`, `drift` | done | `scripts/ecosystem.py`, errors by the registry (HUB-4.8) |
| Hub gate and CI | done | `scripts/gate.sh` on `uv.lock`, tests in `tests/` |
| Standard checks | done | `uv run scripts/ecosystem.py standard`, in the gate |
| Contradictions in standard 1.0 | done | ECO-042 to ECO-049 and consistency fixes |
| Canonical agent-interface schemas | done | `schemas/agent/`, contract tests (ECO-050) |
| Hand-off schema `nogat-handoff/1` | done 2026-11-02; `node_provenance` 2026-11-10 | `schemas/exchange/handoff-1.schema.json`, contract test; item 6 of the platform plan, approved ahead of the rest as N1 of Hydrolog's GUI; the origin of each node of a network added as step 1 of `plans/2026-11-10-node-provenance-in-handoff.md` (Next 13) |
| Hydrolog's GUI in the registry | done 2026-11-02, branch `feature/hydrolog-gui-registry` | N2 of Hydrolog's GUI: the optional interface `gui` (HUB-2.1), Hydrolog's `hydrolog gui serve`, the route „Open Hydrolog's GUI in the browser” and `hydrolog-gui` in its `provides`; `AGENTS.md` and the map regenerated |
| Data-output convention (ECO-051) | done in Nogat | DEV §19 and AGI-3.4 and related rules, store markers in the registry, plan `docs/plans/2026-10-24-data-output.md` with the state of every project (Results, 2026-10-25) |
| Integration dry run | done 2026-10-25 | historical baseline: six heads, four cross-tool flows and eight failures with owners (`docs/plans/2026-10-25-integration-dry-run.md`). The later final integration plan records the fixes and the pending post-fix repeat |
| Final integration run | initial run done 2026-10-25; repeat pending | F1 to F8 have owners and fixing commits and are fixed and pushed; F6, the history rewrite, is done (2026-11-03, ADOPTION_PLAN phase 1) and closed 2026-11-09 without a further rewrite (`docs/plans/2026-10-25-final-integration.md`, Fixes). Retman, Hydraulik, Hydrograf and Archiwista are re-pinned to the rewritten commits and pushed. Hydrograf (`affine<3` until pyflwdir 0.5.13, its ADR-062) and Archiwista (`affine>=3`) remain incompatible in one environment; the repeat must run them apart |
| Generated `AGENTS.md` (HUB-4.3) | done | `uv run scripts/ecosystem.py agents` from the `routes` of the registry (HUB-2.9, ECO-052), `agents --check` in the gate; the guide links name `main`, so they resolve once each project is merged there (Obserwator after the rename of `master`) |
| One set of pins (HUB-4.9, REL-6.4) | in progress | `release-sets/candidate-2/` since 2026-11-10 (Kartograf, Obserwator, Hydrolog and Retman); every consumer applied it the same day and `set check` exits 0 (Next 10). Tooling: `set check`, `apply`, `bump`, `readme` (plan `docs/plans/2026-11-03-one-pin-set.md`); `verify-candidate` (REL-6.5) does not exist yet |
| `nogat` package (HUB §7) | planned | |
| Adoption in the projects | in progress | current branch evidence is listed below; the 2026-10-25 adoption and data-output snapshots are historical, not current waiting lists. The post-fix integration repeat and first release set remain open |

### Project evidence on 2026-10-28

Heads below were compared with `origin`; a topic branch being published does
not mean it is merged or released. Sources are each branch's
`docs/PROGRESS.md`, recent commits and dependency manifests.

| Project | Audited branch and head | Progress and remaining work |
|---|---|---|
| Nogat | `feature/data-output`, `2ccea34` before this audit | Latest commit adds the GUI visual-identity backlog. The standard remains off `main`; `origin` has no tags. Contribution files and legacy template replacement remain open |
| Kartograf | `feature/data-output`, `a4b92916` | Plain mode is implemented at library and command-layer level; its own Next 4 still leaves a real-CLI subprocess smoke and plain-mode prose open. Later commits add `store_state`, shared task arguments for `project add`, project-lock reasons, report-cache reuse and PL-2000 sheet outlines. Message-catalog migration is closed; `kartograf mcp` and domain JSON Schemas remain open |
| IMGWTools | `feature/data-output`, `a28783d` | Data-output migration, MCP stdout fix, `parse_command`/`format_command` and catalog examples are recorded as done. Live plain-mode smoke, English documentation and release work remain open |
| Hydrolog | `feature/routing-schematic`, `2a5ba1a` (routing worktree) | `hydrolog.testing` exists (introduced at `6bf2c5f`); network objects, rainfall/runoff and SVG schematics are implemented on stacked routing branches. The main checkout remains at `chore/nogat-2.1`, `8ae4a6d`; inspecting that checkout alone misses this work. Merge, CLA, notebook translations and release remain open |
| Retman | `feature/kartograf-data-output`, `cc6d1ee` | Both producer migrations are done on the branch. Manifest pins Kartograf `d11f6219` and IMGWTools `71bae77`, not their latest heads. The Status table's older pins and “nothing is pushed” statement are stale; Next 2 has the matching pins. Documentation translations and the evaluation on the 630-command set remain open |
| Archiwista | `feature/kartograf-data-output`, `b7775bb`; `feature/v0.4-team`, `815c8b2`; `feature/v0.4-review`, `8118c33` | Data output, English documentation and the message catalog are done on the branches. v0.3 actions and station comparison (I8, `b7775bb`) progressed beyond the integration baseline. The data-output manifest now pins Kartograf `a4b92916`, but IMGWTools stays at `71bae77`. v0.4 team/shared/review work is separate; D7 refusal/sign-in auditing is done at `815c8b2`, not the whole security checklist or T12 |
| Hydrograf | `feature/producer-heads`, `f9d2118` | Producer migrations, quality tooling and contribution files are implemented; CLA, translation/REST gaps and history work remain open. Pins remain Kartograf `d11f6219`, IMGWTools `71bae77`, Hydrolog `2a5ba1a`; `affine<3` is retained. The checkout is on older `feature/kartograf-wykorzystanie`, `bc0b438`; the running Docker image is not evidence of the newer branch being deployed |
| Hydraulik | `feature/sfincs-swmm`, `46f7fd2` | Extracted SFINCS/SWMM implementation and Hydrolog hand-off are committed; pins are Hydrolog `2a5ba1a` and IMGWTools `71bae77`. Contract tests using `hydrolog.testing` are present, not run in this audit. The old claim that Kartograf has no plain mode is stale; the live terrain flow still needs verification. The older uncommitted PoC and documents stay local by the author's choice in this audit |

DEV-10.6 follow-up: `hydrolog.testing` is no longer missing, and since
2026-11-09 the registry lists `hydrolog-testing` on Hydraulik's Hydrolog edge.
`kartograf.testing` already builds a GeoTIFF as part of its fixture store;
`imgwtools.testing` exports store fixtures, not a dedicated PMAXTP builder.
Do not treat the remaining file-contract work as uniformly absent or done.

### Changes on 2026-10-29 and 2026-10-30

These rows supersede the Archiwista and Hydrograf rows above where they
differ. Gate results named here were run in this session.

| Project | Branch and head | Change |
|---|---|---|
| Archiwista | `feature/v0.4-team`, `df7e71e`, pushed | Plan v0.4 complete: T12 (three-person acceptance, every C9 route called by each role against the matrix, ASVS checklist, LAN runbook) and review defects D6 and D10. Full gate green on `54cded3` (2556 passed, coverage 93.53%) after four fixes it found (`c8d4b5e`, `bbe223d`, `96ddda8`, `54cded3`; the last a real Esc race in the web shell). Decided by the author's delegated approval: the five checklist deviations are accepted for LAN use; v0.3 and v0.4 are released separately, v0.3 first, after the first release set. Open: the author's three-computer run of the runbook. Git: `feature/v0.4-review` and `feature/v0.4-shared` deleted locally (both contained in `v0.4-team`, still on `origin`), their worktree removed, every branch tracks its own `origin` branch, `feat/mockup` pushed as a backup |
| Hydrograf | `feature/logowanie-testow`, `8d4d2f8`, pushed | Request logging and rotation, nginx bound to loopback, the tester guide; the test service runs this branch (Kartograf 0.7.0, IMGWTools 2.1.0, Hydrolog 0.6.3), not `feature/producer-heads`. Merging it into `producer-heads` conflicts in `README.md`, `backend/api/main.py`, `docs/CHANGELOG.md` and `docs/PROGRESS.md`. A Kaczawa bootstrap (183M cells) was OOM-killed twice; a smaller area (66M cells) succeeded and is served. Memory plan F1–F7 (~19 GB → ~9 GB, results identical) and clipping of shown data to the analysis boundary (high priority) are backlog items in its `docs/PROGRESS.md` and `docs/TECHNICAL_DEBT.md`. Before its first push the branch history (`develop..`) was rewritten to replace a share path and a LAN address with placeholders |

Git hygiene audit (2026-10-29, after `git fetch`): Hydraulik has uncommitted
documents on `develop` and an unpushed PoC worktree branch; IMGWTools has two
stashes (one is REST C5 work in progress) and `fix/archiwista-compat`, most
likely superseded by `fix/archiwista-compat-2`; Hydrolog's
`feature/v1-catalog-mcp-hsg` is merged and can be deleted; local
`backup/*` branches in Hydrograf and IMGWTools have no `origin` copy.

### Changes on 2026-11-01 and 2026-11-02

These rows supersede the rows above where they differ. Nothing here is
merged or pushed.

| Project | Branch and head | Change |
|---|---|---|
| Hydrograf | `feature/visual-identity`, `70beff6`; production on 127.0.0.1:8080 | Backup of production in `/data/nmt/hydrograf-backup-2026-11-01/` (verified). The shown data are clipped to the Kaczawa catchment above 51.222825, 16.179380 (790.57 km², segments 159 of 870; a first clip to 813.17 km² took in part of the Czarna Woda), which closes the clipping item of 2026-10-29. New: the group „Wyniki analiz” (manifest `hydrograf-results/1`, `8377c23`, `5449d70`) with SFINCS run 2; the ISOK flood hazard map (MZP) from the Wody Polskie WMS (`0e12eca`, `6aea0d4`); versioned asset URLs and no-cache HTML, because Cloudflare kept old JS (`357b997`); the water surface of results on the terrain profile (`9d281b8`, `2c4aff7`, `70beff6`); the profile finishes on phones (`08df412`); the guide's „Na start” and a welcome dialog (`2ba7cc9`, `30a4164`, `8847fdf`). The frontend test report (5 medium findings, no high) and the open choices go to its `docs/PROGRESS.md` |
| Hydraulik | `feature/sfincs-swmm`, `46f7fd2` (code unchanged) | SFINCS on the Kamiennik catchment (37.22 km², segment 21911, the Świerzawa dam without an outlet, 5 m grid of 1,491,703 cells), run outside the repository. Run 1 (12 h, p = 1 %, 105 mm) is useless: with the default `huthresh` 0.05 water under 5 cm did not flow. Run 2 (`huthresh` 0.001) is published in Hydrograf. Run 3 (24 h, p = 1 %, 134.5 mm, seven cross sections) started 2026-11-02 01:03; its sections are then compared with Hydrolog's hydrology. Eight findings for `hydraulik` (among them `huthresh`, `dtout`/`dtmaxout` and cross sections missing from `model build`, a wrong summary when `dtmaxout` < `tstop`, no water level in `results export`) belong in Hydraulik's `docs/PROGRESS.md` |
| Hydrolog | `feature/gui`, `a328656` | The GUI of its plan `docs/plans/2026-11-02-hydrolog-gui.md` is implemented, waves A to C (its `docs/PROGRESS.md` and the plan's Results). `hydrolog gui serve` runs as the persistent service `hydrolog-gui` on 127.0.0.1:8070, where a Cloudflare tunnel points; the author sets up its Access |
| Archiwista | `feature/archiwista-projects`, `e9a18b9`; paused by the author | The fix „obszar projektu nie daje się użyć do pobierania i sprawdzania danych” is ready and not committed: the index holds commit 1 (backend), the unstaged changes commit 2 (web). Its gate stopped on a hang of `tests/e2e/test_guide.py` in Firefox. The public instance on :8090 still runs `dd4268c`; the welcome dialog and the new guide wait. Leave its working tree and index as they are |
| Nogat | see Next 7 | The Hydrolog mockup (`3d6608f`, `dc8cee4`, `ed3473c`), the pointer plan (`7719b1d`), N1 (`a01097c`) and N2 (`33920ec`) |

### Changes on 2026-11-02 and 2026-11-03

These rows supersede the rows above where they differ.

| Project | Branch and head | Change |
|---|---|---|
| Hydrograf | `develop`, `d62646c` (version `0.5.0.dev0`), pushed; production in place since 2026-11-02 22:18, rebuilt from `aafeb5a` on 2026-11-03 | The v0.5.0 candidate. FROZEN until the author merges it into `main` and tags `v0.5.0`: only critical API-breaking fixes or glaring bugs; one exception so far, `certifi` 2026.10.23 for PYSEC-2026-4320 (`a6fe779`, production rebuilt; Archiwista `34e83f4` the same). Pins Hydrolog `1708a09` (`fix/snyder-recession`, pushed: Snyder's unit hydrograph runs to the end of its recession, peak = qpR), Kartograf `eab8612`, IMGWTools `71bae77`, by commit in `[tool.uv.sources]`. Rollback image `hydrograf-api:pre-0.5.0`, backup `/data/nmt/hydrograf-backup-2026-11-02/`. Production shows the SFINCS result `sfincs-kamiennik-24h-p1` (24 h, p = 1 %, Kamiennik; reservoir maximum 281.43 m). Reads Archiwista's project sets (`--project`/`--set`, closed sets only, ADR-067: H1 of item 8); the bootstrap of the full area from a set (H2, S5) is postponed until after v0.5.0 |
| Archiwista | `feature/archiwista-projects`, `4027755`; on :8090 since 2026-11-03 ~00:00 | The project-area fix (A1) and draft sets, open or closed with `pins_sha256`, one producer per set (A2), deployed with `TMPDIR` on disk (A3). The rebuild of the index to schema 17 dropped the sessions, the job history and 18 drawn rectangles; they are kept in `/home/claude-agent/data/archiwista-public/backup-2026-11-02/index.sqlite`. Renaming `archiwista-state/2` to `/1` is deferred to the release preparation (the author's rule: identifiers `<name>/<N>` not yet released on `main` stay at `/1`) |
| Hydrolog | `feature/gui`, `a328656` | Served as the omp service on 127.0.0.1:8070 behind a Cloudflare tunnel; `fix/snyder-recession`, `1708a09`, pushed and pinned by Hydrograf |
| Nogat | `develop`, merge `ed3b8a0` (2026-11-03) | The whole stack (`fix/hub-gaps` … `plan/archiwista-sets-hydrograf`) is merged into `develop` and its topic branches are deleted, except `feature/hydrolog-gui-mockup`, which the shared checkout keeps for the mockup on :8765. The sets plan records A1 to A3 and H1 as done, A4 and A5 waiting for the author, H2 and S5 postponed after Hydrograf v0.5.0 (item 7) |

Ports of the local GUIs, settled 2026-11-02: 8000 IMGWTools, 8070 Hydrolog (`hydrolog gui serve`), 8080 Hydrograf, 8090 Archiwista; the `nogat-specimen` container keeps 8765.

### Changes on 2026-11-04

These rows supersede the rows above where they differ.

| Project | Branch and head | Change |
|---|---|---|
| Obserwator | `develop` `84e43a1` (3.0.0.dev0) | v3.0.0 blocker B6 done: the result, error and catalog documents of standard 1.0, `--json`, paging by cursor (ADR-010; plan `2026-11-04-obserwator-agent-contracts.md`, Results). CI green on the three systems |

### Changes on 2026-11-05 and 2026-11-06

These rows supersede the rows above where they differ. Details: Results of `plans/2026-11-05-official-tc-inputs.md` and `plans/2026-11-05-archiwista-series-to-hydrolog.md`, and each project's `docs/PROGRESS.md`.

| Project | Branch and head | Change |
|---|---|---|
| Nogat | `develop` `9aa55c9` | `candidate-1`: Hydrolog `1ffcd6b` (Kartograf `9deaa31`, Obserwator `1ee5457` unchanged); `set check` ok. The example of `nogat-handoff/1` carries the longest flow path (`8727f6e`). The series plan merged (`269c388`), its Results filled. CI was red on every push since 2026-11-04: `tests/integration/test_check_commits.py` inherited CI's `GATE_CHECK_AUTHOR=0`; the test now pins the check's settings; CI green |
| Hydrolog | `develop` `88dbe71`; :8070 serves `33b5568` (a systemd user unit) | Time of concentration from the inputs its source defines (ADR-0019): `flow_path_length_km`, `flow_path_slope_m_per_m`, no substitutes; `NashIUH.from_tc` removed. „Wczytaj z Archiwisty” (ADR-0020); fixes for macOS and Windows (MIME types of the GUI's scripts, LF reports, the guide on a phone, two racy browser tests). CI green on Linux and macOS; Windows reports without blocking until its port (the author's decision of 2026-11-06, deviation DEV-7.7 in Hydrolog's CLAUDE.md) |
| Hydrograf | `develop` `520f886`, production (since 2026-11-05 12:53 UTC, updated in place the same day) | tc only through Hydrolog; flow path heads, overland segments and channel sources measured (ADR-070, migration 004, backfilled); thresholds 1 and 10 km²; PMAXTP depth as the watershed mean by Thiessen polygons (ADR-069) with an optional areal reduction factor; tester reports #13, #14, #16, #20, #23–#27, #35, #37, #39, #40; the author's review: boundary flow path from the watershed's boundary cells, full unsimplified lines, legend „Zlewnia” (plan Results 5). Hydrolog's comparison of the hand-off reads „zgodny” for every tc method. Rollback `/data/nmt/hydrograf-backup-2026-11-05-v050/` (image `hydrograf-api:pre-v050`, runbook §9). No `v0.5.0` tag yet: the author continues the review |
| Archiwista | `develop` `cd29b6f`; :8090 runs it since 2026-11-06 | Merged and deployed: Obserwator's commands, monthly and annual charts (A-ADR-051), the map's station products, the series hand-off to Hydrolog (A-ADR-052) with a choice of data and variable; the map draws a station catalog without series (ČHMÚ's `store catalogs`). The store `zespol` lives on the SMB share `/mnt/magazyn/agent-tmp/archiwista-zespol/`. CI green for the first time (`8f34a4c`): the gate's limit 30 → 90 min, the run without the extra `obserwator` fixed |

### Heads and pins on 2026-11-10

After `git fetch`; pins at each consumer's integration branch. These rows supersede the rows above where they differ. `set check` against `candidate-2`: every pin `ok`, exit 0.

| Project | Head | Pins and deployment |
|---|---|---|
| Kartograf, Obserwator | `develop` `d0990c8`, `f9f4ee7` | members of `candidate-2`; pin no project |
| Hydrolog | `develop` `759d7ef` | member; Obserwator `f9f4ee7` |
| Retman | `develop` `320a7d6` | member (`set bump` from `a9c04ad`); Kartograf `d0990c8`, Obserwator `f9f4ee7`, Hydrolog `759d7ef` |
| Hydrograf | `develop` `fd0b533` (the set applied in `01ab00a`) | the set's Kartograf, Obserwator and Hydrolog. Hydroni runs `fd0b533`; production runs `894810c` (since 2026-11-10) with Kartograf `9deaa31`, Obserwator `1ee5457`, Hydrolog `4fad769` until its next rebuild (images only) |
| Hydraulik | `feature/sfincs-swmm` `d0f3938` | Obserwator `f9f4ee7`, Hydrolog `759d7ef` (its CN of water follows Hydrolog, 98); Kartograf through its CLI, not pinned |
| Archiwista | `develop` `a656ee1` | Kartograf `d0990c8`, Obserwator `f9f4ee7` |

## Next

1. Close the remaining data-output documentation and CLI smoke in Kartograf,
   the live plain-mode smoke in Obserwator, and the file-contract/registry
   follow-ups above (each project in its own session, DEV-3.4).
   Reconcile consumers' stale progress text with their manifests; newer
   producer commits do not automatically replace reviewed pins. Prepare
   the first release set only after the remaining integration work.
   When a tool renames a command, change its `routes` and run `agents`
   (CLAUDE.md).
2. Repeat the final integration run at explicitly recorded heads, including
   the changes after 2026-10-25 in Kartograf, Obserwator and Archiwista,
   with Hydrograf and Archiwista apart and the two flows of F2. Record the
   outcome in the data-output plan; no repeat was performed in this audit.
3. Publish 1.0 to `main` with the author (ADOPTION_PLAN 0.3, 0.4). Numbers
   count from `main` (ECO-056): plan
   `docs/plans/2026-11-03-numbering-from-main.md`, approved 2026-11-03; step
   1 (Nogat) done on `plan/numbering-from-main`, not merged; steps 2 to 5
   change the projects' references before their next merge into `main`
   (Archiwista's `archiwista-state/2` back to `/1`); step 6 is this
   publication.
4. Visual identity (user request, 2026-10-28): plan
   `docs/plans/2026-11-01-visual-identity.md`, approved 2026-11-01, steps 1
   to 4 done on `feature/visual-identity`: `design/` (tokens, eight marks,
   guidelines, specimen), DEV-15.3 and ECO-055, the Hydrograf mockup
   (approved). Step 6: Hydrograf's `feature/visual-identity` (AMC, an own
   rainfall series, CN to 0.1, `GET /api/layers`, the delineation preview and
   verified (i) texts) is merged into its `develop`, which runs in
   production on port 8080 (changes on 2026-11-02 and 2026-11-03); the
   review instance on 8081 is removed. The specimen and mockup stay on the LAN through the
   `nogat-specimen` container (192.168.88.9:8765, outside ufw). The Hydrolog
   mockup (`feature/hydrolog-gui-mockup`, not merged, not pushed) is revised
   after the author's review: no variants and no compute button in the
   hydrograph section, the network schematic vertical, node settings on
   click; the author accepted its choices on 2026-11-02. Its implementation
   is planned in Hydrolog (`docs/plans/2026-11-02-hydrolog-gui.md` on
   Hydrolog's `feature/gui`, from `feature/routing-schematic`; approved
   2026-11-02), with this repository's pointer
   `docs/plans/2026-11-02-hydrolog-gui.md` (branch `plan/hydrolog-gui`):
   Nogat publishes the `handoff-1` schema (N1, done on `feature/handoff-1`)
   before Hydrolog's hand-off slice and adds Hydrolog's `gui` interface to
   the registry (N2, done on `feature/hydrolog-gui-registry` after
   Hydrolog's wave A, `e004a5d` on `feature/gui`). Hydrolog's waves A to C
   are done (`a328656`) and its GUI is served on 127.0.0.1:8070 behind a
   Cloudflare tunnel (changes on 2026-11-01 and 2026-11-02). Next:
   Archiwista and Obserwator adopt the identity (steps 5 and 7). The platform draft
   `docs/plans/2026-11-01-nogat-gui-platform.md` (author's decisions A1–A5,
   B1–B6 recorded; 10 questions open) is deferred to a later session by the
   author; it may replace steps 5 to 7.
5. Archiwista's release (decision D2 of the projects plan, 2026-10-31,
   replacing the separate v0.3 and v0.4 of 2026-10-29): one release holding
   v0.3, v0.4 and the projects, after step 5 of that plan, outside the first
   release set (D3, REL-5.4).
6. Projects move to Archiwista (ECO-054): plan
   `docs/plans/2026-10-31-archiwista-projects.md`, approved 2026-10-31 with
   D1 to D7 as recommended; steps 1 to 5 are done on
   `feature/archiwista-projects` (the plan's Results). Pushed with green
   gates: Kartograf `eab8612d` (also ADR-058: `--geometry` by feature shape,
   GeoJSON), Obserwator `8cd6844c`, Retman `5c3be44` (still pins Kartograf
   `dbcfe5bb`; re-pin before the release). Archiwista `e9a18b9` is pushed
   with a green full gate (2026-11-01: 2719 passed, coverage 93.63%; its only
   change after `dd4268c`, which runs on the author's test server, makes the
   doctor test independent of port 8090). Open: the
   release (step 6); no branch is merged. Gaps found in
   use: Kartograf KD-3/KD-4 (Archiwista's "U źródła" offers only nmt, nmpt
   and laz, so BDOT10k and orthophoto are downloaded by pasting a Kartograf
   command) and KH (plans show no size); Kartograf's LAZ sidecars carry no
   survey work, so Archiwista's "pobrane" badge never matches LAZ (a
   `request` issue for Kartograf, not filed: no `gh` on this machine). The
   final integration repeat (item 2) must use these heads. Paused by the
   author on 2026-11-02 and finished since: the fix of the project area and
   draft sets are deployed on :8090 at `4027755` (steps A1 to A3 of item 8's
   plan; changes on 2026-11-02 and 2026-11-03).
7. Merges and releases (DEV-3.3). Nogat's stack (`fix/hub-gaps` to
   `plan/archiwista-sets-hydrograf`) is merged into `develop` (`--no-ff`,
   `ed3b8a0`, approved by the author on 2026-11-03, no PR by the author's
   decision). The merged topic branches are deleted locally and on `origin`
   except `feature/hydrolog-gui-mockup`, kept because the shared checkout
   serves the mockup on :8765. The GUI platform plan
   (`docs/plans/2026-11-01-nogat-gui-platform.md`) stays `Approved:
   pending`. The tools' branches await the author's review and release:
   - Hydrograf: v0.5.0 frozen on `develop` (`f3404cd`, pushed; code of
     `d62646c` with the producer pins and hashes of the rewrite); next,
     `develop` into `main` and the tag `v0.5.0`, both the author's.
   - Archiwista: `feature/archiwista-projects`.
   - Hydrolog: `fix/snyder-recession`, `feature/gui` (with `chore/nogat-2.1`
     and the routing stack beneath it; its `docs/PROGRESS.md`).
   - Hydraulik: `feature/sfincs-swmm`.
   - Kartograf: v0.8.0 FROZEN on `develop` (`1ed40b9a`, pushed, 2026-11-03;
     code of `882a1c3e`, then only the hashes of the rewrite in its docs):
     only fixes of critical defects or API breaks until the tag; the
     Windows/macOS fixes are in, two Windows test expectations and the
     macOS run wait for 0.8.1 (its `docs/PROGRESS.md` Next 1); next,
     `verify-candidate`, the release commit, `develop` into `main` and
     `v0.8.0`, merged locally.
   - Obserwator (repository `IMGWTools`): branches renamed `main`/`develop`
     on 2026-11-03 (GitHub rename API, `main` the default branch); `develop`
     has the English documentation (one CHANGELOG `[Unreleased]` against
     v2.1.1) and a green CI matrix (ubuntu, macOS, Windows; Windows fixes of
     the CLI output, pipes and the agent guide). Remaining for v3.0.0: the
     rename to Obserwator (item 9), AGI-4.1/ERR-3 conformance (B6),
     `SECURITY.md` and the GitHub settings, `3.0.0.devN`, the author's
     review; its `docs/PROGRESS.md`.
8. Archiwista's sets as Hydrograf's only Kartograf input (the author's
   variant B, 2026-11-02): plan
   `docs/plans/2026-11-02-archiwista-sets-for-hydrograf.md` on
   `plan/archiwista-sets-hydrograf`, decided by the author on 2026-11-02
   except D6 (the deploy window on :8090, nobody deploys before it) and the
   new D12 (one producer per draft set, recommended). Order b: A1, the area
   fix with its gate; A2, draft sets in Archiwista („zestaw w budowie”,
   `state`, `closed_at`, `closed_by`, `pins_sha256`; a closed set frozen);
   A3, the deploy; A4, the author moves Kaczawa to `projects/kaczawa`; A5,
   the author builds the set (NMT 5 m 2020 by the area, 205 sheets; BDOT10k
   by the area; HSG for Poland's box) in the web interface and closes it;
   then H2 and S5. Hydrograf's H1 may proceed in parallel; consumers read
   only closed sets (N2's rule for `archiwista-project/1`). Found on the
   way: BDOT10k, SoilGrids and HSG leave files UID 999 reads (Hydrograf's
   ADR-066 fact 4 names the wrong function; the mode defect is Kartograf's
   RCN and WFS cut-outs), and the clip catchment leaves Kaczawa's area by
   2.87 km², its outlet by 972 m; about 935 m² of it lie outside the 205
   sheets, S5's tolerance. State on 2026-11-03: A1 to A3 done (`4027755` on
   :8090), H1 done (in Hydrograf's `develop`, `1794f76`); A4 and A5 wait
   for the author; H2 and S5 are postponed until after Hydrograf v0.5.0.
9. IMGWTools is Obserwator (ECO-057, plan `docs/plans/2026-11-03-imgwtools-to-obserwator.md`): done everywhere (changes on 2026-11-04).
10. `candidate-2` is applied by every consumer (2026-11-10, heads and pins above; Retman's
   member bumped to `320a7d6`). Left: production Hydrograf's rebuild on `develop`; Hydrolog
   v1.0.0 waits for Obserwator 3.0.0's tag (producers first, HUB-5.2) and `verify-candidate`.
11. Feedback „Zgłoś uwagę” in Archiwista and Hydrolog: merged and deployed
   with their productions; Hydrograf's 26 reports are backed up in
   `/data/nmt/hydrograf-feedback-backup-2026-11-03T2319/`.
12. Retman covers every basic route of the registry for Kartograf (10
   operations), Obserwator (19) and Hydrolog (9); a smoke of all 38 with the
   real tools at the set's commits: 43 cases planned, 41 run, 2 skipped as
   large downloads, none failed (its `docs/PROGRESS.md`). Eval rows of the
   new operations are unmeasured: no model server on this machine.
13. The origin of each node in the hand-off (B7 of Hydrograf's network delineation): plan `docs/plans/2026-11-10-node-provenance-in-handoff.md`,
   approved 2026-11-10; step 1 done (`node_provenance`, still `/1`). Next: Hydrograf's `delineate-network` (step 2) and Hydrolog's Sieć
   (A6, step 3) copy the schema; step 4, the registry edge, once step 2 is merged.

## Open questions

- Publishing 1.0 to `main` (tag `std-1.0`, Next 3) and replacing the legacy
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

Decided by the author on 2026-11-09 (CHANGELOG): F6 is closed; the rewrite of
2026-11-03 (`git-filter-repo` a40bce548d2c, bundles in
`~/backups/history-rewrite-2026-11-03/`; every commit by `Daldek
<git@debever.pl>`, PL1B5J kept in IMGWTools, no AI trailer) stands and
Hydrograf's `develop` and IMGWTools are not rewritten again, because
Hydrograf's rollback procedures name their hashes (`f772f4e`, `08d8190`) and
`candidate-1` names Hydrolog's; other branches (Hydrolog `feature/gui`,
Kartograf `feature/pgw`) keep old hashes in their docs, and IMGWTools pull
request #1 keeps old commits reachable until GitHub Support removes them.
Hydraulik stays `research` until `feature/sfincs-swmm` is merged; its roads
come from BDOT10k through Kartograf (README `d9d8536`), so its entry keeps
no direct data source (HUB-2.7) and its Kartograf edge names the BDOT10k
GeoPackage. The merge order of `fix/hub-gaps` and `feature/data-output` is
stale (both in `ed3b8a0`). The dry run and the final integration plan carry
the data-output plan's approval (2026-10-24). `SECURITY.md`,
`CONTRIBUTING.md` and `CONTRIBUTORS.md` are adapted from Archiwista's, and
the entry left `CLAUDE.md`'s Deviations.
