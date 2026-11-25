# Release set v0.4.0

The release set of the round of 2026-11-25 (REL-6.6, HUB-7.2): the
candidate [candidate-16](../candidate-16/) with each member's commit
replaced by its release tag. Every tag is annotated and points at the merge
commit of the release on the member's `main`. Against
[v0.3.0](../v0.3.0/README.md) it brings Obserwator 3.3.0, with the providers
fed by files (an operator's own network declared beside `nogat.toml`, its
ADR-033), Gdańskie Wody (its ADR-034, built and off by default) and PIG-PIB's
groundwater monitoring (its ADR-035; plans
`docs/plans/2026-11-21-obserwator-instance.md`,
`docs/plans/2026-11-20-hydromet-providers.md` and
`docs/plans/2026-11-24-pig-groundwater.md`); Hydrolog 0.10.0, with the
interval estimates beside the point estimates and five hydrological
signatures checked against CAMELS-PL (plans
`docs/plans/2026-11-24-interval-estimation.md` and
`docs/plans/2026-11-22-camels-pl.md`); and Hydrograf 0.7.0, with its API at
`/api/v1` (step HG1 of `docs/plans/2026-11-24-latarnik.md`), the kit's base
maps and charts and the browser tests of its map. Archiwista 0.4.2 reads
Obserwator 3.3.0: two of its contract tests held Obserwator 3.2's registry.
Kartograf 0.9.0 is unchanged. With it Nogat publishes standard 1.3.

| Member | Tag | Commit | Installed by this set |
|---|---|---|---|
| Kartograf | [`v0.9.0`](https://github.com/Daldek/Kartograf/releases/tag/v0.9.0) | `4cd96785b926ed199b9878a9d3b691b2dc403cc5` | `kartograf[mcp]==0.9.0` |
| Obserwator | [`v3.3.0`](https://github.com/Daldek/Obserwator/releases/tag/v3.3.0) | `34978a45b0b3450a338d4facb3f3e677ab0ac343` | `obserwator[full]==3.3.0` |
| Hydrolog | [`v0.10.0`](https://github.com/Daldek/Hydrolog/releases/tag/v0.10.0) | `a06487cf8bae42b9cfcf74881989c7df4a79732d` | `hydrolog[all]==0.10.0` |
| Hydrograf | [`v0.7.0`](https://github.com/Daldek/Hydrograf/releases/tag/v0.7.0) | `b026b052779ab43a98742d44f14792436bee4677` | no: an app on its own lock (ECO-074, ECO-077) |
| Archiwista | [`v0.4.2`](https://github.com/Daldek/Archiwista/releases/tag/v0.4.2) | `d313647fc7f9f44e50546491d3dbdba788456428` | `archiwista[obserwator]==0.4.2` |

`pyproject.toml` and `uv.lock` give the installable members at their tags
and every third-party package at one version for Linux, macOS and Windows:
the same 137 packages and third-party versions as candidate-16's lock.
candidate-16 verified each member at the commit of its release branch
(Kartograf `4cd9678`, Obserwator `2637350`, Hydrolog `d65472b`, Hydrograf
`e7a4ad8` and Archiwista `2a602ec`); a tag adds only the commit that
replaces the commit pins with these tags, in the lock and in the documents
that name them, Hydrograf's range of Hydrolog narrowed to the release,
`>=0.10.0,<0.11` (REL-2.1, REL-5.6), and the merge into `main`. Obserwator's
`v3.3.0` adds no commit: it is the merge of `2637350`, already 3.3.0, into
`main`, and Kartograf's `v0.9.0` is the commit candidate-16 pinned. The
`nogat` package (HUB §7) does not exist yet, so the set is installed as an
environment, not with `uv tool install`:

```bash
git clone --branch v0.4.0 https://github.com/Daldek/Nogat
cd Nogat/release-sets/v0.4.0
uv sync --locked --no-dev --python 3.12
```

The members' commands (`kartograf`, `obserwator`, `hydrolog`, `archiwista`)
are then in `.venv/bin/`.

## Verification

candidate-16 passed the workflow verify-candidate on Linux, macOS and Windows
with Python 3.12,
[run 45652499176](https://github.com/Daldek/Nogat/actions/runs/45652499176);
the experimental Python 3.15 job on macOS failed one Obserwator e2e test,
which is not blocking (REL-6.5). Its first run,
[45626852114](https://github.com/Daldek/Nogat/actions/runs/45626852114) at
Obserwator `0f8fd31`, failed on Windows (no `tzdata` for PIG-PIB's
`Europe/Warsaw` and three tests of paths and line endings) and on Linux (a
race of the welcome window), each fixed in Obserwator's release branch. This
set installs from its lock with `uv sync --locked --no-dev --python 3.12`,
and each member reports its release version.
