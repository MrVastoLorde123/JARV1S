from typing import Callable, Iterable, Mapping, Any

from src.context.models import ContextItem
from src.context.working_context import WorkingContext
from src.context.jarvis_working_context import JARVISWorkingContextRuntime
from src.core.execution_loop import ExecutionObservation
from src.core.task_models import TaskRequest


class ExecutionWorkingContextBridge:
    """Bridge verified execution observations into refreshed working context."""

    def __init__(self, runtime: JARVISWorkingContextRuntime):
        if not isinstance(runtime, JARVISWorkingContextRuntime):
            raise TypeError("runtime must be a JARVISWorkingContextRuntime.")
        self.runtime = runtime
        self.latest: WorkingContext | None = None

    def observe(
        self,
        task: TaskRequest,
        observation: ExecutionObservation,
        *,
        observations: Iterable[ContextItem | Mapping[str, Any] | str] | None = None,
    ) -> WorkingContext:
        if not isinstance(task, TaskRequest):
            raise TypeError("task must be a TaskRequest.")
        if not isinstance(observation, ExecutionObservation):
            raise TypeError("observation must be an ExecutionObservation.")
        if observation.state is None or observation.progress is None:
            raise ValueError("execution observation must contain state and progress.")

        working = self.runtime.compose(
            task.content,
            task=task,
            execution_state=observation.state,
            execution_progress=observation.progress,
            observations=observations,
            metadata={
                "execution_iteration": observation.metadata.get("iteration"),
                "execution_plan_id": observation.plan.plan_id,
                "execution_status": observation.state.status.value,
            },
        )
        self.latest = working
        return working

    def __call__(self, task: TaskRequest, observation: ExecutionObservation) -> None:
        self.observe(task, observation)


ExecutionWorkingContextObserver = Callable[[TaskRequest, ExecutionObservation], None]
