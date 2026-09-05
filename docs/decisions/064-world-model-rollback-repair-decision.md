# M23.30 — World Model Rollback Repair Decision Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Establish the explicit decision boundary between M23.29 rollback repair proposal evidence and any future repair application.

## Contract
`EnvironmentWorldModelRollbackRepairDecisionService` consumes exactly one `EnvironmentWorldModelRollbackRepairProposal`.

- `REPAIR` deterministically becomes `ACCEPT`.
- `NO_REPAIR` deterministically becomes `REJECT`.
- The decision preserves proposal/environment/expected/observed model identities, reasons, and lineage.
- `DEFER` is a valid decision-artifact state but is not fabricated by this deterministic boundary.
- Invalid recommendation values fail closed.
- The source repair proposal remains unchanged.

## Authority boundary
Repair decision is advisory evidence. It does not apply repair, mutate persistence or history, establish truth, authorize execution, grant permissions, retry providers, synchronize distributed stores, resolve conflicts, revoke anything, or establish adaptation truth.

An `ACCEPT` decision is evidence required by a later repair-application boundary; it is not itself the repair operation.

## Explicitly deferred
Repair application, repair verification, persistence coordination for repair, transaction guarantees, distributed synchronization, conflict resolution, audit/event publication, and policy-rich defer logic remain separate boundaries.

## Files
- `src/core/environment_world_model_rollback_repair_decision.py`
- `src/core/tests/test_environment_world_model_rollback_repair_decision.py`
- `docs/decisions/064-world-model-rollback-repair-decision.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_world_model_rollback_repair_decision -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
