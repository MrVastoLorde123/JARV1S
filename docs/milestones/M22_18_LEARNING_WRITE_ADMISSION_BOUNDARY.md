# M22.18 — Learning Write Admission Boundary

## Purpose

Establish the policy boundary between an inert `LearningWriteProposal` and any later learning-state or memory mutation.

## Contract

- `LearningWriteAdmissionService` consumes one `LearningWriteProposal`.
- A replaceable `LearningWriteAdmissionProvider` returns an immutable `LearningWriteAdmission`.
- Admission is explicit: `ADMITTED` or `REJECTED`.
- The exact proposal, decision, and candidate identities must be preserved.
- Payload, evidence, provenance, and confidence are checked before admission.
- Admission itself does not grant write authority.
- No learning state or memory is mutated by this milestone.

## Deterministic baseline policy

The baseline rejects proposals with an empty payload, missing evidence, missing provenance, or confidence below `0.5`.

This threshold is a baseline policy, not an absolute truth. Future domain-specific policies may be stricter and must remain behind the same boundary.

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

## Verification

Remote implementation status: **IMPLEMENTED / AWAITING LOCAL RECEIPT**.

Expected focused command:

```powershell
python -m unittest src.tools.tests.test_learning_write_admission -v
```

Regression command:

```powershell
python -m unittest discover -s src\core -p "test*.py"
```

Parent M22.17 was locally verified:
- 13/13 focused
- 502/502 core regression
