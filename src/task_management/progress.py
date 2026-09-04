"""M20.4 progress and state-evaluation boundary.

Progress evaluation compares the recorded task state with explicitly supplied
observations. It does not mutate task state, infer authorization, or choose
what should happen next.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Iterable, Mapping

from .task import Task, TaskState


class ObservedState(str, Enum):
    """State reported by an external observation/evidence source."""

    NOT_OBSERVED = "NOT_OBSERVED"
    PROPOSED = "PROPOSED"
    READY = "READY"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    SUPERSEDED = "SUPERSEDED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class ProgressStatus(str, Enum):
    """Relationship between recorded task state and supplied observations."""

    UNVERIFIED = "UNVERIFIED"
    ALIGNED = "ALIGNED"
    CONFLICTED = "CONFLICTED"


@dataclass(frozen=True)
class ProgressEvidence:
    """Explicit observation used to evaluate one task."""

    evidence_id: str
    task_id: str
    observed_state: ObservedState
    source: str
    reference_id: str
    observed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: str = ""

    def __post_init__(self) -> None:
        _validate_id(self.evidence_id, "evidence_id")
        _validate_id(self.task_id, "task_id")
        _validate_id(self.source, "source")
        _validate_id(self.reference_id, "reference_id")
        _validate_text(self.observed_at, "observed_at")
        if not isinstance(self.observed_state, ObservedState):
            try:
                object.__setattr__(self, "observed_state", ObservedState(self.observed_state))
            except (TypeError, ValueError) as exc:
                raise TypeError("observed_state must be an ObservedState") from exc
        if not isinstance(self.details, str):
            raise TypeError("details must be a string")


@dataclass(frozen=True)
class ProgressEvaluation:
    """Immutable comparison between recorded task state and observation."""

    task_id: str
    recorded_state: TaskState
    observed_state: ObservedState
    status: ProgressStatus
    evidence_ids: tuple[str, ...] = ()

    @property
    def conflicts_with_recorded_state(self) -> bool:
        return self.status is ProgressStatus.CONFLICTED

    def to_context(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "recorded_state": self.recorded_state.value,
            "observed_state": self.observed_state.value,
            "progress_status": self.status.value,
            "evidence_ids": self.evidence_ids,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
        }


class ProgressEvaluationError(ValueError):
    """Raised when progress evidence cannot be evaluated safely."""


def _validate_id(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _validate_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _status_for(recorded: TaskState, observed: ObservedState) -> ProgressStatus:
    if observed in {ObservedState.NOT_OBSERVED, ObservedState.UNKNOWN}:
        return ProgressStatus.UNVERIFIED
    if observed.value == recorded.value:
        return ProgressStatus.ALIGNED
    return ProgressStatus.CONFLICTED


class TaskProgressEvaluator:
    """Read-only evaluator for task progress against explicit evidence."""

    def __init__(self, tasks: Iterable[Task] = ()) -> None:
        self._tasks: dict[str, Task] = {}
        self._evidence: dict[str, ProgressEvidence] = {}
        for task in tasks:
            self.register_task(task)

    def register_task(self, task: Task) -> None:
        if not isinstance(task, Task):
            raise TypeError("task must be a Task")
        existing = self._tasks.get(task.task_id)
        if existing is not None and existing != task:
            raise ProgressEvaluationError(f"task identity conflict: {task.task_id}")
        self._tasks[task.task_id] = task

    def add_evidence(self, evidence: ProgressEvidence) -> None:
        if evidence.task_id not in self._tasks:
            raise ProgressEvaluationError(f"unknown task_id: {evidence.task_id}")
        existing = self._evidence.get(evidence.evidence_id)
        if existing is not None and existing != evidence:
            raise ProgressEvaluationError(f"evidence identity conflict: {evidence.evidence_id}")
        self._evidence[evidence.evidence_id] = evidence

    def evaluate(self, task_id: str) -> ProgressEvaluation:
        _validate_id(task_id, "task_id")
        task = self._tasks.get(task_id)
        if task is None:
            raise ProgressEvaluationError(f"unknown task_id: {task_id}")

        evidence = sorted(
            (item for item in self._evidence.values() if item.task_id == task_id),
            key=lambda item: (item.observed_at, item.evidence_id),
        )
        if not evidence:
            return ProgressEvaluation(
                task_id=task.task_id,
                recorded_state=task.state,
                observed_state=ObservedState.NOT_OBSERVED,
                status=ProgressStatus.UNVERIFIED,
            )

        latest = evidence[-1]
        return ProgressEvaluation(
            task_id=task.task_id,
            recorded_state=task.state,
            observed_state=latest.observed_state,
            status=_status_for(task.state, latest.observed_state),
            evidence_ids=tuple(item.evidence_id for item in evidence),
        )

    def evaluations(self) -> tuple[ProgressEvaluation, ...]:
        return tuple(self.evaluate(task_id) for task_id in sorted(self._tasks))

    def evidence_for(self, task_id: str) -> tuple[ProgressEvidence, ...]:
        _validate_id(task_id, "task_id")
        if task_id not in self._tasks:
            raise ProgressEvaluationError(f"unknown task_id: {task_id}")
        return tuple(
            sorted(
                (item for item in self._evidence.values() if item.task_id == task_id),
                key=lambda item: (item.observed_at, item.evidence_id),
            )
        )

    def to_context(self, task_id: str) -> Mapping[str, object]:
        return self.evaluate(task_id).to_context()
