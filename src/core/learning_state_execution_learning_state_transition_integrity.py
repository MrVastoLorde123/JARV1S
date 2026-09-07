"""M23.134: validate formulated learning-state transitions without applying them."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.learning_state_execution_learning_state_transition import (
    LearningStateExecutionLearningStateTransition,
    LearningStateExecutionLearningStateTransitionStatus,
)


class LearningStateExecutionLearningStateTransitionIntegrityError(RuntimeError):
    """Raised when transition-integrity evidence cannot be formed safely."""


class LearningStateExecutionLearningStateTransitionIntegrityStatus(str, Enum):
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


def _canonical(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted((_canonical(item) for item in value), key=lambda item: repr(item))
    if isinstance(value, Enum):
        return value.value
    return value


def _expected_transition_fingerprint(transition: LearningStateExecutionLearningStateTransition) -> str:
    payload = {
        "transition_id": transition.transition_id,
        "state_key": transition.state_key,
        "state_before": _canonical(transition.state_before),
        "state_after": _canonical(transition.state_after),
        "evidence_id": transition.evidence_id,
        "integrity_id": transition.integrity_id,
        "proposed_change": _canonical(transition.proposed_change),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class LearningStateExecutionLearningStateTransitionIntegrity:
    """Immutable evidence about the structural integrity of one learning-state transition."""

    integrity_id: str
    transition_id: str
    evidence_id: str
    transition_fingerprint: str
    computed_transition_fingerprint: str
    state_key: str
    state_before: Any
    state_after: Any
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
    source_application_fingerprint: str
    computed_application_fingerprint: str
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
    status: LearningStateExecutionLearningStateTransitionIntegrityStatus
    reasons: tuple[str, ...]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        required_strings = (
            "integrity_id", "transition_id", "evidence_id", "transition_fingerprint", "computed_transition_fingerprint",
            "state_key", "application_id", "decision_id", "proposal_id", "eligibility_id", "source_integrity_id",
            "signal_id", "evaluation_id", "feedback_id", "outcome_id", "attempt_id", "admission_id", "validation_id",
            "use_id", "request_id", "interpretation_id", "source_request_id", "read_validation_id", "read_id",
            "consumption_request_id", "source_validation_id", "source_application_fingerprint", "computed_application_fingerprint",
            "consumer_id", "execution_target_id", "execution_purpose", "objective", "evaluator_id", "evaluation_purpose",
            "signal_purpose", "learner_id", "eligibility_purpose", "proposer_id", "proposal_purpose", "decision_maker_id",
            "decision_purpose", "applier_id", "application_purpose", "evidence_collector_id", "evidence_purpose",
            "transition_actor_id", "transition_purpose",
        )
        for name in required_strings:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        if not isinstance(self.status, LearningStateExecutionLearningStateTransitionIntegrityStatus):
            raise TypeError("status must be a learning-state transition integrity status")
        if not isinstance(self.reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in self.reasons):
            raise TypeError("reasons must be a tuple of non-empty strings")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        if self.status is LearningStateExecutionLearningStateTransitionIntegrityStatus.VALID:
            for name in ("transition_fingerprint", "computed_transition_fingerprint"):
                if len(getattr(self, name)) != 64:
                    raise ValueError("transition integrity requires SHA-256 fingerprints")
        object.__setattr__(self, "state_before", _freeze(self.state_before))
        object.__setattr__(self, "state_after", _freeze(self.state_after))
        object.__setattr__(self, "proposal_rationale", _freeze(self.proposal_rationale))
        object.__setattr__(self, "decision_rationale", _freeze(self.decision_rationale))
        object.__setattr__(self, "application_rationale", _freeze(self.application_rationale))
        object.__setattr__(self, "application_evidence", _freeze(self.application_evidence))
        object.__setattr__(self, "evidence_rationale", _freeze(self.evidence_rationale))
        object.__setattr__(self, "evidence_payload", _freeze(self.evidence_payload))
        object.__setattr__(self, "transition_rationale", _freeze(self.transition_rationale))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_valid(self) -> bool:
        return self.status is LearningStateExecutionLearningStateTransitionIntegrityStatus.VALID

    @property
    def validates_transition(self) -> bool:
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
    def mutates_state(self) -> bool:
        return False

    @property
    def persists_state(self) -> bool:
        return False

    @property
    def executes_work(self) -> bool:
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


class LearningStateExecutionLearningStateTransitionIntegrityService:
    """Validate transition structure and fingerprint without applying or repairing the transition."""

    def validate(
        self,
        transition: LearningStateExecutionLearningStateTransition,
        *,
        integrity_id: str,
        reasons: tuple[str, ...] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> LearningStateExecutionLearningStateTransitionIntegrity:
        if type(transition) is not LearningStateExecutionLearningStateTransition:
            raise TypeError("transition must be a learning-state transition artifact")
        if not isinstance(integrity_id, str) or not integrity_id.strip():
            raise ValueError("integrity_id must be a non-empty string")
        if reasons is not None and (not isinstance(reasons, tuple) or not all(isinstance(reason, str) and reason.strip() for reason in reasons)):
            raise TypeError("reasons must be a tuple of non-empty strings")

        checks: list[str] = []
        if transition.status is not LearningStateExecutionLearningStateTransitionStatus.FORMULATED:
            checks.append("transition is not FORMULATED")
        if transition.transition_id != transition.lineage.get("transition_id", transition.transition_id):
            checks.append("transition lineage mismatch")
        if transition.evidence_id != transition.lineage.get("evidence_id", transition.evidence_id):
            checks.append("evidence lineage mismatch")
        if transition.state_before == transition.state_after:
            checks.append("state before and after are identical")
        expected = _expected_transition_fingerprint(transition)
        if transition.transition_fingerprint != expected:
            checks.append("transition fingerprint mismatch")
        valid = not checks
        if reasons is not None:
            final_reasons = reasons
        elif valid:
            final_reasons = ("transition structure, lineage, and fingerprint checks passed",)
        else:
            final_reasons = tuple(checks)
        status = LearningStateExecutionLearningStateTransitionIntegrityStatus.VALID if valid else LearningStateExecutionLearningStateTransitionIntegrityStatus.INVALID
        return LearningStateExecutionLearningStateTransitionIntegrity(
            integrity_id=integrity_id,
            transition_id=transition.transition_id,
            evidence_id=transition.evidence_id,
            transition_fingerprint=transition.transition_fingerprint,
            computed_transition_fingerprint=expected,
            state_key=transition.state_key,
            state_before=transition.state_before,
            state_after=transition.state_after,
            application_id=transition.application_id,
            decision_id=transition.decision_id,
            proposal_id=transition.proposal_id,
            eligibility_id=transition.eligibility_id,
            source_integrity_id=transition.source_integrity_id,
            signal_id=transition.signal_id,
            evaluation_id=transition.evaluation_id,
            feedback_id=transition.feedback_id,
            outcome_id=transition.outcome_id,
            attempt_id=transition.attempt_id,
            admission_id=transition.admission_id,
            validation_id=transition.validation_id,
            use_id=transition.use_id,
            request_id=transition.request_id,
            interpretation_id=transition.interpretation_id,
            source_request_id=transition.source_request_id,
            read_validation_id=transition.read_validation_id,
            read_id=transition.read_id,
            consumption_request_id=transition.consumption_request_id,
            source_validation_id=transition.source_validation_id,
            source_application_fingerprint=transition.source_application_fingerprint,
            computed_application_fingerprint=transition.computed_application_fingerprint,
            confidence=transition.confidence,
            consumer_id=transition.consumer_id,
            execution_target_id=transition.execution_target_id,
            execution_purpose=transition.execution_purpose,
            objective=transition.objective,
            evaluator_id=transition.evaluator_id,
            evaluation_purpose=transition.evaluation_purpose,
            signal_kind=transition.signal_kind,
            signal_purpose=transition.signal_purpose,
            learner_id=transition.learner_id,
            eligibility_purpose=transition.eligibility_purpose,
            proposer_id=transition.proposer_id,
            proposal_purpose=transition.proposal_purpose,
            proposal_rationale=transition.proposal_rationale,
            decision_maker_id=transition.decision_maker_id,
            decision_purpose=transition.decision_purpose,
            decision_rationale=transition.decision_rationale,
            applier_id=transition.applier_id,
            application_purpose=transition.application_purpose,
            application_rationale=transition.application_rationale,
            application_evidence=transition.application_evidence,
            application_status=transition.application_status,
            evidence_collector_id=transition.evidence_collector_id,
            evidence_purpose=transition.evidence_purpose,
            evidence_rationale=transition.evidence_rationale,
            evidence_payload=transition.evidence_payload,
            transition_actor_id=transition.transition_actor_id,
            transition_purpose=transition.transition_purpose,
            transition_rationale=transition.transition_rationale,
            status=status,
            reasons=tuple(final_reasons),
            lineage=lineage if lineage is not None else {"integrity_id": integrity_id, "transition_id": transition.transition_id},
        )


__all__ = [
    "LearningStateExecutionLearningStateTransitionIntegrityError",
    "LearningStateExecutionLearningStateTransitionIntegrityStatus",
    "LearningStateExecutionLearningStateTransitionIntegrity",
    "LearningStateExecutionLearningStateTransitionIntegrityService",
]
