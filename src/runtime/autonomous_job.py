"""M54 bounded autonomous-job lifecycle for the JARVIS V1 application layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping


class AutonomousJobValidationError(ValueError):
    """Raised when an autonomous job violates its lifecycle contract."""


class AutonomousJobStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    WAITING_AUTHORIZATION = "WAITING_AUTHORIZATION"
    WAITING_INPUT = "WAITING_INPUT"
    WAITING_TOOL = "WAITING_TOOL"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class AutonomousJobEventKind(str, Enum):
    CREATED = "CREATED"
    STARTED = "STARTED"
    STEP_RECORDED = "STEP_RECORDED"
    WAITING_AUTHORIZATION = "WAITING_AUTHORIZATION"
    WAITING_INPUT = "WAITING_INPUT"
    WAITING_TOOL = "WAITING_TOOL"
    PAUSED = "PAUSED"
    RESUMED = "RESUMED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    RECONCILED = "RECONCILED"


_TERMINAL = frozenset(
    {
        AutonomousJobStatus.COMPLETED,
        AutonomousJobStatus.FAILED,
        AutonomousJobStatus.CANCELLED,
    }
)
_RESUMABLE = frozenset(
    {
        AutonomousJobStatus.WAITING_AUTHORIZATION,
        AutonomousJobStatus.WAITING_INPUT,
        AutonomousJobStatus.WAITING_TOOL,
        AutonomousJobStatus.PAUSED,
    }
)
_MAX_GOAL_LENGTH = 4096
_MAX_REASON_LENGTH = 2048
_MAX_RESULT_LENGTH = 16384
_MAX_EVENTS = 1024


def _text(value: str, field_name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AutonomousJobValidationError(f"{field_name} must be a non-empty string")
    if len(value) > maximum:
        raise AutonomousJobValidationError(f"{field_name} exceeds maximum length of {maximum}")
    return value.strip()


def _freeze(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(_freeze(item) for item in value)
    raise AutonomousJobValidationError(
        f"unsupported context value type: {type(value).__name__}"
    )


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    if isinstance(value, frozenset):
        return sorted((_thaw(item) for item in value), key=repr)
    return value


@dataclass(frozen=True)
class AutonomousJobEvent:
    """Immutable event describing one lifecycle transition or work cycle."""

    event_id: str
    job_id: str
    sequence: int
    kind: AutonomousJobEventKind
    summary: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _text(self.event_id, "event_id", 256)
        _text(self.job_id, "job_id", 256)
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int) or self.sequence <= 0:
            raise AutonomousJobValidationError("sequence must be a positive integer")
        if not isinstance(self.kind, AutonomousJobEventKind):
            raise AutonomousJobValidationError("kind must be an AutonomousJobEventKind")
        _text(self.summary, "summary", _MAX_REASON_LENGTH)
        if not isinstance(self.metadata, Mapping):
            raise AutonomousJobValidationError("metadata must be a mapping")
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "job_id": self.job_id,
            "sequence": self.sequence,
            "kind": self.kind.value,
            "summary": self.summary,
            "metadata": _thaw(self.metadata),
        }


@dataclass(frozen=True)
class AutonomousJobStep:
    """Immutable record of one bounded work cycle."""

    step_id: str
    job_id: str
    sequence: int
    phase: str
    summary: str
    observation: str = ""
    context_delta: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _text(self.step_id, "step_id", 256)
        _text(self.job_id, "job_id", 256)
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int) or self.sequence <= 0:
            raise AutonomousJobValidationError("sequence must be a positive integer")
        _text(self.phase, "phase", 256)
        _text(self.summary, "summary", _MAX_REASON_LENGTH)
        if not isinstance(self.observation, str):
            raise AutonomousJobValidationError("observation must be a string")
        if len(self.observation) > _MAX_RESULT_LENGTH:
            raise AutonomousJobValidationError("observation exceeds maximum length")
        if not isinstance(self.context_delta, Mapping):
            raise AutonomousJobValidationError("context_delta must be a mapping")
        object.__setattr__(self, "context_delta", _freeze(self.context_delta))

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "job_id": self.job_id,
            "sequence": self.sequence,
            "phase": self.phase,
            "summary": self.summary,
            "observation": self.observation,
            "context_delta": _thaw(self.context_delta),
        }


@dataclass(frozen=True)
class AutonomousJob:
    """Immutable lifecycle snapshot for one bounded long-running goal."""

    job_id: str
    goal: str
    status: AutonomousJobStatus = AutonomousJobStatus.QUEUED
    step_count: int = 0
    max_steps: int = 32
    steps: tuple[AutonomousJobStep, ...] = ()
    events: tuple[AutonomousJobEvent, ...] = ()
    working_context: Mapping[str, Any] = field(default_factory=dict)
    waiting_reason: str | None = None
    result: str | None = None
    failure_reason: str | None = None

    def __post_init__(self) -> None:
        _text(self.job_id, "job_id", 256)
        _text(self.goal, "goal", _MAX_GOAL_LENGTH)
        if not isinstance(self.status, AutonomousJobStatus):
            raise AutonomousJobValidationError("status must be an AutonomousJobStatus")
        if isinstance(self.step_count, bool) or not isinstance(self.step_count, int) or self.step_count < 0:
            raise AutonomousJobValidationError("step_count must be a non-negative integer")
        if isinstance(self.max_steps, bool) or not isinstance(self.max_steps, int) or self.max_steps <= 0:
            raise AutonomousJobValidationError("max_steps must be a positive integer")
        if self.step_count > self.max_steps:
            raise AutonomousJobValidationError("step_count cannot exceed max_steps")
        if not isinstance(self.steps, tuple) or any(not isinstance(step, AutonomousJobStep) for step in self.steps):
            raise AutonomousJobValidationError("steps must be a tuple of AutonomousJobStep values")
        if len(self.steps) != self.step_count:
            raise AutonomousJobValidationError("steps length must equal step_count")
        if [step.sequence for step in self.steps] != list(range(1, self.step_count + 1)):
            raise AutonomousJobValidationError("step sequences must be contiguous and ordered")
        if any(step.job_id != self.job_id for step in self.steps):
            raise AutonomousJobValidationError("every step must belong to the job")
        if not isinstance(self.events, tuple) or any(not isinstance(event, AutonomousJobEvent) for event in self.events):
            raise AutonomousJobValidationError("events must be a tuple of AutonomousJobEvent values")
        if len(self.events) > _MAX_EVENTS:
            raise AutonomousJobValidationError("event history exceeds maximum size")
        if [event.sequence for event in self.events] != list(range(1, len(self.events) + 1)):
            raise AutonomousJobValidationError("event sequences must be contiguous and ordered")
        if any(event.job_id != self.job_id for event in self.events):
            raise AutonomousJobValidationError("every event must belong to the job")
        if not isinstance(self.working_context, Mapping):
            raise AutonomousJobValidationError("working_context must be a mapping")
        object.__setattr__(self, "working_context", _freeze(self.working_context))
        if self.waiting_reason is not None and (not isinstance(self.waiting_reason, str) or not self.waiting_reason.strip()):
            raise AutonomousJobValidationError("waiting_reason must be a non-empty string or None")
        if self.result is not None and (not isinstance(self.result, str) or len(self.result) > _MAX_RESULT_LENGTH):
            raise AutonomousJobValidationError("result must be a bounded string or None")
        if self.failure_reason is not None and (not isinstance(self.failure_reason, str) or len(self.failure_reason) > _MAX_REASON_LENGTH):
            raise AutonomousJobValidationError("failure_reason must be a bounded string or None")
        if self.status in _TERMINAL and self.waiting_reason is not None:
            raise AutonomousJobValidationError("terminal jobs cannot retain waiting_reason")
        if self.status is AutonomousJobStatus.COMPLETED and not self.result:
            raise AutonomousJobValidationError("completed jobs require a result")
        if self.status is AutonomousJobStatus.FAILED and not self.failure_reason:
            raise AutonomousJobValidationError("failed jobs require a failure_reason")

    @classmethod
    def create(
        cls,
        goal: str,
        *,
        job_id: str | None = None,
        max_steps: int = 32,
        working_context: Mapping[str, Any] | None = None,
    ) -> "AutonomousJob":
        goal_value = _text(goal, "goal", _MAX_GOAL_LENGTH)
        if job_id is None:
            job_id = cls._deterministic_job_id(goal_value, max_steps)
        job = cls(
            job_id=job_id,
            goal=goal_value,
            max_steps=max_steps,
            working_context=working_context or {},
        )
        return job._append_event(
            AutonomousJobEventKind.CREATED,
            f"Created autonomous job for goal: {goal_value}",
        )

    @property
    def terminal(self) -> bool:
        return self.status in _TERMINAL

    @property
    def resumable(self) -> bool:
        return self.status in _RESUMABLE

    @property
    def capacity_remaining(self) -> int:
        return self.max_steps - self.step_count

    def start(self) -> "AutonomousJob":
        if self.status is not AutonomousJobStatus.QUEUED:
            raise AutonomousJobValidationError("only queued jobs can start")
        return self._replace(
            status=AutonomousJobStatus.RUNNING,
            waiting_reason=None,
            events=self._next_event(AutonomousJobEventKind.STARTED, "Job started"),
        )

    def resume(self) -> "AutonomousJob":
        if not self.resumable:
            raise AutonomousJobValidationError("only waiting or paused jobs can resume")
        return self._replace(
            status=AutonomousJobStatus.RUNNING,
            waiting_reason=None,
            events=self._next_event(AutonomousJobEventKind.RESUMED, "Job resumed"),
        )

    def record_step(
        self,
        *,
        phase: str,
        summary: str,
        observation: str = "",
        context_delta: Mapping[str, Any] | None = None,
    ) -> "AutonomousJob":
        self._require_running()
        if self.step_count >= self.max_steps:
            raise AutonomousJobValidationError("job has reached its maximum step budget")
        sequence = self.step_count + 1
        step_id = self._deterministic_step_id(sequence, phase, summary, observation)
        step = AutonomousJobStep(
            step_id=step_id,
            job_id=self.job_id,
            sequence=sequence,
            phase=phase,
            summary=summary,
            observation=observation,
            context_delta=context_delta or {},
        )
        next_context = dict(_thaw(self.working_context))
        next_context.update(_thaw(step.context_delta))
        event = self._build_event(
            AutonomousJobEventKind.STEP_RECORDED,
            f"Recorded work step {sequence}: {summary}",
            metadata={"step_id": step.step_id, "phase": phase},
        )
        return self._replace(
            step_count=sequence,
            steps=self.steps + (step,),
            working_context=next_context,
            events=self.events + (event,),
        )

    def wait_for_authorization(self, reason: str) -> "AutonomousJob":
        return self._wait(AutonomousJobStatus.WAITING_AUTHORIZATION, AutonomousJobEventKind.WAITING_AUTHORIZATION, reason)

    def wait_for_input(self, reason: str) -> "AutonomousJob":
        return self._wait(AutonomousJobStatus.WAITING_INPUT, AutonomousJobEventKind.WAITING_INPUT, reason)

    def wait_for_tool(self, reason: str) -> "AutonomousJob":
        return self._wait(AutonomousJobStatus.WAITING_TOOL, AutonomousJobEventKind.WAITING_TOOL, reason)

    def pause(self, reason: str) -> "AutonomousJob":
        return self._wait(AutonomousJobStatus.PAUSED, AutonomousJobEventKind.PAUSED, reason)

    def complete(self, result: str) -> "AutonomousJob":
        self._require_running()
        result_value = _text(result, "result", _MAX_RESULT_LENGTH)
        context = dict(_thaw(self.working_context))
        context.update(
            {
                "active_execution_attempt_id": None,
                "active_execution_attempt_state": None,
                "active_execution_attempt_step_count": None,
            }
        )
        return self._replace(
            status=AutonomousJobStatus.COMPLETED,
            waiting_reason=None,
            result=result_value,
            failure_reason=None,
            working_context=context,
            events=self._next_event(AutonomousJobEventKind.COMPLETED, "Job completed"),
        )

    def fail(self, reason: str) -> "AutonomousJob":
        self._require_running()
        reason_value = _text(reason, "failure_reason", _MAX_REASON_LENGTH)
        context = dict(_thaw(self.working_context))
        context.update(
            {
                "active_execution_attempt_id": None,
                "active_execution_attempt_state": None,
                "active_execution_attempt_step_count": None,
            }
        )
        return self._replace(
            status=AutonomousJobStatus.FAILED,
            waiting_reason=None,
            result=None,
            failure_reason=reason_value,
            working_context=context,
            events=self._next_event(AutonomousJobEventKind.FAILED, f"Job failed: {reason_value}"),
        )

    def reconcile_completed(self, result: str, evidence: str) -> "AutonomousJob":
        if self.status is not AutonomousJobStatus.PAUSED:
            raise AutonomousJobValidationError("only paused jobs can be reconciled")
        if self.working_context.get("recovery_required") != "AMBIGUOUS_EXECUTION":
            raise AutonomousJobValidationError("job does not require ambiguous execution reconciliation")
        result_value = _text(result, "result", _MAX_RESULT_LENGTH)
        evidence_value = _text(evidence, "evidence", _MAX_REASON_LENGTH)
        context = dict(_thaw(self.working_context))
        context.update(
            {
                "recovery_required": None,
                "reconciliation_source": "operator",
                "external_effect_verified": False,
                "reconciliation_evidence": evidence_value,
            }
        )
        return self._replace(
            status=AutonomousJobStatus.COMPLETED,
            waiting_reason=None,
            result=result_value,
            failure_reason=None,
            working_context=context,
            events=self._next_event(
                AutonomousJobEventKind.RECONCILED,
                "Ambiguous execution outcome reconciled by operator.",
                metadata={
                    "outcome": "COMPLETED",
                    "external_effect_verified": False,
                },
            ),
        )

    def reconcile_failed(self, reason: str, evidence: str) -> "AutonomousJob":
        if self.status is not AutonomousJobStatus.PAUSED:
            raise AutonomousJobValidationError("only paused jobs can be reconciled")
        if self.working_context.get("recovery_required") != "AMBIGUOUS_EXECUTION":
            raise AutonomousJobValidationError("job does not require ambiguous execution reconciliation")
        reason_value = _text(reason, "failure_reason", _MAX_REASON_LENGTH)
        evidence_value = _text(evidence, "evidence", _MAX_REASON_LENGTH)
        context = dict(_thaw(self.working_context))
        context.update(
            {
                "recovery_required": None,
                "reconciliation_source": "operator",
                "external_effect_verified": False,
                "reconciliation_evidence": evidence_value,
            }
        )
        return self._replace(
            status=AutonomousJobStatus.FAILED,
            waiting_reason=None,
            result=None,
            failure_reason=reason_value,
            working_context=context,
            events=self._next_event(
                AutonomousJobEventKind.RECONCILED,
                "Ambiguous execution outcome reconciled as failed by operator.",
                metadata={
                    "outcome": "FAILED",
                    "external_effect_verified": False,
                },
            ),
        )

    def cancel(self, reason: str = "Job cancelled") -> "AutonomousJob":
        if self.terminal:
            raise AutonomousJobValidationError("terminal jobs cannot be cancelled")
        reason_value = _text(reason, "reason", _MAX_REASON_LENGTH)
        return self._replace(
            status=AutonomousJobStatus.CANCELLED,
            waiting_reason=None,
            result=None,
            failure_reason=reason_value,
            events=self._next_event(AutonomousJobEventKind.CANCELLED, reason_value),
        )

    def with_working_context(self, values: Mapping[str, Any]) -> "AutonomousJob":
        if self.terminal:
            raise AutonomousJobValidationError("terminal jobs cannot mutate working context")
        if not isinstance(values, Mapping):
            raise AutonomousJobValidationError("values must be a mapping")
        context = dict(_thaw(self.working_context))
        context.update(_thaw(_freeze(values)))
        return self._replace(working_context=context)

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "goal": self.goal,
            "status": self.status.value,
            "step_count": self.step_count,
            "max_steps": self.max_steps,
            "capacity_remaining": self.capacity_remaining,
            "steps": [step.to_dict() for step in self.steps],
            "events": [event.to_dict() for event in self.events],
            "working_context": _thaw(self.working_context),
            "waiting_reason": self.waiting_reason,
            "result": self.result,
            "failure_reason": self.failure_reason,
            "job_state_is_authorization": False,
            "job_state_is_execution": False,
            "authorization_granted": False,
            "authority_granted": False,
            "execution_requested": False,
            "truth_guaranteed": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)

    def _wait(
        self,
        status: AutonomousJobStatus,
        event_kind: AutonomousJobEventKind,
        reason: str,
    ) -> "AutonomousJob":
        self._require_running()
        reason_value = _text(reason, "reason", _MAX_REASON_LENGTH)
        return self._replace(
            status=status,
            waiting_reason=reason_value,
            events=self._next_event(event_kind, reason_value),
        )

    def _require_running(self) -> None:
        if self.status is not AutonomousJobStatus.RUNNING:
            raise AutonomousJobValidationError("job must be RUNNING for this transition")

    def _replace(self, **changes: Any) -> "AutonomousJob":
        data = {
            "job_id": self.job_id,
            "goal": self.goal,
            "status": self.status,
            "step_count": self.step_count,
            "max_steps": self.max_steps,
            "steps": self.steps,
            "events": self.events,
            "working_context": self.working_context,
            "waiting_reason": self.waiting_reason,
            "result": self.result,
            "failure_reason": self.failure_reason,
        }
        data.update(changes)
        return AutonomousJob(**data)

    def _append_event(self, kind: AutonomousJobEventKind, summary: str, metadata: Mapping[str, Any] | None = None) -> "AutonomousJob":
        return self._replace(events=self.events + (self._build_event(kind, summary, metadata=metadata),))

    def _next_event(self, kind: AutonomousJobEventKind, summary: str, metadata: Mapping[str, Any] | None = None) -> tuple[AutonomousJobEvent, ...]:
        return self.events + (self._build_event(kind, summary, metadata=metadata),)

    def _build_event(self, kind: AutonomousJobEventKind, summary: str, metadata: Mapping[str, Any] | None = None) -> AutonomousJobEvent:
        sequence = len(self.events) + 1
        event_id = self._deterministic_event_id(sequence, kind, summary)
        return AutonomousJobEvent(
            event_id=event_id,
            job_id=self.job_id,
            sequence=sequence,
            kind=kind,
            summary=summary,
            metadata=metadata or {},
        )

    @staticmethod
    def _deterministic_job_id(goal: str, max_steps: int) -> str:
        payload = json.dumps({"goal": goal, "max_steps": max_steps}, sort_keys=True, separators=(",", ":"))
        return f"autonomous-job-{hashlib.sha256(payload.encode()).hexdigest()[:24]}"

    def _deterministic_step_id(self, sequence: int, phase: str, summary: str, observation: str) -> str:
        payload = json.dumps(
            {"job_id": self.job_id, "sequence": sequence, "phase": phase, "summary": summary, "observation": observation},
            sort_keys=True,
            separators=(",", ":"),
        )
        return f"autonomous-step-{hashlib.sha256(payload.encode()).hexdigest()[:24]}"

    def _deterministic_event_id(self, sequence: int, kind: AutonomousJobEventKind, summary: str) -> str:
        payload = json.dumps(
            {"job_id": self.job_id, "sequence": sequence, "kind": kind.value, "summary": summary},
            sort_keys=True,
            separators=(",", ":"),
        )
        return f"autonomous-event-{hashlib.sha256(payload.encode()).hexdigest()[:24]}"


__all__ = [
    "AutonomousJob",
    "AutonomousJobEvent",
    "AutonomousJobEventKind",
    "AutonomousJobStatus",
    "AutonomousJobStep",
    "AutonomousJobValidationError",
]
