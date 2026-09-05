# M22.24 — Adaptation Proposal Boundary

## Purpose

Establish the inert proposal boundary after adaptation decision so an accepted adaptation decision can be represented as a concrete proposed change without becoming adaptation truth, authorization, retry authority, revocation, or memory mutation.

## Contract

- `LearningWriteAdaptationProposalService` consumes an exact `LearningWriteAdaptationDecisionContext`.
- `LearningWriteAdaptationProposal` is immutable and recursively freezes adaptation, evidence, and provenance snapshots.
- Only `ACCEPT` decisions create proposals; `DEFER` and `REJECT` produce no proposal.
- Exact feedback, execution, admission, learning-write proposal, decision, source-candidate, and domain lineage is preserved.
- Proposal identity is deterministic.
- Adaptation proposals are inert and cannot grant write, mutation, authorization, retry, or revocation authority.

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

## Verification

Remote implementation status: **IMPLEMENTED / AWAITING LOCAL RECEIPT**.

Focused command:

```powershell
python -m unittest src.tools.tests.test_learning_write_adaptation_proposal -v
```

Regression command:

```powershell
python -m unittest discover -s src\core -p "test*.py"
```

Parent M22.23 is locally verified:

- 11/11 focused
- 502/502 core regression
- 513/513 total
