"""M23.97: bounded learning-state evidence over valid applied integrity v4."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_integrity_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV4 as ApplicationIntegrity,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationIntegrityV4Status as IntegrityStatus,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_application_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Status as ApplicationStatus,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4Error(RuntimeError):
    """Raised when learning-state evidence cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4Status(str, Enum):
    READY = "READY"
    BLOCKED = "BLOCKED"


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
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4:
    """Immutable evidence for a future durable learning-state transition."""

    evidence_id: str
    application_id: str
    integrity_id: str
    decision_id: str
    proposal_id: str
    source_proposal_id: str
    eligibility_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    classification_id: str
    source_integrity_id: str
    source_decision_id: str
    outcome_id: str
    confidence: float
    application_status: ApplicationStatus
    integrity_status: IntegrityStatus
    source_application_fingerprint: str
    computed_application_fingerprint: str
    evidence_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4Status
    failure_reason: str | None
    evidence: Mapping[str, Any]
    reasons: Mapping[str, Any]
    lineage: Mapping[str, Any]

    def __post_init__(self) -> None:
        required = (
            "evidence_id", "application_id", "integrity_id", "decision_id", "proposal_id", "source_proposal_id",
            "eligibility_id", "signal_id", "evaluation_id", "feedback_id", "classification_id", "source_integrity_id",
            "source_decision_id", "outcome_id", "source_application_fingerprint", "computed_application_fingerprint",
        )
        for name in required:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        for name in ("source_application_fingerprint", "computed_application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("learning-state evidence requires SHA-256 fingerprints")
        if not isinstance(self.application_status, ApplicationStatus):
            raise TypeError("application_status must be an application v4 status")
        if not isinstance(self.integrity_status, IntegrityStatus):
            raise TypeError("integrity_status must be an application integrity v4 status")
        if not isinstance(self.evidence_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4Status):
            raise TypeError("evidence_status must be a learning-state evidence v4 status")
        if self.evidence_status is EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4Status.READY:
            if self.integrity_status is not IntegrityStatus.VALID:
                raise ValueError("READY evidence requires VALID application integrity")
            if self.application_status is not ApplicationStatus.APPLIED:
                raise ValueError("READY evidence requires APPLIED application status")
            if self.failure_reason is not None:
                raise ValueError("READY evidence cannot carry a failure reason")
        else:
            if self.failure_reason is None or not self.failure_reason.strip():
                raise ValueError("BLOCKED evidence requires a failure reason")
        if not isinstance(self.evidence, Mapping) or not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("evidence, reasons, and lineage must be mappings")
        object.__setattr__(self, "evidence", _freeze(self.evidence))
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_advisory_only(self) -> bool:
        return True

    @property
    def establishes_truth(self) -> bool:
        return False

    @property
    def grants_authority(self) -> bool:
        return False

    @property
    def persists_state(self) -> bool:
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
    def schedules_work(self) -> bool:
        return False

    @property
    def executes_action(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4Service:
    """Emit learning-state evidence without persistence, learning, or authority mutation."""

    def record(
        self,
        integrity: ApplicationIntegrity,
        *,
        evidence_id: str,
        evidence: Mapping[str, Any] | None = None,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4:
        if type(integrity) is not ApplicationIntegrity:
            raise TypeError("integrity must be an application integrity v4 artifact")
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            raise ValueError("evidence_id must be a non-empty string")
        ready = integrity.integrity_status is IntegrityStatus.VALID and integrity.application_status is ApplicationStatus.APPLIED
        status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4Status.READY if ready else EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4Status.BLOCKED
        failure = None if ready else "learning-state evidence requires VALID integrity over an APPLIED application"
        evidence_payload = evidence if evidence is not None else {
            "application_id": integrity.application_id,
            "application_fingerprint": integrity.computed_application_fingerprint,
            "integrity_id": integrity.integrity_id,
        }
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4(
            evidence_id=evidence_id,
            application_id=integrity.application_id,
            integrity_id=integrity.integrity_id,
            decision_id=integrity.decision_id,
            proposal_id=integrity.proposal_id,
            source_proposal_id=integrity.source_proposal_id,
            eligibility_id=integrity.eligibility_id,
            signal_id=integrity.signal_id,
            evaluation_id=integrity.evaluation_id,
            feedback_id=integrity.feedback_id,
            classification_id=integrity.classification_id,
            source_integrity_id=integrity.source_integrity_id,
            source_decision_id=integrity.source_decision_id,
            outcome_id=integrity.outcome_id,
            confidence=integrity.confidence,
            application_status=integrity.application_status,
            integrity_status=integrity.integrity_status,
            source_application_fingerprint=integrity.source_application_fingerprint,
            computed_application_fingerprint=integrity.computed_application_fingerprint,
            evidence_status=status,
            failure_reason=failure,
            evidence=evidence_payload,
            reasons=reasons if reasons is not None else {"evidence_status": status.value},
            lineage=lineage if lineage is not None else {"evidence_id": evidence_id, "integrity_id": integrity.integrity_id},
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationLearningStateEvidenceV4Service",
]
