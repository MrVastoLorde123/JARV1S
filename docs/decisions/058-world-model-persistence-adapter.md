# M23.20 — World Model Persistence Adapter Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Provide an explicit filesystem-backed persistence adapter behind the M23.19 provider-neutral world-model store contract.

## Contract
`FileEnvironmentWorldModelStore` persists one immutable `EnvironmentWorldModel` per environment as JSON.

- `get(environment_id)` reconstructs the validated immutable model or returns `None` when absent.
- `put(model, expected_model_id=...)` writes one model and supports compare-and-swap style identity protection.
- `remove(environment_id)` removes and returns the current model when present.
- malformed or identity-mismatched persisted data fails closed.
- filesystem writes use a temporary file followed by replacement to avoid exposing a partially written JSON artifact.
- environment identifiers are restricted to simple path-safe keys.

## Architectural boundary
The adapter is an implementation of M23.19 storage semantics. The core remains independent of filesystem technology through the existing store contract.

Persistence retains an upstream-selected model; it does not establish truth, grant authority, authorize execution, infer permissions, mutate model objects in place, retry providers, synchronize distributed state, resolve conflicts, or establish adaptation truth.

## Explicitly deferred
Database-specific persistence, transactions, encryption at rest, distributed synchronization, locking beyond the store's compare-and-swap identity check, historical retention, rollback, replication, and external side effects remain separate boundaries.

## Files
- `src/core/environment_world_model_persistence.py`
- `src/core/tests/test_environment_world_model_persistence.py`
- `docs/decisions/058-world-model-persistence-adapter.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_world_model_persistence -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
