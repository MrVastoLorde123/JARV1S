# M22.34 — Adaptation Evaluation Execution Boundary

## Purpose

Execute exactly one prepared adaptation-evaluation artifact from M22.33 through a replaceable applier while preserving lineage and keeping execution separate from authorization, retry, revocation, and memory mutation.

## Boundary

```text
Adaptation Evaluation Proposal Admission
↓
Future Adaptation Execution Preparation
↓
Future Adaptation Execution
↓
Future Outcome / Result Integrity
```

## Contract

- Consume one exact M22.33 preparation artifact.
- Reject preparation carrying authorization, started state, retry, revocation, or memory-mutation permission.
- Create a deterministic execution ID distinct from the historical source execution ID and preparation ID.
- Preserve exact preparation/admission/proposal/decision/evaluation/feedback/source-feedback/candidate/source-candidate/source-execution/domain/policy lineage.
- Pass an immutable execution request to a replaceable applier.
- Convert applier exceptions into an explicit FAILED result rather than leaking execution exceptions through the boundary.
- Return an immutable COMPLETED or FAILED result.

## Authority walls

- Preparation ≠ Execution
- Execution ≠ Authorization
- Execution Result ≠ Truth
- Execution Result ≠ Memory Mutation
- Execution Result ≠ Retry Authorization
- Execution Result ≠ Revocation
- Learning ≠ Authority

## Verification

Focused:

```powershell
python -m unittest src.tools.tests.test_learning_write_adaptation_evaluation_execution -v
```

Regression:

```powershell
python -m unittest discover -s src\core -p "test*.py"
```

M22.34 remains unverified until the user provides the local receipt.
