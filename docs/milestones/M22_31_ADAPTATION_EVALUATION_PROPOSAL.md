# M22.31 — Adaptation Evaluation → Proposal Boundary

## Purpose

Establish the proposal boundary after adaptation-evaluation decision so an accepted decision becomes an explicit, immutable proposal before downstream admission.

## Contract

- `LearningWriteAdaptationEvaluationProposalService` consumes an exact `LearningWriteAdaptationEvaluationDecision` plus a non-empty proposal payload.
- Only `ACCEPT` produces a proposal; `DEFER` and `REJECT` produce no proposal.
- `LearningWriteAdaptationEvaluationProposal` is immutable.
- Proposal, evidence, and provenance are recursively frozen snapshots.
- Exact evaluation, feedback, source-feedback, adaptation-candidate, source-candidate, execution, admission, proposal, and domain lineage is preserved.
- Confidence remains bounded to `[0.0, 1.0]`.
- Proposal IDs are deterministic for identical source decision and proposal evidence.
- Proposal is non-authorizing and non-executing.

## Boundary

```text
Adaptation Feedback
↓
Adaptation Feedback Evaluation
↓
Adaptation Evaluation Decision
↓
Adaptation Evaluation Proposal
↓
Future Adaptation Proposal / Admission
```

## Authority walls

- Evaluation Decision ≠ Proposal
- Proposal ≠ Admission
- Proposal ≠ Authorization
- Proposal ≠ Execution
- Proposal ≠ Retry Authorization
- Proposal ≠ Revocation
- Proposal ≠ Memory Mutation

## Verification

Remote implementation status: **IMPLEMENTED / AWAITING LOCAL RECEIPT**.

Focused command:

```powershell
python -m unittest src.tools.tests.test_learning_write_adaptation_evaluation_proposal -v
```

Regression command:

```powershell
python -m unittest discover -s src\core -p "test*.py"
```

Parent M22.30 is awaiting/expected local verification from the preceding receipt chain.
M22.29 is locally verified:

- 11/11 focused
- 502/502 core regression
- 513/513 total
