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

## Required invariants

- Failure remains failure.
- Interruption remains distinguishable from failure and success.
- Partial completion is explicit and cannot be treated as full completion.
- Retry eligibility is bounded data, not permission.
- Recovery attempts have explicit bounds.
- Repeated failure cannot create an unbounded loop.
- Reconciliation uses known execution evidence and does not invent missing observations.
- Original execution identity remains preserved; follow-up execution identity is explicit.
- M8.6 does not replace `ExecutionLifecycle`, `ControlledAgency`, or plan-level `ExecutionState`.

## Existing-stack relationship

M8.1 produces execution observations. M8.2 realizes capabilities/plugins. M8.3 integrates observations into context/state. M8.4 owns per-execution lifecycle. M8.5 owns bounded sequencing. M8.6 adds reliability and recovery semantics around these existing components.

## Non-goals

M8.6 does not implement unrestricted autonomous recovery, hidden retries, policy or authorization decisions, dynamic plugin loading, workers, unrestricted planning, or automatic credential/provider substitution.

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

Checkpoint: `milestone/m8-6-complete`
Decision: `docs/decisions/051-m8-6-agency-reliability-recovery.md`
Decision: `docs/decisions/052-m8-complete.md`
