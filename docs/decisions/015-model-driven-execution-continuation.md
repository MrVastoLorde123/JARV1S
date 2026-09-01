# Decision 015 — Model-Driven Execution Continuation

## Status
Accepted

## Decision

M3 may use an AI provider to propose the next corrective `TaskRequest` after an execution failure, but the model is not granted execution authority.

The continuation boundary is:

`ExecutionObservation -> ModelContinuationPlanner -> TaskRequest`

The returned `TaskRequest` must re-enter the existing guarded execution loop:

`TaskRequest -> ExecutionPlan -> PlanValidator -> ExecutionPolicy -> Confirmation -> PlanExecutor -> ExecutionObservation`

## Constraints

The model continuation layer:

- receives provider-neutral task and execution-observation data;
- requests structured output containing only the next task and task type;
- never invokes a capability directly;
- never validates or authorizes an `ExecutionPlan`;
- never bypasses confirmation;
- may return no corrective task, terminating continuation.

`GuardedExecutionLoop.max_iterations` remains the hard bound on repeated execution attempts.

This keeps reasoning separate from execution authority and preserves one safety path for both initial and corrective plans.
