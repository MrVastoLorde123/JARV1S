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
