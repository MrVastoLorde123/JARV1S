# Decision 050 — Execution Lifecycle / Continuation

## Context

M8.1 established single-attempt execution runtime semantics, M8.2 established provider-neutral capability/plugin realization, and M8.3 established structured execution observation flowing back into `WorkingContext`.

JARVIS now needs lifecycle semantics for an individual execution that may remain in progress, terminate with an explicit outcome, or require bounded continuation without turning continuation into a second authority mechanism.

## Decision

Introduce an immutable `ExecutionLifecycle` around one stable `execution_id`.

```text
ExecutionRequest
      ↓
ExecutionLifecycle
      ↓
ExecutionObservation
      ↓
Terminal OR Continuation-Required
      ↓
Explicit Lifecycle Transition
```

Continuation is represented as immutable `ContinuationRequest` data tied to the originating `execution_id`. Consuming a continuation returns the lifecycle to `PENDING`; it does not create authorization and does not invoke execution.

## Constraints

1. `execution_id` remains stable across the lifecycle.
2. Lifecycle state transitions are explicit and immutable.
3. `SUCCEEDED`, `FAILED`, `BLOCKED`, and `CANCELLED` are terminal.
4. `NOT_ATTEMPTED` maps to `BLOCKED`, never successful completion.
5. A mismatched observation identity is rejected.
6. Continuation is permitted only from explicitly defined non-terminal states and remains identity-bound.
7. Terminal lifecycles cannot silently continue or be cancelled.
8. Consuming continuation clears the continuation marker and returns to `PENDING` without authorizing another action.
9. Lifecycle state does not create policy, confirmation, authorization, retry permission, or execution side effects.
10. Any distinct future action must traverse the established M7 authority chain.
11. M8.4 is per-execution lifecycle state and does not replace the existing plan-level execution state model.

## Consequence

JARVIS can now represent execution progress and bounded continuation explicitly without creating a hidden retry loop or a second authority path. This provides the lifecycle foundation required by later controlled multi-step agency while keeping planning, policy, authorization, and worker orchestration outside the lifecycle layer.
