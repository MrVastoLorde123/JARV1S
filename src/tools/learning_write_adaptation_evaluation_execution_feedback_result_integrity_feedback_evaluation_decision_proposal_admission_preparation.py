"""Preparation boundary after the M22.48 future-adaptation admission.

An admitted M22.48 artifact may cross into immutable preparation state for a
later execution boundary. Preparation is inert handoff state: it cannot
authorize, start, retry, revoke, mutate memory, or grant authority.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from .learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal_admission import (
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmission,
    LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationError(ValueError):
    """Raised when the M22.49 preparation contract is invalid."""


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
class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationContext:
    """Immutable M22.49 inputs: one exact M22.48 admission."""

    admission: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmission
    related_context: Mapping[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if not isinstance(
            self.admission,
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmission,
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationError(
                "admission must be a LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmission"
            )
        related = {} if self.related_context is None else self.related_context
        if not isinstance(related, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationError(
                "related_context must be a mapping"
            )
        object.__setattr__(self, "related_context", _freeze(related))


@dataclass(frozen=True)
class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparation:
    """Immutable preparation artifact derived from exactly one admitted M22.48 artifact."""

    preparation_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    evaluation_id: str
    feedback_id: str
    outcome_id: str
    execution_id: str
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
    execution_started: bool = False
    retry_requested: bool = False
    revocation_requested: bool = False
    memory_mutation_allowed: bool = False
    authority_granted: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "preparation_id", "admission_id", "proposal_id", "decision_id", "evaluation_id",
            "feedback_id", "outcome_id", "execution_id", "source_admission_id", "source_proposal_id",
            "decision_source_evaluation_id", "evaluation_id_from_feedback", "source_feedback_id",
            "candidate_id", "source_candidate_id", "execution_source_id", "source_execution_id",
            "domain", "source_policy_id", "policy_id",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationError(
                    f"{field_name} must be a non-empty string"
                )
        for field_name in ("payload", "evidence"):
            if not isinstance(getattr(self, field_name), Mapping):
                raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationError(
                    f"{field_name} must be a mapping"
                )
        if not isinstance(self.provenance, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationError(
                "provenance must be a mapping"
            )
        if not all(
            isinstance(key, str) and key.strip() and isinstance(value, str) and value.strip()
            for key, value in self.provenance.items()
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationError(
                "provenance must contain non-empty string keys and values"
            )
        if (
            self.execution_authorized
            or self.execution_started
            or self.retry_requested
            or self.revocation_requested
            or self.memory_mutation_allowed
            or self.authority_granted
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationError(
                "preparation cannot authorize, start, retry, revoke, mutate memory, or grant authority"
            )
        if not self.payload:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationError(
                "preparation payload cannot be empty"
            )
        if not self.evidence:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationError(
                "preparation evidence cannot be empty"
            )
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "evidence", _freeze(self.evidence))
        object.__setattr__(self, "provenance", _freeze(self.provenance))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal_admission_preparation_id": self.preparation_id,
            "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal_admission_id": self.admission_id,
            "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_proposal_id": self.proposal_id,
            "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_decision_id": self.decision_id,
            "learning_write_adaptation_evaluation_execution_feedback_result_integrity_feedback_evaluation_id": self.evaluation_id,
            "learning_write_adaptation_evaluation_execution_feedback_id": self.feedback_id,
            "learning_write_adaptation_evaluation_execution_outcome_id": self.outcome_id,
            "learning_write_adaptation_evaluation_execution_id": self.execution_id,
            "learning_write_adaptation_evaluation_execution_source_admission_id": self.source_admission_id,
            "learning_write_adaptation_evaluation_proposal_source_id": self.source_proposal_id,
            "learning_write_adaptation_evaluation_feedback_decision_source_id": self.decision_source_evaluation_id,
            "learning_write_adaptation_evaluation_execution_feedback_source_evaluation_id": self.evaluation_id_from_feedback,
            "learning_write_adaptation_evaluation_execution_feedback_source_feedback_id": self.source_feedback_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_evaluation_execution_source_id": self.execution_source_id,
            "learning_write_adaptation_source_execution_id": self.source_execution_id,
            "learning_write_adaptation_domain": self.domain,
            "learning_write_adaptation_source_policy_id": self.source_policy_id,
            "learning_write_adaptation_evaluation_execution_policy_id": self.policy_id,
            "execution_prepared": True,
            "execution_authorized": False,
            "execution_started": False,
            "retry_requested": False,
            "revocation_requested": False,
            "memory_mutation_allowed": False,
            "authority_granted": False,
            "payload": dict(self.payload),
            "evidence": dict(self.evidence),
            "provenance": dict(self.provenance),
        }


class LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationService:
    """Prepare an admitted M22.48 artifact without authorizing or executing it."""

    def prepare(
        self,
        context: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationContext,
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparation:
        if not isinstance(
            context,
            LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationContext,
        ):
            raise TypeError(
                "context must be a LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationContext"
            )
        admission = context.admission
        if admission.status is not LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionStatus.ADMITTED:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationError(
                "only admitted M22.48 proposals may cross into preparation"
            )

        if (
            admission.execution_authorized
            or admission.authorization_granted
            or admission.execution_requested
            or admission.retry_requested
            or admission.revocation_requested
            or admission.memory_mutation_allowed
            or admission.authority_granted
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparationError(
                "admission carries forbidden authority"
            )

        payload = admission.proposal
        evidence = admission.evidence
        provenance = admission.provenance
        preparation_id = self._preparation_id(admission)
        return LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmissionPreparation(
            preparation_id=preparation_id,
            admission_id=admission.admission_id,
            proposal_id=admission.proposal_id,
            decision_id=admission.decision_id,
            evaluation_id=admission.evaluation_id,
            feedback_id=admission.feedback_id,
            outcome_id=admission.outcome_id,
            execution_id=admission.execution_id,
            source_admission_id=admission.source_admission_id,
            source_proposal_id=admission.source_proposal_id,
            decision_source_evaluation_id=admission.decision_source_evaluation_id,
            evaluation_id_from_feedback=admission.evaluation_id_from_feedback,
            source_feedback_id=admission.source_feedback_id,
            candidate_id=admission.candidate_id,
            source_candidate_id=admission.source_candidate_id,
            execution_source_id=admission.execution_source_id,
            source_execution_id=admission.source_execution_id,
            domain=admission.domain,
            source_policy_id=admission.source_policy_id,
            policy_id=admission.policy_id,
            payload=payload,
            evidence=evidence,
            provenance=provenance,
        )

    @staticmethod
    def _preparation_id(
        admission: LearningWriteAdaptationEvaluationExecutionFeedbackResultIntegrityFeedbackEvaluationDecisionProposalAdmission,
    ) -> str:
        serialized = json.dumps(
            {
                "admission_id": admission.admission_id,
                "proposal_id": admission.proposal_id,
                "decision_id": admission.decision_id,
                "evaluation_id": admission.evaluation_id,
                "feedback_id": admission.feedback_id,
                "outcome_id": admission.outcome_id,
                "execution_id": admission.execution_id,
                "policy_id": admission.policy_id,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return "adaptation-evaluation-execution-feedback-result-integrity-proposal-admission-preparation-" + hashlib.sha256(serialized).hexdigest()[:24]
