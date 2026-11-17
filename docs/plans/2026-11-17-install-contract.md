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
- The server stack is every server, each GUI's public instance included (Hydrolog's GUI too, as the others): Hydrograf (API, PostGIS, nginx, the bootstrap), Archiwista, the public GUIs of Obserwator and Hydrolog, and their back end (stores, nightly jobs, backups, updates, monitoring). The local tools are the libraries, CLIs and MCP servers a person installs for themselves.
- Images: I2 now (no published images; the Dockerfiles and compose files are public, built images only for clients), I3 later (a private registry, access after registration).
- The licence stays MIT: a copy cannot be prevented or proven anyway.
- Open: where a deployment repository lives.

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
   - `nogat.toml` is found through `NOGAT_CONFIG`, with `data_dir`, `cache_dir` and `state_dir` (DEV-18.1, DEV-18.2).
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

## Images and openness

With MIT code, a closed image is a speed bump, not a protection: anyone can build it from the Dockerfile. The value the author sells is elsewhere:
- prepared areas and data sets (the bootstrap of a region, curated stores);
- running and updating the whole;
- support and the domain knowledge.

| Option | Who gets images | Fits |
|---|---|---|
| I1 | Public images for every server (GHCR) | the portfolio; easiest for anyone, competitors included |
| I2 | No published images: the Dockerfiles and compose files are public, a user builds them; built images only for clients | a competent administrator installs it, an inexperienced user does not; no infrastructure |
| I3 | Images in a private registry; access tokens issued after registration, by hand at first (the Deltares model) | lead collection and control; a little upkeep per token |
| I4 | Public images of the local tools for the portfolio; the server stack as I2 or I3 | a demo for everyone, the operational stack for clients |

Chosen (the author, 2026-11-17): I2 now for every server, Hydrolog's GUI included, then I3. CI builds every image (S4) to prove it builds, and publishes none; a client gets an image by the deployment, later from the private registry.

The licence stays MIT (the author, 2026-11-17). The CLA of DEV-16.2 is still needed before outside contributions, as DEV §16 requires.

## Steps [proposed]

| Step | Project | Result |
|---|---|---|
| S1 | Nogat | an ECO decision and the DEV section of the contract above; the registry's `interfaces` name the server extra and the image |
| S2 | Archiwista | a package with `archiwista serve` from `uv tool install`; the checkout run becomes development only |
| S3 | Obserwator, Hydrolog, Archiwista, Hydrograf | the contract's variables, `/health`, directories and `config show` fields where they differ (each in its own branch) |
| S4 | each server | a Dockerfile from the release tag, a compose file and a systemd unit template in the project's repository (public, English); CI builds the image and publishes none (I2) |
| S5 | private deployment repository | the combined compose of the server stack, the overlays of each instance (the author's, Hydroni, later a client's; no secrets), backup, update and restore runbooks in Polish |
| S6 | the author's machine | production moved to the contract: the stack of S5; Hydrograf without the development override |
| S7 | later | PyPI names `nogat-<project>` (ADOPTION_PLAN 6.1); `nogat service render <tool>` only if hand-made units repeat |

## Deployment repository and service templates (the author's decision, 2026-11-17)

- **One private repository**, e.g. `Daldek/wdrozenia`, for everything about running instances:
  - the combined compose of the server stack;
  - each instance's overlay and settings, with secrets kept outside Git;
  - the Polish runbooks: install, backup, update, restore;
  - the register of references.
  
  It answers C3 and C4 of the portfolio plan in one place. It is private because instances and clients are not public. Nogat's „computes nothing itself” stays true.
- **What a client needs from public sources stays in each project:** its Dockerfile, compose file, systemd unit template and English install section. A competent administrator can therefore build and run any server without the private repository (I2). The private repository adds the combination, the data and the operating knowledge, which is what the author sells.
- **No `nogat service render` command now.** Each server's repository ships its own unit template next to its compose file; the deployment repository fills them in. A command in the `nogat` package (HUB-7.3) waits until the same filling-in repeats by hand for several instances.

## Versions

The author's decision (2026-11-17): the contract is split by what an update can break, and none of it enters the patch releases now being prepared, whose scope is closed. The contract is the release after them.

- **Additive, as a patch or with no release at all:**
  - files that do not change the installed package: Dockerfiles, compose files, unit templates, install documentation;
  - fixes of the author's deployment (Hydrograf's development override; done in the deployment repository);
  - new variables and `/health` where they only add, the old names still working.
- **A minor release:** whatever renames or moves something, or changes how a tool is installed or started:
  - Archiwista as a package;
  - renamed variables or directories.

| Project | Release with the contract | Why |
|---|---|---|
| Nogat | standard 1.1 (HUB-6.1); `nogat` 0.2.0 with the next set if a member takes a minor | a new DEV section; HUB-7.4 counts a member's minor bump in `0.y` as major |
| Archiwista | 0.4.0 | S2 changes how it is installed and started (REL-1.1: in `0.y.z` a minor bump may break) |
| Hydrograf, Hydrolog | the next patch if every change is additive, else the next minor (0.6.0, 0.9.0) | S3 and S4 for their servers |
| Obserwator | 3.0.2 or 3.1.0 if additive; 4.0.0 only if something is renamed (from 1.0 only a major bump may break) | [proposed] additive: its names already follow `OBSERWATOR_*` and DEV §18 |
| Kartograf | none, unless `config show` needs a field | it has no server |

Order: the current patches first (Kartograf 0.8.1, Obserwator 3.0.1, Hydrolog 0.8.1, Hydrograf 0.5.1, Archiwista 0.3.1), unchanged; then the contract on each `develop` as the next release; then a candidate and the next `nogat`.

## Open questions

1. The name of the private deployment repository.
2. How a client registers when I3 starts (by hand at first).

Decided (the author, 2026-11-17): I3 starts with the first client. The portfolio plan's demo (P4) runs on an instance the author hosts, or the author deploys it himself. The deployment repository and the service templates as recommended above.
