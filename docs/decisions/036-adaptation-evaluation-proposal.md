# Decision 036 — Adaptation Evaluation → Proposal Boundary

## Decision

An accepted `LearningWriteAdaptationEvaluationDecision` becomes a separate immutable proposal before downstream admission. Deferred or rejected evaluation decisions produce no proposal.

## Rationale

A decision is not an executable instruction. A dedicated proposal boundary preserves the separation between interpretation/decision and downstream admission while carrying explicit evidence and provenance forward.

## Contract

- Input is an exact `LearningWriteAdaptationEvaluationDecision` plus a non-empty proposal payload.
- Only `ACCEPT` produces a `LearningWriteAdaptationEvaluationProposal`.
- `DEFER` and `REJECT` produce no proposal.
- Proposal, evidence, and provenance are recursively immutable snapshots.
- Exact evaluation, feedback, source-feedback, adaptation-candidate, source-candidate, execution, admission, proposal, and domain lineage is preserved.
- Confidence remains bounded to `[0.0, 1.0]`.
- Proposal identity is deterministic for identical source decision and proposal evidence.
- Proposal cannot grant adaptation authorization, memory mutation, execution, retry, or revocation.

## Authority walls

- Evaluation Decision ≠ Proposal
- Proposal ≠ Admission
- Proposal ≠ Authorization
- Proposal ≠ Execution
- Proposal ≠ Retry Authorization
- Proposal ≠ Revocation
- Proposal ≠ Memory Mutation
- Decision ≠ Truth
- Learning ≠ Authority
