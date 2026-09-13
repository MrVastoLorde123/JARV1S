from typing import Callable, Any, Mapping

from src.runtime.autonomous_job import AutonomousJob
from src.runtime.autonomous_job_driver import (
    AutonomousCycleDisposition,
    AutonomousCycleResult,
)
from src.runtime.autonomous_reasoning_action import (
    AutonomousReasoningAction,
    AutonomousReasoningDisposition,
)
from src.runtime.autonomous_task_ownership import AutonomousTaskOwnershipState


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
    def _ownership_context(action: AutonomousReasoningAction, *, fallback_blocker: str | None = None) -> dict[str, object] | None:
        metadata = action.metadata
        raw = metadata.get("task_ownership") if isinstance(metadata, Mapping) else None
        if raw is not None and not isinstance(raw, Mapping):
            raise ValueError("task_ownership action metadata must be a mapping")

        if raw is None:
            if action.disposition is AutonomousReasoningDisposition.COMPLETE:
                return {"task_ownership": {"remaining_work": [], "next_action": None, "blocker": None}}
            if action.disposition in {
                AutonomousReasoningDisposition.WAIT_AUTHORIZATION,
                AutonomousReasoningDisposition.WAIT_INPUT,
                AutonomousReasoningDisposition.WAIT_TOOL,
            }:
                return {"task_ownership": {"remaining_work": [], "next_action": None, "blocker": fallback_blocker}}
            return {"task_ownership": {"remaining_work": [], "next_action": action.rationale, "blocker": None}}

        normalized = AutonomousTaskOwnershipState.normalize_context(raw)
        if normalized["next_action"] is None and action.disposition in {
            AutonomousReasoningDisposition.CONTINUE,
            AutonomousReasoningDisposition.TOOL_REQUEST,
        }:
            normalized["next_action"] = action.rationale if action.disposition is AutonomousReasoningDisposition.CONTINUE else f"use tool: {action.tool_name}"
        if normalized["blocker"] is None and fallback_blocker is not None:
            normalized["blocker"] = fallback_blocker
        return {"task_ownership": normalized}

    @staticmethod
    def action_to_cycle_result(action: AutonomousReasoningAction) -> AutonomousCycleResult:
        if not isinstance(action, AutonomousReasoningAction):
            raise TypeError("action must be an AutonomousReasoningAction")

        d = action.disposition
        base = {"reasoning_action": action.to_dict()}
        if d is AutonomousReasoningDisposition.CONTINUE:
            return AutonomousCycleResult(
                AutonomousCycleDisposition.CONTINUE,
                "reasoning",
                action.rationale,
                context_delta={**base, **(AutonomousReasoningWorker._ownership_context(action) or {})},
            )
        if d is AutonomousReasoningDisposition.TOOL_REQUEST:
            blocker = f"tool request pending: {action.tool_name}"
            return AutonomousCycleResult(
                AutonomousCycleDisposition.WAIT_TOOL,
                "reasoning_action",
                action.rationale,
                reason=blocker,
                context_delta={
                    **base,
                    "pending_tool_request": action.to_dict(),
                    **(AutonomousReasoningWorker._ownership_context(action, fallback_blocker=blocker) or {}),
                },
            )
        if d is AutonomousReasoningDisposition.WAIT_AUTHORIZATION:
            return AutonomousCycleResult(
                AutonomousCycleDisposition.WAIT_AUTHORIZATION,
                "reasoning",
                action.rationale,
                reason=action.wait_reason,
                context_delta={**base, **(AutonomousReasoningWorker._ownership_context(action, fallback_blocker=action.wait_reason) or {})},
            )
        if d is AutonomousReasoningDisposition.WAIT_INPUT:
            return AutonomousCycleResult(
                AutonomousCycleDisposition.WAIT_INPUT,
                "reasoning",
                action.rationale,
                reason=action.wait_reason,
                context_delta={**base, **(AutonomousReasoningWorker._ownership_context(action, fallback_blocker=action.wait_reason) or {})},
            )
        if d is AutonomousReasoningDisposition.WAIT_TOOL:
            return AutonomousCycleResult(
                AutonomousCycleDisposition.WAIT_TOOL,
                "reasoning",
                action.rationale,
                reason=action.wait_reason,
                context_delta={**base, **(AutonomousReasoningWorker._ownership_context(action, fallback_blocker=action.wait_reason) or {})},
            )
        if d is AutonomousReasoningDisposition.COMPLETE:
            return AutonomousCycleResult(
                AutonomousCycleDisposition.COMPLETE,
                "reasoning",
                action.rationale,
                result=str(action.result),
                context_delta={**base, **(AutonomousReasoningWorker._ownership_context(action) or {})},
            )
        failure_reason = action.wait_reason or "reasoning failed"
        return AutonomousCycleResult(
            AutonomousCycleDisposition.FAIL,
            "reasoning",
            action.rationale,
            reason=failure_reason,
            context_delta={**base, **(AutonomousReasoningWorker._ownership_context(action, fallback_blocker=failure_reason) or {})},
        )

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
