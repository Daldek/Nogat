# Plan: the origin of each node of a network in the hand-off

Approved: 2026-11-10, the author (B7 of Hydrograf's network delineation at control points: the origin of each node in the hand-off, an additive change of Nogat first, producers before consumers); the decisions below by delegated authority.

Status: done 2026-11-11. Steps 1 to 4 merged into the `develop` of Nogat, Hydrograf and Hydrolog ([Results](#results)); no tags, no release.

Requirements: HUB-5.2 (producers before consumers), DEV-17.4, AGI-4.1, ECO-050; `schemas/exchange/handoff-1.schema.json` (`nogat-handoff/1`, item 6 of [the GUI platform](2026-11-01-nogat-gui-platform.md)).

## Goal

A hand-off that carries a whole network says where each of its nodes came from. Hydrograf's `POST /api/delineate-network` (B6 of the network delineation) hands Hydrolog one `hydrolog-network/1` with several subcatchments, intermediate catchments (przyrzecza), reaches and junctions; Hydrolog's „Sieć i trasowanie” shows each node's origin in its node panel (A6 of the Sieć correction) and writes it again when it hands the network on. This plan adds the field to the envelope; it does not change the payload.

## Where it starts (2026-11-10)

| Fact | Consequence |
|---|---|
| `provenance` is required and keyed by input (`rainfall`, `watershed`, `runoff`; `propertyNames` `^[a-z][a-z0-9_]*$`), each value an `origin` with a required `source` | one origin per input for the whole payload: right for one watershed, too coarse for a network |
| Node ids of `hydrolog-network/1` are `^\w[\w.-]*$`, at most 64 characters, unique without regard to case (Hydrolog `src/hydrolog/schemas/hydrolog-network-1.schema.json`, `origin/develop` `055a433`): `Z1` and `OUT` in Hydrograf's hand-off (`backend/core/handoff.py`, `origin/develop` `b33594d`) | a node id is not a valid key of `provenance` |
| Every node of `hydrolog-network/1` has `additionalProperties: false`, and `route network` refuses unknown fields | the origin cannot go into the payload's nodes without a change of Hydrolog's schema |
| The envelope's top level has no `additionalProperties: false`; its description and the case `unknown-field` of `tests/contract/test_handoff_schema.py` allow unknown fields (AGI-4.1) | an optional field keeps `nogat-handoff/1`, and every copy of today validates documents that carry it |
| Copies: Hydrolog, Hydrograf and Archiwista keep the schema unchanged in `schemas/nogat/handoff-1.schema.json`, pinned by SHA-256; Hydrolog repeats its validation keywords in `gui/web/src/handoff/envelope.js` (checked against the copy by `tests/e2e/test_exports.py`) | a new copy changes their pinned hash and Hydrolog's keywords |
| Hydrolog's Sieć adds the subcatchments of a hand-off to the open network under a free id when its own is taken (`siecAddition`, `freeId` in `handoff/mapping.js`) and gives each added node the whole hand-off as `origin` | a node's origin must follow it to its new id |

## Options

| Option | Verdict |
|---|---|
| O1. Node ids as more keys of `provenance` (`"Z1": {"watershed": {...}}`) | Rejected: `Z1` breaks the key pattern and a node entry has no `source`, so every copy of today refuses the document: a breaking change, `nogat-handoff/2`. A node named `rainfall` would also collide with an input. |
| O2. The origin inside each node of the payload | Rejected: `hydrolog-network/1` refuses unknown fields, so it needs a change of Hydrolog's schema and of `route network`, and it mixes where values came from with the values that are computed (the envelope exists to keep them apart). |
| O3. A list of `{node, input, origin}` | Rejected: the schema cannot keep one entry per node and input, and a reader has to search it. |
| O4. A new optional object `node_provenance` beside `provenance`, keyed by node id, each value shaped like `provenance` | **Chosen**: additive, the same `origin` as today, one lookup per node. |

## Decisions

| # | Decision |
|---|---|
| D1 | The envelope gains the optional top-level field `node_provenance`: an object keyed by the `id` of a node of the payload; each value is an object keyed by input name, shaped like `provenance`, whose values are `origin` (the existing `$defs/origin`, `source` required, any other parameters). Both levels have `minProperties: 1`: a producer with nothing to say per node leaves the field out. |
| D2 | The input names of a node are the node's members the origin applies to: `watershed`, `runoff` and `rainfall` of a subcatchment, as in `provenance`; `node` names the origin of the node's own fields and place (the length and slope of a reach, the place of a junction or an outlet). They keep the key pattern of `provenance`, `^[a-z][a-z0-9_]*$`. |
| D3 | The outer keys are not constrained beyond `minLength: 1`: node ids are the payload owner's rule (`hydrolog-network/1` `$defs/id`), which the envelope does not repeat (its description: the envelope does not check the payload's content) and which would drift if Hydrolog changed it. A consumer that knows the field checks that each key is the `id` of a node of the payload, matched exactly. |
| D4 | Precedence: the origin of input *i* of node *n* is `node_provenance[n][i]` when present, else `provenance[i]`. `provenance` stays required and stays true for the whole payload: Hydrograf writes there the delineation of the closing section A (`watershed`, its point) and, when the network has one rainfall, its origin (`rainfall`); `node_provenance` refines it per node. |
| D5 | A consumer that does not know the field (Hydrolog and Archiwista on today's copy, any tool reading only `provenance`): the document validates (unknown fields, AGI-4.1), opens and computes the same, since no value of the payload depends on provenance; it shows only `provenance`, the network's origin, correct but coarser. |
| D6 | A consumer that knows the field: a key that names no node of the payload is a producer's error, but the hand-off still opens; that entry is left out with a notice naming the key, because an origin changes no computation and refusing would lose a valid network over a label. A node without an entry takes `provenance` (D4). When Sieć adds a hand-off's nodes to an open network under new ids, each node's origin goes with it. A payload without node ids (`hydrolog-series/1`) never carries the field; a consumer ignores it there. |
| D7 | Producers: Hydrograf's `POST /api/delineate-network` writes `node_provenance` for every subcatchment, intermediate catchment, reach and junction it made. The origin parameters (`element`, `point`, the place, the method of a reach's length and slope, the vector-line length of MPHP or BDOT10k as a check value) are Hydrograf's to settle in its plan for the endpoint; the example below shows the intended form. The single-watershed hand-offs of `delineate-watershed` and `generate-hydrograph` do not change. Hydrolog's Sieć writes it too (D8). |
| D8 | Hydrolog's Sieć (A6) shows each node's origin in its node panel from `node_provenance` with the precedence of D4, and writes `node_provenance` in its own network hand-off (amended on 2026-11-10 by the coordinator's decision, so that an origin survives Hydrograf → Hydrolog → file → Hydrolog): the origins it received pass through unchanged, under each node's current id when Sieć renamed it on a clash; a node added from a single-watershed hand-off takes that hand-off's `provenance` as its entry; an input the person changed since is marked as Hydrogram zlewni marks its watershed (`changed`, the keys of the fields that differ). Nodes the person drew have no entry. Its `provenance` stays `siecProvenance`'s. Hydrogram zlewni reads one subcatchment and keeps using `provenance`. |
| D9 | The version stays `nogat-handoff/1` (AGI-4.1: an optional field, nothing removed or changed in meaning). The description of `provenance` names `node_provenance` as its refinement per node; the existing example stays byte for byte (Hydrolog's fixtures copy it) and a second example carries a network with `node_provenance`. Copies: Hydrolog and Hydrograf copy the new schema in their steps (a producer's tests must validate the field, which the old copy ignores); Archiwista keeps its copy until it next changes its hand-off, since it writes no network. |
| D10 | Registry: Hydrograf's edge to Hydrolog gains the hand-off it already writes and the network it will write (`via` adds `file`, `exchange` adds `hydrolog-network/1`, a note), once Hydrograf's endpoint exists; the copies of Nogat's schemas are no registry edges (ECO-050). |

### The field in the schema (step 1)

```json
"node_provenance": {
  "description": "Where the inputs of each node of the payload came from, keyed by the `id` of the node (a payload with nodes, such as `hydrolog-network/1`); each value is keyed like `provenance`, by input (`watershed`, `runoff`, `rainfall` of a subcatchment, `node` for the node's own fields and place). An entry here takes precedence over `provenance` for its node and input; a node or input without one takes `provenance`. A key that names no node of the payload is left out by the consumer with a notice",
  "type": "object",
  "minProperties": 1,
  "propertyNames": {"minLength": 1},
  "additionalProperties": {"$ref": "#/$defs/node_inputs"}
}
```

and in `$defs`:

```json
"node_inputs": {
  "description": "The origins of the inputs of one node, one entry per input",
  "type": "object",
  "minProperties": 1,
  "propertyNames": {"pattern": "^[a-z][a-z0-9_]*$"},
  "additionalProperties": {"$ref": "#/$defs/origin"}
}
```

### The example (the schema's second example, step 1)

A network of three subcatchments from Hydrograf: the main river above the confluence (`Z1`, headwater), the tributary of point P1 to its mouth (`Z2`), the reach below the confluence (`R1`) with its intermediate catchment (`Z3`) entering the junction at A (`J2`) unrouted; 20.1 + 12.4 + 4.72 = 37.22 km², the area of A. `J2` and `OUT` have no entry and take `provenance`.

```json
{
  "schema": "nogat-handoff/1",
  "created_at": "2026-11-12T09:30:00Z",
  "producer": {"tool": "hydrograf", "version": "0.5.0.dev0"},
  "subject": "Kamiennik — Świerzawa, sieć 3 zlewni",
  "provenance": {
    "watershed": {"source": "hydrograf", "latitude": 51.0154, "longitude": 15.89},
    "rainfall": {"source": "pmaxtp", "probability_percent": 1, "duration_min": 720,
                 "latitude": 51.0154, "longitude": 15.89, "interpolation": "thiessen"}
  },
  "node_provenance": {
    "Z1": {"watershed": {"source": "hydrograf", "element": "headwater", "latitude": 51.0391, "longitude": 15.8436}},
    "Z2": {"watershed": {"source": "hydrograf", "element": "tributary", "point": "P1", "latitude": 51.0402, "longitude": 15.8459}},
    "J1": {"node": {"source": "hydrograf", "element": "confluence", "latitude": 51.0391, "longitude": 15.8436}},
    "R1": {"node": {"source": "hydrograf", "element": "reach", "length": "flow-distance", "slope": "nmt",
                    "vector_length_km": 5.12, "vector_source": "mphp"}},
    "Z3": {"watershed": {"source": "hydrograf", "element": "intermediate", "reach": "R1"}}
  },
  "payload": {
    "schema": "hydrolog-network/1",
    "name": "Kamiennik — Świerzawa, sieć 3 zlewni",
    "timestep_min": 10,
    "rainfall": {"kind": "design", "hietogram_type": "beta", "total_mm": 105.0, "duration_min": 720.0, "alpha": 2.0, "beta": 5.0},
    "nodes": [
      {"id": "Z1", "type": "subcatchment",
       "watershed": {"area_km2": 20.1, "cn": 63, "flow_path_length_km": 9.84, "flow_path_slope_m_per_m": 0.0187},
       "runoff": {"model": "curve-number", "tc_method": "kirpich", "amc": "II", "uh_model": "scs"}},
      {"id": "Z2", "type": "subcatchment",
       "watershed": {"area_km2": 12.4, "cn": 68, "flow_path_length_km": 7.21, "flow_path_slope_m_per_m": 0.0236},
       "runoff": {"model": "curve-number", "tc_method": "kirpich", "amc": "II", "uh_model": "scs"}},
      {"id": "J1", "type": "junction", "from": ["Z1", "Z2"]},
      {"id": "R1", "type": "reach", "method": "muskingum-cunge", "from": ["J1"], "length_km": 5.07, "slope_m_per_m": 0.0098},
      {"id": "Z3", "type": "subcatchment",
       "watershed": {"area_km2": 4.72, "cn": 66, "flow_path_length_km": 3.35, "flow_path_slope_m_per_m": 0.0311},
       "runoff": {"model": "curve-number", "tc_method": "kirpich", "amc": "II", "uh_model": "scs"}},
      {"id": "J2", "type": "junction", "from": ["R1", "Z3"]},
      {"id": "OUT", "type": "outlet", "from": ["J2"]}
    ]
  }
}
```

Checked on 2026-11-10 with `jsonschema` (draft 2020-12): the example validates against today's schema (`a979fc8`, D5) and, with D1 applied in a scratch copy, against the new one; its payload validates against `hydrolog-network/1` of Hydrolog `055a433`. The reach's cross-section (Manning's n, width) is left to Hydrolog (B4 of the delineation), so `route network` needs it from the person in Sieć before it runs.

## Steps

| # | Project | Change | Verified by |
|---|---|---|---|
| 1 | Nogat | D1–D3, D9 in `schemas/exchange/handoff-1.schema.json`: the field, `$defs/node_inputs`, the description of `provenance`, the second example; `tests/contract/test_handoff_schema.py` (below); CHANGELOG `### Added` | `uv run pytest tests/contract/test_handoff_schema.py`; `scripts/gate.sh` |
| 2 | Hydrograf | Within its plan for `POST /api/delineate-network` (B6): copy the schema of step 1 (its SHA-256 in the CHANGELOG, as for `8727f6e`), write `node_provenance` (D4, D7) | its gate; a unit test that the network's hand-off validates against the new copy, that every key names a node of its payload, and that every subcatchment, reach and junction has an entry |
| 3 | Hydrolog | Within A6 of the Sieć correction: copy the schema (SHA-256 in `schemas/nogat/README.md`), the keywords in `handoff/envelope.js`; the node panel shows each node's origin (D4, D6), and Sieć's hand-off writes `node_provenance` (D8) | its gate and e2e; a contract test that opens the second example: each node shows its own origin, `J2` that of `provenance`, an added node renamed on a clash keeps its origin, a key of no node gives a notice and the network still opens; the hand-off written back carries the received origins under the current ids, `changed` for an edited input, and validates against the copy |
| 4 | Nogat | D10 in `ecosystem.yaml` (below); `uv run scripts/ecosystem.py map`; Results of this plan | `uv run scripts/ecosystem.py validate`; `scripts/gate.sh` |

Order (HUB-5.2): step 1 first, since Nogat owns the envelope; steps 2 and 3 in either order, each against the schema's second example (a consumer on the old copy keeps working, D5); step 4 when step 2 is merged. Archiwista changes nothing.

Tests of step 1, beside the parametrized check that every example validates:

- valid: a node with only `node`; a node's `rainfall` beside `provenance.rainfall`; a node id with `.` and `-` (`Z1.a-2`);
- invalid: `node_provenance` `{}`; a node's entry `{}`; an input name not in lowercase (`Watershed`); an origin without `source`; an origin that is a string; an empty node id; `node_provenance` as an array;
- every key of `node_provenance` in the examples names a node of their payload (consumers copy the example as a fixture).

The registry lines of step 4, in Hydrograf's `depends_on` (the `uses` list stays):

```yaml
      - project: Hydrolog
        kind: runtime
        status: active
        via: [library, file]
        exchange: [watershed-parameters, hydrolog-python-api, hydrolog-network/1]
        note: POST /api/delineate-watershed and /api/generate-hydrograph hand a watershed (ADR-068), POST /api/delineate-network a network, to Hydrolog's GUI as nogat-handoff/1 around hydrolog-network/1; the network's carries the origin of each node in node_provenance.
```

## Results

- 2026-11-10, step 1: Nogat `8848c26` on `develop`. `node_provenance` and `$defs/node_inputs` in `schemas/exchange/handoff-1.schema.json` as D1 gives them, the description of `provenance`, the second example as above; the first example unchanged. SHA-256 of the schema `84c6856d1148acdc08bf79600c8cdab03674e81fe1f30eb7abeb66629b5742ed`, the hash Hydrograf and Hydrolog record when they copy it (steps 2 and 3). `tests/contract/test_handoff_schema.py`: 45 passed (the cases above).
- 2026-11-10/11, step 2: Hydrograf, inside its plan `docs/plans/2026-11-10-network-delineation.md` (ADR-080): the copy of the schema `5ed0aea` (`schemas/nogat/handoff-1.schema.json`, SHA-256 as above), `POST /api/delineate-network` and `build_network_handoff` in `27432f7` and `d6ece5d`, writing `node_provenance` for every subcatchment, reach and junction (D7; `OUT` takes `provenance`); merged into `develop` at `824bebd` after its gate (2088 passed); `tests/unit/test_network_endpoint.py` and `tests/integration/test_network_delineation_db.py` check the keys against the payload's nodes. Deployed on the Hydroni instance (127.0.0.1:8081) on 2026-11-11 and smoke-tested there (a network of 250.39 km², 4 subcatchments, 2 reaches, 2 junctions); Hydrograf's production (8080) is not redeployed, pending the author's decision.
- 2026-11-10/11, step 3: Hydrolog, W5 of its plan `docs/plans/2026-11-10-network-wizard.md` (A6): the copy of the schema (same SHA-256), the node panel's origin with the precedence of D4 and the notice of D6, Sieć's hand-off writing `node_provenance` (D8), in `cead00a`, `3de9e20`, `c2bf2e7`, `4c3c3e8`; W6 opened Hydrograf's own network hand-off as a fixture. Merged into `develop` at `3b28b15` after its gate (7659 passed); the plan closed at `d86b3a9`.
- 2026-11-11, step 4: D10 in `ecosystem.yaml`, Hydrograf's edge to Hydrolog as above, its note naming ADR-080 for the network; and the route „Delineate a network of subcatchments at control points (closing section, tributaries, gauges)” → `POST /api/delineate-network` among Hydrograf's routes (HUB-2.9). Hydrolog's network wizard gets no route: the routing table names its GUI only by `hydrolog gui serve`. `docs/ECOSYSTEM_MAP.md` and `AGENTS.md` regenerated; `uv run scripts/ecosystem.py validate` and `scripts/gate.sh` pass.
