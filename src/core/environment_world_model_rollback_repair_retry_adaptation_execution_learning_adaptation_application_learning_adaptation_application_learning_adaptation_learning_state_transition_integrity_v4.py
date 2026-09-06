"""M23.99: deterministic integrity evidence over one learning-state transition v4."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, fields
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_learning_state_transition_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4 as LearningStateTransition,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4Status as TransitionStatus,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionIntegrityV4Error(RuntimeError):
    """Raised when transition integrity evidence cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionIntegrityV4Status(str, Enum):
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
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _canonical(value[key]) for key in sorted(value, key=lambda item: str(item))}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if isinstance(value, set):
        return sorted(
            (_canonical(item) for item in value),
            key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")),
        )
    return value


def _transition_fingerprint(transition: LearningStateTransition) -> str:
    payload = {field.name: _canonical(getattr(transition, field.name)) for field in fields(transition)}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionIntegrityV4:
    """Immutable integrity evidence over exactly one M23.98 transition artifact."""

    integrity_id: str
    transition_id: str
    evidence_id: str
    application_id: str
    transition_source_id: str
    decision_id: str
    proposal_id: str
    eligibility_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    classification_id: str
    source_integrity_id: str
    source_decision_id: str
    outcome_id: str
    confidence: float
    source_application_fingerprint: str
    computed_application_fingerprint: str
    state_key: str
    transition_status: TransitionStatus
    computed_transition_fingerprint: str
    integrity_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionIntegrityV4Status
    failure_reason: str | None
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        required = (
            "integrity_id", "transition_id", "evidence_id", "application_id", "transition_source_id", "decision_id",
            "proposal_id", "eligibility_id", "signal_id", "evaluation_id", "feedback_id", "classification_id",
            "source_integrity_id", "source_decision_id", "outcome_id", "state_key", "source_application_fingerprint",
            "computed_application_fingerprint", "computed_transition_fingerprint",
        )
        for name in required:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        if len(self.source_application_fingerprint) != 64 or len(self.computed_application_fingerprint) != 64 or len(self.computed_transition_fingerprint) != 64:
            raise ValueError("transition integrity requires SHA-256 fingerprints")
        if not isinstance(self.transition_status, TransitionStatus):
            raise TypeError("transition_status must be a learning-state transition v4 status")
        if not isinstance(self.integrity_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionIntegrityV4Status):
            raise TypeError("integrity_status must be a transition integrity v4 status")
        if self.integrity_status is EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionIntegrityV4Status.VALID and self.failure_reason is not None:
            raise ValueError("VALID integrity cannot carry a failure reason")
        if self.integrity_status is EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionIntegrityV4Status.INVALID and (self.failure_reason is None or not self.failure_reason.strip()):
            raise ValueError("INVALID integrity requires a failure reason")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def establishes_truth(self) -> bool:
        return False

    @property
    def establishes_correctness(self) -> bool:
        return False

    @property
    def grants_authority(self) -> bool:
        return False

    @property
    def invokes_learner(self) -> bool:
        return False

    @property
    def updates_model(self) -> bool:
        return False

    @property
    def mutates_durable_state(self) -> bool:
        return False

    @property
    def mutates_policy(self) -> bool:
        return False

    @property
    def schedules_work(self) -> bool:
        return False

    @property
    def executes_action(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionIntegrityV4Service:
    """Fingerprint one transition artifact without retry, mutation, or correctness claims."""

    def assess(
        self,
        transition: LearningStateTransition,
        *,
        integrity_id: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionIntegrityV4:
        if type(transition) is not LearningStateTransition:
            raise TypeError("transition must be a learning-state transition v4 artifact")
        if not isinstance(integrity_id, str) or not integrity_id.strip():
            raise ValueError("integrity_id must be a non-empty string")

        computed = _transition_fingerprint(transition)
        status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionIntegrityV4Status.VALID
        reason_payload = reasons if reasons is not None else {
            "integrity_status": status.value,
            "transition_status": transition.transition_status.value,
        }
        lineage_payload = lineage if lineage is not None else {
            "integrity_id": integrity_id,
            "transition_id": transition.transition_id,
        }
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionIntegrityV4(
            integrity_id=integrity_id,
            transition_id=transition.transition_id,
            evidence_id=transition.evidence_id,
            application_id=transition.application_id,
            transition_source_id=transition.integrity_id,
            decision_id=transition.decision_id,
            proposal_id=transition.proposal_id,
            eligibility_id=transition.eligibility_id,
            signal_id=transition.signal_id,
            evaluation_id=transition.evaluation_id,
            feedback_id=transition.feedback_id,
            classification_id=transition.classification_id,
            source_integrity_id=transition.source_integrity_id,
            source_decision_id=transition.source_decision_id,
            outcome_id=transition.outcome_id,
            confidence=transition.confidence,
            source_application_fingerprint=transition.source_application_fingerprint,
            computed_application_fingerprint=transition.computed_application_fingerprint,
            state_key=transition.state_key,
            transition_status=transition.transition_status,
            computed_transition_fingerprint=computed,
            integrity_status=status,
            failure_reason=None,
            reasons=reason_payload,
            lineage=lineage_payload,
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionIntegrityV4Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionIntegrityV4Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionIntegrityV4",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionIntegrityV4Service",
]
