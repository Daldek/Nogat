# Plan: providers named by their national acronyms, one way of naming a location's source, the CSV's duplicate attribution columns removed

Approved: pending (requested by the author on 2026-11-21: „mylse, ze bedzie lepiej wszedzie korzystac z nazw narodowych, ale bez znakow diakrytycznych. Teraz mieszamy polska nazwe IMGW z angielska nazwe czeskiego CMHU. Problem musi zostac rozwiaany po stronie Archiwisty jako fix. Na razie zostajemy we wszystkich schematach przy `/1`, bo jest to wciaz wersja rozwojowa”; on the location source and the attribution columns: „B - inaczej. […] wejdzie jako minor juz teraz; C - jak w B”)

Status: proposed.

Requirements: DEV-20.3, DEV-20.5, REL-1.3, REL-1.4, AGI-4.1, ECO-072; Obserwator ADR-001 Q10, ADR-003, ADR-012, ADR-021. Raised by the author's test of Obserwator's station list on 2026-11-21.

## Decisions (the author, 2026-11-21)

1. **National acronyms, without diacritics, in every identifier.** ČHMÚ becomes `CHMU` / `chmu` where the code says the English `CHMI` / `chmi` today: Obserwator's provider id (`--provider CHMU`), its dataset keys `cz.chmu.*`, their slugs `chmu_*` and the store directories named by them (`series/versions/chmu_*`, `stations/versions/chmu_stations`, `analyses/versions/cz.chmu`), message keys, modules, tests; Nogat's registry ids (`chmu`, `chmu-json/1`) and the regulamin's block `chmu`; the consumers' copies of them. IMGW-PIB's identifiers (`IMGW-PIB`, `pl.imgw.*`) are national already and stay. Texts for people keep the names with diacritics („ČHMÚ”, the lines C, CP, CK), and the provider's own addresses (`opendata.chmi.cz`) stay as they are.
2. **`location_source` names the dataset the location came from**, its key, for both providers: `api_hydro` → `pl.imgw.hydro_now`, `api_meteo` → `pl.imgw.meteo_now`, `chmi_hydro_now` and `chmi_hydro_meta3` → `cz.chmu.hydro_now` (both files of that dataset; the catalog's `sources` keep naming the file), `chmi_hydro_stations` → `cz.chmu.hydro_stations`, `chmi_meteo_now` → `cz.chmu.meteo_now`, `chmi_meteo_stations` → `cz.chmu.meteo_stations`. The two sources outside any dataset stay: `static` (Obserwator's reference file `hydro_stations_locations.csv`) and `user` (the user's file). `pl.imgw.meteo_details` (GEO-03 Q2, Obserwator `v3.2.0`) will be its own value.
3. **The CSV of a series, of the stations and of an analysis drops `attribution_source` and `attribution_processed`**: their two cells repeated the first two cells of `attribution` (checked on the stations export of 2026-11-21: S and P for IMGW-PIB, C and CP for ČHMÚ). The trailing columns are `attribution` and `terms_notice` alone (DEV-20.5).
4. **Every schema and format stays `/1`, and the change is minor**: Obserwator `3.1.0`, not `4.0.0`. No old name is accepted beside the new one.
5. **Archiwista takes the change as a fix**, in `0.3.3`.
6. Not in this plan: `pl.imgw.meteo_details` (GEO-03 Q2, approved for Obserwator `v3.2.0`), which gives elevation to 856 IMGW-PIB meteo stations from `hydro-back.imgw.pl/station/meteo/status` (`properties.altitude`).

## Risks, named to the author

- **A user of Obserwator 3.0.x** whose scripts say `--provider CHMI`, `cz.chmi.*`, read `location_source` values or the two CSV columns gets a refusal or a missing column from 3.1.0, though its number says compatible (decision 4).
- **Production's data root** holds ČHMÚ under the old names (series 716 MB, analyses 3.6 GB, catalog 2.5 MB in `~/data/obserwator-target/data`): 3.1.0 does not read them. The deploy builds a new data root from the unchanged raw root (its directories follow the provider's paths, no `chmi` in them) and switches only after the check; the move to Hydrolog `0.9.0` rebuilds every analysis there anyway (about 6 h). The old root stays for a rollback.
- Files exported by 3.0.x keep the two columns: Hydrolog still reads them as lines, not data, since such files exist on users' disks (decision 3 removes their writing, not their reading).

## Steps

| # | Repository, branch | Change |
|---|---|---|
| 1 | Nogat, `feat/national-provider-names` | ECO-082 (decisions 1 and 3 as rules: identifiers by national acronyms without diacritics; DEV-20.5 amended, a CSV's attribution columns are `attribution` and `terms_notice` only, „Columns a project already has stay” removed); `ecosystem.yaml` and its schema (`chmu`, `chmu-json/1`); the regulamin's block `chmu` in `nogat-terms.md`, `nogat-terms-operator.md`, the generated HTML and `scripts/terms.py`, the kit's hashes (kit `1.1.0`, ECO-081); `design/README.md`; CHANGELOG |
| 2 | Obserwator, `feat/national-provider-names` | decisions 1 to 3 in code, schemas (`contract_schemas.json` stays `/1`), messages, GUI and its manual, tests and fixtures (`test_*_chmi.py` renamed), docs (ADR-003 and ADR-001 Q10 errata, ADR-028 for this change, USAGE, ARCHITECTURE, AGENTS, README); the kit's copy of step 1; CHANGELOG `[Unreleased]` under Changed with the migration (rebuild the data root) |
| 3 | Hydrolog, `feat/national-provider-names` | its `chmi` identifiers become `chmu`; the reader of Obserwator's CSV keeps recognising the two old columns; the kit's copy |
| 4 | Archiwista, `fix/national-provider-names` | the new provider id, keys and `location_source` values in its adapter, index, labels and tests; the index rebuilt from the new data root (no translation of old values); the kit's copy; `0.3.3` |
| 5 | Hydrograf, `feat/phone-sources-strip` (open) | the kit's copy with block `chmu` in its regulamin filling |
| 6 | Retman | its Obserwator tool layer and evaluation set with its next pin of Obserwator; outside the release set |
| 7 | Production, with the author's consent | Obserwator 3.1.0 deploy: a new data root built from the raw root (`series build`, catalogs, `analyses build`), checked on :8060, then switched; Archiwista's index rebuilt |

Steps 2 to 5 are part of the round's releases (Obserwator `v3.1.0`, Hydrolog `v0.9.0`, Archiwista `v0.3.3`, Hydrograf `v0.6.0`); nothing is tagged before the round ends.
