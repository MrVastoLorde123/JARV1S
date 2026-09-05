# Decision 030 — Adaptation Proposal Admission Boundary

## Context

M22.24 represents an accepted adaptation decision as an immutable, inert proposal. The next boundary must determine whether that proposed change is structurally admissible before any future adaptation execution path can consume it.

## Decision

Introduce `LearningWriteAdaptationAdmissionService` and `LearningWriteAdaptationAdmission` as a non-mutating admission boundary after adaptation proposal.

The boundary:

- consumes only an existing `LearningWriteAdaptationProposal`;
- validates proposal structure through a replaceable provider;
- preserves exact proposal, decision, candidate, feedback, and execution lineage;
- produces deterministic admission identity;
- returns `ADMITTED` or `REJECTED`;
- applies a conservative baseline requiring non-empty adaptation, evidence, provenance, and confidence >= 0.5;
- cannot apply adaptations, mutate learning or memory, authorize tools, retry, or revoke.

## Boundary

```text
Adaptation Decision
↓
Adaptation Proposal
↓
Adaptation Admission
↓
Future Adaptation Execution
↓
Learning State / Memory
```

## Authority walls

- Adaptation Proposal != Adaptation Admission
- Adaptation Admission != Adaptation Execution
- Adaptation Admission != Memory Mutation
- Adaptation Admission != Authorization
- Adaptation Admission != Retry Authorization
- Adaptation Admission != Revocation
- Admission != Truth
- Completion != Certainty
- Evidence != Truth
- Learning != Authority

## Explicit exclusions

This milestone does not apply adaptations, mutate memory or learning state, authorize execution, trigger retries, revoke capabilities, or define concrete persistent adaptation stores/executors.
