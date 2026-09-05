# M23.38 — World Model Rollback Repair Retry Policy / Eligibility Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Establish the explicit boundary for evaluating whether an accepted rollback-repair retry action is eligible for a later retry under bounded retry limits and deterministic backoff.

## Contract
`EnvironmentWorldModelRollbackRepairRetryEligibilityService` consumes exactly one `EnvironmentWorldModelRollbackRepairFollowUpActionDecision` and one `EnvironmentWorldModelRollbackRepairRetryPolicy`, plus explicit retry state and a timezone-aware evaluation timestamp.

- `ACCEPT` is eligible only while `retry_count < max_retries`.
- `REJECT` is not eligible.
- `DEFER` is not eligible.
- `max_retries` is explicit and bounded by a non-negative integer.
- Backoff is deterministic from `base_backoff_seconds`, `backoff_multiplier`, `retry_count`, and `max_backoff_seconds`.
- Backoff is capped at `max_backoff_seconds`.
- `next_eligible_at` is derived from the supplied evaluation timestamp; no scheduler entry is created.
- Environment, action-decision, model, and lineage identities are preserved.
- Evidence is recursively immutable.

## Authority boundary
Retry eligibility is advisory evidence. `eligible=True` does not authorize retry, repair application, persistence mutation, capability execution, scheduler registration, distributed synchronization, or any other side effect.

```text
Retry Eligibility ≠ Retry Authorization
Retry Eligibility ≠ Retry Execution
Backoff Calculation ≠ Scheduling
Retry Count ≠ Permission
Policy ≠ Authority
```

## Explicitly deferred
Actual retry execution, authorization, repair re-application, persistence coordination, scheduler integration, transaction guarantees, distributed synchronization, conflict resolution, audit/event publication, and automated corrective execution remain separate boundaries.

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_world_model_rollback_repair_retry_eligibility -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
