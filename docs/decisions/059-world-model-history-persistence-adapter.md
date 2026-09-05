# M23.22 — World Model History Persistence Adapter Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Provide a concrete filesystem-backed persistence adapter for the immutable ordered world-model history established by M23.21.

## Contract
`FileEnvironmentWorldModelHistoryStore` persists one ordered `EnvironmentWorldModelHistory` per environment as JSON.

- reads reconstruct validated immutable model/history artifacts
- writes preserve model order and latest semantics
- malformed or identity-mismatched payloads fail closed
- environment identifiers are path-safe keys
- temporary-file replacement is used for writes
- source history/model objects are never mutated

## Authority boundary
Persistence retains historical descriptive evidence. It does not establish truth, select an authoritative model, authorize execution, apply rollback, infer permissions or executability, synchronize distributed state, or establish adaptation truth.

## Explicitly deferred
Rollback execution, pruning, compaction, transactions, distributed synchronization, replication, encryption at rest, and conflict resolution remain separate boundaries.

## Files
- `src/core/environment_world_model_history_persistence.py`
- `src/core/tests/test_environment_world_model_history_persistence.py`
- `docs/decisions/059-world-model-history-persistence-adapter.md`

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_world_model_history_persistence -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
