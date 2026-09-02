# M8.6 — Agency Reliability / Recovery

**Status:** VERIFIED / COMPLETE

M8.6 defines explicit, bounded reliability semantics for agency runs and execution attempts that encounter failure, interruption, partial completion, retry eligibility, or reconciliation needs.

## Authority boundary

```text
Recovery ≠ Authorization
Retry Eligibility ≠ Permission
Partial Completion ≠ Success
Interruption ≠ Failure
Reconciliation ≠ Truth
```

Any retry or follow-up execution requires a fresh M7 authority-bearing `ExecutionPreparation`. Recovery cannot manufacture authority, execution requests, credentials, provider handles, or hidden retries.

## Implemented

- `ReliabilityClassifier` classifies execution observations using explicit reliability signals.
- `ReliabilityAssessment` preserves the originating `execution_id` and observed evidence.
- `RecoveryPlanner` converts classifications into bounded, non-executing recovery intent.
- Retryable failure can only request **fresh authorization**; it cannot authorize a retry.
- Recovery requests carry an explicit bounded request count and never contain execution/provider credentials or handles.
- Blocked and terminal failures stop rather than enter implicit retry loops.
- Interruption, partial completion, and reconciliation requirements remain distinct from ordinary failure/success.

## Verification

From the user's real checkout:

```text
python -m unittest src.agency.tests.test_reliability -v
Ran 11 tests in 0.002s
OK

python -m unittest
Ran 942 tests in 5.692s
OK
```

M8.6 is complete. M9 is unblocked.
