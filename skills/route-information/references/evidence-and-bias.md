# Evidence, Relations, and Bias

Use this reference to normalize results, merge versions and study families, construct RelationEdges, and audit search-process bias.

## Contents

1. EvidenceRecord
2. Appraisal dimensions
3. Three-stage deduplication
4. RelationEdge
5. Contradiction handling
6. Long-tail appraisal
7. BiasLedger
8. Coverage audit
9. Evidence language

## 1. EvidenceRecord

Required conceptual fields:

- `record_id`: local stable ID;
- `source_id`: DOI, URL, repository SHA, standard ID, registry ID, or equivalent;
- `version_id` and `status`: current, superseded, corrected, withdrawn, retracted, deprecated, or unknown;
- `study_family_id`: groups publication versions or reports of one underlying study;
- `independence_group`: groups records that reuse the same data, cohort, experiment, benchmark, or code path;
- `claim`: narrow statement supported or challenged;
- `polarity`: supporting, contradicting, null, mixed, contextual, or not_applicable;
- `evidence_kind`: primary study, synthesis, official record, code, data, benchmark, report, commentary, or other;
- `directness`: direct, indirect, or inference;
- `method`: method relevant to interpretation;
- `context`: population/system, setting, time, dose, geography, version, and other applicability limits;
- `provenance`: query block, retrieval date, locator, and access limitation.

Unknown is preferable to invented precision.

## 2. Appraisal dimensions

Evaluate separately:

1. relevance to the user's exact question;
2. directness of the observation;
3. methodological limitations;
4. applicability to the target context;
5. independence from other records;
6. version/status integrity;
7. precision or uncertainty;
8. risk of selective reporting;
9. reproducibility or inspectability;
10. consistency with and explanation of other evidence.

Do not collapse these into a single universal score. A small mechanistic study can be highly relevant and direct while still uncertain and context-limited.

## 3. Three-stage deduplication

### Exact record

Merge identical identifier, URL, content hash, repository SHA, or bibliographic identity.

### Version chain

Link preprint, abstract, conference paper, accepted manuscript, published version, correction, expression of concern, retraction, updated standard, renamed page, release, tag, and commit.

Select a display version appropriate to the claim but preserve all status-changing events.

### Study/evidence family

Group records that use the same participant cohort, experiment, dataset, simulation, benchmark, survey, incident, or code implementation. Record partial overlap when the boundary is uncertain.

Evidence counts and phrases such as “multiple studies” must reflect independence groups, not raw records.

## 4. RelationEdge

Required fields:

- `source` entity;
- domain-specific `relation` verb;
- `target` entity;
- structural relation class;
- `context` and conditions;
- `assertion_status`;
- supporting and conflicting EvidenceRecord IDs;
- confidence basis stated in words;
- inference note when status is `inferred` or `hypothesized`.

### Assertion status

- `reported`: a source explicitly makes or demonstrates the relation;
- `inferred`: the Agent combines evidence to infer it;
- `hypothesized`: proposed only to guide retrieval or future work;
- `disputed`: material evidence conflicts over the relation.

Do not equate:

- association with causation;
- expression with activity;
- physical interaction with functional dependence;
- sequence with mechanism;
- shared citation with corroboration;
- issue discussion with merged code;
- database curation with independent experimental replication.

## 5. Contradiction handling

When records conflict:

1. verify they address the same entity, relation, outcome, and direction;
2. compare population/system, setting, time, dose, geography, and version;
3. compare methods, measurement, controls, analysis, and thresholds;
4. check corrections, retractions, later versions, and data overlap;
5. separate true contradiction from context-specific heterogeneity;
6. state what additional evidence would discriminate the explanations.

Preserve unresolved conflict. Do not average incompatible claims into a vague consensus.

## 6. Long-tail appraisal

Long-tail sources are included for discovery and bias correction, not granted automatic authority.

Record:

- evidence role and uniqueness;
- review or publication status;
- access to underlying method/data;
- sample or observation scope;
- independence from larger publications;
- whether it is later superseded;
- whether it reports a null, failure, unusual context, or novel relation missing elsewhere.

A small paper may be decisive for identifying a possible relation but insufficient for estimating general prevalence or effect size.

## 7. BiasLedger

Each entry contains:

```yaml
bias_type: string
signal: string
affected_scope: [query_blocks | source_classes | claims | relations]
compensation: string
residual_risk: string
status: open | mitigated | accepted
```

### Publication and polarity bias

Signals: mostly positive formal publications; absent registered outcomes; many references to unpublished results.

Actions: search registries, preprints, proceedings, theses, negative/null terms, failure replication, corrections, and withdrawals.

### Source concentration

Signals: one database, vendor, lab, country, organization, repository, or community dominates.

Actions: add source classes with different evidence roles; label dependence when no independent source exists.

### Ranking bias

Signals: review limited to the top-ranked results; sources repeat the same popular narrative.

Actions: use independent query formulations, citation traversal, targeted long-tail searches, and stratified sampling beyond the first page when justified.

### Terminology bias

Signals: current name only; older dates have few results; different disciplines use disjoint vocabularies.

Actions: identifiers, former names, abbreviations, translations, spelling, renamed packages/projects, and domain-specific synonyms.

### Language and geography bias

Signals: evidence is limited to one language or region despite context-sensitive claims.

Actions: add relevant regional sources or explicitly limit generalization. Do not machine-translate beyond what can be validated when precision is critical.

### Availability bias

Signals: only open or easily parsed sources are used; inaccessible primary sources are silently omitted.

Actions: record inaccessible items, use lawful metadata or secondary discussion with lower directness, and avoid detailed claims not supported by accessible content.

### Algorithmic recommendation bias

Signals: recommended items are near-duplicates or share the same citation cluster.

Actions: switch source class, create adversarial queries, and sample outside the recommendation graph.

### Confirmation and framing bias

Signals: all query terms presuppose one mechanism or desired answer; synthesis starts before alternatives are logged.

Actions: write alternative explanations and disconfirming blocks before final synthesis; retain null and mixed evidence.

### Authority and prestige bias

Signals: venue, institution, citation count, or maintainer status substitutes for content inspection.

Actions: trace the exact claim to method/data/code; classify authority by claim type.

## 8. Coverage audit

Before stopping, audit the matrix:

- required entities × contexts;
- selected lanes × completed blocks;
- material claims × supporting/contradicting/null evidence;
- relation classes × reported/inferred/disputed status;
- source roles × independent evidence groups;
- current mutable claims × retrieval date/version;
- must-preserve items × output location.

An empty cell is not automatically a failure. It must be classified as not applicable, no evidence found, blocked, or not searched with a reason.

## 9. Evidence language

Use calibrated wording:

- “reports” or “observed” for source-level findings;
- “supports” for convergent evidence;
- “suggests” for limited or indirect evidence;
- “is consistent with” when evidence does not uniquely identify a cause;
- “conflicts with” for substantive contradiction;
- “no evidence was found in the executed route” rather than “no evidence exists”;
- “hypothesis” for an untested relation.
