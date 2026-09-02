# Decision 049 — Execution Result + Observation Integration

## Context

M8.1 produces a provider-neutral `ExecutionObservation` describing what an execution attempt actually did. M8.2 resolves provider-neutral operations to concrete capabilities/plugins and translates plugin results into the M8.1 execution contract.

The existing `WorkingContext` already carries immutable `ContextItem` observations. M8.3 therefore needs a controlled feedback boundary rather than a second competing memory/state architecture.

## Decision

Introduce an immutable `ExecutionObservationStore` and an `ExecutionObservationContextIntegrator`.

```text
ExecutionObservation
        ↓
ObservationStore
        ↓
ContextItem(source_type=OBSERVATION)
        ↓
WorkingContext (new immutable value)
```

The store deduplicates by `execution_id`. The context projection serializes the complete provider-neutral observation deterministically and records execution identity/status in provenance.

## Authority boundary

Observations are evidence of an execution event. They do not create authority.

```text
Observation ≠ Authorization
Observation ≠ Confirmation
Observation ≠ Policy
Success ≠ permission for another action
Failure ≠ permission to retry
```

M8.3 does not choose the next action, authorize a new action, retry an action, or mutate the existing authority chain.

## Constraints

1. Every stored observation must be an `ExecutionObservation`.
2. `execution_id` is the stable observation identity and may not be duplicated in one store.
3. Projection into `WorkingContext` must remain immutable.
4. Projection must preserve observed status and execution provenance.
5. Serialization must be deterministic.
6. Existing context/state models remain the integration surface.
7. Retry, continuation, and recovery decisions remain deferred to later M8 milestones.

## Consequence

JARVIS can now bring the result of an action back into its working context without turning the result into a hidden permission or second authority channel. This establishes the feedback leg required for later lifecycle and controlled agency milestones.
