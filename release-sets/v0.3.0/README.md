# Release set v0.3.0

The release set of the round of 2026-11-24 (REL-6.6, HUB-7.2): the
candidate [candidate-15](../candidate-15/) with each member's commit
replaced by its release tag. Every tag is annotated and points at the merge
commit of the release on the member's `main`. Against
[v0.2.0](../v0.2.0/README.md) it brings Kartograf 0.9.0, with the catchments
and gauging stations of CAMELS-PL (its ADR-062), and Obserwator 3.2.1: 3.2.0,
released on 2026-11-23 outside a release set, with the captures of every
answer of a source of current data, the hourly operational series, the
provider adapters and credentials and ČHMÚ's groundwater (plans
`docs/plans/2026-11-16-operational-series.md` and
`docs/plans/2026-11-20-hydromet-providers.md`), and 3.2.1's fix of one
defect. Archiwista 0.4.1 reads them: 0.4.0, released with Obserwator 3.2.0,
reads its new tiers, captures, hourly series and groundwater stations, and
0.4.1 pins Kartograf 0.9.0 and Obserwator 3.2.1. Hydrolog 0.9.1 and
Hydrograf 0.6.1 install the same producers. With it Nogat publishes standard
1.2.

| Member | Tag | Commit | Installed by this set |
|---|---|---|---|
| Kartograf | [`v0.9.0`](https://github.com/Daldek/Kartograf/releases/tag/v0.9.0) | `4cd96785b926ed199b9878a9d3b691b2dc403cc5` | `kartograf[mcp]==0.9.0` |
| Obserwator | [`v3.2.1`](https://github.com/Daldek/Obserwator/releases/tag/v3.2.1) | `288b32e44af21bfa0bedfdbe4635231082c92aa4` | `obserwator[full]==3.2.1` |
| Hydrolog | [`v0.9.1`](https://github.com/Daldek/Hydrolog/releases/tag/v0.9.1) | `d729ffb4517ead2aab6ecff8aef9362a3abad2f0` | `hydrolog[all]==0.9.1` |
| Hydrograf | [`v0.6.1`](https://github.com/Daldek/Hydrograf/releases/tag/v0.6.1) | `ba6681fd375ddd5dcd0c734f3f47787c37db893f` | no: an app on its own lock (ECO-074, ECO-077) |
| Archiwista | [`v0.4.1`](https://github.com/Daldek/Archiwista/releases/tag/v0.4.1) | `d0f71fb7f7d787f7db068607ff8ffb4b8efb51e2` | `archiwista[obserwator]==0.4.1` |

`pyproject.toml` and `uv.lock` give the installable members at their tags
and every third-party package at one version for Linux, macOS and Windows:
the same 136 packages and third-party versions as candidate-15's lock.
candidate-15 verified each member at the commit its release branch started
from (Kartograf `05052b3`, Obserwator `1ffe40d`, Hydrolog `1b25a91`,
Hydrograf `ce4fefb` and Archiwista `0b1949b`); a tag adds only the release
commit, which sets the version (Hydrolog's commit was 0.9.1 already), the
CHANGELOG heading and the lock and replaces the commit pins with these tags,
their ranges narrowed to the releases (REL-2.1, REL-5.6). Obserwator's
`v3.2.1` adds no commit: it is the merge of `1ffe40d`, already 3.2.1, into
`main`. The `nogat` package (HUB §7) does not exist yet, so the set is
installed as an environment, not with `uv tool install`:

```bash
git clone --branch v0.3.0 https://github.com/Daldek/Nogat
cd Nogat/release-sets/v0.3.0
uv sync --locked --no-dev --python 3.12
```

The members' commands (`kartograf`, `obserwator`, `hydrolog`, `archiwista`)
are then in `.venv/bin/`.

## Verification

candidate-15 passed the workflow verify-candidate on Linux, macOS and Windows
with Python 3.12,
[run 45515449114](https://github.com/Daldek/Nogat/actions/runs/45515449114);
the experimental Python 3.15 job on Linux failed one Obserwator e2e test,
which is not blocking (REL-6.5). This set installs from its lock with
`uv sync --locked --no-dev --python 3.12`, and each member reports its
release version.
