# Plan: Obserwator's data in Archiwista, read and fetched, on the test server

Not approved for implementation. Written on 2026-11-05 at the author's request („przygotuj nową gałąź dla tej współpracy i napisz plan, ale nie wdrażaj go”), on branch `plan/obserwator-in-archiwista`; work starts after the author approves it. Archiwista's own plan of steps 1 and 2: `docs/plans/2026-11-05-obserwator-actions.md` on its branch `feature/obserwator-actions`.

Requirements: HUB-5.2 (producers before consumers), ECO-054, ECO-057, Archiwista SPEC 12.2 (KB-1..KB-5 as the model) and 12.7 (IMGW-1..IMGW-13, IMGW-21), release v0.5 „IMGW stations” of the SPEC (section 14).

## Goal

A person on Archiwista's test server (:8090, `archiwista-test.debever.pl`) browses IMGW-PIB stations and series of an Obserwator store, and fetches or refreshes that store's data from Archiwista as for Kartograf: the plan window, a job, the project's check, re-pin and restore of pinned IMGW versions.

## Facts (2026-11-05)

- Archiwista `develop` `4ac2933` reads an Obserwator store through its plugin `archiwista.adapter.obserwator` (extra `obserwator`, Obserwator `1ee5457` of `candidate-1`): sources, scan, station catalog, series index and values, `command_for_version` (IMGW-21). 128 contract tests pass. A live smoke on 2026-11-05 (a throwaway store with `pl.imgw.hydro_daily` 2024 and the IMGW-PIB catalog) showed station 149180010 and its Q series of 2024, 366 of 366 days.
- The plugin has no `ActionAdapter` (`src/archiwista/sources/protocol.py:355`): `archiwista commands list` lists Kartograf only, so nothing in Archiwista fetches IMGW data; `docs/PROGRESS.md` says „the Obserwator actions are planned for v0.5”.
- Obserwator `1ee5457` has what such an adapter calls, offline or on a store: `data_commands`, `list_commands`, `command_schema`, `check_command`, the parsing and formatting of command lines, `check_store` and `sync_store` with `plan`, `on_progress` and `cancel` (`src/obserwator/store/sync.py:782, 1089`), `obserwator-plan/1`, `command_for_version`.
- :8090 runs `b2307ee` without the extra; its `config.toml` names only a Kartograf store; no Obserwator store exists on the server. The registry's edge Archiwista → Obserwator is `planned`.
- IMGW-PIB archives are national files (a year or a month per file), so an area does not narrow what is fetched; stations of an area are a filter of the views.

## Decisions

| # | Decision |
|---|---|
| D1 | Archiwista's Obserwator plugin implements `ActionAdapter`: `commands` (Obserwator's store-writing data commands: `store sync`, `store catalog`, the series build, as `data_commands` lists them), `parse`, `validate`, `format`, `check` (`obserwator-plan/1` → `ActionPlan`), `run` (with `plan`, progress, cancel through `KeyboardInterrupt`), `scope`, `narrow`. `availability` reports no product (`availability_products()` empty) unless Obserwator offers an availability report; `with_area` refuses with `no_area_option` (national files). No Obserwator change is planned; a missing Obserwator function becomes a `request` in Obserwator, not a workaround. |
| D2 | The project jobs check, re-pin and restore work for pinned IMGW versions through `command_for_version` + `check`/`run`, as for Kartograf (A-ADR-049 D5). |
| D3 | The plan window and the forms take Obserwator's commands from the catalog like Kartograf's; Polish texts from Obserwator's catalog (`lang="pl"`). |
| D4 | Test server: Archiwista `develop` with the extra `obserwator`; the store `zespol` gains `obserwator = "/data/nmt/archiwista-obserwator"` (separate from the Kartograf store, never nested); first data fetched by Archiwista's own job: the IMGW-PIB station catalog, `pl.imgw.hydro_daily` 1951–2024 and its series. Backup and rollback as in the deploy of 2026-11-04. |
| D5 | The registry's edge Archiwista → Obserwator becomes `active` with `via: [library, store]` once D4 is live. |

## Steps

| # | Project | Change | Verified by |
|---|---|---|---|
| 1 | Archiwista | D1–D3: adapter actions, jobs, plan window; tests offline on `obserwator.testing` stores and recorded plans; one `live` test | gate; a throwaway instance runs a real `store sync` of one year from the plan window |
| 2 | Archiwista | D4: deploy on :8090, the Obserwator store, the first fetch through Archiwista | `archiwista status`, station card and chart on the public host; GPT browser test |
| 3 | Nogat | D5: registry, ECOSYSTEM_MAP, AGENTS.md regenerated, PROGRESS | Nogat gate |

## Results

Pending.
