# Decision 029 — Adaptation Proposal Boundary

## Context

M22.23 establishes an explicit, non-mutating adaptation decision over a learning-write adaptation candidate. An accepted decision needs a structured proposal before any later adaptation policy, admission, or mutation boundary can evaluate a concrete change.

## Decision

Introduce `LearningWriteAdaptationProposalService` and `LearningWriteAdaptationProposal` as an inert proposal boundary after adaptation decision.

The boundary:

- consumes an exact adaptation decision and its exact source adaptation candidate;
- creates a proposal only for `ACCEPT` decisions;
- preserves feedback, execution, admission, learning-write proposal, decision, source candidate, and domain lineage;
- carries a recursively frozen adaptation payload plus evidence and provenance snapshots;
- produces deterministic proposal identity;
- remains non-writing and non-authorizing.

## Boundary

```text
Learning Write Feedback
↓
Adaptation Candidate
↓
Adaptation Decision
↓
Adaptation Proposal
↓
Adaptation Policy / Admission
↓
Adaptation Execution
```

## Authority walls

- Adaptation Decision ≠ Adaptation Proposal
- Adaptation Proposal ≠ Adaptation Write
- Adaptation Proposal ≠ Memory Mutation
- Adaptation Proposal ≠ Authorization
- Adaptation Proposal ≠ Retry Authorization
- Adaptation Proposal ≠ Revocation
- Evaluation ≠ Authority
- Completion ≠ Certainty
- Evidence ≠ Truth
- Learning ≠ Authority

## Explicit exclusions

This milestone does not apply adaptations, mutate learning state or memory, authorize execution, trigger retries, revoke capabilities, or define adaptation persistence/execution infrastructure.
