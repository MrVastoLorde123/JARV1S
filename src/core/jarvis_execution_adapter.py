from types import MethodType

from src.core.execution_loop import GuardedExecutionLoop
from src.core.model_continuation import ModelContinuationPlanner
from src.core.models import JARVISResponse


class JARVISExecutionAdapter:
    """Attach the guarded M3 execution loop to an existing JARVIS instance.

    The adapter replaces only the task-execution seam already called by
    JARVIS.ask(). The loop itself still owns the full validator -> policy ->
    confirmation -> executor path.
    """

    def __init__(self, jarvis, max_iterations: int = 3, continuation_planner=None):
        if jarvis is None:
            raise TypeError("jarvis is required.")
        if not isinstance(max_iterations, int) or max_iterations < 1:
            raise ValueError("max_iterations must be a positive integer.")

        self.jarvis = jarvis
        self.loop = GuardedExecutionLoop(
            planner=jarvis.execution_planner,
            validator=jarvis.plan_validator,
            policy=jarvis.execution_policy,
            executor=jarvis.plan_executor,
            confirmation=jarvis.execution_confirmation_service,
            max_iterations=max_iterations,
        )
        self.continuation_planner = continuation_planner or ModelContinuationPlanner(
            jarvis.ai_service
        )
        self._original_handle_task = jarvis._handle_task

    def install(self):
        """Install this adapter on the JARVIS instance and return the instance."""
        self.jarvis._handle_task = MethodType(self._handle_task, self.jarvis)
        self.jarvis.execution_adapter = self
        return self.jarvis

    def uninstall(self):
        """Restore JARVIS's original task handler."""
        self.jarvis._handle_task = self._original_handle_task
        if hasattr(self.jarvis, "execution_adapter"):
            del self.jarvis.execution_adapter
        return self.jarvis

    def _handle_task(self, jarvis, task):
        result = self.loop.run(
            task,
            corrective_planner=self.continuation_planner.propose,
        )
        return self._to_response(result)

    @staticmethod
    def _to_response(result):
        if result.status == "AWAITING_CONFIRMATION":
            return JARVISResponse(
                content=(
                    "The task is ready for execution, but confirmation is required.\n\n"
                    f"Operation ID: {result.pending_operation_id}\n\n"
                    "Use /CONFIRM to authorize it or /CANCEL to discard it."
                ),
                ai_response=None,
                context=None,
                metadata={
                    "route": "TASK",
                    "stage": "CONFIRMATION",
                    "execution_loop": True,
                    "status": result.status,
                    "iterations": result.iterations,
                    "operation_id": result.pending_operation_id,
                    "policy_decision": (
                        result.last_policy.decision.value
                        if result.last_policy is not None
                        else None
                    ),
                },
            )

        if result.status == "VALIDATION_FAILED":
            return JARVISResponse(
                content="A generated execution plan failed validation before execution.",
                ai_response=None,
                context=None,
                metadata={
                    "route": "TASK",
                    "stage": "VALIDATION",
                    "execution_loop": True,
                    "status": result.status,
                    "iterations": result.iterations,
                },
            )

        if result.status == "POLICY_DENIED":
            return JARVISResponse(
                content="The execution policy denied the generated plan.",
                ai_response=None,
                context=None,
                metadata={
                    "route": "TASK",
                    "stage": "POLICY",
                    "execution_loop": True,
                    "status": result.status,
                    "iterations": result.iterations,
                },
            )

        if not result.observations:
            return JARVISResponse(
                content="The execution loop ended without an execution observation.",
                ai_response=None,
                context=None,
                metadata={
                    "route": "TASK",
                    "stage": "EXECUTION_LOOP",
                    "execution_loop": True,
                    "status": result.status,
                    "iterations": result.iterations,
                },
            )

        observation = result.observations[-1]
        outputs = tuple(
            step.output
            for step in observation.execution.steps
            if step.status.value == "COMPLETED" and step.output is not None
        )
        if result.status == "COMPLETED":
            content = (
                "Task completed successfully.\n\n"
                f"Completed {observation.execution.step_count} step(s)."
            )
            if outputs:
                content += "\n\nResults:\n" + "\n\n".join(str(output) for output in outputs)
        else:
            content = (
                "The task could not be completed.\n\n"
                + (observation.execution.error or result.status)
            )

        return JARVISResponse(
            content=content,
            ai_response=None,
            context=None,
            metadata={
                "route": "TASK",
                "stage": "EXECUTION_LOOP",
                "execution_loop": True,
                "status": result.status,
                "iterations": result.iterations,
                "plan_id": observation.plan.plan_id,
                "execution_status": observation.execution.status.value,
                "step_count": observation.execution.step_count,
                "observation_count": len(result.observations),
                "failed_steps": tuple(
                    step.step_id for step in observation.execution.failed_steps
                ),
                "execution_outputs": outputs,
            },
        )


def install_execution_loop(jarvis, max_iterations: int = 3, continuation_planner=None):
    """Install bounded model-driven continuation on JARVIS.ask()."""
    return JARVISExecutionAdapter(
        jarvis,
        max_iterations=max_iterations,
        continuation_planner=continuation_planner,
    ).install()
