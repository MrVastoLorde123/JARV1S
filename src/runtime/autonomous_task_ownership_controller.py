"""Explicit control boundary for durable task ownership state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.runtime.autonomous_job import AutonomousJob
from src.runtime.autonomous_job_persistence import AutonomousJobPersistenceReceipt, AutonomousJobPersistenceService
from src.runtime.autonomous_task_ownership import AutonomousTaskOwnershipState


class _TaskRuntime(Protocol):
    def inspect(self, job_id: str) -> AutonomousJob | None: ...


@dataclass(frozen=True)
class AutonomousTaskOwnershipUpdateResult:
    job: AutonomousJob
    ownership: AutonomousTaskOwnershipState
    persistence_receipt: AutonomousJobPersistenceReceipt


class AutonomousTaskOwnershipController:
    """Observe and explicitly mutate task ownership metadata without execution authority."""

    def __init__(self, runtime: _TaskRuntime, persistence: AutonomousJobPersistenceService) -> None:
        if not hasattr(runtime, "inspect") or not callable(runtime.inspect):
            raise TypeError("runtime must provide inspect")
        if not isinstance(persistence, AutonomousJobPersistenceService):
            raise TypeError("persistence must be an AutonomousJobPersistenceService")
        self._runtime = runtime
        self._persistence = persistence

    def inspect(self, job_id: str) -> AutonomousTaskOwnershipState | None:
        job = self._runtime.inspect(job_id)
        return None if job is None else AutonomousTaskOwnershipState.from_job(job)

    def update(
        self,
        job_id: str,
        *,
        remaining_work: list[str] | tuple[str, ...],
        next_action: str | None,
        blocker: str | None = None,
    ) -> AutonomousTaskOwnershipUpdateResult:
        job = self._runtime.inspect(job_id)
        if job is None:
            raise LookupError(f"autonomous task not found: {job_id}")
        if job.terminal:
            raise ValueError("terminal tasks cannot update ownership state")
        normalized = AutonomousTaskOwnershipState.normalize_context(
            {
                "remaining_work": list(remaining_work),
                "next_action": next_action,
                "blocker": blocker,
            }
        )
        updated = job.with_working_context({"task_ownership": normalized})
        receipt = self._persistence.persist(updated)
        return AutonomousTaskOwnershipUpdateResult(
            job=updated,
            ownership=AutonomousTaskOwnershipState.from_job(updated),
            persistence_receipt=receipt,
        )


__all__ = [
    "AutonomousTaskOwnershipController",
    "AutonomousTaskOwnershipUpdateResult",
]
