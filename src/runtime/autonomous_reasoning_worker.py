from typing import Callable, Any

from src.runtime.autonomous_job import AutonomousJob
from src.runtime.autonomous_job_driver import (
    AutonomousCycleDisposition,
    AutonomousCycleResult,
)
from src.runtime.autonomous_reasoning_action import (
    AutonomousReasoningAction,
    AutonomousReasoningActionValidationError,
    AutonomousReasoningDisposition,
)


class AutonomousReasoningWorker:
    """Convert one provider-backed reasoning result into a bounded cycle result."""

    def __init__(self, reason: Callable[[AutonomousJob], Any]):
        if not callable(reason):
            raise TypeError("reason must be callable")
        self._reason = reason

    def reason_action(self, job: AutonomousJob) -> AutonomousReasoningAction:
        """Produce one validated reasoning action without executing it."""
        if not isinstance(job, AutonomousJob):
            raise TypeError("job must be an AutonomousJob")
        value = self._reason(job)
        return (
            value
            if isinstance(value, AutonomousReasoningAction)
            else AutonomousReasoningAction.from_mapping(value)
        )

    @staticmethod
    def action_to_cycle_result(action: AutonomousReasoningAction) -> AutonomousCycleResult:
        if not isinstance(action, AutonomousReasoningAction):
            raise TypeError("action must be an AutonomousReasoningAction")

        d = action.disposition
        base = {"reasoning_action": action.to_dict()}
        if d is AutonomousReasoningDisposition.CONTINUE:
            return AutonomousCycleResult(AutonomousCycleDisposition.CONTINUE, "reasoning", action.rationale, context_delta=base)
        if d is AutonomousReasoningDisposition.TOOL_REQUEST:
            return AutonomousCycleResult(
                AutonomousCycleDisposition.WAIT_TOOL,
                "reasoning_action",
                action.rationale,
                reason=f"tool request pending: {action.tool_name}",
                context_delta={**base, "pending_tool_request": action.to_dict()},
            )
        if d is AutonomousReasoningDisposition.WAIT_AUTHORIZATION:
            return AutonomousCycleResult(AutonomousCycleDisposition.WAIT_AUTHORIZATION, "reasoning", action.rationale, reason=action.wait_reason, context_delta=base)
        if d is AutonomousReasoningDisposition.WAIT_INPUT:
            return AutonomousCycleResult(AutonomousCycleDisposition.WAIT_INPUT, "reasoning", action.rationale, reason=action.wait_reason, context_delta=base)
        if d is AutonomousReasoningDisposition.WAIT_TOOL:
            return AutonomousCycleResult(AutonomousCycleDisposition.WAIT_TOOL, "reasoning", action.rationale, reason=action.wait_reason, context_delta=base)
        if d is AutonomousReasoningDisposition.COMPLETE:
            return AutonomousCycleResult(AutonomousCycleDisposition.COMPLETE, "reasoning", action.rationale, result=str(action.result), context_delta=base)
        return AutonomousCycleResult(AutonomousCycleDisposition.FAIL, "reasoning", action.rationale, reason=action.wait_reason or "reasoning failed", context_delta=base)

    def run_cycle(self, job: AutonomousJob) -> AutonomousCycleResult:
        try:
            action = self.reason_action(job)
            return self.action_to_cycle_result(action)
        except Exception as exc:
            return AutonomousCycleResult(
                AutonomousCycleDisposition.FAIL,
                "reasoning",
                "reasoning action could not be produced",
                reason=f"reasoning worker failed: {type(exc).__name__}: {exc}",
            )


__all__ = ["AutonomousReasoningWorker"]
