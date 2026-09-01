# Decision 017 — Model-Assisted Multi-Step Planning

## Status
Accepted for M3.

## Decision
Introduce `ModelExecutionPlanner` as an AI-assisted implementation of the provider-neutral `ExecutionPlannerProtocol`.

The model is allowed to propose only an ordered list of ordinary `TaskRequest` objects. The planner then delegates composition to the existing `MultiStepExecutionPlanner`, which produces the canonical `ExecutionPlan`.

The model therefore does not produce authoritative execution plans, invoke tools, authorize work, or execute anything.

## Flow

```text
TaskRequest
    ↓
ModelExecutionPlanner
    ↓
AI proposes subtasks
    ↓
TaskRequest[]
    ↓
MultiStepExecutionPlanner
    ↓
ExecutionPlan
    ↓
PlanValidator
    ↓
ExecutionPolicy
    ↓
Confirmation
    ↓
PlanExecutor
```

## Tool subtasks

A model-proposed `TOOL` subtask contains only a natural-language capability intent. It does not contain tool arguments or execution authority.

When a capability realization service is provided, the subtask passes through capability selection and invocation construction before it becomes an executable TOOL task.

The capability realization boundary remains non-executing; the resulting task still enters the normal plan validation, policy, confirmation, and executor path.

## Safety rules

- Model output is untrusted data and is structurally validated.
- The model cannot return an `ExecutionPlan` directly.
- Unknown task types are rejected.
- The number of model-proposed steps is bounded.
- TOOL subtasks cannot bypass capability realization.
- The planner never validates, authorizes, confirms, or executes plans.
- Existing downstream safety components remain authoritative.
