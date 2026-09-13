"""M57 one-pulse resumable execution for persisted autonomous jobs."""

from __future__ import annotations

from dataclasses import dataclass

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_driver import AutonomousJobDriver
from src.runtime.autonomous_job_persistence import (
    AutonomousJobPersistenceReceipt,
    AutonomousJobPersistenceService,
)


@dataclass(frozen=True)
class AutonomousJobExecutionPulseResult:
    """Result of one load/advance/persist heartbeat."""

    job: AutonomousJob
    persistence_receipt: AutonomousJobPersistenceReceipt | None
    progressed: bool

    @property
    def waiting(self) -> bool:
        return self.job.status in {
            AutonomousJobStatus.WAITING_AUTHORIZATION,
            AutonomousJobStatus.WAITING_INPUT,
            AutonomousJobStatus.WAITING_TOOL,
            AutonomousJobStatus.PAUSED,
        }


class AutonomousJobExecutionPulse:
    """Advance one persisted autonomous job by at most one worker cycle."""

    def __init__(self, persistence: AutonomousJobPersistenceService, driver: AutonomousJobDriver) -> None:
        if not isinstance(persistence, AutonomousJobPersistenceService):
            raise TypeError("persistence must be an AutonomousJobPersistenceService")
        if not isinstance(driver, AutonomousJobDriver):
            raise TypeError("driver must be an AutonomousJobDriver")
        self._persistence = persistence
        self._driver = driver

    def pulse(self, job_id: str) -> AutonomousJobExecutionPulseResult:
        job = self._persistence.restore(job_id)
        if job is None:
            raise LookupError(f"autonomous job not found: {job_id}")

        current = job
        if job.status is AutonomousJobStatus.QUEUED:
            current = job.start()
            current = self._driver.tick(current)
        elif job.status is AutonomousJobStatus.RUNNING:
            current = self._driver.tick(job)

        progressed = current != job
        receipt = None
        if progressed:
            receipt = self._persistence.persist(current)

        return AutonomousJobExecutionPulseResult(
            job=current,
            persistence_receipt=receipt,
            progressed=progressed,
        )


__all__ = [
    "AutonomousJobExecutionPulse",
    "AutonomousJobExecutionPulseResult",
]
