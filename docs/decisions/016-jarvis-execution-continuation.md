# Decision 016 — JARVIS Execution Continuation

## Status
Accepted for M3.

## Decision
The M3 execution loop is integrated into the existing JARVIS task seam through `JARVISExecutionAdapter`.

`JARVIS.ask()` already routes task requests into `_handle_task()`. The adapter intercepts that seam without rewriting `jarvis.py`, then delegates to `GuardedExecutionLoop`.

The resulting path is:

`User input → JARVIS routing → _handle_task → GuardedExecutionLoop → planner → validator → policy → confirmation → PlanExecutor → observation → model continuation → repeat`

## Safety invariant

A continuation model may propose only a new `TaskRequest`. It cannot execute tools, mutate plans, bypass validation, bypass policy, or bypass confirmation.

Every corrective task is planned again and therefore re-enters the complete validator → policy → confirmation → executor path.

The loop is bounded by `max_iterations` and defaults to three iterations when installed through the adapter.

## Compatibility

The adapter is intentionally opt-in in this milestone. Existing JARVIS construction and `_handle_task()` behavior remain unchanged until an application installs the M3 execution adapter. This avoids silently changing legacy orchestration while the loop is being validated in production-like integration tests.

Example integration:

```python
from src.core.jarvis_execution_adapter import install_execution_loop

jarvis = JARVIS(ai_service=ai_service, ...)
install_execution_loop(jarvis, max_iterations=3)
```

After installation, both `ask()` task routing and `ask_task()` use the guarded continuation path because both converge on JARVIS's `_handle_task()` seam.
