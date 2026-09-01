# Decision 019 — Execution State and Rich Observation

## Status
Accepted for M4.1.

## Decision

Introduce `ExecutionState` as provider-neutral, immutable state derived from a `PlanExecutionResult`.

`ExecutionObservation` carries this state alongside the original plan and raw execution result. Existing observation construction remains compatible: when state is omitted, the observation derives it from the plan task description and execution result.

The state describes:

- the objective/goal
- the plan that produced the observation
- completed steps
- failed steps
- outputs produced by completed steps
- unresolved requirements caused by failures
- the next control-level actions available to the continuation layer

## Flow

```text
Goal
  ↓
ExecutionPlan
  ↓
Validator → Policy → Confirmation → Executor
  ↓
PlanExecutionResult
  ↓
ExecutionObservation
  ↓
ExecutionState
  ↓
Continuation planner
```

## Safety rules

- ExecutionState is derived state; it does not grant execution authority.
- State does not contain executor, policy, confirmation, capability, or provider objects.
- The continuation planner may consume state but still returns only a `TaskRequest` or `None`.
- Any resulting task re-enters the existing guarded execution loop.
- `next_allowed_actions` describes orchestration decisions such as COMPLETE, CORRECT, and STOP; it is not a tool permission list.

## Consequence

M4 now has a stable provider-neutral state surface for richer continuation reasoning without introducing a second execution authority or changing the existing safety pipeline.
