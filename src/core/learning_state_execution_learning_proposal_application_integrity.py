"""M23.163: verify proposal-application integrity without applying, repairing, or executing it."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.learning_state_execution_learning_proposal_application import LearningStateExecutionLearningProposalApplication


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


def _canonicalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _canonicalize(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [_canonicalize(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted((_canonicalize(item) for item in value), key=lambda item: repr(item))
    if isinstance(value, Enum):
        return value.value
    return value


def _application_fingerprint(application: "LearningStateExecutionLearningProposalApplication") -> str:
    payload = {
        "application_id": application.application_id,
        "decision_id": application.decision_id,
        "proposal_id": application.proposal_id,
        "eligibility_id": application.eligibility_id,
        "integrity_id": application.integrity_id,
        "signal_id": application.signal_id,
        "evaluation_id": application.evaluation_id,
        "feedback_id": application.feedback_id,
        "outcome_id": application.outcome_id,
        "attempt_id": application.attempt_id,
        "admission_id": application.admission_id,
        "eligibility_source_id": application.eligibility_source_id,
        "handling_id": application.handling_id,
        "consumption_id": application.consumption_id,
        "receipt_id": application.receipt_id,
        "handoff_id": application.handoff_id,
        "inherited_integrity_id": application.inherited_integrity_id,
        "validation_id": application.validation_id,
        "semantic_use_id": application.semantic_use_id,
        "source_request_id": application.source_request_id,
        "source_request_lineage_id": application.source_request_lineage_id,
        "source_validation_id": application.source_validation_id,
        "source_validation_lineage_id": application.source_validation_lineage_id,
        "interpretation_id": application.interpretation_id,
        "read_id": application.read_id,
        "consumption_request_id": application.consumption_request_id,
        "requester_id": application.requester_id,
        "consumer_id": application.consumer_id,
        "handoff_target_id": application.handoff_target_id,
        "recipient_id": application.recipient_id,
        "handling_target_id": application.handling_target_id,
        "execution_target_id": application.execution_target_id,
        "signal_kind": application.signal_kind,
        "signal_purpose": application.signal_purpose,
        "signal_context": application.signal_context,
        "signal_status": application.signal_status,
        "source_signal_fingerprint": application.source_signal_fingerprint,
        "computed_signal_fingerprint": application.computed_signal_fingerprint,
        "learner_id": application.learner_id,
        "eligibility_purpose": application.eligibility_purpose,
        "proposer_id": application.proposer_id,
        "proposal_purpose": application.proposal_purpose,
        "proposed_change": application.proposed_change,
        "proposal_rationale": application.proposal_rationale,
        "decision_maker_id": application.decision_maker_id,
        "decision_purpose": application.decision_purpose,
        "decision_rationale": application.decision_rationale,
        "applier_id": application.applier_id,
        "application_purpose": application.application_purpose,
        "application_rationale": application.application_rationale,
        "application_evidence": application.application_evidence,
        "status": application.status,
        "reasons": application.reasons,
        "lineage": application.lineage,
    }
    encoded = json.dumps(_canonicalize(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class LearningStateExecutionLearningProposalApplicationIntegrity:
    """Immutable integrity evidence for one learning-proposal application artifact."""

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
    eligibility_source_id: str
    handling_id: str
    consumption_id: str
    receipt_id: str
    handoff_id: str
    inherited_integrity_id: str
    validation_id: str
    semantic_use_id: str
    source_request_id: str
    source_request_lineage_id: str
    source_validation_id: str
    source_validation_lineage_id: str
    interpretation_id: str
    read_id: str
    consumption_request_id: str
    requester_id: str
    consumer_id: str
    handoff_target_id: str
    recipient_id: str
    handling_target_id: str
    execution_target_id: str
    signal_kind: Any
    signal_purpose: str
    signal_context: Any
    signal_status: Any
    source_signal_fingerprint: str
    computed_signal_fingerprint: str
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
    source_application_fingerprint: str
    computed_application_fingerprint: str
    status: LearningStateExecutionLearningProposalApplicationIntegrityStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "integrity_id", "application_id", "decision_id", "proposal_id", "eligibility_id", "source_integrity_id",
            "signal_id", "evaluation_id", "feedback_id", "outcome_id", "attempt_id", "admission_id", "eligibility_source_id",
            "handling_id", "consumption_id", "receipt_id", "handoff_id", "inherited_integrity_id", "validation_id",
            "semantic_use_id", "source_request_id", "source_request_lineage_id", "source_validation_id",
            "source_validation_lineage_id", "interpretation_id", "read_id", "consumption_request_id", "requester_id",
            "consumer_id", "handoff_target_id", "recipient_id", "handling_target_id", "execution_target_id", "signal_purpose",
            "source_signal_fingerprint", "computed_signal_fingerprint", "learner_id", "eligibility_purpose", "proposer_id",
            "proposal_purpose", "decision_maker_id", "decision_purpose", "applier_id", "application_purpose",
            "source_application_fingerprint", "computed_application_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if len(self.source_signal_fingerprint) != 64 or len(self.computed_signal_fingerprint) != 64:
            raise ValueError("learning proposal application integrity requires SHA-256 signal fingerprints")
        if len(self.source_application_fingerprint) != 64 or len(self.computed_application_fingerprint) != 64:
            raise ValueError("learning proposal application integrity requires SHA-256 application fingerprints")
        if not isinstance(self.status, LearningStateExecutionLearningProposalApplicationIntegrityStatus):
            raise TypeError("status must be a learning-proposal application integrity status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "signal_context", _freeze(self.signal_context))
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
    """Verify application structure, identity, lineage, and fingerprint without repairing or executing it."""

    def verify(
        self,
        application: "LearningStateExecutionLearningProposalApplication",
        *,
        integrity_id: str,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningProposalApplicationIntegrity:
        from src.core.learning_state_execution_learning_proposal_application import LearningStateExecutionLearningProposalApplication

        if type(application) is not LearningStateExecutionLearningProposalApplication:
            raise TypeError("application must be a learning-proposal application artifact")
        if not isinstance(integrity_id, str) or not integrity_id.strip():
            raise ValueError("integrity_id must be a non-empty string")
        if integrity_id == application.application_id or integrity_id == application.integrity_id:
            raise ValueError("integrity identity must be distinct")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        checks.append("application is APPLIED or REJECTED" if application.status.value in {"APPLIED", "REJECTED"} else "invalid application status")
        checks.append("application lineage" if application.application_id == application.lineage.get("application_id", application.application_id) else "application lineage mismatch")
        checks.append("decision lineage" if application.decision_id == application.lineage.get("decision_id", application.decision_id) else "decision lineage mismatch")
        computed = _application_fingerprint(application)
        stored = application.lineage.get("application_fingerprint", computed)
        checks.append("application fingerprint" if stored == computed else "application fingerprint mismatch")
        valid = not any(check.startswith("invalid") or check.endswith("mismatch") for check in checks)
        final_reasons = reasons if reasons is not None else (("application structure, lineage, and fingerprint checks passed",) if valid else tuple(check for check in checks if check.startswith("invalid") or check.endswith("mismatch")))

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
            eligibility_source_id=application.eligibility_source_id,
            handling_id=application.handling_id,
            consumption_id=application.consumption_id,
            receipt_id=application.receipt_id,
            handoff_id=application.handoff_id,
            inherited_integrity_id=application.inherited_integrity_id,
            validation_id=application.validation_id,
            semantic_use_id=application.semantic_use_id,
            source_request_id=application.source_request_id,
            source_request_lineage_id=application.source_request_lineage_id,
            source_validation_id=application.source_validation_id,
            source_validation_lineage_id=application.source_validation_lineage_id,
            interpretation_id=application.interpretation_id,
            read_id=application.read_id,
            consumption_request_id=application.consumption_request_id,
            requester_id=application.requester_id,
            consumer_id=application.consumer_id,
            handoff_target_id=application.handoff_target_id,
            recipient_id=application.recipient_id,
            handling_target_id=application.handling_target_id,
            execution_target_id=application.execution_target_id,
            signal_kind=application.signal_kind,
            signal_purpose=application.signal_purpose,
            signal_context=application.signal_context,
            signal_status=application.signal_status,
            source_signal_fingerprint=application.source_signal_fingerprint,
            computed_signal_fingerprint=application.computed_signal_fingerprint,
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
            source_application_fingerprint=stored,
            computed_application_fingerprint=computed,
            status=LearningStateExecutionLearningProposalApplicationIntegrityStatus.VALID if valid else LearningStateExecutionLearningProposalApplicationIntegrityStatus.INVALID,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {"integrity_id": integrity_id, "application_id": application.application_id},
        )

    validate = verify


__all__ = [
    "LearningStateExecutionLearningProposalApplicationIntegrityError",
    "LearningStateExecutionLearningProposalApplicationIntegrityStatus",
    "LearningStateExecutionLearningProposalApplicationIntegrity",
    "LearningStateExecutionLearningProposalApplicationIntegrityService",
]
