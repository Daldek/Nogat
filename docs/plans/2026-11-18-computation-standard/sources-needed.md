# Sources the author is asked to supply (scans or PDFs)

Part of [the computation standard plan](../2026-11-18-computation-standard.md), step 9. The literature research of 2026-11-18 used open sources only (the author's decision). The items below could not be opened. Each would confirm a constant, a definition or a range that today rests on secondary sources, or would move a formula from `oracle only` to `referenced` (CMP-2.4, CMP-5.1). Grouped by priority: A covers the most formulas per item.

## A. Polish textbooks and methodologies (also the handbook's terminology)

| Source | Confirms |
|---|---|
| Ozga-Zielińska M., Brzeziński J. (1994/1997) *Hydrologia stosowana*, PWN | SCS-CN in Polish practice: the μ(CN) table of initial losses, the 5-day AMC thresholds 13/28 and 35/53 mm, the CN table of KZGW 2017 C.1; Nash and Kalinin–Milyukov values for Polish reaches; areal precipitation and design storms; Polish names of shape indices |
| Byczkowski A. (1996/1999) *Hydrologia* t. I–II, SGGW | characteristic values (Z as median, WSQ, NSQ, WNQ, NWQ; first-degree ZQ); duration-curve class tables; Muskingum and Kalinin–Milyukov; Nash, Snyder, SCS unit hydrographs; Thiessen and isohyets |
| Banasik K., Górski D., Ignar S. (2000) *Modelowanie wezbrań opadowych i jakość odpływu z małych nieobserwowanych zlewni rolniczych*, SGGW | the Polish adaptation of Lutz cited by KZGW: the sign of eq. 6.18 and the transformed eq. 6.19 (triage T2) |
| Banasik K. (2009) *Wyznaczanie wezbrań powodziowych w małych zlewniach zurbanizowanych*, SGGW | the Rao regression and the definition of U; the 52 km² limit; HSG of Polish soils; the DVWK storm |
| Lutz W. (1984) *Berechnung von Hochwasserabflüssen unter Anwendung von Gebietskenngrößen*, IHW Karlsruhe H. 24 | P2 = 0.66 vs 0.64; P2/P3 per time step; the P1–n relation; the definition of Jg (gewogenes Gefälle, triage T3); the 75 basins and the area limit |
| Ciepielowski A., Dąbkowski Sz. (2006) *Metody obliczania przepływów maksymalnych w małych zlewniach rzecznych* | which tc formulas Polish practice teaches, with which length and slope |
| Dynowska I. (1997) „Reżim odpływu rzecznego”, *Atlas Rzeczypospolitej Polskiej*; Dynowska & Pociask-Karteczka (1999) in *Geografia Polski*, PWN, pp. 343–373 | regime thresholds 130/180/100 %, the months of spring and summer, „prawie równy”, the order of the criteria |
| Ozga-Zielińska M., Brzeziński J., Ozga-Zieliński B. (1999) Materiały Badawcze IMGW, Hydrologia i Oceanologia 27 | the MAZ method and the decile method of design floods |
| Bogdanowicz E., Stachý J. (1998) Materiały Badawcze IMGW, Hydrologia i Oceanologia 23 | α(R, D) tables, regions and validity |
| Kotowski A., Kaźmierczak B., Dancewicz A. (2010) *Modelowanie opadów do wymiarowania kanalizacji*, PAN | the Polish Euler II construction (triage T34) |
| IMGW-PIB *Instrukcja dla stacji meteorologicznych* (2015, and earlier editions) and *Instrukcja dla stacji hydrologicznych* | the trace „0,0”, the 06 UTC term, date attribution; hydrological observation terms and the time scale of extremum times |
| Niedźwiedź T. (red.) (2003) *Słownik meteorologiczny*; Lorenc H. (red.) (2005) *Atlas klimatu Polski* | the two definitions of „dzień przymrozkowy”, ≥ vs > for hot days |
| Ozga-Zieliński B. (red.) (2022) PMAXTP monograph, IMGW-PIB (open but image-only) | distributions AMP/POT, POT threshold, kriging, grid resolution; a text layer or a printed copy is enough |

## B. Standards (paid)

| Source | Confirms |
|---|---|
| DWA-A 118 (2006/2024) Annex A; ATV-DVWK-A 118 (2001) Kap. 5.2.2.1 and Tab. 9 | the exact Euler II rule (0.3·D, rounding, Δt, interpolation, minimum D) and a worked example (now quoted through Thewes 2005) |
| DVWK-Regeln 113 (1984) | whether it defines Euler II at all |
| ISO 1100-2:2010 | the rating equation, its fitting space, minimum gaugings |
| ČSN 75 1400, ČSN 75 6101 | Czech N-year flows and design storms |

## C. Primary articles and books (secondary confirmation exists; the primary closes the item)

- Flood frequency: Hosking & Wallis (1997) *Regional Frequency Analysis*, Appendix A; Hosking (1990) JRSS-B 52; Stephens (1974) JASA 69 and D'Agostino & Stephens (1986), tables 4.2/4.17 (Anderson–Darling critical values, triage T30); Chowdhury, Stedinger & Lu (1991) WRR 27; Coles (2001) §3.4.1; Cunnane (1978) J. Hydrol. 37.
- Time of concentration: Kirpich (1940) Civil Eng. 10(6); Kerby (1959) Civil Eng.; Mockus (1961) ES-1015; Giandotti (1934) Memorie e Studi Idrografici 8.
- Unit hydrographs: Snyder (1938) Trans. AGU 19; Clark (1945) Trans. ASCE 110; Rao, Delleur & Sarma (1972) J. Hydraul. Div. 98(HY7); Chow, Maidment & Mays (1988) *Applied Hydrology* §7.7–7.8, §8.2, §8.4, Tab. 15.1.2.
- SCS-CN: Hawkins, Hjelmfelt & Zevenbergen (1985) J. Irrig. Drain. Eng. 111(4) (triage T13); Hawkins et al. (2009) *Curve Number Hydrology*, ASCE.
- Trend and regime: Kendall (1975) *Rank Correlation Methods* p. 55; Pettitt (1979) Applied Statistics 28; Sen (1968) JASA 63; Pardé (1933); Walsh & Lawler (1981) Weather 36.
- Morphometry: Horton (1932, 1945); Schumm (1956); Chorley, Malm & Pogorzelski (1957); Strahler (1957, 1964); Melton (1958).
- Meteorological indices: Oliver (1980); Thom (1958); Selyaninov (1928–1937); Edwards & McKee (1997).
- Hydraulics (Hydraulik): Villemonte (1947); Engman (1986); Chow (1959) *Open-Channel Hydraulics*; Wody Polskie (2020/2021) guide to pluvial flood maps with its annex 1 (Manning n per BDOT10k class).
