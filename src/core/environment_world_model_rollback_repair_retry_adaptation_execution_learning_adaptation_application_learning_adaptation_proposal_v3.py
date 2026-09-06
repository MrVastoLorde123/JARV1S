"""M23.83: advisory adaptation proposal derived from application-learning eligibility v3."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_eligibility_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Error(RuntimeError):
    """Raised when an application-learning adaptation proposal cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Status(str, Enum):
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
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3:
    """Immutable advisory proposal evidence derived from one M23.82 artifact."""

    proposal_id: str
    eligibility_id: str
    eligibility_source_id: str
    integrity_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    classification_id: str
    application_id: str
    decision_id: str
    source_proposal_id: str
    source_integrity_id: str
    feedback_signal_id: str
    feedback_source_id: str
    source_evaluation_id: str
    execution_id: str
    handoff_id: str
    authorization_id: str
    validation_id: str
    source_signal_id: str
    outcome_id: str
    preparation_id: str
    assessment_id: str | None
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    proposal_kind: str
    proposal_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Status
    source_application_status: Any
    source_decision_status: Any
    source_outcome_status: Any
    source_feedback_status: Any
    source_evaluation_status: Any
    source_signal_status: Any
    confidence: float
    signal_fingerprint: str
    upstream_proposal_fingerprint: str
    handoff_fingerprint: str
    result_fingerprint: str
    application_fingerprint: str
    authority_principal_id: str | None
    executor_id: str | None
    failure_reason: str | None
    proposal_payload: Mapping[str, Any] | None = None
    reasons: Mapping[str, Any] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = (
            "proposal_id", "eligibility_id", "eligibility_source_id", "integrity_id", "signal_id", "evaluation_id",
            "feedback_id", "classification_id", "application_id", "decision_id", "source_proposal_id",
            "source_integrity_id", "feedback_signal_id", "feedback_source_id", "source_evaluation_id", "execution_id",
            "handoff_id", "authorization_id", "validation_id", "source_signal_id", "outcome_id", "preparation_id",
            "environment_id", "expected_model_id", "observed_model_id", "proposal_kind", "signal_fingerprint",
            "upstream_proposal_fingerprint", "handoff_fingerprint", "result_fingerprint", "application_fingerprint",
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
        if not isinstance(self.proposal_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Status):
            raise TypeError("proposal_status must be an application-learning adaptation proposal v3 status")
        expected_kind = (
            "ADAPTATION_CANDIDATE"
            if self.proposal_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Status.PROPOSED
            else "BLOCKED_ADAPTATION_CANDIDATE"
        )
        if self.proposal_kind != expected_kind:
            raise ValueError("proposal kind does not match proposal status")
        if self.proposal_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Status.PROPOSED:
            if not isinstance(self.proposal_payload, Mapping):
                raise ValueError("PROPOSED proposal requires a mapping payload")
        elif self.proposal_payload is not None:
            raise ValueError("BLOCKED proposal cannot carry a proposal payload")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "proposal_payload", None if self.proposal_payload is None else _freeze(self.proposal_payload))
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_advisory_only(self) -> bool: return True
    @property
    def authorizes_adaptation(self) -> bool: return False
    @property
    def grants_authority(self) -> bool: return False
    @property
    def updates_model(self) -> bool: return False
    @property
    def mutates_memory(self) -> bool: return False
    @property
    def mutates_policy(self) -> bool: return False
    @property
    def mutates_persistence(self) -> bool: return False
    @property
    def schedules_work(self) -> bool: return False
    @property
    def executes_action(self) -> bool: return False


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Service:
    """Create inert application-learning adaptation proposal evidence."""

    def propose(
        self,
        eligibility: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3,
        *,
        proposal_id: str,
        proposal_payload: Mapping[str, Any] | None = None,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3:
        if type(eligibility) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3:
            raise TypeError("eligibility must be an application-learning eligibility v3 artifact")
        if not isinstance(proposal_id, str) or not proposal_id.strip():
            raise ValueError("proposal_id must be a non-empty string")
        proposed = eligibility.status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningEligibilityV3Status.ELIGIBLE
        if proposed:
            if not isinstance(proposal_payload, Mapping):
                raise ValueError("eligible evidence requires a mapping proposal_payload")
            status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Status.PROPOSED
            kind = "ADAPTATION_CANDIDATE"
            default_reason = "eligible application-learning evidence permits an adaptation candidate proposal"
            payload = proposal_payload
        else:
            status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Status.BLOCKED
            kind = "BLOCKED_ADAPTATION_CANDIDATE"
            default_reason = "ineligible application-learning evidence blocks adaptation proposal formation"
            payload = None
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3(
            proposal_id=proposal_id,
            eligibility_id=eligibility.eligibility_id,
            eligibility_source_id=eligibility.eligibility_source_id,
            integrity_id=eligibility.integrity_id,
            signal_id=eligibility.signal_id,
            evaluation_id=eligibility.evaluation_id,
            feedback_id=eligibility.feedback_id,
            classification_id=eligibility.classification_id,
            application_id=eligibility.application_id,
            decision_id=eligibility.decision_id,
            source_proposal_id=eligibility.proposal_id,
            source_integrity_id=eligibility.integrity_id,
            feedback_signal_id=eligibility.feedback_signal_id,
            feedback_source_id=eligibility.feedback_source_id,
            source_evaluation_id=eligibility.source_evaluation_id,
            execution_id=eligibility.execution_id,
            handoff_id=eligibility.handoff_id,
            authorization_id=eligibility.authorization_id,
            validation_id=eligibility.validation_id,
            source_signal_id=eligibility.source_signal_id,
            outcome_id=eligibility.outcome_id,
            preparation_id=eligibility.preparation_id,
            assessment_id=eligibility.assessment_id,
            environment_id=eligibility.environment_id,
            expected_model_id=eligibility.expected_model_id,
            observed_model_id=eligibility.observed_model_id,
            proposal_kind=kind,
            proposal_status=status,
            source_application_status=eligibility.application_status,
            source_decision_status=eligibility.decision_status,
            source_outcome_status=eligibility.outcome_status,
            source_feedback_status=eligibility.feedback_status,
            source_evaluation_status=eligibility.evaluation_status,
            source_signal_status=eligibility.signal_status,
            confidence=eligibility.confidence,
            signal_fingerprint=eligibility.signal_fingerprint,
            upstream_proposal_fingerprint=eligibility.upstream_proposal_fingerprint,
            handoff_fingerprint=eligibility.handoff_fingerprint,
            result_fingerprint=eligibility.result_fingerprint,
            application_fingerprint=eligibility.application_fingerprint,
            authority_principal_id=eligibility.authority_principal_id,
            executor_id=eligibility.executor_id,
            failure_reason=eligibility.failure_reason,
            proposal_payload=payload,
            reasons=reasons if reasons is not None else {"status": default_reason},
            lineage=lineage if lineage is not None else {
                "proposal_id": proposal_id,
                "eligibility_id": eligibility.eligibility_id,
                "eligibility_source_id": eligibility.eligibility_source_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Service",
]
