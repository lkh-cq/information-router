# Academic Protocol

Use this reference when a request is an academic-grade research task: a frozen
research target, versioned sub-themes, a strict three-round retrieval loop, and
an auditable evidence chain. It is the executable contract behind
`schemas/academic-protocol.schema.json` and `scripts/validate_academic.py`.

## When to activate

Activate the academic protocol when the user asks for a systematic review,
evidence map, regulatory or policy decision basis, mechanism synthesis, or any
task where the answer must be reproducible and auditable. Do not activate for a
simple fact lookup or a fast-path answer.

## 1. Non-drifting Target

A Target is the frozen research question. It must not drift across rounds.

```yaml
target:
  target_id: T-<SLUG>
  statement: <frozen question, never reworded>
  statement_hash: <sha256 of statement>
  scope:
    included: [<what is in>]
    excluded: [<what is out>]
  version: 1.0.0
```

Rules:

- `statement_hash` must equal `sha256(statement)`. Every round and alignment
  record must carry the same hash. A mismatch is a hard failure.
- Rewording the statement during retrieval is drift. If the user changes the
  question, freeze a new Target version instead of editing in place.
- `scope.excluded` is as binding as `scope.included`.

## 2. Versioned Themes and sub_n topology

Themes are versioned sub-questions subordinate to the Target. They form a tree.

```yaml
themes:
  - theme_id: TH-ROOT
    statement: <root theme>
    version: 1.0.0
    status: active
  - theme_id: TH-01
    statement: <sub-theme 1>
    version: 1.0.0
    status: active
theme_topology:
  roots: [TH-ROOT]
  edges:
    - parent: TH-ROOT
      child: TH-01
      sub_n: 1
```

Rules:

- Every theme is either a root or a child of exactly one parent. No cycles, no
  disconnected themes.
- `sub_n` is the 1-based ordinal of a child among its parent's children. For a
  parent with `k` children the ordinals must be exactly `1..k`.
- Theme statements are versioned independently of the Target. A superseded
  theme stays in the record with `status: superseded`.

## 3. Strict three-round loop

Rounds must appear in exactly this order and cover these phases:

| Round | Phase | Purpose |
|---|---|---|
| R1 | `coarse` | Broad retrieval: vocabulary, entities, source landscape, sentinels |
| R2 | `subtheme` | Per-sub-theme retrieval driven by the theme topology |
| R3 | `fine` | Citation chains, interest relations, funding sources, basic data verification |

Each round records `target_hash`, an `alignment` (target re-checked, themes
covered), `cleaning` (dedup, version merge, family merge), `review`, a `gate`,
and the query blocks it executed. A round may not skip a phase or repeat one.

## 4. Per-round gates

Every round must pass three checks before the next round starts:

- `cleaning`: exact duplicates, publication versions, and overlapping datasets
  or study families are merged;
- `review`: a named reviewer and method re-check the round's material;
- `regression`: the round still satisfies the frozen Target and scope.

A gate with any unpassed check is a hard failure. Do not claim a round is
complete when its gate is open.

## 5. Evidence chain

Every material evidence record must carry:

- `locator`: a real, verifiable locator (URL, DOI, arXiv ID, PMID, or `file://`
  path). Fabricated or unverifiable locators are hard failures.
- `claim` and `polarity` (`supporting`, `contradicting`, `null`, `uncertain`);
- `interest`: whether conflicts were declared, and the conflict list;
- `funding`: the funding source, or an explicit `unfunded` / `not applicable`;
- `family`: the study family / independence group, so overlapping datasets are
  not counted as independent evidence;
- `query_block`: the block that produced it, which must exist in the protocol.

## 6. Retrieval adapter

Retrieval goes through an adapter so that source content can be verified rather
than assumed. The adapter interface is:

- `verify_locator(locator) -> bool`: checks the locator matches a real scheme
  (URL, DOI, arXiv, PMID, file URI). Implemented in `scripts/validate_academic.py`
  and exercised by `scripts/eval_runner.py`.
- `fetch_source(locator) -> SourceContent | None`: returns the source content for
  a locator. In offline eval, this reads a local fixture; in production it calls
  the available retrieval capability.
- `verify_source_content(source, claim) -> bool`: confirms the recorded claim is
  actually supported by the source content, not merely cited.

A tool result must be confirmed before it is treated as retrieved. Missing
capabilities are recorded as explicit gaps, never as successful searches.

## 7. Validation and eval

- `scripts/validate_academic.py <protocol.json>` executes the real JSON Schema
  and all semantic invariants above. It is dependency-free.
- `scripts/eval_runner.py` runs the positive example, 12 adversarial mutations,
  and every eval case. CI fails on any regression.
- Adversarial fixtures prove the validator rejects drift, wrong phase order,
  fake locators, orphan or unknown query blocks, extra fields, topology cycles,
  missing interest, reported drift, unpassed gates, disconnected themes, and
  incomplete `sub_n` ordinals.

## 8. Relationship to the route plan

The academic protocol is a companion to a `RoutePlan`. The route plan selects
lanes and query blocks; the academic protocol freezes the Target, organizes
Themes, enforces the three-round loop, and audits the evidence chain. Use both
together for academic-grade tasks: compile the RoutePlan first, then execute it
under the academic protocol's rounds and gates.
