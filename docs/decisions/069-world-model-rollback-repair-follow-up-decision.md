# M23.35 — World Model Rollback Repair Follow-Up Decision Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Establish the explicit decision boundary between M23.34 follow-up proposal evidence and any later follow-up action selection.

## Contract
`EnvironmentWorldModelRollbackRepairFollowUpDecisionService` consumes exactly one `EnvironmentWorldModelRollbackRepairFollowUpProposal`.

- `FOLLOW_UP` deterministically becomes `ACCEPT`.
- `NO_FOLLOW_UP` deterministically becomes `REJECT`.
- `DEFER` is a valid decision-artifact state but is not fabricated by this deterministic boundary.
- The decision preserves proposal, verification-decision, environment, expected-model, and observed-model identities.
- Reasons and lineage are recursively immutable.
- The source proposal remains unchanged.

## Authority boundary
Follow-up decision is advisory evidence. `ACCEPT` does not authorize retry, repair application, persistence mutation, capability execution, distributed synchronization, or any other side effect.

## Explicitly deferred
Retry policy, follow-up action selection, repair re-application, persistence coordination, follow-up verification, transactions, distributed synchronization, conflict resolution, audit/event publication, and automated corrective action remain separate boundaries.

## Verification
Focused:
`python -m unittest src.core.tests.test_environment_world_model_rollback_repair_follow_up_decision -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
