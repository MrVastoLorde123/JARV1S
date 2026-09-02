# Decision 049 — Execution Result + Observation Integration

## Context

M8.1 produces a provider-neutral `ExecutionObservation` describing what the execution runtime actually attempted and what outcome it received. M8.2 resolves provider-neutral operations to concrete capabilities/plugins and adapts plugin results into the M8.1 outcome contract.

JARVIS now needs a controlled return path from that observed execution event back into its existing context/state model.

## Decision

Introduce an immutable `ExecutionObservationStore` and an `ExecutionObservationContextIntegrator`.

```text
ExecutionObservation
        ↓
ObservationStore
        ↓
ContextItem(OBSERVATION)
        ↓
new WorkingContext
```

The store is keyed by `execution_id` and rejects duplicate execution identities. The integrator projects observations into the existing `WorkingContext.observations` collection and returns a new context instead of mutating the original.

## Constraints

1. `execution_id` remains the stable identity for one observed execution event.
2. Duplicate execution observations are rejected rather than silently replacing prior evidence.
3. Context projection is deterministic for the same observation.
4. Success, failure, and non-attempted execution remain explicit.
5. Observation data does not create policy, confirmation, authorization, or permission state.
6. Observation integration does not mutate the original `WorkingContext`.
7. M8.3 does not infer a missing observation to be successful.

## Consequence

Execution reality can now re-enter JARVIS's working context as structured evidence. Later reasoning may consume that evidence, but any new action must still traverse the established M7 authority chain before execution.
