# M23.26 — World Model Rollback Persistence Coordination Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Establish the explicit persistence boundary after M23.25 rollback application.

The boundary coordinates writing the immutable resulting world model into the existing current-model store. It does not rewrite world-model history.

## Contract
`EnvironmentWorldModelRollbackPersistenceService` consumes:

- one `EnvironmentWorldModelRollbackApplication`
- one resulting `EnvironmentWorldModel`
- one provider-neutral `EnvironmentWorldModelStore`

For an applied rollback:

- application/environment/resulting-model identities must align;
- the store must contain the application previous model identity;
- the resulting model is written using `expected_model_id=previous_model_id`;
- the compare-and-swap guard therefore fails closed when the store moved unexpectedly;
- successful persistence returns immutable persistence evidence.

For an unapplied rollback (`REJECT`/`DEFER` path from M23.25):

- the store is read and validated against the application previous identity;
- no write occurs;
- persistence evidence records `persisted=False`.

Nested reasons and lineage are recursively frozen.

## Authority boundary
Persistence coordination is a storage boundary, not an authorization boundary. It does not establish truth, select an authoritative model, grant permissions, authorize capability execution, mutate history, retry providers, revoke anything, synchronize distributed stores, resolve conflicts, or establish adaptation truth.

## Explicitly deferred
Transactions/atomic multi-store coordination, rollback verification, distributed synchronization, conflict resolution, audit/event publication, history rewriting, and durable persistence of the application evidence remain separate boundaries.

## Files
- `src/core/environment_world_model_rollback_persistence.py`
- `src/core/tests/test_environment_world_model_rollback_persistence.py`
- `docs/decisions/063-world-model-rollback-persistence-coordination-contract.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_world_model_rollback_persistence -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
