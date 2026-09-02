# Decision 025 — Assessment-Aware Planning

## Status

Implemented — M5.5

## Context

M5.1 established deterministic interpretation of observed `ExecutionState`. M5.2 added model-assisted assessment. M5.3 made that model interpretation admissible only when it agrees with observed execution reality. M5.4 resolved model-described remaining work against authoritative unresolved requirements.

Planning can now consume this grounded understanding without treating the model assessment itself as execution truth.

## Decision

Introduce `AssessmentAwarePlanningService` as the boundary from validated execution interpretation into planning.

The service:

1. receives the original `TaskRequest`, observed `ExecutionState`, and `ExecutionAssessment`;
2. requires the task objective to match the observed state goal;
3. validates the assessment through `ExecutionAssessmentValidator`;
4. resolves remaining work through `RemainingWorkResolver`;
5. passes the resulting `RemainingWork` explicitly to an `ExecutionPlannerProtocol` implementation.

The planner contract now accepts optional `RemainingWork` in addition to `ExecutionProgress`.

`ModelExecutionPlanner` includes grounded remaining work in its model context and prompt. `ExecutionPlanner` and `MultiStepExecutionPlanner` accept the same contract without gaining execution authority.

## Authority Model

```text
Observed ExecutionState
        |
        +--> Deterministic Assessment
        |
        +--> Model Assessment
                 |
                 v
      Assessment Validation
                 |
                 v
        Remaining Work Resolution
                 |
                 v
       Assessment-Aware Planning
                 |
                 v
          Proposed ExecutionPlan
                 |
                 v
      Plan Validation -> Policy -> Confirmation -> Executor
```

The assessment-aware planning layer is proposal-only. It does not authorize, confirm, execute, invoke capabilities, or mutate execution state.

## Safety Invariants

- observed execution remains authoritative;
- an invalid assessment never reaches the planner;
- unresolved observed requirements remain part of grounded remaining work;
- planning receives `RemainingWork` explicitly rather than through untyped task metadata;
- planner output remains an `ExecutionPlan` proposal;
- all plans continue through the existing validation, policy, confirmation, and execution pipeline;
- no new execution authority is introduced.

## Consequence

JARVIS now has a complete semantic bridge from observed execution to future planning:

`reality -> assessment -> validation -> remaining work -> plan`.

This closes the core M5 reasoning loop without allowing assessment or planning to bypass existing safety boundaries.
