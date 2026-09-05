# M23.37 — World Model Rollback Repair Follow-Up Action Decision Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Establish the explicit decision boundary after M23.36 follow-up action proposal evidence.

## Contract
`EnvironmentWorldModelRollbackRepairFollowUpActionDecisionService` consumes exactly one `EnvironmentWorldModelRollbackRepairFollowUpActionProposal`.

- `RETRY_REPAIR` deterministically becomes `ACCEPT`.
- `NO_ACTION` deterministically becomes `REJECT`.
- `DEFER` is a valid decision-artifact state but is not fabricated by this deterministic boundary.
- The decision preserves proposal, follow-up-decision, environment, expected-model, observed-model, reasons, and lineage identities.
- The decision artifact is recursively immutable.
- The source action proposal remains unchanged.

## Authority boundary
The decision is advisory evidence. `ACCEPT` does not authorize execution, retry, repair application, persistence mutation, history mutation, capability execution, distributed synchronization, or any other side effect.

## Explicitly deferred
Actual retry execution, retry policy, retry limits/backoff, repair application, persistence coordination, follow-up verification, transactions, distributed synchronization, conflict resolution, audit/event publication, and automated corrective execution remain separate boundaries.

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_world_model_rollback_repair_follow_up_action_decision -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
