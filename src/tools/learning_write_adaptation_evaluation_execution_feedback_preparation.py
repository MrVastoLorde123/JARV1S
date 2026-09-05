"""Preparation boundary after future-adaptation execution-feedback proposal admission.

An admitted M22.40 proposal may be converted into immutable preparation state
for a later future-execution boundary. Preparation preserves exact lineage and
payload but does not authorize, start, retry, revoke, or mutate memory.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from .learning_write_adaptation_evaluation_execution_feedback_proposal_admission import (
    LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmission,
    LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionStatus,
)
from .learning_write_adaptation_evaluation_execution_feedback_proposal import (
    LearningWriteAdaptationEvaluationExecutionFeedbackProposal,
)


class LearningWriteAdaptationEvaluationExecutionFeedbackPreparationError(ValueError):
    """Raised when the M22.41 preparation contract is invalid."""


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
class LearningWriteAdaptationEvaluationExecutionFeedbackPreparationContext:
    """Immutable inputs for M22.41 future execution preparation."""

    proposal: LearningWriteAdaptationEvaluationExecutionFeedbackProposal
    admission: LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmission

    def __post_init__(self) -> None:
        if not isinstance(
            self.proposal,
            LearningWriteAdaptationEvaluationExecutionFeedbackProposal,
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackPreparationError(
                "proposal must be a LearningWriteAdaptationEvaluationExecutionFeedbackProposal"
            )
        if not isinstance(
            self.admission,
            LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmission,
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackPreparationError(
                "admission must be a LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmission"
            )


@dataclass(frozen=True)
class LearningWriteAdaptationEvaluationExecutionFeedbackPreparation:
    """Immutable preparation artifact for future adaptation execution."""

    preparation_id: str
    admission_id: str
    proposal_id: str
    decision_id: str
    evaluation_id: str
    decision_source_evaluation_id: str
    feedback_id: str
    source_feedback_id: str
    candidate_id: str
    source_candidate_id: str
    execution_id: str
    source_execution_id: str
    source_admission_id: str
    proposal_source_id: str
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
        for field_name, value in (
            ("preparation_id", self.preparation_id),
            ("admission_id", self.admission_id),
            ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id),
            ("evaluation_id", self.evaluation_id),
            ("decision_source_evaluation_id", self.decision_source_evaluation_id),
            ("feedback_id", self.feedback_id),
            ("source_feedback_id", self.source_feedback_id),
            ("candidate_id", self.candidate_id),
            ("source_candidate_id", self.source_candidate_id),
            ("execution_id", self.execution_id),
            ("source_execution_id", self.source_execution_id),
            ("source_admission_id", self.source_admission_id),
            ("proposal_source_id", self.proposal_source_id),
            ("domain", self.domain),
            ("source_policy_id", self.source_policy_id),
            ("policy_id", self.policy_id),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionFeedbackPreparationError(
                    f"{field_name} must be a non-empty string"
                )
        for field_name, value in (("payload", self.payload), ("evidence", self.evidence)):
            if not isinstance(value, Mapping):
                raise LearningWriteAdaptationEvaluationExecutionFeedbackPreparationError(
                    f"{field_name} must be a mapping"
                )
        if not isinstance(self.provenance, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackPreparationError(
                "provenance must be a mapping"
            )
        if not all(
            isinstance(key, str)
            and key.strip()
            and isinstance(value, str)
            and value.strip()
            for key, value in self.provenance.items()
        ):
            raise LearningWriteAdaptationEvaluationExecutionFeedbackPreparationError(
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
            raise LearningWriteAdaptationEvaluationExecutionFeedbackPreparationError(
                "preparation cannot authorize, start, retry, revoke, mutate memory, or grant authority"
            )
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "evidence", _freeze(self.evidence))
        object.__setattr__(self, "provenance", _freeze(self.provenance))

    def to_context(self) -> dict[str, object]:
        return {
            "learning_write_adaptation_evaluation_execution_feedback_preparation_id": self.preparation_id,
            "learning_write_adaptation_evaluation_execution_feedback_proposal_admission_id": self.admission_id,
            "learning_write_adaptation_evaluation_execution_feedback_proposal_id": self.proposal_id,
            "learning_write_adaptation_evaluation_execution_feedback_decision_id": self.decision_id,
            "learning_write_adaptation_evaluation_execution_feedback_evaluation_id": self.evaluation_id,
            "learning_write_adaptation_feedback_evaluation_id": self.decision_source_evaluation_id,
            "learning_write_adaptation_evaluation_execution_feedback_id": self.feedback_id,
            "learning_write_adaptation_source_feedback_id": self.source_feedback_id,
            "learning_write_adaptation_candidate_id": self.candidate_id,
            "learning_candidate_id": self.source_candidate_id,
            "learning_write_adaptation_evaluation_execution_id": self.execution_id,
            "learning_write_adaptation_source_execution_id": self.source_execution_id,
            "learning_write_adaptation_evaluation_execution_source_admission_id": self.source_admission_id,
            "learning_write_adaptation_evaluation_proposal_id": self.proposal_source_id,
            "learning_write_adaptation_domain": self.domain,
            "learning_write_adaptation_source_policy_id": self.source_policy_id,
            "learning_write_adaptation_evaluation_execution_policy_id": self.policy_id,
            "payload": dict(self.payload),
            "evidence": dict(self.evidence),
            "provenance": dict(self.provenance),
            "execution_prepared": True,
            "execution_authorized": False,
            "execution_started": False,
            "retry_requested": False,
            "revocation_requested": False,
            "memory_mutation_allowed": False,
            "authority_granted": False,
        }


class LearningWriteAdaptationEvaluationExecutionFeedbackPreparationService:
    """Prepare an admitted M22.39 proposal without executing it."""

    def prepare(
        self,
        proposal: LearningWriteAdaptationEvaluationExecutionFeedbackProposal,
        admission: LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmission,
    ) -> LearningWriteAdaptationEvaluationExecutionFeedbackPreparation:
        if not isinstance(
            proposal,
            LearningWriteAdaptationEvaluationExecutionFeedbackProposal,
        ):
            raise TypeError(
                "proposal must be a LearningWriteAdaptationEvaluationExecutionFeedbackProposal"
            )
        if not isinstance(
            admission,
            LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmission,
        ):
            raise TypeError(
                "admission must be a LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmission"
            )
        if admission.status is not LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmissionStatus.ADMITTED:
            raise LearningWriteAdaptationEvaluationExecutionFeedbackPreparationError(
                "only admitted future-adaptation execution-feedback proposals may be prepared for execution"
            )

        checks = (
            ("proposal", admission.proposal_id, proposal.proposal_id),
            ("decision", admission.decision_id, proposal.decision_id),
            ("evaluation", admission.evaluation_id, proposal.evaluation_id),
            (
                "decision source evaluation",
                admission.decision_source_evaluation_id,
                proposal.decision_source_evaluation_id,
            ),
            ("feedback", admission.feedback_id, proposal.feedback_id),
            ("source feedback", admission.source_feedback_id, proposal.source_feedback_id),
            ("candidate", admission.candidate_id, proposal.candidate_id),
            ("source candidate", admission.source_candidate_id, proposal.source_candidate_id),
            ("execution", admission.execution_id, proposal.execution_id),
            ("source execution", admission.source_execution_id, proposal.source_execution_id),
            ("preparation source admission", admission.source_admission_id, proposal.admission_id),
            ("preparation proposal source", admission.proposal_source_id, proposal.proposal_source_id),
            ("domain", admission.domain, proposal.domain),
            ("source policy", admission.source_policy_id, proposal.policy_id),
        )
        for label, actual, expected in checks:
            if actual != expected:
                raise LearningWriteAdaptationEvaluationExecutionFeedbackPreparationError(
                    f"admission {label} identity does not match proposal"
                )

        preparation_id = self._preparation_id(admission, proposal)
        return LearningWriteAdaptationEvaluationExecutionFeedbackPreparation(
            preparation_id=preparation_id,
            admission_id=admission.admission_id,
            proposal_id=proposal.proposal_id,
            decision_id=proposal.decision_id,
            evaluation_id=proposal.evaluation_id,
            decision_source_evaluation_id=proposal.decision_source_evaluation_id,
            feedback_id=proposal.feedback_id,
            source_feedback_id=proposal.source_feedback_id,
            candidate_id=proposal.candidate_id,
            source_candidate_id=proposal.source_candidate_id,
            execution_id=proposal.execution_id,
            source_execution_id=proposal.source_execution_id,
            source_admission_id=proposal.admission_id,
            proposal_source_id=proposal.proposal_source_id,
            domain=proposal.domain,
            source_policy_id=proposal.policy_id,
            policy_id=admission.policy_id,
            payload=proposal.proposal,
            evidence=proposal.evidence,
            provenance=proposal.provenance,
        )

    @staticmethod
    def _preparation_id(
        admission: LearningWriteAdaptationEvaluationExecutionFeedbackProposalAdmission,
        proposal: LearningWriteAdaptationEvaluationExecutionFeedbackProposal,
    ) -> str:
        payload = json.dumps(
            {
                "admission_id": admission.admission_id,
                "proposal_id": proposal.proposal_id,
                "decision_id": proposal.decision_id,
                "evaluation_id": proposal.evaluation_id,
                "decision_source_evaluation_id": proposal.decision_source_evaluation_id,
                "feedback_id": proposal.feedback_id,
                "source_feedback_id": proposal.source_feedback_id,
                "candidate_id": proposal.candidate_id,
                "source_candidate_id": proposal.source_candidate_id,
                "execution_id": proposal.execution_id,
                "source_execution_id": proposal.source_execution_id,
                "source_admission_id": proposal.admission_id,
                "proposal_source_id": proposal.proposal_source_id,
                "domain": proposal.domain,
                "source_policy_id": proposal.policy_id,
                "policy_id": admission.policy_id,
                "payload": dict(proposal.proposal),
                "evidence": dict(proposal.evidence),
                "provenance": dict(proposal.provenance),
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return (
            "adaptation-evaluation-execution-feedback-preparation-"
            f"{hashlib.sha256(payload).hexdigest()[:24]}"
        )
