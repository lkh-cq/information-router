# Information Router

Information Router is an independent skills-only plugin that turns complex information requests into traceable routing, retrieval, evidence normalization, relation expansion, bias auditing, and stopping decisions.

Status: `v0.1.0` scaffold. The architecture is intentionally independent from any existing routing or consciousness-bus repository.

## Included

- `route-information`: the executable Agent workflow;
- routing, source, evidence, bias, and output references;
- JSON Schemas for route plans and evidence records;
- boundary and end-to-end eval cases;
- product plan and implementation guidance.

## Design principles

- Relevance, evidence strength, and decision weight stay separate.
- Small studies and long-tail sources are discoverable, then appraised in context.
- Relations include upstream, downstream, parallel, bypass, compensatory, antagonistic, feedback, and off-target paths.
- Supporting, contradictory, null, corrected, and withdrawn evidence remain visible.
- The router selects a minimal sufficient set of lanes and keeps simple questions simple.
- Missing tools produce an explicit execution gap, never a fabricated search result.

See [the product plan](docs/PLAN.md) and [the technical guide](docs/TECHNICAL_GUIDE.md).
