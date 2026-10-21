# Progress

## Status

| Component | State | Note |
|---|---|---|
| Standard 2.1 | done | not tagged: `std-2.1` awaits the author (ADOPTION_PLAN 0.4) |
| Registry and schema | done | `ecosystem.yaml`, `schemas/ecosystem.schema.json` |
| `validate`, `map`, `deps`, `drift` | done | `scripts/ecosystem.py` |
| Hub gate and CI | done | `scripts/gate.sh` on `uv.lock`, tests in `tests/` |
| Standard checks | done | `uv run scripts/ecosystem.py standard`, in the gate |
| Contradictions in standard 2.1 | planned | decisions as ECO entries, standard 2.2 |
| Canonical agent-interface schemas | planned | envelope, error, catalog; conformance test |
| `nogat` package (HUB §7) | planned | |
| Adoption in the projects | planned | ADOPTION_PLAN phases 1 to 6 |

## Next

1. Settle the contradictions found in standard 2.1 (language of agent-facing
   messages, DEV-17.5 scope, hub exit codes and ERR, rule precedence).
2. Canonical schemas in `schemas/` for `<tool>-result/1`, `<tool>-error/1`
   and `<tool>-commands/1`, with a conformance test.

## Open questions

- Hydraulik's registry entry declares a CLI and package that are not
  committed (code in an uncommitted worktree): commit it, or mark the entry
  `research` until then?
- `std-2.1` tag and replacement of the v1 `templates/` and `configs/`
  (root-owned files).
