# Decision 038 — Adaptation Evaluation Execution Preparation

## Decision

An admitted adaptation-evaluation proposal must cross an explicit, non-executing preparation boundary before any future adaptation execution attempt.

## Rationale

M22.32 establishes admission, but admission is not an execution request. The next boundary must convert admitted evidence into an immutable handoff artifact while preserving exact lineage and preventing execution authority from leaking backward into preparation.

## Contract

- `LearningWriteAdaptationEvaluationExecutionPreparationService` consumes one exact M22.31 proposal and one exact M22.32 admission.
- Only `ADMITTED` proposals may be prepared.
- Exact proposal, decision, evaluation, feedback, source-feedback, candidate, source-candidate, and source-execution lineage is preserved.
- The M22.32 admission policy ID is preserved as policy provenance.
- The downstream payload is recursively frozen.
- The preparation ID is deterministic and is distinct from the historical source execution ID.
- Preparation does not authorize, start, retry, revoke, or mutate memory.
- Future execution remains a separate milestone and boundary.

## Authority wall

```text
Adaptation Evaluation Proposal
↓
Adaptation Evaluation Proposal Admission
↓
Future Adaptation Execution Preparation
↓
Future Adaptation Execution
```

Preparation is a handoff artifact, not permission to execute.

## Invariants

- Admission ≠ Preparation
- Preparation ≠ Authorization
- Preparation ≠ Execution
- Preparation ≠ Retry Authorization
- Preparation ≠ Revocation
- Preparation ≠ Memory Mutation
- Source Execution ID ≠ Future Preparation ID
- Evidence ≠ Truth
- Learning ≠ Authority
