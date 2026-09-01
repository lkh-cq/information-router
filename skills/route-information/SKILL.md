---
name: route-information
description: Route complex research and information requests across web, literature, code, data, relation-topology, contradiction, long-tail, and provenance channels. Use when the user asks for a comprehensive or reproducible search, evidence mapping, source routing, pathway or dependency expansion, small-study discovery, bias auditing, or when a task spans multiple source types and must preserve traceability. Do not use for a simple one-step fact lookup unless the user explicitly asks for the routing process.
---

# Route Information

Compile a complex request into the smallest sufficient set of information routes, execute them with available capabilities, preserve provenance and contradictions, and return an answer whose coverage and limits are inspectable.

## Core invariants

- Keep retrieval relevance, evidence strength, and decision weight separate.
- Do not discard an item at retrieval merely because it is small, new, non-mainstream, negative, or inconclusive.
- Do not treat search rank, venue prestige, citation count, or organization reputation as truth.
- Preserve user constraints and all `must_preserve` entities, relations, contexts, dates, and exclusions.
- Label relations as `reported`, `inferred`, `hypothesized`, or `disputed`; never convert co-occurrence into a mechanism without evidence.
- Merge publication versions and overlapping datasets before judging independence.
- Treat unavailable tools, inaccessible originals, and unresolved contradictions as explicit gaps.
- Use the fast path for simple requests. A routing skill should not make ordinary answers needlessly elaborate.

## Fast path

Use a direct answer rather than the full workflow when all are true:

1. the request asks for one narrow fact or explanation;
2. comprehensive coverage, reproducibility, relations, or bias auditing are not requested;
3. the stakes are not high;
4. the answer does not depend on unstable current information that needs broad verification.

If the fact is current or could have changed, verify it with an authoritative source. Return the answer, source, and material limitation; do not expose a full RoutePlan.

## Full workflow

### 1. Compile the request profile

Capture:

- `goal`: the decision, question, or artifact the user needs;
- `mode`: `lookup`, `discover`, `verify`, `synthesize`, `reproduce`, or `monitor`;
- `domain` and relevant source ecosystems;
- `stakes`: `low`, `medium`, or `high`;
- `freshness`: historical, as-of date, current, or recurring;
- `modalities`: web, literature, code, data, standards, patents, registries, or user files;
- `constraints`: date, language, geography, access, source, licensing, and user prohibitions;
- `must_preserve`: entities, contexts, relation types, exclusions, and exact requirements;
- `output_contract`: direct answer, search plan, evidence map, audit, or reproduction package.

Resolve only ambiguities that materially change the route. Otherwise state a reasonable assumption and proceed.

### 2. Choose minimal lanes

Always consider `direct`. Add a lane only when its trigger is present:

- `orientation`: terminology or scope is unclear;
- `alias`: historical names, abbreviations, identifiers, spelling, or cross-domain terminology matter;
- `topology`: mechanism, causality, dependency, upstream/downstream, parallel, bypass, compensation, feedback, antagonism, or off-target effects matter;
- `contradiction`: the task verifies a claim, informs a high-stakes decision, or may contain contested evidence;
- `long-tail`: evidence is sparse, novel, small-scale, unpublished, gray, non-mainstream, or explicitly requested;
- `resource`: the task needs code, data, protocols, standards, registries, reagents, or implementation artifacts;
- `citation`: the user supplied a seed paper, repository, standard, issue, patent, or other citable starting point.

Read `references/routing-model.md` when lane choice, topology vocabulary, or task decomposition is nontrivial.

For every selected lane record its trigger, objective, source classes, completion condition, and residual risk. Do not select every lane by default.

### 3. Compile query blocks

Create small query blocks with one testable objective each. Combine only the dimensions needed for that objective:

- entity;
- context;
- relation;
- path or process;
- source type;
- time or version;
- viewpoint or polarity.

Prefer several blocks such as `entity + context`, `entity + relation`, and `entity + path + contradiction` over one query that ANDs every dimension. Preserve critical constraints, but relax nonessential terms during broad discovery.

Each block must have an ID, lane, objective, concept set, source classes, must-preserve constraints, and status.

### 4. Build the source plan

Choose sources by task and capability, not by a universal database checklist. Prefer original and authoritative sources where they directly support the claim.

Read `references/source-policy.md` before acting when the task is current, high-stakes, source-constrained, multi-modal, or technically specialized.

General rules:

- Browse for current or unstable facts, high-stakes guidance, precise citations, named pages or papers, niche topics, and explicit verification requests.
- For technical questions, prefer official documentation, specifications, source code, release history, and primary research.
- For repository questions, distinguish code on the default branch from issues, commits, releases, and forks.
- Use user-provided material as a seed and constraint source, not automatically as ground truth.
- Respect access, licensing, privacy, robots, and user prohibitions.
- If a capability is missing, degrade to a planned route and name what was not executed.

### 5. Execute in rounds

Use four possible rounds, stopping early when sufficient:

1. `orient`: establish vocabulary, entities, source landscape, and sentinels;
2. `retrieve`: execute direct, alias, and task-specific blocks;
3. `expand`: follow relations, citations, versions, code/data links, and newly discovered entities;
4. `challenge`: search contradictions, null results, failed replication, corrections, retractions, boundary conditions, and alternative explanations.

Run independent lanes in parallel when the environment supports it. Keep dependent expansions sequential so new entities and identifiers inform later blocks.

Do not claim that a search, page read, or database query succeeded unless the tool result confirms it.

### 6. Normalize evidence

For every material item record:

- stable source identifier and locator;
- version and status;
- claim or observation;
- polarity;
- evidence kind and method;
- directness;
- population, system, setting, dose, time, geography, software version, or other context;
- study family and independence group;
- query block and retrieval date;
- access limits and uncertainty.

Merge exact duplicates, then publication versions, then overlapping datasets or study families. Keep version history visible even after merging.

Read `references/evidence-and-bias.md` when constructing an evidence ledger, RelationEdges, independence groups, or a bias audit.

### 7. Expand and test relations

When topology is selected, test at least the relation classes relevant to the domain:

- upstream and downstream;
- parallel or redundant;
- bypass or alternative route;
- compensatory or adaptive response;
- feedback and feed-forward;
- activating, inhibitory, antagonistic, or synergistic;
- dependency, prerequisite, substitution, and off-target;
- temporal order and context-specific reversal.

For each RelationEdge preserve source entity, relation, target entity, context, assertion status, supporting evidence records, and conflicting evidence records.

Generate hypotheses only to drive retrieval. Clearly mark them and never present them as reported facts.

### 8. Audit bias

Inspect the search process for:

- publication and positive-result bias;
- source and platform concentration;
- ranking and availability bias;
- terminology and historical-name bias;
- language and geography bias;
- algorithmic recommendation loops;
- authority and citation prestige bias;
- confirmation bias and premature narrative lock-in;
- AI framing and unsupported relation inference.

For each material bias record its signal, affected scope, compensation performed, and residual risk. Do not hide a limitation because compensation was attempted.

### 9. Test stopping rules

Stop only when the applicable conditions are met:

- all core and must-preserve requirements map to executed or explicitly blocked query blocks;
- known sentinel items can be recovered when sentinels exist;
- recent rounds add little independent evidence, new relation types, or changed conclusions;
- no high-value lane has an unexplained coverage gap;
- material contradictions are resolved or explicitly retained as unresolved;
- provenance, retrieval dates, versions, and limitations are complete enough to audit.

High-stakes tasks also require authoritative-source and contradiction checks. A fixed result count is not a stopping rule.
If a quantitative marginal-yield threshold is used, derive it from the task design or obtain user agreement. Never invent a universal percentage or round count.

If the user asks for a reproducible plan rather than execution, stop after producing an executable RoutePlan with these conditions.

### 10. Render the output contract

Lead with the answer or decision-relevant result. Then include only the structures the task needs:

- coverage and lane summary;
- supporting, contradicting, null, or uncertain evidence;
- relation map or table;
- source and version provenance;
- bias ledger;
- unresolved gaps and next-best query blocks;
- reproducible query and stopping record.

Read `references/output-contracts.md` for detailed templates.

Do not provide a raw bibliography without synthesis unless the user explicitly requests one. Cite web sources near the claims they support.

## Academic protocol

For academic-grade tasks (systematic review, evidence map, regulatory or policy decision basis, mechanism synthesis), run the workflow under the academic protocol in `references/academic-protocol.md`:

- Freeze a non-drifting `Target` with a `statement_hash`; never reword it mid-run.
- Organize versioned `Themes` under the Target with a `sub_n` parent-child topology.
- Execute the strict three-round loop in order: `coarse` broad retrieval, `subtheme` per-theme retrieval, `fine` citation/interest/funding/data verification.
- Record per-round alignment (target re-checked, themes covered), cleaning (dedup, version and family merge), review, and a regression gate before advancing.
- Keep every evidence record with a real locator (URL/DOI/arXiv/PMID/file), declared interest, funding, and study family.

The executable contract is `schemas/academic-protocol.schema.json`, enforced by `scripts/validate_academic.py` and `scripts/eval_runner.py`. A protocol that fails validation is not complete.

## Quality gate

Before finalizing, verify:

1. Did the route match the user's actual mode and output?
2. Were small, negative, old-name, relation, and non-mainstream sources considered when relevant?
3. Are reported facts, inference, and hypotheses visibly distinct?
4. Were versions and overlapping evidence merged?
5. Does every material claim have traceable support or an uncertainty label?
6. Are current or high-stakes claims verified appropriately?
7. Are tool failures and source-access limits visible?
8. Would another Agent be able to reproduce the route and understand why it stopped?

If any answer is no, repair the plan or state the residual gap before delivering.
