"""M23.93: advisory adaptation proposal derived from application-learning eligibility v4."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_eligibility_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningEligibilityV4,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningEligibilityV4Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Error(RuntimeError):
    """Raised when an application-learning adaptation proposal cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status(str, Enum):
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
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4:
    """Immutable advisory proposal evidence derived from one M23.92 artifact."""

    proposal_id: str
    eligibility_id: str
    integrity_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    feedback_source_id: str
    classification_id: str
    source_integrity_id: str
    application_id: str
    source_decision_id: str
    source_proposal_id: str
    outcome_id: str
    outcome_status: Any
    feedback_status: Any
    confidence: float
    signal_fingerprint: str
    source_signal_fingerprint: str
    result_fingerprint: str
    application_fingerprint: str
    failure_reason: str | None
    evaluation_status: Any
    signal_status: Any
    integrity_status: Any
    eligibility_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningEligibilityV4Status
    proposal_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status
    proposal_kind: str
    proposal_payload: Mapping[str, Any] | None = None
    reasons: Mapping[str, Any] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = (
            "proposal_id", "eligibility_id", "integrity_id", "signal_id", "evaluation_id", "feedback_id",
            "feedback_source_id", "classification_id", "source_integrity_id", "application_id", "source_decision_id",
            "source_proposal_id", "outcome_id", "signal_fingerprint", "source_signal_fingerprint",
            "result_fingerprint", "application_fingerprint", "proposal_kind",
        )
        for name in required:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        if self.failure_reason is not None and (not isinstance(self.failure_reason, str) or not self.failure_reason.strip()):
            raise ValueError("failure_reason must be None or a non-empty string")
        if not isinstance(
            self.eligibility_status,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningEligibilityV4Status,
        ):
            raise TypeError("eligibility_status must be an application-learning eligibility v4 status")
        if not isinstance(
            self.proposal_status,
            EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status,
        ):
            raise TypeError("proposal_status must be an application-learning adaptation proposal v4 status")
        expected_kind = (
            "ADAPTATION_CANDIDATE"
            if self.proposal_status
            is EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status.PROPOSED
            else "BLOCKED_ADAPTATION_CANDIDATE"
        )
        if self.proposal_kind != expected_kind:
            raise ValueError("proposal kind does not match proposal status")
        if self.proposal_status is EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status.PROPOSED:
            if not isinstance(self.proposal_payload, Mapping):
                raise ValueError("PROPOSED proposal requires a mapping payload")
        elif self.proposal_payload is not None:
            raise ValueError("BLOCKED proposal cannot carry a proposal payload")
        for name in ("signal_fingerprint", "source_signal_fingerprint", "result_fingerprint", "application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("adaptation proposal requires SHA-256 fingerprints")
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
    def grants_authority(self) -> bool:
        return False

    @property
    def is_learning(self) -> bool:
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
    def executes_action(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Service:
    """Create inert application-learning adaptation proposal evidence."""

    def propose(
        self,
        eligibility: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningEligibilityV4,
        *,
        proposal_id: str,
        proposal_payload: Mapping[str, Any] | None = None,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4:
        if type(eligibility) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningEligibilityV4:
            raise TypeError("eligibility must be an application-learning eligibility v4 artifact")
        if not isinstance(proposal_id, str) or not proposal_id.strip():
            raise ValueError("proposal_id must be a non-empty string")
        proposed = eligibility.status is EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningEligibilityV4Status.ELIGIBLE
        if proposed:
            if not isinstance(proposal_payload, Mapping):
                raise ValueError("eligible evidence requires a mapping proposal_payload")
            status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status.PROPOSED
            kind = "ADAPTATION_CANDIDATE"
            default_reason = "eligible application-learning evidence permits an adaptation candidate proposal"
            payload = proposal_payload
        else:
            status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status.BLOCKED
            kind = "BLOCKED_ADAPTATION_CANDIDATE"
            default_reason = "ineligible application-learning evidence blocks adaptation proposal formation"
            payload = None
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4(
            proposal_id=proposal_id,
            eligibility_id=eligibility.eligibility_id,
            integrity_id=eligibility.integrity_id,
            signal_id=eligibility.signal_id,
            evaluation_id=eligibility.evaluation_id,
            feedback_id=eligibility.feedback_id,
            feedback_source_id=eligibility.feedback_source_id,
            classification_id=eligibility.classification_id,
            source_integrity_id=eligibility.source_integrity_id,
            application_id=eligibility.application_id,
            source_decision_id=eligibility.decision_id,
            source_proposal_id=eligibility.proposal_id,
            outcome_id=eligibility.outcome_id,
            outcome_status=eligibility.outcome_status,
            feedback_status=eligibility.feedback_status,
            confidence=eligibility.confidence,
            signal_fingerprint=eligibility.signal_fingerprint,
            source_signal_fingerprint=eligibility.source_signal_fingerprint,
            result_fingerprint=eligibility.result_fingerprint,
            application_fingerprint=eligibility.application_fingerprint,
            failure_reason=eligibility.failure_reason,
            evaluation_status=eligibility.evaluation_status,
            signal_status=eligibility.signal_status,
            integrity_status=eligibility.integrity_status,
            eligibility_status=eligibility.status,
            proposal_status=status,
            proposal_kind=kind,
            proposal_payload=payload,
            reasons=reasons if reasons is not None else {"status": default_reason},
            lineage=lineage if lineage is not None else {
                "proposal_id": proposal_id,
                "eligibility_id": eligibility.eligibility_id,
                "integrity_id": eligibility.integrity_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Service",
]
