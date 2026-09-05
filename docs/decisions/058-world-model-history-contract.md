# M23.21 — World Model History Contract

## Status
IMPLEMENTED / AWAITING LOCAL VERIFICATION

## Purpose
Establish immutable historical retention for descriptive `EnvironmentWorldModel` artifacts without changing current-model selection or authority semantics.

## Contract
`EnvironmentWorldModelHistoryService` appends validated world-model artifacts into an ordered, environment-scoped history.

- History may be created from an empty state.
- Every model must belong to the history environment.
- Model identities must be unique within a history.
- Ordering is preserved; the latest artifact is the final entry.
- Prior model artifacts are retained as immutable values.
- Nested lineage is recursively immutable.
- Source models are never mutated.

## Authority boundary
History is retention and provenance support only. It does not establish truth, select an authoritative model, authorize execution, infer permissions or executability, mutate current state in place, retry providers, synchronize distributed state, or establish adaptation truth.

## Explicitly deferred
History persistence, rollback execution, pruning, compaction, distributed synchronization, conflict resolution, and confidence calibration remain separate boundaries.

## Verification
Local verification is required before marking VERIFIED / COMPLETE.

Focused:
`python -m unittest src.core.tests.test_environment_world_model_history -v`

Regression:
`python -m unittest discover -s src\\core -p "test*.py"`

No merge performed.
