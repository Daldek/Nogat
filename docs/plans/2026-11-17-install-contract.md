# Plan: one installation contract for every tool (path C)

Approved: pending

Status: a draft of 2026-11-17 after the author's choice of path C the same day. It is not approved, so no code starts (DEV-17.4). Proposals are marked „[proposed]”; the open questions are the author's.

Requirements: DEV-6.2, DEV-6.3 (uv, `uv sync --locked` in every environment, container builds included), DEV-6.5 (extras), DEV-12.4 (server logs), DEV §18 (`nogat.toml`, directories, variables, `config show`), DEV-16.2 (CLA), HUB-7.1 to HUB-7.3 (the `nogat` package), REL (releases), DEV-17.5 and DEV-3.4 (each project in its own session and branch).

## The author's decisions (2026-11-17)

- Path C: two channels, one contract.
  - **Tools:** Python packages, installed one by one or as the set `nogat`.
  - **Servers:** an image and service templates for every app with a GUI or an API, built from the same released package and lock.
- Linux is the priority. macOS and Windows are wanted for local tools, but not at any cost.
- The system stays open, but its author will commercialise it later: he wants to earn on processing (preparing areas and data) and on operating the whole. He does not want installation made too easy for inexperienced users. The model is Deltares: open code, with some conveniences (built binaries) behind registration.
- Open: whether the images are public, and where a deployment repository lives.

## What differs today (2026-11-17)

| Tool | Install | Server |
|---|---|---|
| Kartograf, Obserwator, Hydrolog | `uv tool install "<tool>[extras] @ git+…@vX.Y.Z"` | `obserwator gui serve`, `hydrolog gui serve` |
| Archiwista | checkout + `uv sync --locked` + `uv run archiwista serve`; Linux only | its own server |
| Hydrograf | `docker compose up -d` (PostGIS, API, nginx); production overlay | API and nginx |
| Retman, Hydraulik | `uv tool install git+…` from a branch; Retman pins pre-release commits | none |
| The set | `uv sync --locked --no-dev --python 3.12` in `release-sets/v0.1.0` | none |

On the author's machine every server is set up by hand. Hydrolog, Obserwator and Archiwista run as checkouts with systemd user units. Hydrograf runs with the development override, its code mounted from the checkout. Backups and updates are recorded only in PROGRESS.

## The contract [proposed]

A new section of DEV, one rule per point, the same in every project:

1. **Install.**
   - A tool is a package. `uv tool install "<tool>[<extras>]"` from its tag, later from PyPI (ADOPTION_PLAN phase 6).
   - The server is an extra (`[gui]`, `[api]`), and `<tool> serve` (or the existing `gui serve`) starts it.
   - Archiwista becomes such a package; no app runs from a checkout.
2. **Configuration.**
   - `nogat.toml` is found through `NOGAT_CONFIG`, with `data_dir`, `cache_dir` and `state_dir` (DEV-18).
   - Variables are named `<TOOL>_*`. Credentials come from files named by `<TOOL>_*_FILE`, e.g. the admin key.
   - `<tool> config show --json` reports all of it.
3. **Server.**
   - Port `<TOOL>_PORT` with each tool's default (8060 Obserwator, 8070 Hydrolog, 8080 Hydrograf, 8090 Archiwista).
   - `GET /health` with `status`, `version` and its checks.
   - Logs as DEV-12.4: one JSON line per event on stdout.
   - Behind a reverse proxy: trusted proxies set by one variable.
4. **Directories in a container.** `/config/nogat.toml`, `/data`, `/state`, `/cache`, and the uid/gid set by the deployment, so that a share with fixed owners works (the lesson of Hydroni's CIFS share).
5. **Image.**
   - Built in CI from the release tag, with `uv sync --locked` (DEV-6.3) on one base image.
   - Contents: the package with its server extra, no development tools.
   - Labels: the version, the commit and the release set.
6. **Service templates.**
   - A compose file per server, and a systemd unit generated from the same parameters (port, directories, user), e.g. by `nogat service render <tool>`.
   - Hydrograf keeps PostGIS as a second service; its production overlay is the default and the development override a separate file.
7. **Backup and update.**
   - Backup: each tool states what to copy. Stores by `rsync -aH` (DEV-18.5), databases by their dump, `state_dir`.
   - Update: change the tag, pull or reinstall, restart, run the tool's smoke command.
   - `nogat doctor` checks the installed versions against the set.
8. **Platforms.**
   - Linux is supported and blocking in CI.
   - macOS and Windows are best effort and non-blocking, for the tools' CLI and the local GUIs (Hydrolog's CI is the model).
   - Servers run on Linux only.

## Open: images and how open they are

With MIT code, a closed image is a speed bump, not a protection: anyone can build it from the Dockerfile. The value the author sells is elsewhere:
- prepared areas and data sets (the bootstrap of a region, curated stores);
- running and updating the whole;
- support and the domain knowledge.

| Option | Who gets images | Fits |
|---|---|---|
| I1 | Public images for every server (GHCR) | the portfolio; easiest for anyone, competitors included |
| I2 | No published images: the Dockerfiles and compose files are public, a user builds them; built images only for clients | a competent administrator installs it, an inexperienced user does not; no infrastructure |
| I3 | Images in a private registry; access tokens issued after registration, by hand at first (the Deltares model) | lead collection and control; a little upkeep per token |
| I4 | Public images of the local tools (e.g. Hydrolog's GUI) for the portfolio; the server stack (Hydrograf, Archiwista, data processing) as I2 or I3 | a demo for everyone, the operational stack for clients |

[proposed] I4 with I2 for the server stack now (no registry to run), moving to I3 when the first clients come.

The licence is a separate question, the author's decision:
- All projects are MIT with a single copyright holder. Future versions can change licence; released ones stay MIT.
- EUPL-1.2 (the EU's own licence) or AGPL-3.0 would require a competitor who runs a modified copy as a service to publish the changes. MIT does not.
- A future dual licence needs the CLA of DEV-16.2 (its text waits for the author) before any outside contribution.

## Steps [proposed]

| Step | Project | Result |
|---|---|---|
| S1 | Nogat | an ECO decision and the DEV section of the contract above; the registry's `interfaces` name the server extra and the image |
| S2 | Archiwista | a package with `archiwista serve` from `uv tool install`; the checkout run becomes development only |
| S3 | Obserwator, Hydrolog, Archiwista, Hydrograf | the contract's variables, `/health`, directories and `config show` fields where they differ (each in its own branch) |
| S4 | each server | a Dockerfile from the release tag and a compose file; CI builds the image (published per the images question) |
| S5 | Nogat | `nogat service render <tool>` for systemd units, or templates in the deployment repository |
| S6 | deployment repository or `deploy/` (open) | the combined compose, backup, update and restore runbooks in Polish (the deviation C2 of `2026-11-17-public-sector-portfolio.md`) |
| S7 | the author's machine | production moved to the contract: the units from S5 or compose from S4; Hydrograf without the development override |
| S8 | later | PyPI names `nogat-<project>` (ADOPTION_PLAN 6.1) |

## Open questions

1. Images: I1, I2, I3 or I4, and when to move to I3.
2. The licence of future versions: MIT, EUPL-1.2 or AGPL-3.0; the CLA text before it matters.
3. The deployment repository or `deploy/` in Nogat (also C4 of the portfolio plan).
4. Whether `nogat service render` belongs in the `nogat` package (HUB-7.3 lists its commands) or in the deployment repository.
