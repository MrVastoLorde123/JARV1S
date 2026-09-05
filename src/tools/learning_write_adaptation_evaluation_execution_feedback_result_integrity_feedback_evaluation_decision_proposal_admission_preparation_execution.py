"""Execution attempt boundary after M22.49 preparation.

M22.50 converts exactly one immutable preparation artifact into an immutable
execution request and invokes a replaceable applier. Execution is an attempt
and observation, not authorization or truth.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping, Protocol
from enum import Enum

from .learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal_admission_preparation import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparation,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionError(ValueError):
    """Raised when the M22.50 execution contract is invalid."""


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionRequest:
    execution_id: str
    preparation_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    evaluation_id: str
    feedback_id: str
    outcome_id: str
    source_admission_id: str
    source_proposal_id: str
    decision_source_evaluation_id: str
    evaluation_id_from_feedback: str
    source_feedback_id: str
    candidate_id: str
    source_candidate_id: str
    execution_source_id: str
    source_execution_id: str
    domain: str
    source_policy_id: str
    policy_id: str
    payload: Mapping[str, Any]
    evidence: Mapping[str, Any]
    provenance: Mapping[str, str]
    execution_authorized: bool = False
    authorization_granted: bool = False
    execution_requested: bool = False
    retry_requested: bool = False
    revocation_requested: bool = False
    memory_mutation_allowed: bool = False
    authority_granted: bool = False

    def __post_init__(self) -> None:
        for name in (
            "execution_id", "preparation_id", "admission_id", "proposal_id", "decision_id",
            "evaluation_id", "feedback_id", "outcome_id", "source_admission_id", "source_proposal_id",
            "decision_source_evaluation_id", "evaluation_id_from_feedback", "source_feedback_id",
            "candidate_id", "source_candidate_id", "execution_source_id", "source_execution_id",
            "domain", "source_policy_id", "policy_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionError(f"{name} must be a non-empty string")
        for name in ("payload", "evidence"):
            if not isinstance(getattr(self, name), Mapping):
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionError(f"{name} must be a mapping")
        if not isinstance(self.provenance, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionError("provenance must be a mapping")
        if not all(isinstance(k, str) and k.strip() and isinstance(v, str) and v.strip() for k, v in self.provenance.items()):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionError("provenance must contain non-empty string keys and values")
        if any((self.execution_authorized, self.authorization_granted, self.execution_requested, self.retry_requested, self.revocation_requested, self.memory_mutation_allowed, self.authority_granted)):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionError("execution request cannot grant authorization, retry, revocation, memory mutation, or general authority")
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "evidence", _freeze(self.evidence))
        object.__setattr__(self, "provenance", _freeze(self.provenance))


@dataclass(frozen=True)
class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResult:
    execution_id: str
    preparation_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    evaluation_id: str
    feedback_id: str
    outcome_id: str
    source_admission_id: str
    source_proposal_id: str
    decision_source_evaluation_id: str
    evaluation_id_from_feedback: str
    source_feedback_id: str
    candidate_id: str
    source_candidate_id: str
    execution_source_id: str
    source_execution_id: str
    domain: str
    source_policy_id: str
    policy_id: str
    status: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionStatus
    execution_result: Any = None
    reason: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "execution_id", "preparation_id", "admission_id", "proposal_id", "decision_id",
            "evaluation_id", "feedback_id", "outcome_id", "source_admission_id", "source_proposal_id",
            "decision_source_evaluation_id", "evaluation_id_from_feedback", "source_feedback_id",
            "candidate_id", "source_candidate_id", "execution_source_id", "source_execution_id",
            "domain", "source_policy_id", "policy_id",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionError(f"{name} must be a non-empty string")
        if not isinstance(self.status, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionStatus):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionError("invalid execution status")
        if self.status is LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionStatus.FAILED:
            if not isinstance(self.reason, str) or not self.reason.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionError("failed execution requires a non-empty reason")
        if self.status is LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionStatus.COMPLETED and self.reason is not None:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionError("completed execution cannot carry a failure reason")
        object.__setattr__(self, "execution_result", _freeze(self.execution_result))


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionApplier(Protocol):
    def apply(self, request: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionRequest) -> Any:
        ...


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionService:
    def __init__(self, applier: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionApplier):
        self._applier = applier

    def execute(self, preparation: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparation) -> LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResult:
        if not isinstance(preparation, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparation):
            raise TypeError("preparation must be a LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparation")
        self._validate(preparation)
        request = self._request(preparation)
        execution_id = request.execution_id
        try:
            observed = self._applier.apply(request)
        except Exception as exc:
            return self._result(request, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionStatus.FAILED, reason=str(exc) or exc.__class__.__name__)
        return self._result(request, LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionStatus.COMPLETED, execution_result=observed)

    @staticmethod
    def _validate(preparation: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparation) -> None:
        if any((preparation.execution_authorized, preparation.execution_started, preparation.retry_requested, preparation.revocation_requested, preparation.memory_mutation_allowed, preparation.authority_granted)):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionError("preparation carries forbidden authority or started state")

    @classmethod
    def _request(cls, preparation: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparation):
        serialized = json.dumps({"preparation_id": preparation.preparation_id, "admission_id": preparation.admission_id, "proposal_id": preparation.proposal_id, "policy_id": preparation.policy_id}, sort_keys=True, separators=(",", ":")).encode("utf-8")
        execution_id = "adaptation-evaluation-execution-feedback-result-integrity-preparation-execution-" + hashlib.sha256(serialized).hexdigest()[:24]
        return LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionRequest(
            execution_id=execution_id,
            preparation_id=preparation.preparation_id,
            admission_id=preparation.admission_id,
            proposal_id=preparation.proposal_id,
            decision_id=preparation.decision_id,
            evaluation_id=preparation.evaluation_id,
            feedback_id=preparation.feedback_id,
            outcome_id=preparation.outcome_id,
            source_admission_id=preparation.source_admission_id,
            source_proposal_id=preparation.source_proposal_id,
            decision_source_evaluation_id=preparation.decision_source_evaluation_id,
            evaluation_id_from_feedback=preparation.evaluation_id_from_feedback,
            source_feedback_id=preparation.source_feedback_id,
            candidate_id=preparation.candidate_id,
            source_candidate_id=preparation.source_candidate_id,
            execution_source_id=preparation.execution_source_id,
            source_execution_id=preparation.source_execution_id,
            domain=preparation.domain,
            source_policy_id=preparation.source_policy_id,
            policy_id=preparation.policy_id,
            payload=preparation.payload,
            evidence=preparation.evidence,
            provenance=preparation.provenance,
        )

    @staticmethod
    def _result(request, status, execution_result=None, reason=None):
        return LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationExecutionResult(
            execution_id=request.execution_id,
            preparation_id=request.preparation_id,
            admission_id=request.admission_id,
            proposal_id=request.proposal_id,
            decision_id=request.decision_id,
            evaluation_id=request.evaluation_id,
            feedback_id=request.feedback_id,
            outcome_id=request.outcome_id,
            source_admission_id=request.source_admission_id,
            source_proposal_id=request.source_proposal_id,
            decision_source_evaluation_id=request.decision_source_evaluation_id,
            evaluation_id_from_feedback=request.evaluation_id_from_feedback,
            source_feedback_id=request.source_feedback_id,
            candidate_id=request.candidate_id,
            source_candidate_id=request.source_candidate_id,
            execution_source_id=request.execution_source_id,
            source_execution_id=request.source_execution_id,
            domain=request.domain,
            source_policy_id=request.source_policy_id,
            policy_id=request.policy_id,
            status=status,
            execution_result=execution_result,
            reason=reason,
        )
