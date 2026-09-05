# Decision 021 — Learning Decision Boundary

## Context

M22.15 converts execution feedback into an inert `LearningCandidate`. JARVIS already has a provider-neutral memory decision layer and a separate mutation executor. The next boundary must decide whether a learning candidate should proceed without confusing that decision with memory mutation or authority.

## Decision

Introduce a provider-neutral `LearningDecisionService` that consumes `LearningCandidate` values and produces immutable `LearningDecision` records.

The decision layer:

- preserves candidate identity;
- exposes an explicit confidence value;
- distinguishes accept, defer, and reject actions;
- remains replaceable through a provider contract;
- cannot write memory or learning state;
- cannot authorize, retry, revoke, or execute tools.

The deterministic provider is only a dependency-free baseline. It is not treated as truth and does not replace a future model-backed learner or policy layer.

## Boundary

```text
ExecutionFeedbackEvent
↓
Feedback Evaluation
↓
LearningCandidate
↓
LearningDecisionService
↓
LearningDecision
↓
Learning / Memory Write Boundary
```

## Authority walls

- Learning Candidate ≠ Learning Decision
- Learning Decision ≠ Learning Write
- Learning Decision ≠ Memory Mutation
- Learning ≠ Authority
- Confidence ≠ Certainty
- Evidence ≠ Truth
- Learning Decision ≠ Retry Authorization
- Learning Decision ≠ Execution

## Explicit exclusions

This milestone does not persist learning, mutate memory, add automatic retries, re-authorize execution, revoke capabilities, or bypass the existing memory decision/executor architecture.
