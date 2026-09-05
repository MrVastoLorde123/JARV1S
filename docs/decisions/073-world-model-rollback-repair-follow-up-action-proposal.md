# M23.36 — World Model Rollback Repair Follow-Up Action Proposal Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Establish the explicit advisory action-selection boundary after M23.35 follow-up decision evidence.

## Contract
`EnvironmentWorldModelRollbackRepairFollowUpActionProposalService` consumes exactly one `EnvironmentWorldModelRollbackRepairFollowUpDecision`.

- `ACCEPT` deterministically becomes `RETRY_REPAIR`.
- `REJECT` deterministically becomes `NO_ACTION`.
- `DEFER` is supported as an upstream decision-artifact state but is not fabricated or handled by this deterministic action-proposal service.
- The action proposal preserves follow-up decision, environment, expected-model, and observed-model identities, reasons, and lineage.
- Proposal evidence is recursively immutable.
- The source follow-up decision remains unchanged.

## Authority boundary
A follow-up action proposal is advisory evidence. `RETRY_REPAIR` does not execute a retry, authorize capability execution, mutate the current-model store, mutate history, establish truth, grant permissions, synchronize distributed state, resolve conflicts, revoke anything, or establish adaptation truth.

The proposal says what action may be considered by a later boundary; it does not permit the action by itself.

## Explicitly deferred
Action decision, retry policy, repair re-application, persistence coordination, retry limits, backoff, transaction guarantees, distributed synchronization, conflict resolution, audit/event publication, and automated corrective execution remain separate boundaries.

## Files
- `src/core/environment_world_model_rollback_repair_follow_up_action_proposal.py`
- `src/core/tests/test_environment_world_model_rollback_repair_follow_up_action_proposal.py`
- `docs/decisions/073-world-model-rollback-repair-follow-up-action-proposal.md`

## Verification
Focused:
`python -m unittest src.core.tests.test_environment_world_model_rollback_repair_follow_up_action_proposal -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
