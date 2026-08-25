# Output Contracts

Use this reference to format the result for the user's decision or artifact. Do not emit every section by default.

## Contents

1. Quick answer
2. Search plan
3. Evidence map
4. Bias audit
5. Reproduction package
6. StopReport
7. Citation and claim discipline
8. Brevity controls

## 1. Quick answer

Use for fast-path tasks.

```markdown
<Direct answer in the first sentence.>

<One short explanation or material qualification.> [Source](url)
```

Add an as-of date when the fact is mutable.

## 2. Search plan

Use when the user wants a complete, reproducible retrieval strategy.

### Decision frame

- Goal:
- Mode / stakes / freshness:
- Must-preserve:
- Assumptions:
- Output:

### Route table

| Lane | Trigger | Objective | Source classes | Completion condition |
|---|---|---|---|---|

### Query blocks

| ID | Lane | Concepts | Example query | Source/adapter | Status |
|---|---|---|---|---|---|

### Evidence handling

- Inclusion and exclusion logic;
- version and study-family merging;
- context and relation fields;
- polarity and contradiction handling;
- resource and provenance capture.

### Bias and stopping

- anticipated biases and compensation;
- sentinels;
- marginal-yield and coverage tests;
- blocking constraints;
- audit/reporting format.

## 3. Evidence map

Lead with the decision-relevant synthesis.

### Claim matrix

| Claim | Supporting | Contradicting/null | Context | Status |
|---|---|---|---|---|

### Relation map

| Source | Relation | Target | Context | Assertion | Evidence |
|---|---|---|---|---|---|

### Independence and version notes

Group versions and overlapping datasets. State the number of independent evidence groups only when it can be supported.

### Gaps

List unresolved contradictions, missing contexts, inaccessible sources, blocked lanes, and the next query that could change the conclusion.

## 4. Bias audit

```markdown
| Bias | Signal | Affected scope | Compensation | Residual risk | Status |
|---|---|---|---|---|---|
```

Include only biases actually assessed. Do not mark `mitigated` unless the compensation was executed.

## 5. Reproduction package

### Scope and environment

- target behavior or result;
- date and version boundary;
- platform/environment;
- access and permission assumptions.

### Artifacts

| Artifact | Identifier/version | Location | Role | Status |
|---|---|---|---|---|

### Steps

Numbered, executable sequence with inputs, commands or procedures, expected outputs, and validation.

### Provenance

Queries, retrieval dates, repository SHAs, release/tag, data version, protocol version, and any transformation applied.

### Blockers and variance

List unavailable artifacts, environment differences, nondeterminism, and what a successful reproduction would or would not establish.

## 6. StopReport

```yaml
status: stopped | paused | blocked
reason:
  coverage: string
  sentinel_recovery: string
  marginal_yield: string
  contradictions: string
  provenance: string
uncovered:
  - item: string
    reason: not_applicable | no_evidence_found | blocked | not_searched
next_best_actions:
  - query_block_or_action
```

Use `paused` when another round could materially improve the result but the current task boundary or budget has been reached. Use `blocked` when a required source, permission, tool, or clarification is unavailable.

## 7. Citation and claim discipline

- Place citations next to the claims they support.
- Prefer direct pages and primary/authoritative sources.
- Distinguish source quotation from Agent inference.
- Do not cite one source as support for a broader claim than it makes.
- Use a retrieval date for mutable pages.
- Respect quotation and copyright limits.

## 8. Brevity controls

Default to the smallest output that satisfies the contract:

- summarize RoutePlan when the user wants findings, not process;
- collapse low-impact query blocks into a reproducibility appendix;
- show only material BiasLedger entries;
- keep full EvidenceRecord objects in an artifact when the user needs auditability;
- do not repeat the same limitations in every section.
