"""M23.73: advisory adaptation proposal derived from v3 learning eligibility."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_eligibility_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_signal_integrity_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_signal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Error(RuntimeError):
    """Raised when an adaptation proposal cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status(str, Enum):
    PROPOSED = "PROPOSED"
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
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3:
    """Immutable advisory adaptation proposal derived from one M23.72 eligibility artifact."""

    proposal_id: str
    eligibility_id: str
    integrity_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    classification_id: str
    execution_id: str
    handoff_id: str
    authorization_id: str
    validation_id: str
    source_signal_id: str
    outcome_id: str
    preparation_id: str
    decision_id: str
    source_proposal_id: str
    source_integrity_id: str
    assessment_id: str | None
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    execution_status: Any
    feedback_status: Any
    evaluation_status: Any
    integrity_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status
    eligibility_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status
    signal_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status
    confidence: float
    signal_fingerprint: str
    upstream_proposal_fingerprint: str
    handoff_fingerprint: str
    result_fingerprint: str
    authority_principal_id: str | None
    executor_id: str | None
    failure_reason: str | None
    proposal_kind: str
    proposal_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status
    proposal_payload: Mapping[str, Any] | None = None
    reasons: Mapping[str, Any] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = (
            "proposal_id", "eligibility_id", "integrity_id", "signal_id", "evaluation_id", "feedback_id",
            "classification_id", "execution_id", "handoff_id", "authorization_id", "validation_id",
            "source_signal_id", "outcome_id", "preparation_id", "decision_id", "source_proposal_id",
            "source_integrity_id", "environment_id", "expected_model_id", "observed_model_id",
            "signal_fingerprint", "upstream_proposal_fingerprint", "handoff_fingerprint", "result_fingerprint",
            "proposal_kind",
        )
        for name in required:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name in ("assessment_id", "authority_principal_id", "executor_id"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be None or a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        if self.failure_reason is not None and (not isinstance(self.failure_reason, str) or not self.failure_reason.strip()):
            raise ValueError("failure_reason must be None or a non-empty string")
        if not isinstance(self.integrity_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalIntegrityV3Status):
            raise TypeError("integrity_status must be a learning-signal integrity v3 status")
        if not isinstance(self.eligibility_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status):
            raise TypeError("eligibility_status must be a learning-eligibility v3 status")
        if not isinstance(self.signal_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningSignalV3Status):
            raise TypeError("signal_status must be a learning-signal v3 status")
        if not isinstance(self.proposal_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status):
            raise TypeError("proposal_status must be an adaptation-proposal v3 status")
        expected_status = {
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status.ELIGIBLE:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.PROPOSED,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status.INELIGIBLE:
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.BLOCKED,
        }[self.eligibility_status]
        if self.proposal_status != expected_status:
            raise ValueError("proposal status does not match eligibility status")
        expected_kind = "ADAPTATION_CANDIDATE" if self.proposal_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.PROPOSED else "BLOCKED_ADAPTATION_CANDIDATE"
        if self.proposal_kind != expected_kind:
            raise ValueError("proposal kind does not match proposal status")
        if self.proposal_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.PROPOSED:
            if not isinstance(self.proposal_payload, Mapping):
                raise ValueError("PROPOSED adaptation proposal requires a mapping payload")
        elif self.proposal_payload is not None:
            raise ValueError("BLOCKED adaptation proposal cannot carry a proposal payload")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "proposal_payload", None if self.proposal_payload is None else _freeze(self.proposal_payload))
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_advisory_only(self) -> bool:
        return True

    @property
    def authorizes_adaptation(self) -> bool:
        return False

    @property
    def requests_adaptation_execution(self) -> bool:
        return False

    @property
    def grants_authority(self) -> bool:
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
    def mutates_persistence(self) -> bool:
        return False

    @property
    def schedules_work(self) -> bool:
        return False

    @property
    def executes(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Service:
    """Create inert adaptation proposal evidence from one v3 eligibility artifact."""

    def propose(self, eligibility: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3, *, proposal_id: str, proposal_payload: Mapping[str, Any] | None = None, reasons: Mapping[str, Any] | None = None, lineage: Mapping[str, Any] | None = None) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3:
        if type(eligibility) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3:
            raise TypeError("eligibility must be EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3")
        if not isinstance(proposal_id, str) or not proposal_id.strip():
            raise ValueError("proposal_id must be a non-empty string")
        proposed = eligibility.status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningEligibilityV3Status.ELIGIBLE
        if proposed:
            if not isinstance(proposal_payload, Mapping):
                raise ValueError("eligible evidence requires a mapping proposal_payload")
            status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.PROPOSED
            kind = "ADAPTATION_CANDIDATE"
            payload = proposal_payload
            default_reason = "eligible learning evidence permits an adaptation candidate proposal"
        else:
            status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.BLOCKED
            kind = "BLOCKED_ADAPTATION_CANDIDATE"
            payload = None
            default_reason = "ineligible learning evidence blocks adaptation proposal formation"
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3(
            proposal_id=proposal_id,
            eligibility_id=eligibility.eligibility_id,
            integrity_id=eligibility.integrity_id,
            signal_id=eligibility.signal_id,
            evaluation_id=eligibility.evaluation_id,
            feedback_id=eligibility.feedback_id,
            classification_id=eligibility.classification_id,
            execution_id=eligibility.execution_id,
            handoff_id=eligibility.handoff_id,
            authorization_id=eligibility.authorization_id,
            validation_id=eligibility.validation_id,
            source_signal_id=eligibility.source_signal_id,
            outcome_id=eligibility.outcome_id,
            preparation_id=eligibility.preparation_id,
            decision_id=eligibility.decision_id,
            source_proposal_id=eligibility.proposal_id,
            source_integrity_id=eligibility.source_integrity_id,
            assessment_id=eligibility.assessment_id,
            environment_id=eligibility.environment_id,
            expected_model_id=eligibility.expected_model_id,
            observed_model_id=eligibility.observed_model_id,
            execution_status=eligibility.execution_status,
            feedback_status=eligibility.feedback_status,
            evaluation_status=eligibility.evaluation_status,
            integrity_status=eligibility.integrity_status,
            eligibility_status=eligibility.status,
            signal_status=eligibility.signal_status,
            confidence=eligibility.confidence,
            signal_fingerprint=eligibility.signal_fingerprint,
            upstream_proposal_fingerprint=eligibility.proposal_fingerprint,
            handoff_fingerprint=eligibility.handoff_fingerprint,
            result_fingerprint=eligibility.result_fingerprint,
            authority_principal_id=eligibility.authority_principal_id,
            executor_id=eligibility.executor_id,
            failure_reason=eligibility.failure_reason,
            proposal_kind=kind,
            proposal_status=status,
            proposal_payload=payload,
            reasons=reasons if reasons is not None else {"status": default_reason},
            lineage=lineage if lineage is not None else {"proposal_id": proposal_id, "eligibility_id": eligibility.eligibility_id, "integrity_id": eligibility.integrity_id, "signal_id": eligibility.signal_id, "evaluation_id": eligibility.evaluation_id, "feedback_id": eligibility.feedback_id, "classification_id": eligibility.classification_id, "outcome_id": eligibility.outcome_id, "decision_id": eligibility.decision_id},
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Service",
]
