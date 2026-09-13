"""Deterministic progress evaluation for durable autonomous task cycles."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from src.runtime.autonomous_job import AutonomousJob, AutonomousJobStatus
from src.runtime.autonomous_job_driver import AutonomousCycleDisposition, AutonomousCycleResult


class AutonomousTaskProgressVerdict(str, Enum):
    PROGRESSED = "PROGRESSED"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    NO_PROGRESS = "NO_PROGRESS"


@dataclass(frozen=True)
class AutonomousTaskProgressResult:
    """Validated observation about one bounded task cycle."""

    verdict: AutonomousTaskProgressVerdict
    summary: str
    evidence: str
    step_count_before: int
    step_count_after: int

    def __post_init__(self) -> None:
        if not isinstance(self.verdict, AutonomousTaskProgressVerdict):
            raise TypeError("verdict must be an AutonomousTaskProgressVerdict")
        for name, value, maximum in (("summary", self.summary, 1024), ("evidence", self.evidence, 4096)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
            if len(value) > maximum:
                raise ValueError(f"{name} exceeds maximum length of {maximum}")
        for name, value in (("step_count_before", self.step_count_before), ("step_count_after", self.step_count_after)):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if self.step_count_after < self.step_count_before:
            raise ValueError("step_count_after cannot be less than step_count_before")

    def to_context(self) -> dict[str, object]:
        return {"verdict": self.verdict.value, "summary": self.summary, "evidence": self.evidence, "step_count_before": self.step_count_before, "step_count_after": self.step_count_after}


class AutonomousTaskProgressEvaluator(Protocol):
    """Authority-neutral evaluator for one bounded autonomous cycle."""

    def evaluate(self, before: AutonomousJob, after: AutonomousJob, cycle: AutonomousCycleResult) -> AutonomousTaskProgressResult:
        ...


class DeterministicAutonomousTaskProgressEvaluator:
    """Classify lifecycle progress without trusting model claims as truth."""

    def evaluate(self, before: AutonomousJob, after: AutonomousJob, cycle: AutonomousCycleResult) -> AutonomousTaskProgressResult:
        if not isinstance(before, AutonomousJob):
            raise TypeError("before must be an AutonomousJob")
        if not isinstance(after, AutonomousJob):
            raise TypeError("after must be an AutonomousJob")
        if not isinstance(cycle, AutonomousCycleResult):
            raise TypeError("cycle must be an AutonomousCycleResult")
        before_count = before.step_count
        after_count = after.step_count
        if cycle.disposition is AutonomousCycleDisposition.COMPLETE or after.status is AutonomousJobStatus.COMPLETED:
            return AutonomousTaskProgressResult(AutonomousTaskProgressVerdict.COMPLETED, "task reached its runtime completion disposition", cycle.result or after.result or "completion result persisted", before_count, after_count)
        if cycle.disposition in {AutonomousCycleDisposition.WAIT_AUTHORIZATION, AutonomousCycleDisposition.WAIT_INPUT, AutonomousCycleDisposition.WAIT_TOOL, AutonomousCycleDisposition.PAUSE} or after.status in {AutonomousJobStatus.WAITING_AUTHORIZATION, AutonomousJobStatus.WAITING_INPUT, AutonomousJobStatus.WAITING_TOOL, AutonomousJobStatus.PAUSED}:
            return AutonomousTaskProgressResult(AutonomousTaskProgressVerdict.BLOCKED, "task is waiting for an external condition", cycle.reason or after.waiting_reason or "waiting state persisted", before_count, after_count)
        if cycle.disposition is AutonomousCycleDisposition.FAIL or after.status in {AutonomousJobStatus.FAILED, AutonomousJobStatus.CANCELLED}:
            return AutonomousTaskProgressResult(AutonomousTaskProgressVerdict.FAILED, "task entered a terminal non-success disposition", cycle.reason or after.failure_reason or after.status.value, before_count, after_count)
        if after_count <= before_count:
            return AutonomousTaskProgressResult(AutonomousTaskProgressVerdict.NO_PROGRESS, "bounded cycle produced no durable work-step advance", cycle.summary, before_count, after_count)
        return AutonomousTaskProgressResult(AutonomousTaskProgressVerdict.PROGRESSED, "bounded cycle recorded durable work progress", cycle.observation or cycle.summary, before_count, after_count)


__all__ = ["AutonomousTaskProgressEvaluator", "AutonomousTaskProgressResult", "AutonomousTaskProgressVerdict", "DeterministicAutonomousTaskProgressEvaluator"]
