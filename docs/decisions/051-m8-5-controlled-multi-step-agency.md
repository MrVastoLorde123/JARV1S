# Decision 051 — Controlled Multi-Step Agency

## Context

M8.1 established single-attempt execution, M8.2 established capability/plugin realization, M8.3 established observation integration, and M8.4 established per-execution lifecycle and bounded continuation semantics.

JARVIS now needs to coordinate multiple actions without allowing the coordinator to become an alternate authorization system.

## Decision

Introduce a bounded `ControlledAgency` coordinator that accepts an initial M7 `ExecutionPreparation` and, optionally, an injected next-step provider.

The provider may derive its next step from the updated `WorkingContext` and the previous `ExecutionObservation`, but it must return another `ExecutionPreparation`. The coordinator accepts only `READY` preparations for execution and enforces unique execution identities and a hard step limit.

```text
Authorized Preparation
        ↓
ControlledAgency
        ↓
M8.4 Lifecycle
        ↓
M8.1 Runtime
        ↓
M8.3 Observation Integration
        ↓
Updated WorkingContext
        ↓
Next Authorized Preparation
```

## Constraints

1. The coordinator never creates, modifies, or infers authorization.
2. Every executable step has a distinct `execution_id`.
3. Every executable step is a `READY` `ExecutionPreparation`.
4. A blocked or malformed next preparation never reaches the execution runtime.
5. Each step produces its own execution observation and lifecycle record.
6. Observations accumulate in the existing `WorkingContext`; no competing memory/state model is introduced.
7. A fixed positive `max_steps` prevents unbounded agency.
8. No implicit retry is performed after failure.
9. A next step may follow a failed observation only when an explicit step provider supplies a new authorized preparation.
10. The step provider has no direct tool or plugin invocation capability through this interface.
11. Capability/plugin realization remains owned by M8.2.
12. Policy, confirmation, authorization, and authorization integrity remain owned by M7.

## Consequence

JARVIS can now perform controlled sequences while preserving the critical distinction between orchestration and authority. Multi-step agency becomes a bounded execution loop over independently authorized actions rather than a new decision or permission system.
