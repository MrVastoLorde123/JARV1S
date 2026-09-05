# Decision 022 — Learning Write Proposal Boundary

## Context

M22.16 creates a non-writing `LearningDecision` from an inert `LearningCandidate`. A later layer must be able to describe what learning state could be written without treating a learning decision as permission to mutate memory or learning storage.

## Decision

Introduce an inert `LearningWriteProposal` boundary.

An accepted `LearningDecision`, together with the exact source `LearningCandidate`, may produce a proposal that contains:

- stable proposal, decision, candidate, execution, and handoff identities;
- an explicit learning domain;
- an immutable payload supplied for later write-policy evaluation;
- preserved candidate evidence and provenance;
- bounded confidence.

`DEFER` and `REJECT` do not produce a write proposal.

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
LearningWriteProposalService
↓
LearningWriteProposal
↓
Learning / Memory Write Policy
↓
Learning State / Memory Mutation
```

## Authority walls

- Learning Decision ≠ Learning Write Proposal
- Learning Write Proposal ≠ Learning Write
- Learning Write Proposal ≠ Memory Mutation
- Learning ≠ Authority
- Proposal ≠ Authorization
- Proposal ≠ Execution
- Candidate Evidence ≠ Truth
- Confidence ≠ Certainty
- Learning Domain ≠ Memory Domain

## Explicit exclusions

This milestone does not persist learning, mutate memory, authorize execution, trigger retries, revoke capabilities, or bypass the existing memory decision/executor architecture.
