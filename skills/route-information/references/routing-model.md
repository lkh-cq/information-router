# Routing Model

Use this reference to compile RequestProfile, select lanes, expand relations, and design query blocks.

## Contents

1. RequestProfile
2. Mode classifier
3. Lane catalog
4. Relation vocabulary
5. Query dimensions
6. QueryBlock compiler
7. Lane selection examples
8. Over-routing guard

## 1. RequestProfile

```yaml
goal: string
mode: lookup | discover | verify | synthesize | reproduce | monitor
domain: string
stakes: low | medium | high
freshness:
  kind: historical | as_of | current | recurring
  as_of: date | null
modalities: [web, literature, code, data, standards, patents, registries, local_files]
constraints:
  dates: object | null
  languages: [string]
  geographies: [string]
  access: string | null
  prohibited_sources: [string]
  required_sources: [string]
must_preserve:
  entities: [string]
  contexts: [string]
  relations: [string]
  exclusions: [string]
output_contract: quick_answer | search_plan | evidence_map | audit | reproduction_package
```

Do not invent fields that look precise but are unknown. Use `null`, `unknown`, or an explicit assumption.

## 2. Mode classifier

### lookup

Use for one bounded fact, definition, status, or explanation. Default to fast path unless the fact is current, high-stakes, disputed, or the user asks for process.

### discover

Use when the user wants candidate topics, mechanisms, products, sources, or research directions and does not already know the answer space. Prioritize orientation, alias, long-tail, and diversity of source classes.

### verify

Use when testing a proposition or claim. Require contradiction checks, evidence polarity, source directness, and clear conclusion boundaries.

### synthesize

Use for reviews, comparisons, evidence maps, or a unified view across many sources. Require deduplication, context grouping, and explicit heterogeneity.

### reproduce

Use when another person must rerun an analysis, experiment, implementation, or search. Require resource and version routing, executable steps, and blocking dependencies.

### monitor

Use when future changes matter. Define a current baseline, change signals, authoritative sources, cadence or event trigger, and notification condition. Do not create a recurring action unless the user asks for it and the environment supports it.

## 3. Lane catalog

### orientation

Objectives:

- disambiguate names and scope;
- identify canonical entities and identifiers;
- find relevant source ecosystems and sentinel materials;
- discover vocabulary used by different disciplines.

Completion: core entities and meanings are stable enough to compile focused blocks.

### direct

Objectives:

- retrieve evidence directly answering the core question;
- establish the shortest evidence path to the requested output.

Completion: the central claim or decision has direct evidence or a documented evidence gap.

### alias

Objectives:

- cover synonyms, abbreviations, identifiers, former names, translations, spelling variants, project renames, gene/protein naming differences, package names, and deprecated APIs.

Completion: high-value naming periods and communities are represented.

### topology

Objectives:

- retrieve structured relations rather than mere topic co-occurrence;
- search both known paths and alternatives around them;
- reveal nodes whose influence is indirect or conditional.

Completion: requested relation classes are searched and material edges have contexts and assertion status.

### contradiction

Objectives:

- find evidence that refutes, limits, reverses, fails to reproduce, corrects, or withdraws a claim;
- identify differences in methods or context that may explain conflict.

Completion: at least one adversarial query family is executed and conflicts are classified.

### long-tail

Objectives:

- discover small studies, brief reports, proceedings, posters, theses, preprints, registries, supplementary data, niche venues, non-English records, archived pages, and lesser-known repositories when relevant;
- counter publication, venue, and ranking bias.

Completion: selected long-tail classes are searched or explicitly blocked, and their appraisal is separate from retrieval.

### resource

Objectives:

- locate code, datasets, protocols, standards, materials, registries, configuration, dependency versions, package artifacts, and issue histories.

Completion: required artifacts are located with version/status, or blockers are listed.

### citation

Objectives:

- follow backward references, forward citations, related records, derivative software/data, corrections, and later versions from seed materials.

Completion: each seed's most relevant inbound/outbound paths are checked to the chosen depth.

## 4. Relation vocabulary

Use a domain-specific verb when available. Map it to one or more structural classes for coverage auditing.

| Structural class | Example verbs or signals |
|---|---|
| identity | is, aliases, renames, supersedes |
| membership | contains, belongs_to, part_of |
| sequence | precedes, follows, transitions_to |
| causation | causes, induces, produces, triggers |
| regulation | activates, inhibits, upregulates, suppresses |
| dependency | requires, depends_on, prerequisite_for |
| substitution | replaces, substitutes_for, fallback_for |
| bypass | bypasses, circumvents, alternative_route_to |
| compensation | compensates_for, adapts_to, rescues |
| parallelism | operates_in_parallel, redundant_with |
| feedback | feeds_back_to, reinforces, dampens |
| interaction | binds, calls, imports, communicates_with |
| contradiction | refutes, conflicts_with, fails_to_reproduce |
| provenance | derived_from, cites, implements, reproduces |
| version | updates, corrects, retracts, forks, deprecates |

Consider conditional reversals: a relation may change by species, tissue, dose, time, environment, geography, software version, permissions, or configuration.

## 5. Query dimensions

The mnemonic `E-C-R-P-S-T-V` describes coverage, not a single Boolean query.

- `E Entity`: object, population, technology, person, organization, component;
- `C Context`: setting, organism, tissue, dose, time window, geography, platform, version;
- `R Relation`: association, action, dependency, contrast, contradiction;
- `P Path/Process`: mechanism, workflow, causal chain, upstream/downstream, alternative route;
- `S Source`: web, paper, code, data, registry, patent, standard;
- `T Time`: publication, event, update, validity, correction, deprecation;
- `V Viewpoint`: supporting, null, negative, disputed, failed, boundary, alternative explanation.

## 6. QueryBlock compiler

Generate blocks in families:

1. canonical entity + direct objective;
2. aliases + direct objective;
3. entity + one relation class;
4. entity + process/path terms;
5. entity + contradiction viewpoint;
6. entity + selected long-tail source class;
7. seed identifier + citation/version traversal;
8. discovered entity/edge + targeted follow-up.

Each block must state why it exists. If two blocks have the same objective and source behavior, merge them.

## 7. Lane selection examples

### Simple current software version

Mode `lookup`; lanes `direct`, possibly `resource`. Verify official release source. No long-tail or full bias ledger.

### Mechanistic biomedical review with bypass routes

Mode `synthesize`; lanes `orientation`, `direct`, `alias`, `topology`, `contradiction`, `long-tail`, `citation`, and `resource` if data/protocols are requested.

### Verify a vendor performance claim

Mode `verify`; lanes `direct`, `contradiction`, `resource`, and `long-tail` for independent benchmarks. Separate vendor evidence from independent evidence.

### Reproduce a GitHub bug

Mode `reproduce`; lanes `direct`, `alias`, `resource`, `citation`. Search issue, code, release, commit, dependency, and environment versions. Add contradiction if maintainers dispute the cause.

## 8. Over-routing guard

Remove a lane when:

- it cannot change the decision or requested artifact;
- another selected lane fully covers the same objective;
- the user explicitly excludes it;
- the cost is disproportionate to stakes and no significant bias would remain;
- it is speculative and lacks a retrieval hypothesis.

Record only material omitted lanes, not an exhaustive list of everything theoretically possible.
