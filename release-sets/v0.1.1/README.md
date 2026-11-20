# Release set v0.1.1

A patch release set of the ecosystem (REL-6.6, HUB-7.2): the candidate
[candidate-10](../candidate-10/) with each member's commit replaced by its
release tag. Every tag is annotated and points at the merge commit of the
release on the member's `main`. Against [v0.1.0](../v0.1.0/README.md) it
brings Kartograf's hotfix of the USDA texture classes at clay = 20 % and
27 % (HSG B becomes C on those cells), Hydrograf's pinned images with nginx
1.31.9 (a security fix), Archiwista's defect fixes of 0.3.2, and the defect
fixes of Kartograf 0.8.1, Obserwator 3.0.1, Hydrolog 0.8.1 and Hydrograf
0.5.1 released on 2026-11-18.

| Member | Tag | Commit | Installed by this set |
|---|---|---|---|
| Kartograf | [`v0.8.2`](https://github.com/Daldek/Kartograf/releases/tag/v0.8.2) | `66197871f468869b437e8256e04bd00a0ea7c6aa` | `kartograf[mcp]==0.8.2` |
| Obserwator | [`v3.0.1`](https://github.com/Daldek/Obserwator/releases/tag/v3.0.1) | `533c42ab8ce1facacb1b4590f62d2d05c23990d8` | `obserwator[full]==3.0.1` |
| Hydrolog | [`v0.8.1`](https://github.com/Daldek/Hydrolog/releases/tag/v0.8.1) | `bf35db27edb1dee314944036b4a5e37090d0c06f` | `hydrolog[all]==0.8.1` |
| Hydrograf | [`v0.5.2`](https://github.com/Daldek/Hydrograf/releases/tag/v0.5.2) | `2f6da1d2504bb5097af5449d1823daad13ccbc70` | no: an app on its own lock (ECO-074, ECO-077) |
| Archiwista | [`v0.3.2`](https://github.com/Daldek/Archiwista/releases/tag/v0.3.2) | `514162db195da06bafd501b540f458b5ce2b3354` | `archiwista[obserwator]==0.3.2` |

`pyproject.toml` and `uv.lock` give the installable members at their tags
and every third-party package at one version for Linux, macOS and Windows:
the same 127 packages and third-party versions as candidate-10's lock.
candidate-10 verified Obserwator at `8edccf7`, a commit after `v3.0.1` that
changes only its PROGRESS and an e2e test; the package is the same. The
`nogat` package (HUB §7) does not exist yet, so the set is installed as an
environment, not with `uv tool install`:

```bash
git clone --branch v0.1.1 https://github.com/Daldek/Nogat
cd Nogat/release-sets/v0.1.1
uv sync --locked --no-dev --python 3.12
```

The members' commands (`kartograf`, `obserwator`, `hydrolog`, `archiwista`)
are then in `.venv/bin/`.

## Verification

candidate-10 passed the workflow verify-candidate on Linux, macOS and Windows
with Python 3.12 and 3.15,
[run 44775327473](https://github.com/Daldek/Nogat/actions/runs/44775327473),
on its second attempt: the first failed one e2e test each, Archiwista's
project card in Firefox (Ubuntu, Python 3.12) and Hydrolog's session test
(macOS, Python 3.15), both flaky. Archiwista's and Hydrograf's release
commits then passed their full gates (3,043 and 2,404 tests). This set
installs from its lock with `uv sync --locked --no-dev --python 3.12`, and
each member reports its release version.
