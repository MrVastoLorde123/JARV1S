"""Bounded reliability and recovery decisions for M8.6.

This module classifies explicit execution conditions and produces recovery
intent as data. It never executes an action, grants authorization, mutates
an execution request, or schedules an implicit retry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from src.agency.execution_runtime import ExecutionObservation, ExecutionStatus


class ReliabilityClass(str, Enum):
    """Deterministic reliability classification for an execution event."""

    HEALTHY = "healthy"
    FAILED_RETRYABLE = "failed_retryable"
    FAILED_TERMINAL = "failed_terminal"
    INTERRUPTED = "interrupted"
    PARTIAL_COMPLETION = "partial_completion"
    BLOCKED = "blocked"
    REQUIRES_RECONCILIATION = "requires_reconciliation"


class RecoveryAction(str, Enum):
    """Non-executing recovery intent produced by M8.6."""

    NONE = "none"
    STOP = "stop"
    RECONCILE = "reconcile"
    REQUEST_FRESH_AUTHORIZATION = "request_fresh_authorization"


@dataclass(frozen=True)
class ReliabilitySignal:
    """Explicit supplemental reliability information from an execution owner."""

    interrupted: bool = False
    partial_completion: bool = False
    requires_reconciliation: bool = False
    retryable_failure: bool = False
    reason: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "interrupted",
            "partial_completion",
            "requires_reconciliation",
            "retryable_failure",
        ):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a bool")
        if self.reason is not None and (
            not isinstance(self.reason, str) or not self.reason.strip()
        ):
            raise ValueError("reason must be a non-empty string when provided")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")


@dataclass(frozen=True)
class ReliabilityAssessment:
    """Immutable classification of one observed execution event."""

    execution_id: str
    classification: ReliabilityClass
    reason: str
    observation: ExecutionObservation
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.execution_id, str) or not self.execution_id.strip():
            raise ValueError("execution_id must be a non-empty string")
        if not isinstance(self.classification, ReliabilityClass):
            raise TypeError("classification must be a ReliabilityClass")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")
        if not isinstance(self.observation, ExecutionObservation):
            raise TypeError("observation must be an ExecutionObservation")
        if self.observation.execution_id != self.execution_id:
            raise ValueError("observation execution_id must match assessment execution_id")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")

    def to_context(self) -> dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "classification": self.classification.value,
            "reason": self.reason,
            "observation": self.observation.to_context(),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class RecoveryRequest:
    """Explicit recovery intent; never an executable or authorized request."""

    execution_id: str
    action: RecoveryAction
    reason: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.execution_id, str) or not self.execution_id.strip():
            raise ValueError("execution_id must be a non-empty string")
        if not isinstance(self.action, RecoveryAction):
            raise TypeError("action must be a RecoveryAction")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")

    def to_context(self) -> dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "action": self.action.value,
            "reason": self.reason,
            "metadata": dict(self.metadata),
            "authorization_granted": False,
        }


@dataclass(frozen=True)
class ReliabilityDecision:
    """Assessment plus bounded recovery intent."""

    assessment: ReliabilityAssessment
    request: RecoveryRequest

    def __post_init__(self) -> None:
        if not isinstance(self.assessment, ReliabilityAssessment):
            raise TypeError("assessment must be a ReliabilityAssessment")
        if not isinstance(self.request, RecoveryRequest):
            raise TypeError("request must be a RecoveryRequest")
        if self.request.execution_id != self.assessment.execution_id:
            raise ValueError("recovery request execution identity must match assessment")

    def to_context(self) -> dict[str, Any]:
        return {
            "assessment": self.assessment.to_context(),
            "recovery_request": self.request.to_context(),
        }


class ReliabilityClassifier:
    """Classify explicit execution conditions without inferring hidden state."""

    def assess(
        self,
        observation: ExecutionObservation,
        signal: ReliabilitySignal | None = None,
    ) -> ReliabilityAssessment:
        if not isinstance(observation, ExecutionObservation):
            raise TypeError("observation must be an ExecutionObservation")
        signal = signal or ReliabilitySignal()

        if signal.requires_reconciliation:
            classification = ReliabilityClass.REQUIRES_RECONCILIATION
            reason = signal.reason or "explicit reconciliation is required"
        elif signal.interrupted:
            classification = ReliabilityClass.INTERRUPTED
            reason = signal.reason or "execution was explicitly interrupted"
        elif signal.partial_completion:
            classification = ReliabilityClass.PARTIAL_COMPLETION
            reason = signal.reason or "execution explicitly reported partial completion"
        elif observation.status is ExecutionStatus.NOT_ATTEMPTED:
            classification = ReliabilityClass.BLOCKED
            reason = signal.reason or "execution was not attempted"
        elif observation.status is ExecutionStatus.SUCCEEDED:
            classification = ReliabilityClass.HEALTHY
            reason = signal.reason or "execution completed successfully"
        elif observation.status is ExecutionStatus.FAILED:
            if signal.retryable_failure:
                classification = ReliabilityClass.FAILED_RETRYABLE
                reason = signal.reason or "execution failed and was explicitly marked retryable"
            else:
                classification = ReliabilityClass.FAILED_TERMINAL
                reason = signal.reason or "execution failed without an explicit retryable classification"
        else:
            classification = ReliabilityClass.REQUIRES_RECONCILIATION
            reason = signal.reason or "execution status requires reconciliation"

        return ReliabilityAssessment(
            execution_id=observation.execution_id,
            classification=classification,
            reason=reason,
            observation=observation,
            metadata=dict(signal.metadata),
        )


class RecoveryPlanner:
    """Produce bounded recovery intent from a reliability assessment."""

    def __init__(self, max_recovery_requests: int = 1) -> None:
        if (
            not isinstance(max_recovery_requests, int)
            or isinstance(max_recovery_requests, bool)
            or max_recovery_requests <= 0
        ):
            raise ValueError("max_recovery_requests must be a positive integer")
        self._max_recovery_requests = max_recovery_requests

    @property
    def max_recovery_requests(self) -> int:
        return self._max_recovery_requests

    def plan(
        self,
        assessment: ReliabilityAssessment,
        recovery_count: int = 0,
    ) -> ReliabilityDecision:
        if not isinstance(assessment, ReliabilityAssessment):
            raise TypeError("assessment must be a ReliabilityAssessment")
        if (
            not isinstance(recovery_count, int)
            or isinstance(recovery_count, bool)
            or recovery_count < 0
        ):
            raise ValueError("recovery_count must be a non-negative integer")

        if assessment.classification is ReliabilityClass.HEALTHY:
            action = RecoveryAction.NONE
            reason = "no recovery is required after a healthy execution"
        elif assessment.classification in {
            ReliabilityClass.REQUIRES_RECONCILIATION,
            ReliabilityClass.PARTIAL_COMPLETION,
            ReliabilityClass.INTERRUPTED,
        }:
            action = RecoveryAction.RECONCILE
            reason = "execution state must be reconciled before another action is considered"
        elif assessment.classification is ReliabilityClass.FAILED_RETRYABLE:
            if recovery_count >= self._max_recovery_requests:
                action = RecoveryAction.STOP
                reason = "bounded recovery request budget is exhausted"
            else:
                action = RecoveryAction.REQUEST_FRESH_AUTHORIZATION
                reason = "a retry requires a fresh M7 authority path"
        elif assessment.classification is ReliabilityClass.BLOCKED:
            action = RecoveryAction.STOP
            reason = "blocked execution cannot be retried by the reliability layer"
        else:
            action = RecoveryAction.STOP
            reason = "terminal failure must stop rather than trigger implicit recovery"

        request = RecoveryRequest(
            execution_id=assessment.execution_id,
            action=action,
            reason=reason,
            metadata={
                "recovery_count": recovery_count,
                "max_recovery_requests": self._max_recovery_requests,
                "authority_required_for_new_action": True,
                "recovery_planner": "m8.6",
            },
        )
        return ReliabilityDecision(assessment=assessment, request=request)
