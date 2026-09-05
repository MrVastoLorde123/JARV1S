"""Preparation boundary for future adaptation execution.

An admitted adaptation-evaluation proposal may be converted into an immutable
preparation artifact for a later execution boundary. Preparation preserves
lineage and payload but does not authorize, start, retry, revoke, or mutate.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from .learning_write_adaptation_evaluation_proposal import (
    LearningWriteAdaptationEvaluationProposal,
)
from .learning_write_adaptation_evaluation_proposal_admission import (
    LearningWriteAdaptationEvaluationProposalAdmission,
    LearningWriteAdaptationEvaluationProposalAdmissionStatus,
)


class LearningWriteAdaptationEvaluationExecutionPreparationError(ValueError):
    """Raised when future adaptation execution preparation evidence is invalid."""


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
class LearningWriteAdaptationEvaluationExecutionPreparation:
    """Immutable handoff artifact for future adaptation execution."""

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
    execution_authorized: bool = False
    execution_started: bool = False
    memory_mutation_allowed: bool = False
    retry_requested: bool = False
    revocation_requested: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("preparation_id", self.preparation_id),
            ("admission_id", self.admission_id),
            ("proposal_id", self.proposal_id),
            ("decision_id", self.decision_id),
            ("evaluation_id", self.evaluation_id),
            ("feedback_id", self.feedback_id),
            ("source_feedback_id", self.source_feedback_id),
            ("candidate_id", self.candidate_id),
            ("source_candidate_id", self.source_candidate_id),
            ("source_execution_id", self.source_execution_id),
            ("domain", self.domain),
            ("policy_id", self.policy_id),
        ):
            if not isinstance(value, str) or not value.strip():
                raise LearningWriteAdaptationEvaluationExecutionPreparationError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.payload, Mapping):
            raise LearningWriteAdaptationEvaluationExecutionPreparationError(
                "payload must be a mapping"
            )
        if (
            self.execution_authorized
            or self.execution_started
            or self.memory_mutation_allowed
            or self.retry_requested
            or self.revocation_requested
        ):
            raise LearningWriteAdaptationEvaluationExecutionPreparationError(
                "preparation cannot authorize, start, mutate, retry, or revoke"
            )
        object.__setattr__(self, "payload", _freeze(self.payload))

    def to_context(self) -> dict[str, object]:
        return {
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
            "payload": dict(self.payload),
            "execution_prepared": True,
            "execution_authorized": False,
            "execution_started": False,
            "memory_mutation_allowed": False,
            "retry_requested": False,
            "revocation_requested": False,
        }


class LearningWriteAdaptationEvaluationExecutionPreparationService:
    """Prepare an admitted evaluation proposal without executing it."""

    def prepare(
        self,
        proposal: LearningWriteAdaptationEvaluationProposal,
        admission: LearningWriteAdaptationEvaluationProposalAdmission,
    ) -> LearningWriteAdaptationEvaluationExecutionPreparation:
        if not isinstance(proposal, LearningWriteAdaptationEvaluationProposal):
            raise TypeError(
                "proposal must be a LearningWriteAdaptationEvaluationProposal"
            )
        if not isinstance(
            admission,
            LearningWriteAdaptationEvaluationProposalAdmission,
        ):
            raise TypeError(
                "admission must be a LearningWriteAdaptationEvaluationProposalAdmission"
            )
        if (
            admission.status
            is not LearningWriteAdaptationEvaluationProposalAdmissionStatus.ADMITTED
        ):
            raise LearningWriteAdaptationEvaluationExecutionPreparationError(
                "only admitted evaluation proposals may be prepared for future execution"
            )

        checks = (
            ("proposal", admission.proposal_id, proposal.proposal_id),
            ("decision", admission.decision_id, proposal.decision_id),
            ("evaluation", admission.evaluation_id, proposal.evaluation_id),
            ("feedback", admission.feedback_id, proposal.feedback_id),
            ("source feedback", admission.source_feedback_id, proposal.source_feedback_id),
            ("candidate", admission.candidate_id, proposal.candidate_id),
            ("source candidate", admission.source_candidate_id, proposal.source_candidate_id),
            ("source execution", admission.execution_id, proposal.execution_id),
            ("domain", admission.domain, proposal.domain),
        )
        for label, actual, expected in checks:
            if actual != expected:
                raise LearningWriteAdaptationEvaluationExecutionPreparationError(
                    f"admission {label} identity does not match proposal"
                )

        preparation_id = self._preparation_id(admission, proposal)
        return LearningWriteAdaptationEvaluationExecutionPreparation(
            preparation_id=preparation_id,
            admission_id=admission.admission_id,
            proposal_id=proposal.proposal_id,
            decision_id=proposal.decision_id,
            evaluation_id=proposal.evaluation_id,
            feedback_id=proposal.feedback_id,
            source_feedback_id=proposal.source_feedback_id,
            candidate_id=proposal.candidate_id,
            source_candidate_id=proposal.source_candidate_id,
            source_execution_id=proposal.execution_id,
            domain=proposal.domain,
            policy_id=admission.policy_id,
            payload=proposal.proposal,
        )

    @staticmethod
    def _preparation_id(
        admission: LearningWriteAdaptationEvaluationProposalAdmission,
        proposal: LearningWriteAdaptationEvaluationProposal,
    ) -> str:
        payload = json.dumps(
            {
                "admission_id": admission.admission_id,
                "proposal_id": proposal.proposal_id,
                "decision_id": proposal.decision_id,
                "evaluation_id": proposal.evaluation_id,
                "feedback_id": proposal.feedback_id,
                "source_feedback_id": proposal.source_feedback_id,
                "candidate_id": proposal.candidate_id,
                "source_candidate_id": proposal.source_candidate_id,
                "source_execution_id": proposal.execution_id,
                "domain": proposal.domain,
                "policy_id": admission.policy_id,
                "payload": dict(proposal.proposal),
            },
            sort_keys=True,
            default=repr,
            separators=(",", ":"),
        ).encode("utf-8")
        return (
            "adaptation-evaluation-execution-preparation-"
            f"{hashlib.sha256(payload).hexdigest()[:24]}"
        )
