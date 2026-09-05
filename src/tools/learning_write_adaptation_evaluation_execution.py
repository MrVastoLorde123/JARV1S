"""Execution boundary for prepared adaptation-evaluation proposals."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Mapping, Protocol

from .learning_write_adaptation_evaluation_execution_preparation import (
    LearningWriteAdaptationEvaluationExecutionPreparation,
)


class LearningWriteAdaptationEvaluationExecutionError(ValueError):
    """Raised when the prepared adaptation execution contract is invalid."""


class LearningWriteAdaptationEvaluationExecutionStatus(str, Enum):
    """Normalized result of one prepared adaptation execution."""

    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class LearningWriteAdaptationEvaluationExecutionRequest:
    """Immutable request derived from one exact preparation artifact."""

    execution_id: str
    preparation_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    evaluation_id: str
    feedback_id: str
    source_feedback_id: str
    candidate_id: str
    source_candidate_id: str
    source_execution_id: str
    domain: str
    policy_id: str
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        for field_name, value in (
            ("execution_id", self.execution_id), ("preparation_id", self.preparation_id),
            ("admission_id", self.admission_id), ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id), ("evaluation_id", self.evaluation_id),
            ("feedback_id", self.feedback_id), ("source_feedback_id", self.source_feedback_id),
            ("candidate_id", self.candidate_id), ("source_candidate_id", self.source_candidate_id),
            ("source_execution_id", self.source_execution_id), ("domain", self.domain),
            ("policy_id", self.policy_id),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionError(f"{field_name} must be a non-empty string")
        if not isinstance(self.payload, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionError("payload must be a mapping")


@dataclass(frozen=True)
class LearningWriteAdaptationEvaluationExecutionResult:
    """Immutable execution result bound to one exact prepared request."""

    execution_id: str
    preparation_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    evaluation_id: str
    feedback_id: str
    source_feedback_id: str
    candidate_id: str
    source_candidate_id: str
    source_execution_id: str
    domain: str
    policy_id: str
    status: LearningWriteAdaptationEvaluationExecutionStatus
    execution_result: Any = None
    reason: str | None = None

    def __post_init__(self) -> None:
        for field_name, value in (
            ("execution_id", self.execution_id), ("preparation_id", self.preparation_id),
            ("admission_id", self.admission_id), ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id), ("evaluation_id", self.evaluation_id),
            ("feedback_id", self.feedback_id), ("source_feedback_id", self.source_feedback_id),
            ("candidate_id", self.candidate_id), ("source_candidate_id", self.source_candidate_id),
            ("source_execution_id", self.source_execution_id), ("domain", self.domain),
            ("policy_id", self.policy_id),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionError(f"{field_name} must be a non-empty string")
        if not isinstance(self.status, LearningWriteAdaptationEvaluationExecutionStatus):
            raise LearningWriteAdaptationEvaluationExecutionError("status must be a LearningWriteAdaptationEvaluationExecutionStatus member")
        if self.status is LearningWriteAdaptationEvaluationExecutionStatus.COMPLETED:
            if self.reason is not None:
                raise LearningWriteAdaptationEvaluationExecutionError("a completed execution cannot contain a failure reason")
        elif not isinstance(self.reason, str) or not self.reason.strip():
            raise LearningWriteAdaptationEvaluationExecutionError("a failed execution requires a reason")

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_evaluation_execution_id": self.execution_id,
            "learning_write_adaptation_evaluation_execution_preparation_id": self.preparation_id,
            "learning_write_adaptation_evaluation_proposal_admission_id": self.admission_id,
            "learning_write_adaptation_evaluation_proposal_id": self.proposal_id,
            "learning_write_adaptation_evaluation_decision_id": self.decision_id,
            "learning_write_adaptation_feedback_evaluation_id": self.evaluation_id,
            "learning_write_adaptation_feedback_id": self.feedback_id,
            "learning_write_adaptation_source_feedback_id": self.source_feedback_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_source_execution_id": self.source_execution_id,
            "learning_write_adaptation_domain": self.domain,
            "learning_write_adaptation_evaluation_execution_policy_id": self.policy_id,
            "learning_write_adaptation_evaluation_execution_status": self.status.value,
            "execution_completed": self.status is LearningWriteAdaptationEvaluationExecutionStatus.COMPLETED,
            "authorization_granted": False,
            "retry_requested": False,
            "revocation_requested": False,
            "memory_mutation_allowed": False,
        }


class LearningWriteAdaptationEvaluationExecutionApplier(Protocol):
    """Replaceable applier for the exact prepared execution request."""

    def apply(self, request: LearningWriteAdaptationEvaluationExecutionRequest) -> Any:
        """Apply the exact prepared adaptation execution request."""


class LearningWriteAdaptationEvaluationExecutionService:
    """Execute one exact M22.33 preparation artifact through an applier."""

    def __init__(self, applier: LearningWriteAdaptationEvaluationExecutionApplier) -> None:
        if not callable(getattr(applier, "apply", None)):
            raise TypeError("applier must provide an apply(request) method")
        self._applier = applier

    def execute(self, preparation: LearningWriteAdaptationEvaluationExecutionPreparation) -> LearningWriteAdaptationEvaluationExecutionResult:
        if not isinstance(preparation, LearningWriteAdaptationEvaluationExecutionPreparation):
            raise TypeError("preparation must be a LearningWriteAdaptationEvaluationExecutionPreparation")
        if preparation.execution_authorized or preparation.execution_started:
            raise LearningWriteAdaptationEvaluationExecutionError("preparation cannot carry authorization or already be started")
        if preparation.retry_requested or preparation.revocation_requested:
            raise LearningWriteAdaptationEvaluationExecutionError("preparation cannot request retry or revocation")
        if preparation.memory_mutation_allowed:
            raise LearningWriteAdaptationEvaluationExecutionError("preparation cannot permit memory mutation")

        execution_id = self._execution_id(preparation)
        request = LearningWriteAdaptationEvaluationExecutionRequest(
            execution_id=execution_id, preparation_id=preparation.preparation_id,
            admission_id=preparation.admission_id, proposal_id=preparation.proposal_id,
            decision_id=preparation.decision_id, evaluation_id=preparation.evaluation_id,
            feedback_id=preparation.feedback_id, source_feedback_id=preparation.source_feedback_id,
            candidate_id=preparation.candidate_id, source_candidate_id=preparation.source_candidate_id,
            source_execution_id=preparation.source_execution_id, domain=preparation.domain,
            policy_id=preparation.policy_id, payload=preparation.payload,
        )
        try:
            result = self._applier.apply(request)
        except Exception as exc:  # noqa: BLE001
            return LearningWriteAdaptationEvaluationExecutionResult(
                execution_id=execution_id, preparation_id=preparation.preparation_id,
                admission_id=preparation.admission_id, proposal_id=preparation.proposal_id,
                decision_id=preparation.decision_id, evaluation_id=preparation.evaluation_id,
                feedback_id=preparation.feedback_id, source_feedback_id=preparation.source_feedback_id,
                candidate_id=preparation.candidate_id, source_candidate_id=preparation.source_candidate_id,
                source_execution_id=preparation.source_execution_id, domain=preparation.domain,
                policy_id=preparation.policy_id,
                status=LearningWriteAdaptationEvaluationExecutionStatus.FAILED,
                reason=str(exc) or exc.__class__.__name__,
            )
        return LearningWriteAdaptationEvaluationExecutionResult(
            execution_id=execution_id, preparation_id=preparation.preparation_id,
            admission_id=preparation.admission_id, proposal_id=preparation.proposal_id,
            decision_id=preparation.decision_id, evaluation_id=preparation.evaluation_id,
            feedback_id=preparation.feedback_id, source_feedback_id=preparation.source_feedback_id,
            candidate_id=preparation.candidate_id, source_candidate_id=preparation.source_candidate_id,
            source_execution_id=preparation.source_execution_id, domain=preparation.domain,
            policy_id=preparation.policy_id,
            status=LearningWriteAdaptationEvaluationExecutionStatus.COMPLETED,
            execution_result=result,
        )

    @staticmethod
    def _execution_id(preparation: LearningWriteAdaptationEvaluationExecutionPreparation) -> str:
        raw = json.dumps({
            "preparation_id": preparation.preparation_id, "admission_id": preparation.admission_id,
            "proposal_id": preparation.proposal_id, "decision_id": preparation.decision_id,
            "evaluation_id": preparation.evaluation_id, "feedback_id": preparation.feedback_id,
            "source_feedback_id": preparation.source_feedback_id, "candidate_id": preparation.candidate_id,
            "source_candidate_id": preparation.source_candidate_id, "source_execution_id": preparation.source_execution_id,
            "domain": preparation.domain, "policy_id": preparation.policy_id, "payload": dict(preparation.payload),
        }, sort_keys=True, default=repr, separators=(",", ":")).encode("utf-8")
        return f"adaptation-evaluation-execution-{hashlib.sha256(raw).hexdigest()[:24]}"
