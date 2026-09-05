# M23.25 — World Model Rollback Application Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Establish the explicit application boundary after M23.24 rollback decision evidence.

## Contract
`EnvironmentWorldModelRollbackApplicationService` consumes one immutable history and one matching rollback decision.

- `ACCEPT` selects the historical target as the resulting immutable current model and records an applied transition.
- `REJECT` or `DEFER` retain the current model and record that no rollback was applied.
- Current, target, history, and decision environment/model identities must align.
- The target model must exist in history.
- The application record preserves transition identity, decision identity, previous/target/resulting model identities, reasons, and lineage.
- Source history and model objects are never mutated.

## Mutation boundary
Because `EnvironmentWorldModel` and `EnvironmentWorldModelHistory` are frozen values, application means selecting a validated historical artifact as the resulting state and emitting a new immutable application record. It does not mutate an existing model object in place.

Persistence coordination remains a separate concern; this boundary does not write storage itself.

## Authority boundary
Rollback application does not establish truth, grant permission, authorize capability execution, mutate memory, retry providers, revoke anything, synchronize distributed state, or establish adaptation truth.

## Explicitly deferred
Persistence coordination, transactional rollback, rollback verification, distributed synchronization, conflict resolution, audit/event publication, and external side effects remain separate boundaries.

## Files
- `src/core/environment_world_model_rollback_application.py`
- `src/core/tests/test_environment_world_model_rollback_application.py`
- `docs/decisions/062-world-model-rollback-application.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_world_model_rollback_application -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
