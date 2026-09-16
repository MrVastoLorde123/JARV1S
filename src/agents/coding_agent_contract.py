"""Typed lifecycle contract for JARVIS coding-agent work.

This module describes observable coding-agent state. It does not authorize,
execute, or verify work; those responsibilities remain with the existing
confirmation, tool-authorization, worker, and verification boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class CodingAgentStage(str, Enum):
    IDLE = "IDLE"
    UNDERSTANDING = "UNDERSTANDING"
    PLANNING = "PLANNING"
    AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class CodingAgentState:
    """Safe, presentation-ready coding-agent state."""

    task_id: str
    stage: CodingAgentStage
    objective: str
    operation_id: str | None = None
    plan_fingerprint: str | None = None
    edits_total: int = 0
    edits_applied: int = 0
    verification_runner: str | None = None
    message: str = ""
    metadata: Mapping[str, object] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.task_id, str) or not self.task_id.strip():
            raise ValueError("task_id must be a non-empty string")
        if not isinstance(self.stage, CodingAgentStage):
            raise TypeError("stage must be a CodingAgentStage")
        if not isinstance(self.objective, str) or not self.objective.strip():
            raise ValueError("objective must be a non-empty string")
        for name, value in (("edits_total", self.edits_total), ("edits_applied", self.edits_applied)):
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"{name} must be an integer")
            if value < 0:
                raise ValueError(f"{name} must be non-negative")
        if self.edits_applied > self.edits_total:
            raise ValueError("edits_applied cannot exceed edits_total")
        if self.operation_id is not None and (not isinstance(self.operation_id, str) or not self.operation_id.strip()):
            raise ValueError("operation_id must be non-empty when provided")
        if self.plan_fingerprint is not None and (not isinstance(self.plan_fingerprint, str) or not self.plan_fingerprint.strip()):
            raise ValueError("plan_fingerprint must be non-empty when provided")
        if self.verification_runner is not None and not isinstance(self.verification_runner, str):
            raise TypeError("verification_runner must be a string or None")
        if not isinstance(self.message, str):
            raise TypeError("message must be a string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")


def can_transition(current: CodingAgentStage, target: CodingAgentStage) -> bool:
    """Return whether an observed coding-agent lifecycle transition is valid."""

    transitions = {
        CodingAgentStage.IDLE: {CodingAgentStage.UNDERSTANDING},
        CodingAgentStage.UNDERSTANDING: {CodingAgentStage.PLANNING, CodingAgentStage.BLOCKED, CodingAgentStage.FAILED},
        CodingAgentStage.PLANNING: {CodingAgentStage.AWAITING_CONFIRMATION, CodingAgentStage.BLOCKED, CodingAgentStage.FAILED},
        CodingAgentStage.AWAITING_CONFIRMATION: {CodingAgentStage.EXECUTING, CodingAgentStage.BLOCKED, CodingAgentStage.FAILED},
        CodingAgentStage.EXECUTING: {CodingAgentStage.VERIFYING, CodingAgentStage.BLOCKED, CodingAgentStage.FAILED},
        CodingAgentStage.VERIFYING: {CodingAgentStage.COMPLETE, CodingAgentStage.FAILED, CodingAgentStage.BLOCKED},
        CodingAgentStage.COMPLETE: set(),
        CodingAgentStage.BLOCKED: set(),
        CodingAgentStage.FAILED: set(),
    }
    return target in transitions[current]


__all__ = ["CodingAgentStage", "CodingAgentState", "can_transition"]
