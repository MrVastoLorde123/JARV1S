import json

from src.ai.models import AIRequest
from src.ai.service import AIService
from src.core.capability_realization import CapabilityRealizationService
from src.core.execution_plan_models import ExecutionPlan
from src.core.multi_step_planner import MultiStepExecutionPlanner
from src.core.task_models import TaskRequest, TaskType


class ModelExecutionPlanner:
    """
    AI-assisted multi-step planner behind the provider-neutral planning contract.

    The model proposes only TaskRequest objects. A deterministic composer turns
    those tasks into an ExecutionPlan. Validation, authorization, confirmation,
    execution, and capability invocation remain downstream responsibilities.
    """

    def __init__(
        self,
        ai_service: AIService,
        provider_name: str | None = None,
        capability_realization_service: CapabilityRealizationService | None = None,
        max_steps: int = 8,
    ):
        if not isinstance(ai_service, AIService):
            raise TypeError("ai_service must be an AIService.")
        if not isinstance(max_steps, int) or max_steps < 1:
            raise ValueError("max_steps must be a positive integer.")
        if capability_realization_service is not None and not isinstance(
            capability_realization_service,
            CapabilityRealizationService,
        ):
            raise TypeError(
                "capability_realization_service must be a CapabilityRealizationService."
            )

        self.ai_service = ai_service
        self.provider_name = provider_name
        self.capability_realization_service = capability_realization_service
        self.max_steps = max_steps

    def plan(self, task: TaskRequest) -> ExecutionPlan:
        if not isinstance(task, TaskRequest):
            raise TypeError("task must be a TaskRequest.")

        prompt = (
            "Decompose the user's objective into the smallest useful ordered "
            "set of subtasks. Return ONLY JSON in the form "
            "{\"steps\":[{\"task\":\"...\",\"task_type\":\"...\"}]}. "
            "task_type must be one of INFORMATION, ACTION, TOOL. "
            "Do not execute anything, do not invent results, and do not return "
            "an ExecutionPlan or tool arguments.\n\n"
            f"Objective: {task.content}\n"
            f"Requested task type: {task.task_type.value}\n"
        )

        response = self.ai_service.generate(
            AIRequest(
                task=prompt,
                context={"type": "execution_planning"},
                metadata={"purpose": "multi_step_planning"},
            ),
            provider_name=self.provider_name,
        )

        subtasks = self._parse_subtasks(response.content)
        if len(subtasks) > self.max_steps:
            raise ValueError("Model proposed too many execution steps.")

        realized_subtasks = tuple(self._realize_subtask(item) for item in subtasks)
        composer = MultiStepExecutionPlanner(
            decomposer=lambda _: realized_subtasks,
        )
        return composer.plan(task)

    def _realize_subtask(self, task: TaskRequest) -> TaskRequest:
        if task.task_type != TaskType.TOOL:
            return task
        if self.capability_realization_service is None:
            raise ValueError(
                "Model proposed a TOOL subtask, but no capability realization service is configured."
            )

        realization = self.capability_realization_service.realize(task.content)
        metadata = {
            **task.metadata,
            "tool_name": realization.request.tool_name,
            "arguments": dict(realization.request.arguments),
        }
        if realization.request.invocation_id is not None:
            metadata["invocation_id"] = realization.request.invocation_id
        return TaskRequest(
            content=task.content,
            task_type=TaskType.TOOL,
            metadata=metadata,
        )

    @staticmethod
    def _parse_subtasks(content: str) -> tuple[TaskRequest, ...]:
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Execution planning model returned empty output.")

        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError("Execution planning model returned invalid JSON.") from exc

        if not isinstance(payload, dict):
            raise ValueError("Execution planning model output must be a JSON object.")

        steps = payload.get("steps")
        if not isinstance(steps, list) or not steps:
            raise ValueError("Execution planning model must return a non-empty 'steps' list.")

        parsed: list[TaskRequest] = []
        for item in steps:
            if not isinstance(item, dict):
                raise ValueError("Each execution planning step must be an object.")

            task_text = item.get("task")
            task_type = item.get("task_type")
            if not isinstance(task_text, str) or not task_text.strip():
                raise ValueError("Each execution planning step requires a non-empty task.")
            if not isinstance(task_type, str):
                raise ValueError("Each execution planning step requires a task_type.")

            try:
                parsed_type = TaskType(task_type.strip().upper())
            except ValueError as exc:
                raise ValueError("Execution planning task_type is invalid.") from exc

            if parsed_type == TaskType.UNKNOWN:
                raise ValueError("Execution planning steps cannot use UNKNOWN task_type.")

            parsed.append(
                TaskRequest(
                    content=task_text.strip(),
                    task_type=parsed_type,
                )
            )

        return tuple(parsed)
