"""M23.98: explicit durable learning-state transition boundary."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_learning_state_evidence_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4 as LearningStateEvidence,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4Status as EvidenceStatus,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4Error(RuntimeError):
    """Raised when a learning-state transition cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4Status(str, Enum):
    PERSISTED = "PERSISTED"
    NOT_PERSISTED = "NOT_PERSISTED"


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
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4:
    """Immutable evidence describing one attempted durable learning-state transition."""

    transition_id: str
    evidence_id: str
    application_id: str
    integrity_id: str
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
    transition_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4Status
    state: Mapping[str, Any]
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in (
            "transition_id", "evidence_id", "application_id", "integrity_id", "decision_id", "proposal_id",
            "eligibility_id", "signal_id", "evaluation_id", "feedback_id", "classification_id",
            "source_integrity_id", "source_decision_id", "outcome_id", "state_key",
            "source_application_fingerprint", "computed_application_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        if len(self.source_application_fingerprint) != 64 or len(self.computed_application_fingerprint) != 64:
            raise ValueError("learning-state transition requires SHA-256 fingerprints")
        if not isinstance(self.transition_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4Status):
            raise TypeError("transition_status must be a learning-state transition v4 status")
        if not isinstance(self.state, Mapping) or not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("state, reasons, and lineage must be mappings")
        object.__setattr__(self, "state", _freeze(self.state))
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_advisory_only(self) -> bool:
        return False

    @property
    def establishes_truth(self) -> bool:
        return False

    @property
    def grants_authority(self) -> bool:
        return False

    @property
    def updates_model(self) -> bool:
        return False

    @property
    def mutates_policy(self) -> bool:
        return False

    @property
    def invokes_learner(self) -> bool:
        return False

    @property
    def schedules_work(self) -> bool:
        return False

    @property
    def executes_action(self) -> bool:
        return False


PersistenceAdapter = Callable[[Mapping[str, Any]], bool]


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4Service:
    """Perform one explicit caller-supplied persistence attempt."""

    def transition(
        self,
        evidence: LearningStateEvidence,
        *,
        transition_id: str,
        state_key: str,
        state: Mapping[str, Any],
        persistence_adapter: PersistenceAdapter | None = None,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4:
        if type(evidence) is not LearningStateEvidence:
            raise TypeError("evidence must be a learning-state evidence v4 artifact")
        if evidence.evidence_status is not EvidenceStatus.READY:
            raise ValueError("learning-state transition requires READY learning-state evidence")
        if not isinstance(transition_id, str) or not transition_id.strip():
            raise ValueError("transition_id must be a non-empty string")
        if not isinstance(state_key, str) or not state_key.strip():
            raise ValueError("state_key must be a non-empty string")
        if not isinstance(state, Mapping):
            raise TypeError("state must be a mapping")

        frozen_state = _freeze(state)
        adapter_result: bool | None = None
        adapter_exception = False
        if persistence_adapter is not None:
            adapter_input = MappingProxyType({
                "transition_id": transition_id,
                "evidence_id": evidence.evidence_id,
                "application_id": evidence.application_id,
                "state_key": state_key,
                "state": frozen_state,
            })
            try:
                result = persistence_adapter(adapter_input)
            except Exception:
                adapter_exception = True
                result = None
            if isinstance(result, bool):
                adapter_result = result

        persisted = adapter_result is True and not adapter_exception
        status = (
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4Status.PERSISTED
            if persisted
            else EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4Status.NOT_PERSISTED
        )
        reason_payload = reasons if reasons is not None else {
            "transition_status": status.value,
            "persistence_adapter_supplied": persistence_adapter is not None,
            "adapter_exception": adapter_exception,
        }
        lineage_payload = lineage if lineage is not None else {
            "transition_id": transition_id,
            "evidence_id": evidence.evidence_id,
            "integrity_id": evidence.integrity_id,
        }
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4(
            transition_id=transition_id,
            evidence_id=evidence.evidence_id,
            application_id=evidence.application_id,
            integrity_id=evidence.integrity_id,
            decision_id=evidence.decision_id,
            proposal_id=evidence.proposal_id,
            eligibility_id=evidence.eligibility_id,
            signal_id=evidence.signal_id,
            evaluation_id=evidence.evaluation_id,
            feedback_id=evidence.feedback_id,
            classification_id=evidence.classification_id,
            source_integrity_id=evidence.source_integrity_id,
            source_decision_id=evidence.source_decision_id,
            outcome_id=evidence.outcome_id,
            confidence=evidence.confidence,
            source_application_fingerprint=evidence.source_application_fingerprint,
            computed_application_fingerprint=evidence.computed_application_fingerprint,
            state_key=state_key,
            transition_status=status,
            state=frozen_state,
            reasons=reason_payload,
            lineage=lineage_payload,
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateTransitionV4Service",
]
