# M23.41 — World Model Rollback Repair Retry Authorization Integrity Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Establish the explicit integrity boundary after M23.40 retry-authorization decision evidence. The boundary verifies that an authorization decision is internally consistent with its originating proposal and eligibility evidence before any downstream preparation or execution authority can rely on it.

## Contract
`EnvironmentWorldModelRollbackRepairRetryAuthorizationIntegrityService` consumes exactly one immutable `EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal` and one immutable `EnvironmentWorldModelRollbackRepairRetryAuthorizationDecision`.

- proposal, eligibility, action-decision, environment identities must match.
- requested action must match between proposal and decision.
- `RETRY_REPAIR` is valid only when proposal eligibility is `True` and decision is `ACCEPT`.
- `RETRY_REPAIR` with proposal eligibility `False` is valid only with decision `REJECT`.
- `NO_AUTHORIZATION` is valid only with decision `REJECT`.
- `DEFER` remains representable as an integrity-artifact state but is not treated as executable authority.
- evidence is recursively immutable.
- source proposal and decision remain unchanged.

## Authority boundary
Integrity validates evidence consistency. It does not create or grant execution authority and does not execute retry.

```text
Integrity ≠ Authority
Valid Integrity ≠ Execution
Authorization Decision ≠ Execution
```

## Explicitly deferred
Execution authorization issuance, confirmation/confirmation integrity where required, execution preparation/handoff, retry execution, repair re-application, persistence coordination, scheduling, distributed synchronization, conflict resolution, audit/event publication, and automated corrective execution remain separate boundaries.

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_world_model_rollback_repair_retry_authorization_integrity -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
