# M22.25 — Adaptation Proposal → Admission Boundary

## Purpose

Establish the deterministic admission boundary after adaptation proposal so a proposed self-change can be screened before a future adaptation execution boundary.

## Contract

- `LearningWriteAdaptationAdmissionService` consumes an immutable adaptation proposal.
- `LearningWriteAdaptationAdmission` is immutable and identity-bound.
- Admission status is explicitly `ADMITTED` or `REJECTED`.
- The baseline requires non-empty adaptation, evidence, provenance, and confidence >= 0.5.
- Admission providers are replaceable while the service validates returned identity.
- Admission identity is deterministic.
- Admission never grants mutation, authorization, retry, revocation, or tool-execution authority.

## Boundary

```text
Adaptation Candidate
↓
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

## Verification

Remote implementation status: **IMPLEMENTED / AWAITING LOCAL RECEIPT**.

Expected focused command:

```powershell
python -m unittest src.tools.tests.test_learning_write_adaptation_admission -v
```

Regression command:

```powershell
python -m unittest discover -s src\core -p "test*.py"
```

Parent M22.24 is locally verified:

- 11/11 focused
- 502/502 core regression
- 513/513 total
