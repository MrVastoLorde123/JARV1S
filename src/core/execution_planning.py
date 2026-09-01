from typing import Protocol, runtime_checkable

from src.core.execution_plan_models import ExecutionPlan
from src.core.execution_progress import ExecutionProgress
from src.core.task_models import TaskRequest


@runtime_checkable
class ExecutionPlannerProtocol(Protocol):
    """
    Provider-neutral contract for turning a task into an execution plan.

    Implementations may be deterministic, AI-assisted, or multi-step, but
    they only describe intended work. They do not validate, authorize, or
    execute the resulting plan.
    """

    def plan(
        self,
        task: TaskRequest,
        progress: ExecutionProgress | None = None,
    ) -> ExecutionPlan:
        """
        Produce an execution plan for the supplied task and optional objective progress.
        """
        ...
