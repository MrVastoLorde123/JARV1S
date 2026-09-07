"""M23.135: validate integrity-checked learning-state transitions without consuming or applying them."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_transition_integrity import (
    LearningStateExecutionLearningStateTransitionIntegrity,
    LearningStateExecutionLearningStateTransitionIntegrityStatus,
)


class LearningStateExecutionLearningStateValidationError(RuntimeError):
    """Raised when learning-state validation evidence cannot be formed safely."""


class LearningStateExecutionLearningStateValidationStatus(str, Enum):
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"


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
class LearningStateExecutionLearningStateValidation:
    """Immutable evidence that one integrity-checked transition is acceptable for a later consumer."""

    validation_id: str
    integrity_id: str
    transition_id: str
    evidence_id: str
    state_key: str
    state_before: Any
    state_after: Any
    transition_fingerprint: str
    computed_transition_fingerprint: str
    source_application_fingerprint: str
    computed_application_fingerprint: str
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
    source_validation_id: str
    use_id: str
    request_id: str
    interpretation_id: str
    source_request_id: str
    read_validation_id: str
    read_id: str
    consumption_request_id: str
    confidence: float
    consumer_id: str
    execution_target_id: str
    execution_purpose: str
    objective: str
    evaluator_id: str
    evaluation_purpose: str
    signal_kind: Any
    signal_purpose: str
    learner_id: str
    eligibility_purpose: str
    proposer_id: str
    proposal_purpose: str
    proposal_rationale: Any
    decision_maker_id: str
    decision_purpose: str
    decision_rationale: Any
    applier_id: str
    application_purpose: str
    application_rationale: Any
    application_evidence: Any
    application_status: Any
    evidence_collector_id: str
    evidence_purpose: str
    evidence_rationale: Any
    evidence_payload: Any
    transition_actor_id: str
    transition_purpose: str
    transition_rationale: Any
    validator_id: str
    validation_purpose: str
    validation_rationale: Any
    status: LearningStateExecutionLearningStateValidationStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        required_strings = (
            "validation_id", "integrity_id", "transition_id", "evidence_id", "state_key",
            "transition_fingerprint", "computed_transition_fingerprint", "source_application_fingerprint",
            "computed_application_fingerprint", "application_id", "decision_id", "proposal_id", "eligibility_id",
            "source_integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id", "attempt_id",
            "admission_id", "source_validation_id", "use_id", "request_id", "interpretation_id", "source_request_id",
            "read_validation_id", "read_id", "consumption_request_id", "consumer_id", "execution_target_id",
            "execution_purpose", "objective", "evaluator_id", "evaluation_purpose", "signal_purpose", "learner_id",
            "eligibility_purpose", "proposer_id", "proposal_purpose", "decision_maker_id", "decision_purpose",
            "applier_id", "application_purpose", "evidence_collector_id", "evidence_purpose", "transition_actor_id",
            "transition_purpose", "validator_id", "validation_purpose",
        )
        for name in required_strings:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        if not isinstance(self.status, LearningStateExecutionLearningStateValidationStatus):
            raise TypeError("status must be a learning-state validation status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        if self.status is LearningStateExecutionLearningStateValidationStatus.VALIDATED:
            if len(self.transition_fingerprint) != 64 or len(self.computed_transition_fingerprint) != 64:
                raise ValueError("validated learning-state evidence requires SHA-256 transition fingerprints")
        object.__setattr__(self, "state_before", _freeze(self.state_before))
        object.__setattr__(self, "state_after", _freeze(self.state_after))
        object.__setattr__(self, "proposal_rationale", _freeze(self.proposal_rationale))
        object.__setattr__(self, "decision_rationale", _freeze(self.decision_rationale))
        object.__setattr__(self, "application_rationale", _freeze(self.application_rationale))
        object.__setattr__(self, "application_evidence", _freeze(self.application_evidence))
        object.__setattr__(self, "evidence_rationale", _freeze(self.evidence_rationale))
        object.__setattr__(self, "evidence_payload", _freeze(self.evidence_payload))
        object.__setattr__(self, "transition_rationale", _freeze(self.transition_rationale))
        object.__setattr__(self, "validation_rationale", _freeze(self.validation_rationale))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_validated(self) -> bool:
        return self.status is LearningStateExecutionLearningStateValidationStatus.VALIDATED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionLearningStateValidationStatus.REJECTED

    @property
    def admits_consumption(self) -> bool:
        return self.is_validated

    @property
    def validates_learning_state(self) -> bool:
        return self.is_validated

    @property
    def mutates_state(self) -> bool:
        return False

    @property
    def persists_state(self) -> bool:
        return False

    @property
    def consumes_state(self) -> bool:
        return False

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
    def invokes_executor(self) -> bool:
        return False

    @property
    def schedules_work(self) -> bool:
        return False

    @property
    def plans_work(self) -> bool:
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


class LearningStateExecutionLearningStateValidationService:
    """Validate transition-integrity evidence without consuming or changing learning state."""

    def validate(
        self,
        integrity: LearningStateExecutionLearningStateTransitionIntegrity,
        *,
        validation_id: str,
        validator_id: str,
        validation_purpose: str,
        validation_rationale: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateValidation:
        if type(integrity) is not LearningStateExecutionLearningStateTransitionIntegrity:
            raise TypeError("integrity must be a learning-state transition integrity artifact")
        for name, value in (
            ("validation_id", validation_id),
            ("validator_id", validator_id),
            ("validation_purpose", validation_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if validation_rationale is None:
            raise ValueError("validation_rationale must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if integrity.status is not LearningStateExecutionLearningStateTransitionIntegrityStatus.VALID:
            checks.append("transition integrity is not VALID")
        lineage_integrity_id = integrity.lineage.get("integrity_id", integrity.integrity_id)
        lineage_transition_id = integrity.lineage.get("transition_id", integrity.transition_id)
        lineage_evidence_id = integrity.lineage.get("evidence_id", integrity.evidence_id)
        if lineage_integrity_id != integrity.integrity_id:
            checks.append("integrity lineage mismatch")
        if lineage_transition_id != integrity.transition_id:
            checks.append("transition lineage mismatch")
        if lineage_evidence_id != integrity.evidence_id:
            checks.append("evidence lineage mismatch")
        if integrity.integrity_id == integrity.transition_id:
            checks.append("integrity identity must be distinct from transition identity")
        if integrity.transition_fingerprint != integrity.computed_transition_fingerprint:
            checks.append("transition fingerprint mismatch")
        if len(integrity.computed_transition_fingerprint) != 64:
            checks.append("computed transition fingerprint is not SHA-256")
        if integrity.state_before == integrity.state_after:
            checks.append("state before and after are identical")
        if isinstance(integrity.confidence, bool) or not isinstance(integrity.confidence, (int, float)) or not 0.0 <= float(integrity.confidence) <= 1.0:
            checks.append("confidence is outside bounds")

        valid = not checks
        if reasons is not None:
            final_reasons = reasons
        elif valid:
            final_reasons = ("learning-state integrity evidence passed validation",)
        else:
            final_reasons = tuple(checks)
        status = (
            LearningStateExecutionLearningStateValidationStatus.VALIDATED
            if valid
            else LearningStateExecutionLearningStateValidationStatus.REJECTED
        )
        return LearningStateExecutionLearningStateValidation(
            validation_id=validation_id,
            integrity_id=integrity.integrity_id,
            transition_id=integrity.transition_id,
            evidence_id=integrity.evidence_id,
            state_key=integrity.state_key,
            state_before=integrity.state_before,
            state_after=integrity.state_after,
            transition_fingerprint=integrity.transition_fingerprint,
            computed_transition_fingerprint=integrity.computed_transition_fingerprint,
            source_application_fingerprint=integrity.source_application_fingerprint,
            computed_application_fingerprint=integrity.computed_application_fingerprint,
            application_id=integrity.application_id,
            decision_id=integrity.decision_id,
            proposal_id=integrity.proposal_id,
            eligibility_id=integrity.eligibility_id,
            source_integrity_id=integrity.source_integrity_id,
            signal_id=integrity.signal_id,
            evaluation_id=integrity.evaluation_id,
            feedback_id=integrity.feedback_id,
            outcome_id=integrity.outcome_id,
            attempt_id=integrity.attempt_id,
            admission_id=integrity.admission_id,
            source_validation_id=integrity.validation_id,
            use_id=integrity.use_id,
            request_id=integrity.request_id,
            interpretation_id=integrity.interpretation_id,
            source_request_id=integrity.source_request_id,
            read_validation_id=integrity.read_validation_id,
            read_id=integrity.read_id,
            consumption_request_id=integrity.consumption_request_id,
            confidence=integrity.confidence,
            consumer_id=integrity.consumer_id,
            execution_target_id=integrity.execution_target_id,
            execution_purpose=integrity.execution_purpose,
            objective=integrity.objective,
            evaluator_id=integrity.evaluator_id,
            evaluation_purpose=integrity.evaluation_purpose,
            signal_kind=integrity.signal_kind,
            signal_purpose=integrity.signal_purpose,
            learner_id=integrity.learner_id,
            eligibility_purpose=integrity.eligibility_purpose,
            proposer_id=integrity.proposer_id,
            proposal_purpose=integrity.proposal_purpose,
            proposal_rationale=integrity.proposal_rationale,
            decision_maker_id=integrity.decision_maker_id,
            decision_purpose=integrity.decision_purpose,
            decision_rationale=integrity.decision_rationale,
            applier_id=integrity.applier_id,
            application_purpose=integrity.application_purpose,
            application_rationale=integrity.application_rationale,
            application_evidence=integrity.application_evidence,
            application_status=integrity.application_status,
            evidence_collector_id=integrity.evidence_collector_id,
            evidence_purpose=integrity.evidence_purpose,
            evidence_rationale=integrity.evidence_rationale,
            evidence_payload=integrity.evidence_payload,
            transition_actor_id=integrity.transition_actor_id,
            transition_purpose=integrity.transition_purpose,
            transition_rationale=integrity.transition_rationale,
            validator_id=validator_id,
            validation_purpose=validation_purpose,
            validation_rationale=validation_rationale,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {"validation_id": validation_id, "integrity_id": integrity.integrity_id},
        )


__all__ = [
    "LearningStateExecutionLearningStateValidationError",
    "LearningStateExecutionLearningStateValidationStatus",
    "LearningStateExecutionLearningStateValidation",
    "LearningStateExecutionLearningStateValidationService",
]
