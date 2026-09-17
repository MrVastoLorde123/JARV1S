# Decision — Phase 6 World Model Boundary

## Decision

The JARVIS World Model will be implemented as a derived, provider-neutral state view over provenance-backed observations.

## Reasons

1. Phase 5 already provides durable evidence-bearing memory and provenance.
2. The world model needs current entities, relationships, and temporal state without duplicating durable-memory semantics.
3. Conflicting observations must remain inspectable rather than being silently rewritten into a single truth claim.
4. Reasoning needs an immutable snapshot interface that is independent of provider selection.

## Chosen semantics

- Observations require provenance identifiers.
- Entity and relation states are immutable candidates.
- Temporal validity is explicit.
- Current-view selection is deterministic and confidence/time ordered.
- Conflicts are retained as first-class uncertainty.
- Retraction removes an observation from the current view but keeps the observation record.
- Snapshot identity is deterministic for identical world state and generation time.
- World-model state is contextual/derived and is not itself a durable truth store.

## Rejected semantics

- Silent overwrite of conflicting state.
- Treating confidence as truth or authorization.
- Executing tools from the world-model layer.
- Selecting a model/provider from the world-model layer.
- Introducing a second durable database independent of Phase 5.
