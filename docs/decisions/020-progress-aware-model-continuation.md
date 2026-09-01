# Decision 020 — Progress-Aware Model Continuation

## Status
Accepted for M4.4.

## Decision

Make the model continuation boundary consume accumulated `ExecutionProgress`, not only the current execution observation/state.

`ExecutionProgress` remains provider-neutral and immutable. The continuation planner receives it through the existing `ExecutionObservation.progress` field and exposes the complete accumulated view to the model request.

The model should use this history to:

- preserve the original objective
- recognize work already completed across attempts
- preserve outputs produced by earlier attempts
- understand the current unresolved requirements
- propose a corrective task that changes the approach rather than blindly repeating prior work

## Safety boundary

This change does not increase execution authority.

The continuation model still:

- receives only provider-neutral task/state/progress data
- returns only a `TaskRequest` or `None`
- does not validate plans
- does not authorize plans
- does not confirm plans
- does not invoke capabilities
- does not bypass `PlanValidator -> ExecutionPolicy -> Confirmation -> PlanExecutor`

No persistence is introduced and no unbounded autonomy is introduced. The existing execution-loop iteration bound remains authoritative.

## Flow

```text
User Goal
   ↓
ExecutionPlan
   ↓
Validator → Policy → Confirmation → Executor
   ↓
ExecutionState
   ↓
ExecutionProgress (attempt 1 ... N)
   ↓
ExecutionObservation.progress
   ↓
ModelContinuationPlanner
   ↓
TaskRequest | None
   ↓
existing guarded execution pipeline
```

## Consequence

M4.4 changes the quality of continuation reasoning rather than the authority of the system. JARVIS can now propose corrective work with awareness of objective progress already achieved across attempts.
