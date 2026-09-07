"""M23.136: request bounded consumption of validated learning-state evidence."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_validation import (
    LearningStateExecutionLearningStateValidation,
    LearningStateExecutionLearningStateValidationStatus,
)


class LearningStateExecutionLearningStateConsumptionRequestError(RuntimeError):
    """Raised when a consumption request cannot be formed safely."""


class LearningStateExecutionLearningStateConsumptionRequestStatus(str, Enum):
    REQUESTED = "REQUESTED"
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
class LearningStateExecutionLearningStateConsumptionRequest:
    """Immutable evidence that validated learning-state data was explicitly requested for later consumption."""

    consumption_request_id: str
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
    requester_id: str
    request_purpose: str
    requested_scope: Any
    request_rationale: Any
    status: LearningStateExecutionLearningStateConsumptionRequestStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        required_strings = (
            "consumption_request_id", "validation_id", "integrity_id", "transition_id", "evidence_id", "state_key",
            "transition_fingerprint", "computed_transition_fingerprint", "source_application_fingerprint",
            "computed_application_fingerprint", "application_id", "decision_id", "proposal_id", "eligibility_id",
            "source_integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id", "attempt_id",
            "admission_id", "source_validation_id", "use_id", "request_id", "interpretation_id", "source_request_id",
            "read_validation_id", "read_id", "consumer_id", "execution_target_id", "execution_purpose", "objective",
            "evaluator_id", "evaluation_purpose", "signal_purpose", "learner_id", "eligibility_purpose", "proposer_id",
            "proposal_purpose", "decision_maker_id", "decision_purpose", "applier_id", "application_purpose",
            "evidence_collector_id", "evidence_purpose", "transition_actor_id", "transition_purpose", "validator_id",
            "validation_purpose", "requester_id", "request_purpose",
        )
        for name in required_strings:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        if not isinstance(self.status, LearningStateExecutionLearningStateConsumptionRequestStatus):
            raise TypeError("status must be a consumption-request status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
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
        object.__setattr__(self, "requested_scope", _freeze(self.requested_scope))
        object.__setattr__(self, "request_rationale", _freeze(self.request_rationale))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_requested(self) -> bool:
        return self.status is LearningStateExecutionLearningStateConsumptionRequestStatus.REQUESTED

    @property
    def is_rejected(self) -> bool:
        return self.status is LearningStateExecutionLearningStateConsumptionRequestStatus.REJECTED

    @property
    def admits_read(self) -> bool:
        return self.is_requested

    @property
    def consumes_state(self) -> bool:
        return False

    @property
    def reads_state(self) -> bool:
        return False

    @property
    def mutates_state(self) -> bool:
        return False

    @property
    def persists_state(self) -> bool:
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
    def interprets_state(self) -> bool:
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


class LearningStateExecutionLearningStateConsumptionRequestService:
    """Create a bounded request for later state consumption without reading or mutating state."""

    def request(
        self,
        validation: LearningStateExecutionLearningStateValidation,
        *,
        consumption_request_id: str,
        requester_id: str,
        request_purpose: str,
        requested_scope: Any,
        request_rationale: Any,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateConsumptionRequest:
        if type(validation) is not LearningStateExecutionLearningStateValidation:
            raise TypeError("validation must be a learning-state validation artifact")
        for name, value in (
            ("consumption_request_id", consumption_request_id),
            ("requester_id", requester_id),
            ("request_purpose", request_purpose),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if request_rationale is None:
            raise ValueError("request_rationale must be provided")
        if requested_scope is None:
            raise ValueError("requested_scope must be provided")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if validation.status is not LearningStateExecutionLearningStateValidationStatus.VALIDATED:
            checks.append("learning-state validation is not VALIDATED")
        lineage_validation_id = validation.lineage.get("validation_id", validation.validation_id)
        lineage_integrity_id = validation.lineage.get("integrity_id", validation.integrity_id)
        lineage_transition_id = validation.lineage.get("transition_id", validation.transition_id)
        lineage_evidence_id = validation.lineage.get("evidence_id", validation.evidence_id)
        if lineage_validation_id != validation.validation_id:
            checks.append("validation lineage mismatch")
        if lineage_integrity_id != validation.integrity_id:
            checks.append("integrity lineage mismatch")
        if lineage_transition_id != validation.transition_id:
            checks.append("transition lineage mismatch")
        if lineage_evidence_id != validation.evidence_id:
            checks.append("evidence lineage mismatch")
        if validation.validation_id == consumption_request_id:
            checks.append("consumption request identity must be distinct from validation identity")
        if validation.transition_fingerprint != validation.computed_transition_fingerprint:
            checks.append("transition fingerprint mismatch")
        if len(validation.computed_transition_fingerprint) != 64:
            checks.append("computed transition fingerprint is not SHA-256")
        if validation.state_before == validation.state_after:
            checks.append("state before and after are identical")

        valid = not checks
        if reasons is not None:
            final_reasons = reasons
        elif valid:
            final_reasons = ("learning-state validation is VALIDATED for downstream consumption",)
        else:
            final_reasons = tuple(checks)
        status = (
            LearningStateExecutionLearningStateConsumptionRequestStatus.REQUESTED
            if valid
            else LearningStateExecutionLearningStateConsumptionRequestStatus.REJECTED
        )
        return LearningStateExecutionLearningStateConsumptionRequest(
            consumption_request_id=consumption_request_id,
            validation_id=validation.validation_id,
            integrity_id=validation.integrity_id,
            transition_id=validation.transition_id,
            evidence_id=validation.evidence_id,
            state_key=validation.state_key,
            state_before=validation.state_before,
            state_after=validation.state_after,
            transition_fingerprint=validation.transition_fingerprint,
            computed_transition_fingerprint=validation.computed_transition_fingerprint,
            source_application_fingerprint=validation.source_application_fingerprint,
            computed_application_fingerprint=validation.computed_application_fingerprint,
            application_id=validation.application_id,
            decision_id=validation.decision_id,
            proposal_id=validation.proposal_id,
            eligibility_id=validation.eligibility_id,
            source_integrity_id=validation.source_integrity_id,
            signal_id=validation.signal_id,
            evaluation_id=validation.evaluation_id,
            feedback_id=validation.feedback_id,
            outcome_id=validation.outcome_id,
            attempt_id=validation.attempt_id,
            admission_id=validation.admission_id,
            source_validation_id=validation.source_validation_id,
            use_id=validation.use_id,
            request_id=validation.request_id,
            interpretation_id=validation.interpretation_id,
            source_request_id=validation.source_request_id,
            read_validation_id=validation.read_validation_id,
            read_id=validation.read_id,
            confidence=validation.confidence,
            consumer_id=validation.consumer_id,
            execution_target_id=validation.execution_target_id,
            execution_purpose=validation.execution_purpose,
            objective=validation.objective,
            evaluator_id=validation.evaluator_id,
            evaluation_purpose=validation.evaluation_purpose,
            signal_kind=validation.signal_kind,
            signal_purpose=validation.signal_purpose,
            learner_id=validation.learner_id,
            eligibility_purpose=validation.eligibility_purpose,
            proposer_id=validation.proposer_id,
            proposal_purpose=validation.proposal_purpose,
            proposal_rationale=validation.proposal_rationale,
            decision_maker_id=validation.decision_maker_id,
            decision_purpose=validation.decision_purpose,
            decision_rationale=validation.decision_rationale,
            applier_id=validation.applier_id,
            application_purpose=validation.application_purpose,
            application_rationale=validation.application_rationale,
            application_evidence=validation.application_evidence,
            application_status=validation.application_status,
            evidence_collector_id=validation.evidence_collector_id,
            evidence_purpose=validation.evidence_purpose,
            evidence_rationale=validation.evidence_rationale,
            evidence_payload=validation.evidence_payload,
            transition_actor_id=validation.transition_actor_id,
            transition_purpose=validation.transition_purpose,
            transition_rationale=validation.transition_rationale,
            validator_id=validation.validator_id,
            validation_purpose=validation.validation_purpose,
            validation_rationale=validation.validation_rationale,
            requester_id=requester_id,
            request_purpose=request_purpose,
            requested_scope=requested_scope,
            request_rationale=request_rationale,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {"consumption_request_id": consumption_request_id, "validation_id": validation.validation_id},
        )


__all__ = [
    "LearningStateExecutionLearningStateConsumptionRequestError",
    "LearningStateExecutionLearningStateConsumptionRequestStatus",
    "LearningStateExecutionLearningStateConsumptionRequest",
    "LearningStateExecutionLearningStateConsumptionRequestService",
]
