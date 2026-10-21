# Plan: shared GUI of the ecosystem

Status 2026-10-20: idea; scope and design not written yet. Requirement:
HUB-5.2.

## Goal

One web interface for Archiwista (store browser, web UI) and Hydrograf
(watershed and hydrograph web app on PostGIS), with Kartograf and IMGWTools as
producers of the stores both read. It was proposed in a brainstorming session
on 2026-10-20 (Claude Code web session, not recorded in any repository). Its
only artefact was a storage benchmark committed to Nogat; it was moved to
Hydrograf (`feature/storage-benchmark`, `backend/scripts/benchmark_storage.py`,
`docs/STORAGE_BENCHMARK.md`) and removed from Nogat's history.

## Options

Open question: the source of truth for spatial data. Can Hydrograf's runtime
data live in files (GeoPackage or GeoParquet, read into memory) instead of
PostGIS, without slower responses? The benchmark measures queries Q1–Q9, load
time per layer version and throughput, and checks that both engines return the
same results.

## Decision

None yet. The storage model is decided with the benchmark result (step 1) and
recorded as an ADR in the owning project.

## Steps

1. Run the benchmark on a Hydrograf database with real data
   (`docs/STORAGE_BENCHMARK.md` in Hydrograf).
2. Write the scope: what the shared GUI covers, what stays in each app, which
   project owns it.
3. Decide the storage model with the result of step 1; record it as an ADR in
   the owning project.

## Results

None yet; the benchmark result from step 1 is added here.
