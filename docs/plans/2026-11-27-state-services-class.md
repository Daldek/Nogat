# Plan: the source classes as state services and other sources

Status: drafted 2026-11-27 on the author's report and choice; awaiting approval (DEV-17.4).

Requirements: HUB-5.2, DEV-17.4, DEV-17.5, DEV-20.8, DEV-20.13, REL-2.4, ECO-085, ECO-092. Amends P11 to P13 of `2026-11-20-hydromet-providers.md` and W2 and open question 5 of `2026-11-24-pig-groundwater.md`.

## The author's report and choice (2026-11-27)

- Report, after Obserwator `v3.3.0` was deployed: „Błąd w GUI Obserwatora - dane o wodach podziemnych z PIG (PAŃSTWOWY INSTYTUT GEOLOGICZNY) trafił do kategorii „Inne źródła”, a jest to służba hydrogeologiczna.”
- Choice among four options put to him the same day: „Służby państwowe vs inne”. The other options were rejected:
  - a third class beside the hydro-meteorological services and the other sources;
  - PIG-PIB in `nmhs`;
  - leaving W2 as it is.

## What exists (Obserwator `v3.3.0`, tag `34978a4`)

- **The two classes.** `ProviderAdapter.source_class` is `nmhs` or `other` (`src/obserwator/providers/base.py:248-260`, `:293`). `nmhs` is the default (IMGW-PIB, ČHMÚ). `other` is set by:
  - PIG-PIB (`providers/pl/pig.py:373`);
  - Gdańskie Wody (`providers/pl/gdanskiewody.py:325`);
  - every provider fed by files (`providers/files.py:161`, `_provider_files.py`: `SOURCE_CLASSES = ("other",)`).
- **P11 defines `nmhs` by WMO membership.** It is „a national meteorological and hydrological service of a WMO member”, following the author's answer of 2026-11-20 („…od służb hydrometeorologicznych, co do których mamy pewność, że spełniają wymagania WMO, od pozostałych źródeł…”). W2 of the PIG-PIB plan therefore gave PIG-PIB `other`, and ECO-092 recorded `nmhs` as rejected.
- **The GUI.**
  - The class switch „Wszystkie | Służby | Inne źródła” (`gui/web/src/list.js:43`; `messages/gui/stations.py:18-19`).
  - The headings „Służby hydrologiczno-meteorologiczne” and „Inne źródła” (`messages/gui/words.py:19-23`; `gui/web/src/words.js:80`, `:97`).
  - The legend's „Służba hydrologiczno-meteorologiczna” and „Inne źródło” (`stations.py:116-120`).
  - The outline: solid for `nmhs`, dashed for any other class (`gui/web/src/symbols.js:24`, `:172`, `:208`; `map.js:303`, `:884`).
  - The class reaches the page as `source_class` of `api/session` (`gui/_app.py:675`).
  - The guide names PIG-PIB as an example of „inne źródła” (`gui/web/instrukcja/index.html:194`).
- **The hand-off to Hydrolog** is offered only for an `nmhs` station (`gui/web/src/sections/pobierz.js:157`) and only with daily Q or H, or the flood frequency of Q.
- **P8's notice for PIG-PIB** (`messages/datasets.py:193-196`): „Dane pochodzą z monitoringu wód podziemnych państwowej służby geologicznej (PIG-PIB), nie od państwowej służby hydrologiczno-meteorologicznej”. It is true and stays.
- **No other consumer reads the class.** Archiwista, Retman, Hydrograf and Kartograf do not (`git grep nmhs|source_class` on their checked-out branches, 2026-11-27). Goniec reads Obserwator's REST server, whose `obserwator-provider/1` does not carry the class (`datasets.py:334-335`). Goniec is not checked out here (to check in S1).
- **The legal fact.** PIG-PIB ran the państwowa służba hydrogeologiczna (PSH) from 2002 to 2023. From 2024-01-01 PSH and the państwowa służba geologiczna (PSG) are one service, and PSG carries on PSH's tasks under Prawo wodne (art. 369 ust. 2, art. 380-381, art. 387). Groundwater monitoring and the MWP database are among those tasks. Source: https://www.pgi.gov.pl/psh/o-psh-info.html, read 2026-11-27. W's wording „Monitoring Wód Podziemnych państwowej służby geologicznej” is therefore current and stays.

## Design

| ID | Decision | Rejected |
|---|---|---|
| S1 | **Two classes, redefined by who runs the network.**<br>• `state`: a state service set up by statute and run by a state body or state research institute. It holds IMGW-PIB (PSHM), ČHMÚ and PIG-PIB (PSG, the hydrogeological tasks of Prawo wodne).<br>• `other`: every other operator: municipal companies, offices, universities, an operator's own network. It holds Gdańskie Wody and every provider fed by files.<br>A provider declares its class in its adapter, as now (P11: per provider, never per station or dataset). | A third class: four buttons in the switch and a third outline, which P13 found unreadable at 16 px. PIG-PIB in `nmhs`: the heading „Służby hydrologiczno-meteorologiczne” and the WMO meaning would be untrue for it. |
| S2 | **The identifier `nmhs` becomes `state`**, a clean cutover in one release with no alias. The class's only reader is Obserwator's own page, through the private `api/session`. `obserwator-provider/1` and every `/N` document stay unchanged, so ECO-085 sees no new value in a released document. A provider file keeps `source_class = "other"`, its only value. | Keeping `nmhs` with PIG-PIB in it: the name would contradict its members. |
| S3 | **Words.**<br>• The switch: „Wszystkie \| Służby państwowe \| Inne źródła” (EN „All \| State services \| Other sources”).<br>• The heading: „Służby państwowe” („State services”).<br>• The legend: „Służba państwowa” („State service”).<br>• „Inne źródła” and „Inne źródło” stay.<br>• The guide gives the classes with their members and takes PIG-PIB out of the example of other sources. | — |
| S4 | **The outline follows the class.** Solid for `state`, dashed for `other`. PIG-PIB's points lose the dashed outline. | — |
| S5 | **What stays.**<br>• P8's notice for PIG-PIB: the data come from a state service, but not a hydro-meteorological one.<br>• Lines W, WP, WK and RW.<br>• The tiers: MWP readings `verified`, `mwp_auto` `operational` with „niezweryfikowane” (DEV-20.8).<br>• The hand-off: `pobierz.js:157` tests `state`. A PIG-PIB point has neither Q nor H nor a flood frequency, so it still offers none. | — |
| S6 | **The record.** A new decision, ECO-0NN (the next free number when N1 lands; ECO-095 is the last on `develop` on 2026-11-27). It amends ECO-092 (its rejection of `nmhs` and the class `other` given to PIG-PIB) and the P11 to P13 rows of the providers plan. Why: the author's report and choice of 2026-11-27. Rejected: the options of S1. DEV §20 names no class, so no rule's text changes. | — |

## Steps

Producers first (HUB-5.2). Only Obserwator reads the class.

| Step | Project, branch | What | Acceptance |
|---|---|---|---|
| N1 | Nogat, `feat/state-services-class` | S6's decision in `standards/DECISIONS.md` (index row; ECO-092's row lists it as amending); the amendment lines under P11–P13 of `2026-11-20-hydromet-providers.md` and W2 and question 5 of `2026-11-24-pig-groundwater.md`; CHANGELOG, PROGRESS | `scripts/gate.sh` green |
| O1 | Obserwator, `fix/state-services-class` from the tag `v3.3.0` (patch release, REL-2.4) | S2 to S5:<br>• `Literal["state", "other"]` in `base.py`, `datasets.py`, `files.py`, `gdanskiewody.py`;<br>• `pig.py` set to `state`;<br>• `words.js` `SOURCE_CLASSES`, `list.js`, `map.js`, `symbols.js`, `pobierz.js`;<br>• the messages and the guide;<br>• the tests that name `nmhs`;<br>• errata to ADR-035 W2 and to ADR-034 D12 (the GUI of the source classes);<br>• CHANGELOG `3.3.1`. | Full gate. The GUI on the deployed data: PIG-PIB under „Służby państwowe” with a solid outline, Gdańskie Wody and a provider file under „Inne źródła”, the switch shown only where both classes are held (as now) |
| O2 | Obserwator, merged back into `develop` | The same change on `develop`, so CAMELS-PL's `v3.4.0` carries it | `develop`'s gate |
| R1 | Nogat, release set | candidate-17: Obserwator `v3.3.1`; Archiwista needs no new pin (`>=3.2.0,<4`) | `set verify` |
| D1 | Deployment | `app-331` beside `app-330`, the unit switched; rollback by the unit's copy | The checks of O1 on 127.0.0.1:8060 and the public host |

## Open questions

1. **Release vehicle.** Recommended: patch `v3.3.1` from the tag, so production gets it now. The alternative is to wait for `v3.4.0` (CAMELS-PL).
2. **Do the regulamin's § 5 or the info texts describe the classes?** Checked: § 5 holds only the providers' blocks (DEV-20.7), so no version of the regulamin changes. The info texts (DEV-15.14) of „Stacje” are Obserwator's own and change in O1.

## Results

None yet.
