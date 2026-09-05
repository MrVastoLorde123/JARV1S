# M23.28 — World Model Rollback Verification Decision Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Establish the explicit decision boundary after M23.27 rollback verification evidence.

## Contract
`EnvironmentWorldModelRollbackVerificationDecisionService` consumes exactly one `EnvironmentWorldModelRollbackVerification`.

- `verified=True` deterministically becomes `ACCEPT`.
- `verified=False` deterministically becomes `REJECT`.
- The decision preserves verification identity, environment identity, expected model identity, observed model identity, reasons, and lineage.
- `DEFER` is a valid decision-artifact state but is not fabricated by this deterministic boundary; policy-rich defer logic remains separate.
- The source verification artifact remains unchanged.

## Authority boundary
Rollback verification decision is advisory evidence. It does not repair state, authorize capability execution, mutate persistence or history, establish truth, retry providers, synchronize distributed stores, resolve conflicts, revoke anything, or establish adaptation truth.

An `ACCEPT` decision means the observed current model matched the persisted rollback result. A `REJECT` decision means the observed current model did not establish that match. Neither decision performs corrective action.

## Explicitly deferred
Repair/correction proposals, retry policy, distributed synchronization, transaction guarantees, conflict resolution, audit/event publication, and automated corrective action remain separate boundaries.

## Files
- `src/core/environment_world_model_rollback_verification_decision.py`
- `src/core/tests/test_environment_world_model_rollback_verification_decision.py`
- `docs/decisions/064-world-model-rollback-verification-decision.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_world_model_rollback_verification_decision -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
