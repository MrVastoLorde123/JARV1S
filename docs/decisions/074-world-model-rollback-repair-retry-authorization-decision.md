# M23.40 — World Model Rollback Repair Retry Authorization Decision Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Establish the explicit decision boundary after M23.39 retry-authorization proposal evidence.

## Contract
`EnvironmentWorldModelRollbackRepairRetryAuthorizationDecisionService` consumes exactly one immutable `EnvironmentWorldModelRollbackRepairRetryAuthorizationProposal`.

- `RETRY_REPAIR` deterministically becomes `ACCEPT`.
- `NO_AUTHORIZATION` deterministically becomes `REJECT`.
- `DEFER` is a valid decision-artifact state but is not fabricated by this deterministic boundary.
- Proposal, eligibility, action-decision, environment, expected-model, observed-model, requested-action, reasons, timing, and lineage identities are preserved.
- Decision evidence is recursively immutable.
- The source authorization proposal remains unchanged.

## Authority boundary
This is decision evidence, not the final execution authority boundary. `ACCEPT` confirms only that the proposal is accepted as authorization-decision evidence; it does not itself execute retry or repair re-application.

```text
Authorization Proposal ≠ Authorization
Authorization Decision ≠ Execution
ACCEPT ≠ Retry Execution
Decision ≠ Persistence Mutation
```

## Explicitly deferred
Actual retry execution, repair re-application, persistence coordination, scheduling, distributed synchronization, conflict resolution, audit/event publication, and automated corrective execution remain separate boundaries.

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_world_model_rollback_repair_retry_authorization_decision -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
