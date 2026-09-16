"""M31: explicit work-state substrate for dynamic JARVIS orchestration.

Work state describes what JARVIS is currently working on, where that work sits
in its lifecycle, what is blocking it, and which operational role is currently
appropriate. It is not memory, authority, permission, or execution state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class WorkStage(str, Enum):
    IDLE = "IDLE"
    UNDERSTANDING = "UNDERSTANDING"
    GATHERING_EVIDENCE = "GATHERING_EVIDENCE"
    PLANNING = "PLANNING"
    PROPOSING_ACTION = "PROPOSING_ACTION"
    AWAITING_AUTHORIZATION = "AWAITING_AUTHORIZATION"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


class WorkStatus(str, Enum):
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class WorkRole(str, Enum):
    GENERAL = "GENERAL"
    RESEARCHER = "RESEARCHER"
    REQUIREMENTS_ANALYST = "REQUIREMENTS_ANALYST"
    TECHNICAL_LEAD = "TECHNICAL_LEAD"
    DEBUGGER = "DEBUGGER"
    REVIEWER = "REVIEWER"
    RELEASE_COORDINATOR = "RELEASE_COORDINATOR"


@dataclass(frozen=True)
class WorkBlocker:
    """Observable blocker preventing progress or requiring resolution."""

    blocker_id: str
    message: str
    severity: str = "INFO"
    stage: WorkStage | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("blocker_id", "message", "severity"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.stage is not None and not isinstance(self.stage, WorkStage):
            raise TypeError("stage must be a WorkStage or None")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class WorkState:
    """Immutable operational state shared by JARVIS orchestration components."""

    work_id: str
    objective: str
    stage: WorkStage = WorkStage.IDLE
    status: WorkStatus = WorkStatus.IDLE
    role: WorkRole = WorkRole.GENERAL
    progress: float | None = None
    current_step: str | None = None
    blockers: tuple[WorkBlocker, ...] = ()
    required_capabilities: tuple[str, ...] = ()
    assigned_agent_ids: tuple[str, ...] = ()
    evidence_cursor: int | None = None
    source: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.work_id, str) or not self.work_id.strip():
            raise ValueError("work_id must be a non-empty string")
        if not isinstance(self.objective, str) or not self.objective.strip():
            raise ValueError("objective must be a non-empty string")
        if not isinstance(self.stage, WorkStage):
            raise TypeError("stage must be a WorkStage")
        if not isinstance(self.status, WorkStatus):
            raise TypeError("status must be a WorkStatus")
        if not isinstance(self.role, WorkRole):
            raise TypeError("role must be a WorkRole")
        if self.progress is not None:
            if not isinstance(self.progress, (int, float)) or isinstance(self.progress, bool):
                raise TypeError("progress must be numeric or None")
            if not 0.0 <= float(self.progress) <= 1.0:
                raise ValueError("progress must be between 0.0 and 1.0")
            object.__setattr__(self, "progress", float(self.progress))
        if self.current_step is not None and (not isinstance(self.current_step, str) or not self.current_step.strip()):
            raise ValueError("current_step must be non-empty when provided")
        if not isinstance(self.blockers, tuple) or any(not isinstance(item, WorkBlocker) for item in self.blockers):
            raise TypeError("blockers must be a tuple of WorkBlocker values")
        if not isinstance(self.required_capabilities, tuple) or any(not isinstance(item, str) or not item.strip() for item in self.required_capabilities):
            raise TypeError("required_capabilities must be a tuple of non-empty strings")
        if len(set(self.required_capabilities)) != len(self.required_capabilities):
            raise ValueError("required_capabilities must be unique")
        if not isinstance(self.assigned_agent_ids, tuple) or any(not isinstance(item, str) or not item.strip() for item in self.assigned_agent_ids):
            raise TypeError("assigned_agent_ids must be a tuple of non-empty strings")
        if len(set(self.assigned_agent_ids)) != len(self.assigned_agent_ids):
            raise ValueError("assigned_agent_ids must be unique")
        if self.evidence_cursor is not None:
            if not isinstance(self.evidence_cursor, int) or isinstance(self.evidence_cursor, bool) or self.evidence_cursor < 0:
                raise ValueError("evidence_cursor must be a non-negative integer or None")
        if not isinstance(self.source, str):
            raise TypeError("source must be a string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def is_terminal(self) -> bool:
        return self.stage in {WorkStage.COMPLETE, WorkStage.FAILED}

    @property
    def is_blocked(self) -> bool:
        return self.status is WorkStatus.BLOCKED or self.stage is WorkStage.BLOCKED or bool(self.blockers)


def infer_work_role(
    *,
    stage: WorkStage,
    has_requirements_gap: bool = False,
    has_unknowns: bool = False,
    has_failed_verification: bool = False,
    implementation_ready: bool = False,
    verification_passed: bool = False,
) -> WorkRole:
    """Infer an operational role from observable work-state signals only."""
    if stage in {WorkStage.COMPLETE, WorkStage.VERIFYING} and verification_passed:
        return WorkRole.RELEASE_COORDINATOR
    if has_failed_verification or stage is WorkStage.FAILED:
        return WorkRole.DEBUGGER
    if has_requirements_gap:
        return WorkRole.REQUIREMENTS_ANALYST
    if has_unknowns or stage is WorkStage.GATHERING_EVIDENCE:
        return WorkRole.RESEARCHER
    if implementation_ready or stage in {WorkStage.PLANNING, WorkStage.EXECUTING}:
        return WorkRole.TECHNICAL_LEAD
    if stage is WorkStage.PROPOSING_ACTION:
        return WorkRole.REVIEWER
    return WorkRole.GENERAL


__all__ = [
    "WorkBlocker",
    "WorkRole",
    "WorkStage",
    "WorkState",
    "WorkStatus",
    "infer_work_role",
]
