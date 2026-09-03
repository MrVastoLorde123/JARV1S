# Decision 066 — M10.7 Intelligence Integration

## Status

IN PROGRESS

## Decision

M10.7 integrates the bounded outputs of M10 learning into an immutable provider-neutral `IntelligenceContext` used by future reasoning, without granting authority, truth, authorization, execution, or policy mutation.

## Inputs

```text
M10.2 Evaluation
M10.3 Accepted Adaptation
M10.4 Retrieval
M10.5 Reasoning Feedback
M10.6 Reliability
```

These remain semantically distinct inside the context. Integration is aggregation, not promotion of one learning artifact into another authority class.

## Reliability interaction

Reliability is a safety filter at the intelligence boundary:

```text
SUSPENDED / REVERSED / SUPERSEDED
              ↓
not eligible for active reasoning context
```

Their historical existence remains preserved in M10.6. Filtering is not deletion.

`WATCH` and `CONFLICTED` reliability states remain represented as explicit reliability evidence while they are active in context; they are not silently promoted to truth.

## Adaptation interaction

Only explicitly accepted adaptations may influence intelligence context. Rejected or reversed adaptations are not treated as active behavioral guidance.

## Semantic walls

```text
Intelligence Context ≠ Truth
Intelligence Context ≠ Authority
Learning ≠ Permission
Relevance ≠ Certainty
Adaptation ≠ Authorization
Evaluation ≠ Intent
Reliability ≠ Truth
Integration ≠ Execution
Intelligence ≠ Unbounded Agency
```

## Non-goals

- no authority mutation
- no authorization
- no execution
- no capability expansion
- no automatic policy mutation
- no conversion of learning confidence into certainty
- no silent resurrection of reversed, suspended, or superseded learning
- no provider-specific intelligence runtime

## Architecture

```text
Experience
   ↓
Evaluation
   ↓
Adaptation / Memory / Quality / Reliability
   ↓
Intelligence Integration
   ↓
IntelligenceContext
   ↓
Future Reasoning
   ↓
M7 Authority
```

M10.7 is complete only when this boundary is covered by focused tests and the learning-area suite remains green.
