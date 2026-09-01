import uuid
from collections.abc import Callable, Sequence

from src.core.execution_plan_models import ExecutionPlan, PlanStatus, PlanStep, StepStatus
from src.core.execution_planner import ExecutionPlanner
from src.core.execution_progress import ExecutionProgress
from src.core.task_models import TaskRequest


TaskDecomposer = Callable[[TaskRequest], Sequence[TaskRequest]]


class MultiStepExecutionPlanner:
    """
    Compose multiple ordinary TaskRequests into one ExecutionPlan.

    Each subtask is still planned by the existing provider-neutral
    ExecutionPlanner. This strategy only composes those plans; it never
    validates, authorizes, confirms, or executes them.
    """

    def __init__(
        self,
        step_planner: ExecutionPlanner | None = None,
        decomposer: TaskDecomposer | None = None,
    ):
        self.step_planner = step_planner or ExecutionPlanner()
        if not hasattr(self.step_planner, "plan") or not callable(self.step_planner.plan):
            raise TypeError("step_planner must expose plan(task).")
        self.decomposer = decomposer or self._default_decompose
        if not callable(self.decomposer):
            raise TypeError("decomposer must be callable.")

    def plan(
        self,
        task: TaskRequest,
        progress: ExecutionProgress | None = None,
    ) -> ExecutionPlan:
        if not isinstance(task, TaskRequest):
            raise TypeError("task must be a TaskRequest.")
        if progress is not None and not isinstance(progress, ExecutionProgress):
            raise TypeError("progress must be an ExecutionProgress or None.")
        if progress is not None and progress.goal != task.content:
            raise ValueError("execution progress goal must match the task objective.")

        subtasks = tuple(self.decomposer(task))
        if not subtasks:
            raise ValueError("Task decomposer returned no subtasks.")
        if any(not isinstance(item, TaskRequest) for item in subtasks):
            raise TypeError("Task decomposer must return only TaskRequest objects.")

        combined_steps: list[PlanStep] = []
        previous_step_id: str | None = None

        for index, subtask in enumerate(subtasks, start=1):
            # ExecutionProgress describes the aggregate objective, while each
            # composed subtask has its own objective. Do not forward the
            # aggregate progress into child planning or their objective checks
            # will (correctly) reject the mismatched goal.
            subplan = self.step_planner.plan(subtask)
            for source_step in subplan.steps:
                step_id = f"step-{len(combined_steps) + 1}"
                depends_on = (previous_step_id,) if previous_step_id is not None else ()
                combined_steps.append(
                    PlanStep(
                        step_id=step_id,
                        description=source_step.description,
                        action=source_step.action,
                        order=len(combined_steps),
                        status=StepStatus.READY,
                        depends_on=depends_on,
                        requires_confirmation=source_step.requires_confirmation,
                        metadata={
                            **source_step.metadata,
                            "subtask_index": index,
                        },
                    )
                )
                previous_step_id = step_id

        return ExecutionPlan(
            plan_id=str(uuid.uuid4()),
            task_description=task.content.strip(),
            steps=tuple(combined_steps),
            status=PlanStatus.READY,
            metadata={
                "planner": "multi_step_deterministic",
                "subtask_count": len(subtasks),
                "step_count": len(combined_steps),
            },
        )

    @staticmethod
    def _default_decompose(task: TaskRequest) -> tuple[TaskRequest, ...]:
        """Conservative deterministic decomposition for explicit chained goals."""
        raw_steps = [segment.strip() for segment in task.content.split(" then ")]
        raw_steps = [segment for segment in raw_steps if segment]
        if len(raw_steps) <= 1:
            return (task,)
        return tuple(
            TaskRequest(
                content=content,
                task_type=task.task_type,
                metadata=dict(task.metadata),
            )
            for content in raw_steps
        )
