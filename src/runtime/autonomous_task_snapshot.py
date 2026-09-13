"""Unified read-only view of durable autonomous task state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_task_ownership import AutonomousTaskOwnershipState
from src.runtime.autonomous_task_plan import AutonomousTaskPlan
from src.runtime.autonomous_task_progress import AutonomousTaskProgressResult, AutonomousTaskProgressVerdict


@dataclass(frozen=True)
class AutonomousTaskSnapshot:
    """Read-only aggregate of lifecycle, ownership, plan, and progress state."""

    job: AutonomousJob
    ownership: AutonomousTaskOwnershipState
    plan: AutonomousTaskPlan | None
    progress: AutonomousTaskProgressResult | None

    @property
    def terminal(self) -> bool:
        return self.job.terminal

    @property
    def working(self) -> bool:
        return self.job.status in {AutonomousJobStatus.QUEUED, AutonomousJobStatus.RUNNING}

    @property
    def blocked(self) -> bool:
        return self.job.status in {AutonomousJobStatus.WAITING_AUTHORIZATION, AutonomousJobStatus.WAITING_INPUT, AutonomousJobStatus.WAITING_TOOL, AutonomousJobStatus.PAUSED}

    @property
    def plan_complete(self) -> bool:
        return self.plan is not None and self.plan.complete

    @classmethod
    def from_job(cls, job: AutonomousJob) -> "AutonomousTaskSnapshot":
        if not isinstance(job, AutonomousJob):
            raise TypeError("job must be an AutonomousJob")
        ownership = AutonomousTaskOwnershipState.from_job(job)
        raw_plan = job.working_context.get("task_plan")
        plan = AutonomousTaskPlan.from_mapping(raw_plan) if isinstance(raw_plan, dict) else None
        raw_progress = job.working_context.get("task_progress")
        progress = None
        if isinstance(raw_progress, dict):
            try:
                progress = AutonomousTaskProgressResult(
                    verdict=AutonomousTaskProgressVerdict(raw_progress["verdict"]),
                    summary=raw_progress["summary"],
                    evidence=raw_progress["evidence"],
                    step_count_before=raw_progress["step_count_before"],
                    step_count_after=raw_progress["step_count_after"],
                )
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError("task_progress working context is malformed") from exc
        return cls(job=job, ownership=ownership, plan=plan, progress=progress)

    def to_dict(self) -> dict[str, Any]:
        return {
            "job": self.job.to_dict(),
            "ownership": {
                "goal": self.ownership.goal,
                "status": self.ownership.status.value,
                "remaining_work": list(self.ownership.remaining_work),
                "next_action": self.ownership.next_action,
                "blocker": self.ownership.blocker,
            },
            "plan": None if self.plan is None else self.plan.to_dict(),
            "progress": None if self.progress is None else self.progress.to_context(),
            "terminal": self.terminal,
            "working": self.working,
            "blocked": self.blocked,
            "plan_complete": self.plan_complete,
        }


__all__ = ["AutonomousTaskSnapshot"]
