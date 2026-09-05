# M23.19 — World Model Store Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Establish a provider-neutral storage boundary for retaining one current `EnvironmentWorldModel` per environment without coupling the core contract to a filesystem, database, or synchronization mechanism.

## Contract
`EnvironmentWorldModelStore` exposes:

- `get(environment_id)` → current model or `None`
- `put(model, expected_model_id=...)` → stored model
- `remove(environment_id)` → removed model or `None`

The reference implementation is `InMemoryEnvironmentWorldModelStore`. It exists to prove store semantics and is not presented as durable persistence.

The store is environment-scoped and retains immutable `EnvironmentWorldModel` artifacts rather than mutating them.

An optional `expected_model_id` enables an explicit compare-and-swap style identity check. A mismatch or missing expected current model fails closed and leaves the stored state unchanged.

## Authority boundary
The store does not establish truth, authorize execution, infer permissions, mutate the world-model object in place, retry providers, synchronize distributed state, or establish adaptation truth.

Storage does not make a model more authoritative; it only retains the artifact selected by an upstream application boundary.

## Explicitly deferred
Durable filesystem/database persistence, transactions, rollback, historical revision retention, distributed synchronization, locking, conflict resolution, and external side effects remain separate future boundaries.

## Files
- `src/core/environment_world_model_store.py`
- `src/core/tests/test_environment_world_model_store.py`
- `docs/decisions/057-world-model-store-contract.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_world_model_store -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
