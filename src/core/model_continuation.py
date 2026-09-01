import json

from src.ai.models import AIRequest
from src.ai.service import AIService
from src.core.execution_loop import ExecutionObservation
from src.core.task_models import TaskRequest, TaskType


class ModelContinuationPlanner:
    """
    Provider-neutral boundary for proposing one corrective TaskRequest.

    The model proposes only the next task. It never receives execution
    authority and never validates, authorizes, confirms, or invokes tools.
    """

    def __init__(self, ai_service: AIService, provider_name: str | None = None):
        if not isinstance(ai_service, AIService):
            raise TypeError("ai_service must be an AIService.")
        self.ai_service = ai_service
        self.provider_name = provider_name

    def propose(
        self,
        task: TaskRequest,
        observation: ExecutionObservation,
    ) -> TaskRequest | None:
        if not isinstance(task, TaskRequest):
            raise TypeError("task must be a TaskRequest.")
        if not isinstance(observation, ExecutionObservation):
            raise TypeError("observation must be an ExecutionObservation.")

        state = observation.state
        if state is None:
            raise ValueError("execution observation must contain execution state.")

        prompt = (
            "Propose the next corrective task for this failed objective. "
            "Return ONLY JSON with keys 'task' and 'task_type'. "
            "task_type must be one of INFORMATION, ACTION, TOOL, UNKNOWN. "
            "Do not claim that the task was executed.\n\n"
            f"Original task: {task.content}\n"
            f"Original task type: {task.task_type.value}\n"
            f"Execution state: {json.dumps(state.to_context(), default=str)}\n"
        )

        response = self.ai_service.generate(
            AIRequest(
                task=prompt,
                context={
                    "type": "execution_observation",
                    "plan_id": observation.plan.plan_id,
                    "execution_status": observation.execution.status.value,
                    "failed_steps": state.failed_steps,
                    "execution_state": state.to_context(),
                },
                metadata={"purpose": "execution_correction"},
            ),
            provider_name=self.provider_name,
        )

        return self._parse(response.content)

    @staticmethod
    def _parse(content) -> TaskRequest | None:
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Continuation model returned empty output.")

        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError("Continuation model returned invalid JSON.") from exc

        if not isinstance(payload, dict):
            raise ValueError("Continuation model output must be a JSON object.")

        task_text = payload.get("task")
        task_type = payload.get("task_type")
        if task_text is None:
            return None
        if not isinstance(task_text, str) or not task_text.strip():
            raise ValueError("Continuation task must be a non-empty string.")
        if not isinstance(task_type, str):
            raise ValueError("Continuation task_type must be a string.")

        try:
            parsed_type = TaskType(task_type.strip().upper())
        except ValueError as exc:
            raise ValueError("Continuation task_type is invalid.") from exc

        return TaskRequest(
            content=task_text.strip(),
            task_type=parsed_type,
        )
