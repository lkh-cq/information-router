# Information Router

Information Router is an independent skills-only plugin that turns complex information requests into traceable routing, retrieval, evidence normalization, relation expansion, bias auditing, and stopping decisions.

Status: `v0.1.0` scaffold. The architecture is intentionally independent from any existing routing or consciousness-bus repository.

## Included

- `route-information`: the executable Agent workflow;
- routing, source, evidence, bias, and output references;
- JSON Schemas for route plans, evidence records, and the academic protocol;
- an academic protocol: non-drifting Target, versioned Themes with `sub_n`
  topology, a strict three-round loop, per-round gates, and auditable evidence;
- boundary, end-to-end, academic, and adversarial eval cases;
- product plan and implementation guidance.

## Validation

CI executes the real JSON Schemas and runs a semantic eval runner:

- `scripts/validate_route.py` validates route plans;
- `scripts/validate_evidence.py` validates evidence records;
- `scripts/validate_academic.py` executes `schemas/academic-protocol.schema.json`
  and checks semantic invariants (target hash stability, theme topology, phase
  order, query-block closure, real locators, content hashes,
  interest/funding/family, and derived coverage);
- `scripts/eval_runner.py` runs the positive examples plus 16 adversarial
  mutations and every eval case, so CI turns red on regressions.

The academic protocol also enforces minimum coverage for counter-evidence,
negative results, long-tail sources, small papers, and side paths. Coverage is
**derived** from the actual evidence records (polarity + `evidence_kind`), not
self-reported: a declared `satisfied: true` with too few real records fails
validation.

## Design principles

- Relevance, evidence strength, and decision weight stay separate.
- Small studies and long-tail sources are discoverable, then appraised in context.
- Relations include upstream, downstream, parallel, bypass, compensatory, antagonistic, feedback, and off-target paths.
- Supporting, contradictory, null, corrected, and withdrawn evidence remain visible.
- The router selects a minimal sufficient set of lanes and keeps simple questions simple.
- Missing tools produce an explicit execution gap, never a fabricated search result.

See [the product plan](docs/PLAN.md) and [the technical guide](docs/TECHNICAL_GUIDE.md).

## License

MIT License. See [LICENSE](LICENSE).
