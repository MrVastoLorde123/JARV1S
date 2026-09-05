# Decision 023 — Learning Write Admission Boundary

## Context

M22.17 establishes an inert `LearningWriteProposal` between a learning decision and any later mutation. A proposal is a request-shaped artifact, not permission to write. The next boundary must determine whether the proposal satisfies an explicit write-admission policy without performing the write itself.

## Decision

Introduce a provider-neutral `LearningWriteAdmissionService` that consumes one exact `LearningWriteProposal` and returns an immutable `LearningWriteAdmission`.

The admission layer:

- preserves exact proposal, decision, and candidate identity;
- preserves the explicit learning domain;
- applies structural policy requirements for payload, evidence, provenance, and confidence;
- returns explicit `ADMITTED` or `REJECTED` status;
- records the policy identity and reason;
- remains replaceable through a provider contract;
- cannot mutate learning state or memory;
- cannot authorize execution, retry, revoke, or grant authority.

The deterministic provider is a dependency-free baseline policy, not a claim that every learning domain should use the same threshold forever.

## Boundary

```text
LearningDecision
↓
LearningWriteProposal
↓
LearningWriteAdmissionService
↓
LearningWriteAdmission
↓
Learning / Memory Write Executor
```

## Authority walls

- Learning Write Proposal != Learning Write Admission
- Learning Write Admission != Learning Write
- Admission != Authorization
- Admission != Execution
- Learning != Authority
- Confidence != Certainty
- Evidence != Truth
- Learning Domain != Memory Domain

## Explicit exclusions

This milestone does not persist learning, mutate memory, authorize tools, trigger retries, revoke capabilities, or execute any writer.
