# Decision 018 — Model-Planned JARVIS Execution

## Status
Accepted for M3.

## Decision

`JARVISExecutionAdapter` accepts an optional provider-neutral execution planner. When omitted, JARVIS keeps using its existing planner. When supplied, the injected planner becomes the initial planning strategy for the guarded execution loop.

This makes model-assisted multi-step planning an orchestration choice rather than a new execution path.

```text
JARVIS task seam
    ↓
injected ExecutionPlanner
    ↓
ExecutionPlan
    ↓
PlanValidator
    ↓
ExecutionPolicy
    ↓
ExecutionConfirmation
    ↓
PlanExecutor
    ↓
observation
    ↓
ModelContinuationPlanner
    ↓
repeat through the same guarded loop
```

## Safety Invariants

- The injected planner must expose only `plan(task)`.
- The planner does not validate, authorize, confirm, execute, or invoke tools.
- Model-generated subtasks become ordinary `TaskRequest` values before deterministic plan composition.
- Tool-oriented subtasks must pass through capability realization before they can become executable tool tasks.
- Every generated `ExecutionPlan`, including plans produced after correction, re-enters validation, policy, confirmation, and execution.
- Confirmation remains authoritative for high-risk operations.
- The execution loop remains bounded by `max_iterations`.

## Compatibility

The adapter remains opt-in. Existing JARVIS construction and task behavior remain unchanged unless an application installs the execution adapter.

Example:

```python
from src.core.jarvis_execution_adapter import install_execution_loop
from src.core.model_execution_planner import ModelExecutionPlanner

planner = ModelExecutionPlanner(ai_service, capability_realization_service=jarvis.capability_realization_service)
install_execution_loop(jarvis, execution_planner=planner, max_iterations=3)
```

## Consequence

M3 now has a real model-planned path without granting the model execution authority. Planning strategy can evolve independently while the execution safety pipeline remains singular and authoritative.
