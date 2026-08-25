# Source and Tool Policy

Use this reference to select source classes, verify current or high-stakes claims, and degrade safely when capabilities are absent.

## Contents

1. Source selection hierarchy
2. Source classes
3. Mandatory verification triggers
4. Retrieval behavior
5. Multi-source routing
6. Tool-neutral capability map
7. Capability degradation
8. Access and privacy
9. Source stop conditions

## 1. Source selection hierarchy

Select by the claim that must be supported.

| Claim or task | Preferred evidence path |
|---|---|
| Official status, rule, standard, product behavior | Issuing authority or official documentation, then independent analysis |
| Scientific mechanism or effect | Primary study/data, then synthesis and domain resources |
| Broad evidence estimate | Systematic review/meta-analysis plus recent primary updates and corrections |
| Software behavior | Source code, tests, official docs, releases/commits, then issues and community reports |
| Historical event | Contemporaneous primary records plus reputable historical synthesis |
| Market/product recommendation | Current official specifications plus independent testing and user-relevant constraints |
| Reproduction | Exact code/data/protocol/version artifacts and environment details |
| Disputed claim | Direct supporting and contradicting evidence with method/context comparison |

Authority is claim-specific. A regulator is authoritative for its rule, not automatically for a biological mechanism. A maintainer is authoritative for intended behavior, not always for observed production behavior.

## 2. Source classes

### Authoritative web

Government, standards bodies, official organizations, official product or project documentation, and maintainers' release records.

### Scholarly discovery

General and domain indexes, library catalogs, full-text platforms, preprint servers, theses, proceedings, registries, and institutional repositories.

### Relation resources

Curated pathway/interaction databases, ontologies, knowledge graphs, dependency graphs, citation graphs, and network datasets. Treat database edges as curated claims with their own provenance, not direct experimental proof.

### Code ecosystem

Repository tree, default branch, tags, releases, commits, pull requests, issues, package registry, documentation, examples, tests, and forks. Record commit SHA or version when behavior is version-sensitive.

### Data and materials

Data repositories, supplementary files, protocols, standards, trial or study registries, material catalogs, configuration, and environment locks.

### User material

Attachments, notes, templates, seed lists, previous results, and constraints. Preserve provenance and separate the user's assertions from externally verified claims.

## 3. Mandatory verification triggers

Use current external verification when information may have changed, including:

- news, rules, regulations, schedules, prices, current people or roles;
- software versions, APIs, product specifications, standards, repository state;
- recommendations that could cost substantial time or money;
- medical, legal, financial, safety, or other high-stakes guidance;
- a named page, paper, dataset, repository, issue, standard, or file not supplied in full;
- explicit requests to search, browse, verify, cite, or provide links;
- niche or emerging facts where recall is uncertain.

For technical questions, rely on primary sources such as official documentation, specifications, source code, and research papers.

## 4. Retrieval behavior

1. Search broadly enough to identify the source, then open the source that supports the claim.
2. Do not cite a search result page when a direct page is available.
3. Record retrieval date for current and mutable sources.
4. Distinguish page publication date, event date, update date, and access date.
5. For PDFs, inspect the relevant page rather than relying only on snippets.
6. For code, distinguish current default branch from the version used in the user's context.
7. For discussions, distinguish a report, a maintainer statement, an accepted change, and merged code.
8. Follow licensing and quotation limits; summarize rather than reproduce long copyrighted text.

## 5. Multi-source routing

Do not add a source merely for diversity. Add it when it can provide a different evidence role:

- direct observation;
- independent replication;
- contradiction;
- implementation detail;
- version history;
- broader population or context;
- long-tail discovery;
- official rule or status;
- data/code/protocol needed for reproduction.

Source diversity without evidence-role diversity can create a false sense of corroboration.

## 6. Tool-neutral capability map

Classify available capabilities rather than hard-coding product names:

- `search`: find candidate sources;
- `fetch`: open or download source content;
- `structured_lookup`: query a database or API;
- `repo_read`: inspect repository objects and history;
- `local_read`: inspect user-provided files;
- `transform`: parse, normalize, deduplicate, or validate;
- `persist`: save an artifact or ledger;
- `act`: create or modify an external resource.

The Skill may recommend a class even when no matching tool is available. It must then mark the query block `blocked` or `planned`, not `executed`.

## 7. Capability degradation

| Missing capability | Allowed fallback | Forbidden behavior |
|---|---|---|
| search | use supplied sources; provide executable queries | claim comprehensive coverage |
| fetch/full text | use metadata/abstract with limitation | infer detailed methods not present |
| repo history | use released docs/version notes | claim a specific commit cause |
| specialist database | use adjacent sources and list database plan | say the specialist search ran |
| persistence | return the ledger inline or as a file | imply cross-session storage |
| external write | prepare a patch or plan | claim the external resource was created |

## 8. Access and privacy

- Use only permissions and credentials already configured for the task.
- Never request passwords, tokens, or private keys in chat.
- Do not move sensitive content to a new service without explicit authority.
- External writes require clear task authorization and an exact target.
- When a user prohibits web or a source, comply and describe coverage loss.
- Do not bypass access controls or use mirrors of uncertain legality.

## 9. Source stop conditions

Stop adding source classes when each material claim role is covered, recent source additions do not change the evidence map, and remaining classes are unlikely to alter the decision relative to task stakes.

For high-stakes or disputed claims, retain at least one authoritative path and one adversarial or independent path when available.
