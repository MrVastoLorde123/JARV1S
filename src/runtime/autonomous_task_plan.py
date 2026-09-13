"""Durable, provider-neutral plan state for long-running autonomous tasks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class AutonomousTaskPlanValidationError(ValueError):
    """Raised when a task plan violates its contract."""


class AutonomousTaskPlanStepStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    SKIPPED = "SKIPPED"


_TERMINAL_STEP_STATUSES = frozenset({AutonomousTaskPlanStepStatus.COMPLETED, AutonomousTaskPlanStepStatus.SKIPPED})
_MAX_STEP_ID = 128
_MAX_DESCRIPTION = 1024
_MAX_REASON = 2048
_MAX_STEPS = 256


def _text(value: str, field_name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AutonomousTaskPlanValidationError(f"{field_name} must be a non-empty string")
    if len(value) > maximum:
        raise AutonomousTaskPlanValidationError(f"{field_name} exceeds maximum length of {maximum}")
    return value.strip()


@dataclass(frozen=True)
class AutonomousTaskPlanStep:
    step_id: str
    description: str
    status: AutonomousTaskPlanStepStatus = AutonomousTaskPlanStepStatus.PENDING
    reason: str | None = None

    def __post_init__(self) -> None:
        _text(self.step_id, "step_id", _MAX_STEP_ID)
        _text(self.description, "description", _MAX_DESCRIPTION)
        if not isinstance(self.status, AutonomousTaskPlanStepStatus):
            raise AutonomousTaskPlanValidationError("status must be an AutonomousTaskPlanStepStatus")
        if self.reason is not None:
            _text(self.reason, "reason", _MAX_REASON)
        if self.status is AutonomousTaskPlanStepStatus.BLOCKED and not self.reason:
            raise AutonomousTaskPlanValidationError("BLOCKED steps require a reason")
        if self.status is AutonomousTaskPlanStepStatus.SKIPPED and not self.reason:
            raise AutonomousTaskPlanValidationError("SKIPPED steps require a reason")

    @property
    def terminal(self) -> bool:
        return self.status in _TERMINAL_STEP_STATUSES

    def to_dict(self) -> dict[str, Any]:
        return {"step_id": self.step_id, "description": self.description, "status": self.status.value, "reason": self.reason}


@dataclass(frozen=True)
class AutonomousTaskPlan:
    steps: tuple[AutonomousTaskPlanStep, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.steps, tuple):
            raise AutonomousTaskPlanValidationError("steps must be a tuple")
        if not self.steps:
            raise AutonomousTaskPlanValidationError("plan must contain at least one step")
        if len(self.steps) > _MAX_STEPS:
            raise AutonomousTaskPlanValidationError("plan exceeds maximum step count")
        if any(not isinstance(step, AutonomousTaskPlanStep) for step in self.steps):
            raise AutonomousTaskPlanValidationError("steps must contain AutonomousTaskPlanStep values")
        ids = [step.step_id for step in self.steps]
        if len(set(ids)) != len(ids):
            raise AutonomousTaskPlanValidationError("plan step_id values must be unique")
        in_progress = [step for step in self.steps if step.status is AutonomousTaskPlanStepStatus.IN_PROGRESS]
        if len(in_progress) > 1:
            raise AutonomousTaskPlanValidationError("plan may have at most one IN_PROGRESS step")

    @classmethod
    def from_descriptions(cls, descriptions: list[str] | tuple[str, ...]) -> "AutonomousTaskPlan":
        if not isinstance(descriptions, (list, tuple)) or not descriptions:
            raise AutonomousTaskPlanValidationError("descriptions must be a non-empty list or tuple")
        return cls(tuple(AutonomousTaskPlanStep(step_id=f"step-{index}", description=description) for index, description in enumerate(descriptions, 1)))

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "AutonomousTaskPlan":
        if not isinstance(payload, Mapping):
            raise AutonomousTaskPlanValidationError("plan payload must be a mapping")
        raw_steps = payload.get("steps")
        if not isinstance(raw_steps, (list, tuple)):
            raise AutonomousTaskPlanValidationError("plan payload must contain steps")
        steps: list[AutonomousTaskPlanStep] = []
        for raw in raw_steps:
            if not isinstance(raw, Mapping):
                raise AutonomousTaskPlanValidationError("each plan step must be a mapping")
            try:
                status = AutonomousTaskPlanStepStatus(raw.get("status", "PENDING"))
            except (TypeError, ValueError) as exc:
                raise AutonomousTaskPlanValidationError("unsupported plan step status") from exc
            steps.append(AutonomousTaskPlanStep(step_id=raw.get("step_id", ""), description=raw.get("description", ""), status=status, reason=raw.get("reason")))
        return cls(tuple(steps))

    def to_dict(self) -> dict[str, Any]:
        return {"steps": [step.to_dict() for step in self.steps]}

    @property
    def current(self) -> AutonomousTaskPlanStep | None:
        for status in (AutonomousTaskPlanStepStatus.IN_PROGRESS, AutonomousTaskPlanStepStatus.BLOCKED, AutonomousTaskPlanStepStatus.PENDING):
            for step in self.steps:
                if step.status is status:
                    return step
        return None

    @property
    def complete(self) -> bool:
        return all(step.terminal for step in self.steps)

    @property
    def blocked(self) -> bool:
        return any(step.status is AutonomousTaskPlanStepStatus.BLOCKED for step in self.steps)

    def start(self, step_id: str) -> "AutonomousTaskPlan":
        step = self._require(step_id)
        if step.terminal:
            raise AutonomousTaskPlanValidationError("terminal plan steps cannot start")
        current = self.current
        if current is not None and current.step_id != step_id:
            raise AutonomousTaskPlanValidationError("another plan boundary is active")
        return self._replace_step(step_id, AutonomousTaskPlanStep(step_id=step.step_id, description=step.description, status=AutonomousTaskPlanStepStatus.IN_PROGRESS))

    def complete_step(self, step_id: str, reason: str | None = None) -> "AutonomousTaskPlan":
        step = self._require(step_id)
        if step.status is not AutonomousTaskPlanStepStatus.IN_PROGRESS:
            raise AutonomousTaskPlanValidationError("only IN_PROGRESS plan steps can be completed")
        return self._replace_step(step_id, AutonomousTaskPlanStep(step_id=step.step_id, description=step.description, status=AutonomousTaskPlanStepStatus.COMPLETED, reason=reason))

    def skip_step(self, step_id: str, reason: str) -> "AutonomousTaskPlan":
        step = self._require(step_id)
        if step.terminal:
            raise AutonomousTaskPlanValidationError("terminal plan steps cannot be skipped")
        if not reason:
            raise AutonomousTaskPlanValidationError("SKIPPED steps require a reason")
        return self._replace_step(step_id, AutonomousTaskPlanStep(step_id=step.step_id, description=step.description, status=AutonomousTaskPlanStepStatus.SKIPPED, reason=reason))

    def block(self, step_id: str, reason: str) -> "AutonomousTaskPlan":
        step = self._require(step_id)
        if step.terminal:
            raise AutonomousTaskPlanValidationError("terminal plan steps cannot be blocked")
        return self._replace_step(step_id, AutonomousTaskPlanStep(step_id=step.step_id, description=step.description, status=AutonomousTaskPlanStepStatus.BLOCKED, reason=reason))

    def _require(self, step_id: str) -> AutonomousTaskPlanStep:
        _text(step_id, "step_id", _MAX_STEP_ID)
        for step in self.steps:
            if step.step_id == step_id:
                return step
        raise LookupError(f"plan step not found: {step_id}")

    def _replace_step(self, step_id: str, replacement: AutonomousTaskPlanStep) -> "AutonomousTaskPlan":
        return AutonomousTaskPlan(tuple(replacement if step.step_id == step_id else step for step in self.steps))


__all__ = ["AutonomousTaskPlan", "AutonomousTaskPlanStep", "AutonomousTaskPlanStepStatus", "AutonomousTaskPlanValidationError"]
