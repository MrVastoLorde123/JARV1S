"""Durable task ownership state derived from an autonomous-job snapshot."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus

_MAX_ITEM_LENGTH = 2048
_MAX_ITEMS = 64


def _text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    if len(value) > _MAX_ITEM_LENGTH:
        raise ValueError(f"{field_name} exceeds maximum length of {_MAX_ITEM_LENGTH}")
    return value.strip()


def _remaining_work(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)):
        raise ValueError("remaining_work must be a list or tuple")
    if len(value) > _MAX_ITEMS:
        raise ValueError(f"remaining_work exceeds maximum size of {_MAX_ITEMS}")
    return tuple(_text(item, "remaining_work item") for item in value)


@dataclass(frozen=True)
class AutonomousTaskOwnershipState:
    """Explicit operational view of what JARVIS knows about one owned task."""

    job_id: str
    goal: str
    status: AutonomousJobStatus
    step_count: int
    max_steps: int
    remaining_work: tuple[str, ...] = ()
    next_action: str | None = None
    blocker: str | None = None
    waiting_reason: str | None = None
    last_step_summary: str | None = None
    last_observation: str | None = None

    def __post_init__(self) -> None:
        if self.remaining_work and self.next_action is None:
            raise ValueError("remaining_work requires a next_action")
        if self.status in {
            AutonomousJobStatus.WAITING_AUTHORIZATION,
            AutonomousJobStatus.WAITING_INPUT,
            AutonomousJobStatus.WAITING_TOOL,
            AutonomousJobStatus.PAUSED,
        } and not self.blocker:
            raise ValueError("blocked task state requires a blocker")
        if self.status is AutonomousJobStatus.COMPLETED and self.remaining_work:
            raise ValueError("completed task state cannot retain remaining_work")

    @property
    def terminal(self) -> bool:
        return self.status in {
            AutonomousJobStatus.COMPLETED,
            AutonomousJobStatus.FAILED,
            AutonomousJobStatus.CANCELLED,
        }

    @property
    def working(self) -> bool:
        return self.status in {
            AutonomousJobStatus.QUEUED,
            AutonomousJobStatus.RUNNING,
        }

    @property
    def blocked(self) -> bool:
        return self.status in {
            AutonomousJobStatus.WAITING_AUTHORIZATION,
            AutonomousJobStatus.WAITING_INPUT,
            AutonomousJobStatus.WAITING_TOOL,
            AutonomousJobStatus.PAUSED,
        }

    @property
    def complete(self) -> bool:
        return self.status is AutonomousJobStatus.COMPLETED

    @classmethod
    def normalize_context(cls, payload: Mapping[str, Any] | None) -> dict[str, object]:
        if payload is None:
            return {"remaining_work": [], "next_action": None, "blocker": None}
        if not isinstance(payload, Mapping):
            raise ValueError("task_ownership must be a mapping")
        remaining = _remaining_work(payload.get("remaining_work", []))
        next_action = payload.get("next_action")
        blocker = payload.get("blocker")
        if next_action is not None:
            next_action = _text(next_action, "next_action")
        if blocker is not None:
            blocker = _text(blocker, "blocker")
        if remaining and next_action is None:
            raise ValueError("remaining_work requires a next_action")
        return {
            "remaining_work": list(remaining),
            "next_action": next_action,
            "blocker": blocker,
        }

    @classmethod
    def from_job(cls, job: AutonomousJob) -> "AutonomousTaskOwnershipState":
        if not isinstance(job, AutonomousJob):
            raise TypeError("job must be an AutonomousJob")

        raw = job.working_context.get("task_ownership")
        normalized = cls.normalize_context(raw if isinstance(raw, Mapping) else None)
        remaining = tuple(normalized["remaining_work"])
        next_action = normalized["next_action"]
        blocker = normalized["blocker"]
        waiting_reason = job.waiting_reason

        last_step = job.steps[-1] if job.steps else None
        return cls(
            job_id=job.job_id,
            goal=job.goal,
            status=job.status,
            step_count=job.step_count,
            max_steps=job.max_steps,
            remaining_work=remaining,
            next_action=next_action,
            blocker=blocker or waiting_reason,
            waiting_reason=waiting_reason,
            last_step_summary=last_step.summary if last_step else None,
            last_observation=last_step.observation if last_step else None,
        )

    def to_context(self) -> dict[str, object]:
        return {
            "task_ownership": {
                "remaining_work": list(self.remaining_work),
                "next_action": self.next_action,
                "blocker": self.blocker,
            }
        }


__all__ = ["AutonomousTaskOwnershipState"]
