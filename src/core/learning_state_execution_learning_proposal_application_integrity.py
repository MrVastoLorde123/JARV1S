"""M23.131: validate learning-proposal application integrity without executing it."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_proposal_application import (
    LearningStateExecutionLearningProposalApplication,
)
from src.core.learning_state_execution_learning_signal import LearningStateExecutionLearningSignalKind


class LearningStateExecutionLearningProposalApplicationIntegrityError(RuntimeError):
    """Raised when application-integrity evidence cannot be formed safely."""


class LearningStateExecutionLearningProposalApplicationIntegrityStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class LearningStateExecutionLearningProposalApplicationIntegrity:
    """Immutable evidence about the structural integrity of one learning-proposal application."""

    integrity_id: str
    application_id: str
    decision_id: str
    proposal_id: str
    eligibility_id: str
    source_integrity_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    outcome_id: str
    attempt_id: str
    admission_id: str
    validation_id: str
    use_id: str
    request_id: str
    interpretation_id: str
    source_request_id: str
    read_validation_id: str
    read_id: str
    consumption_request_id: str
    source_validation_id: str
    transition_id: str
    evidence_id: str
    state_key: str
    transition_fingerprint: str
    source_application_fingerprint: str
    computed_application_fingerprint: str
    confidence: float
    consumer_id: str
    execution_target_id: str
    execution_purpose: str
    objective: str
    evaluator_id: str
    evaluation_purpose: str
    signal_kind: LearningStateExecutionLearningSignalKind
    signal_purpose: str
    learner_id: str
    eligibility_purpose: str
    proposer_id: str
    proposal_purpose: str
    proposed_change: Any
    proposal_rationale: Any
    decision_maker_id: str
    decision_purpose: str
    decision_rationale: Any
    applier_id: str
    application_purpose: str
    application_rationale: Any
    application_evidence: Any
    application_status: Any
    status: LearningStateExecutionLearningProposalApplicationIntegrityStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "integrity_id", "application_id", "decision_id", "proposal_id", "eligibility_id", "source_integrity_id",
            "signal_id", "evaluation_id", "feedback_id", "outcome_id", "attempt_id", "admission_id", "validation_id",
            "use_id", "request_id", "interpretation_id", "source_request_id", "read_validation_id", "read_id",
            "consumption_request_id", "source_validation_id", "transition_id", "evidence_id", "state_key",
            "consumer_id", "execution_target_id", "execution_purpose", "objective", "evaluator_id", "evaluation_purpose",
            "signal_purpose", "learner_id", "eligibility_purpose", "proposer_id", "proposal_purpose", "decision_maker_id",
            "decision_purpose", "applier_id", "application_purpose",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        if not isinstance(self.signal_kind, LearningStateExecutionLearningSignalKind):
            raise TypeError("signal_kind must be a learning-signal kind")
        if not isinstance(self.status, LearningStateExecutionLearningProposalApplicationIntegrityStatus):
            raise TypeError("status must be a learning-proposal application integrity status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        if self.status is LearningStateExecutionLearningProposalApplicationIntegrityStatus.VALID:
            for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
                value = getattr(self, name)
                if len(value) != 64:
                    raise ValueError("learning proposal application integrity requires SHA-256 fingerprints")
        object.__setattr__(self, "proposed_change", _freeze(self.proposed_change))
        object.__setattr__(self, "proposal_rationale", _freeze(self.proposal_rationale))
        object.__setattr__(self, "decision_rationale", _freeze(self.decision_rationale))
        object.__setattr__(self, "application_rationale", _freeze(self.application_rationale))
        object.__setattr__(self, "application_evidence", _freeze(self.application_evidence))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_valid(self) -> bool:
        return self.status is LearningStateExecutionLearningProposalApplicationIntegrityStatus.VALID

    @property
    def validates_application(self) -> bool:
        return self.is_valid

    @property
    def is_learning(self) -> bool:
        return False

    @property
    def applies_learning(self) -> bool:
        return False

    @property
    def authorizes_learning(self) -> bool:
        return False

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def authorizes_retry(self) -> bool:
        return False

    @property
    def invokes_learner(self) -> bool:
        return False

    @property
    def updates_model(self) -> bool:
        return False

    @property
    def mutates_memory(self) -> bool:
        return False

    @property
    def mutates_policy(self) -> bool:
        return False

    @property
    def invokes_executor(self) -> bool:
        return False

    @property
    def schedules_work(self) -> bool:
        return False

    @property
    def plans_work(self) -> bool:
        return False

    @property
    def establishes_truth(self) -> bool:
        return False

    @property
    def establishes_correctness(self) -> bool:
        return False

    @property
    def establishes_certainty(self) -> bool:
        return False

    @property
    def establishes_usefulness(self) -> bool:
        return False

    @property
    def proposes_adaptation(self) -> bool:
        return False


class LearningStateExecutionLearningProposalApplicationIntegrityService:
    """Validate application structure and provenance without repairing or executing it."""

    def validate(
        self,
        application: LearningStateExecutionLearningProposalApplication,
        *,
        integrity_id: str,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningProposalApplicationIntegrity:
        if type(application) is not LearningStateExecutionLearningProposalApplication:
            raise TypeError("application must be a learning-proposal application artifact")
        if not isinstance(integrity_id, str) or not integrity_id.strip():
            raise ValueError("integrity_id must be a non-empty string")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        checks.append("application_id" if application.application_id.strip() else "missing application_id")
        checks.append("decision_id" if application.decision_id.strip() else "missing decision_id")
        checks.append("proposal_id" if application.proposal_id.strip() else "missing proposal_id")
        checks.append("decision lineage" if application.decision_id == application.lineage.get("decision_id", application.decision_id) else "decision lineage mismatch")
        checks.append("application lineage" if application.application_id == application.lineage.get("application_id", application.application_id) else "application lineage mismatch")
        for name in ("transition_fingerprint", "source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(application, name)) != 64:
                checks.append(f"invalid {name}")
        valid = not any(check.startswith("missing") or check.startswith("invalid") or check.endswith("mismatch") for check in checks)
        if reasons is not None:
            final_reasons = reasons
        elif valid:
            final_reasons = ("application structure and provenance checks passed",)
        else:
            final_reasons = tuple(
                check for check in checks
                if check.startswith("missing") or check.startswith("invalid") or check.endswith("mismatch")
            )

        status = LearningStateExecutionLearningProposalApplicationIntegrityStatus.VALID if valid else LearningStateExecutionLearningProposalApplicationIntegrityStatus.INVALID
        return LearningStateExecutionLearningProposalApplicationIntegrity(
            integrity_id=integrity_id,
            application_id=application.application_id,
            decision_id=application.decision_id,
            proposal_id=application.proposal_id,
            eligibility_id=application.eligibility_id,
            source_integrity_id=application.integrity_id,
            signal_id=application.signal_id,
            evaluation_id=application.evaluation_id,
            feedback_id=application.feedback_id,
            outcome_id=application.outcome_id,
            attempt_id=application.attempt_id,
            admission_id=application.admission_id,
            validation_id=application.validation_id,
            use_id=application.use_id,
            request_id=application.request_id,
            interpretation_id=application.interpretation_id,
            source_request_id=application.source_request_id,
            read_validation_id=application.read_validation_id,
            read_id=application.read_id,
            consumption_request_id=application.consumption_request_id,
            source_validation_id=application.source_validation_id,
            transition_id=application.transition_id,
            evidence_id=application.evidence_id,
            state_key=application.state_key,
            transition_fingerprint=application.transition_fingerprint,
            source_application_fingerprint=application.source_application_fingerprint,
            computed_application_fingerprint=application.computed_application_fingerprint,
            confidence=application.confidence,
            consumer_id=application.consumer_id,
            execution_target_id=application.execution_target_id,
            execution_purpose=application.execution_purpose,
            objective=application.objective,
            evaluator_id=application.evaluator_id,
            evaluation_purpose=application.evaluation_purpose,
            signal_kind=application.signal_kind,
            signal_purpose=application.signal_purpose,
            learner_id=application.learner_id,
            eligibility_purpose=application.eligibility_purpose,
            proposer_id=application.proposer_id,
            proposal_purpose=application.proposal_purpose,
            proposed_change=application.proposed_change,
            proposal_rationale=application.proposal_rationale,
            decision_maker_id=application.decision_maker_id,
            decision_purpose=application.decision_purpose,
            decision_rationale=application.decision_rationale,
            applier_id=application.applier_id,
            application_purpose=application.application_purpose,
            application_rationale=application.application_rationale,
            application_evidence=application.application_evidence,
            application_status=application.status,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {"integrity_id": integrity_id, "application_id": application.application_id},
        )


__all__ = [
    "LearningStateExecutionLearningProposalApplicationIntegrityError",
    "LearningStateExecutionLearningProposalApplicationIntegrityStatus",
    "LearningStateExecutionLearningProposalApplicationIntegrity",
    "LearningStateExecutionLearningProposalApplicationIntegrityService",
]
