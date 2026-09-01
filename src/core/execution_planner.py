import uuid

from src.core.execution_plan_models import (
    ExecutionPlan,
    PlanStatus,
    PlanStep,
    StepStatus,
)

from src.core.task_models import (
    TaskRequest,
    TaskType,
)


class ExecutionPlanner:
    """
    Deterministic V1 execution planner.

    V1 does not perform AI planning.

    It converts a TaskRequest into a minimal,
    valid ExecutionPlan.

    More advanced planning can be introduced
    behind the same interface later.
    """

    def plan(
        self,
        task: TaskRequest,
    ) -> ExecutionPlan:

        if not isinstance(
            task,
            TaskRequest,
        ):
            raise TypeError(
                "task must be a TaskRequest."
            )

        content = task.content.strip()

        if not content:
            raise ValueError(
                "Task content cannot be empty."
            )

        step_metadata = {
            "planner": "deterministic",
            "task_type": task.task_type.value,
        }

        if task.task_type == TaskType.TOOL:
            tool_name = task.metadata.get("tool_name")
            arguments = task.metadata.get("arguments", {})
            invocation_id = task.metadata.get("invocation_id")

            if not isinstance(tool_name, str) or not tool_name.strip():
                raise ValueError(
                    "TOOL tasks require a non-empty 'tool_name' in metadata."
                )

            if not isinstance(arguments, dict):
                raise ValueError(
                    "TOOL task 'arguments' metadata must be a dictionary."
                )

            if invocation_id is not None and not isinstance(invocation_id, str):
                raise ValueError(
                    "TOOL task 'invocation_id' metadata must be a string or None."
                )

            step_metadata.update(
                {
                    "tool_name": tool_name,
                    "arguments": dict(arguments),
                }
            )

            if invocation_id is not None:
                step_metadata["invocation_id"] = invocation_id

        step = PlanStep(
            step_id="step-1",
            description=content,
            action=self._infer_action(
                task
            ),
            order=0,
            status=StepStatus.READY,
            metadata=step_metadata,
        )

        return ExecutionPlan(
            plan_id=str(
                uuid.uuid4()
            ),
            task_description=content,
            steps=(step,),
            status=PlanStatus.READY,
            metadata={
                "planner": "deterministic",
                "task_type": task.task_type.value,
                "step_count": 1,
            },
        )

    @staticmethod
    def _infer_action(
        task: TaskRequest,
    ) -> str:
        """
        Convert broad TaskType into a stable
        action category.

        This is deliberately coarse in V1.
        """

        if task.task_type == TaskType.INFORMATION:
            return "PROVIDE_INFORMATION"

        if task.task_type == TaskType.ACTION:
            return "PERFORM_ACTION"

        if task.task_type == TaskType.TOOL:
            return "USE_TOOL"

        return "UNCLASSIFIED_TASK"
