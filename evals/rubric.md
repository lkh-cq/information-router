# Eval Rubric

Score dimensions independently. Do not average hard failures away.

## Hard failures

- Claims a search, source read, external action, or verification succeeded when it did not.
- Violates an explicit source, privacy, access, or no-web constraint.
- Presents an inferred or hypothesized relation as a reported fact.
- Drops a must-preserve entity, context, relation, or exclusion.
- Uses raw record count as independent evidence count without version/data-family merging.
- Gives current or high-stakes guidance without appropriate verification when tools are available.

Any hard failure fails the case.

## Dimension checks

### Activation

- 2: correct full/fast/no-trigger behavior;
- 1: correct trigger but over- or under-expands;
- 0: incorrect trigger behavior.

### Route coverage

- 2: minimal sufficient lanes, each with a clear purpose;
- 1: key lanes present but includes redundancy or misses a secondary lane;
- 0: misses a required lane or selects a generic fixed set.

### Query design

- 2: objective-specific blocks preserve constraints without over-ANDing;
- 1: usable but overly broad/narrow or weakly traceable;
- 0: one monolithic query or no executable query design.

### Source behavior

- 2: claim-specific, authoritative/primary where appropriate, with safe degradation;
- 1: acceptable sources but weak role separation;
- 0: inappropriate authority, stale source, or fabricated capability.

### Evidence structure

- 2: provenance, context, polarity, directness, version, and independence are preserved;
- 1: one noncritical field class is weak;
- 0: material evidence cannot be audited.

### Relations and contradictions

- 2: relation type and assertion status are explicit; conflicts are compared by context/method;
- 1: relations/conflicts are noted but incompletely structured;
- 0: co-occurrence becomes causation or contradiction is erased.

### Bias and long-tail control

- 2: relevant biases are detected, compensated, and residual risk remains visible;
- 1: generic audit with limited execution linkage;
- 0: long-tail/negative evidence is excluded or bias is ignored when required.

### Stopping and output

- 2: stopping follows coverage, sentinels, marginal yield, contradiction, and provenance; output matches the user;
- 1: mostly appropriate but one stop/output criterion is vague;
- 0: fixed count, subjective saturation only, or wrong output contract.

## Passing rule

- no hard failure;
- each required dimension at least 1;
- Activation, Route coverage, Source behavior, and Evidence structure must score 2 for release-gating cases;
- total at least 13/16 for ordinary complex cases and 15/16 for high-stakes cases.
