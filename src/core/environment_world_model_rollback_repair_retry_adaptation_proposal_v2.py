"""M23.61: advisory adaptation proposal derived from learning eligibility."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_learning_eligibility_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2,
    EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_learning_signal_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Error(RuntimeError):
    """Raised when an adaptation proposal cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status(str, Enum):
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
class EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2:
    """Immutable advisory proposal for future adaptation consideration."""

    proposal_id: str
    eligibility_id: str
    integrity_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    outcome_id: str
    execution_id: str
    preparation_id: str
    decision_id: str
    source_proposal_id: str
    assessment_id: str | None
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    eligibility_status: EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status
    signal_status: EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status
    confidence: float
    signal_fingerprint: str
    proposal_kind: str
    proposal_status: EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status
    proposal_payload: Mapping[str, Any] | None = None
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "proposal_id", "eligibility_id", "integrity_id", "signal_id", "evaluation_id",
            "feedback_id", "outcome_id", "execution_id", "preparation_id", "decision_id",
            "source_proposal_id", "environment_id", "expected_model_id", "observed_model_id",
            "signal_fingerprint", "proposal_kind",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.assessment_id is not None and (
            not isinstance(self.assessment_id, str) or not self.assessment_id.strip()
        ):
            raise ValueError("assessment_id must be None or a non-empty string")
        if not isinstance(self.eligibility_status, EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status):
            raise TypeError("eligibility_status must be a learning-eligibility v2 status")
        if not isinstance(self.signal_status, EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status):
            raise TypeError("signal_status must be a learning-signal v2 status")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not isinstance(self.proposal_status, EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status):
            raise TypeError("proposal_status must be an adaptation-proposal v2 status")
        if self.proposal_status == EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.PROPOSED:
            if self.eligibility_status != EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.ELIGIBLE:
                raise ValueError("PROPOSED requires ELIGIBLE learning evidence")
            if self.proposal_payload is None or not isinstance(self.proposal_payload, Mapping):
                raise ValueError("PROPOSED requires a proposal payload mapping")
        elif self.proposal_status == EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.BLOCKED:
            if self.eligibility_status != EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.INELIGIBLE:
                raise ValueError("BLOCKED requires INELIGIBLE learning evidence")
            if self.proposal_payload is not None:
                raise ValueError("BLOCKED proposals cannot contain a proposal payload")
        if not isinstance(self.reasons, Mapping):
            raise TypeError("reasons must be a mapping")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        if self.proposal_payload is not None:
            object.__setattr__(self, "proposal_payload", _freeze(self.proposal_payload))
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


class EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Service:
    """Create an inert adaptation proposal from one exact eligibility artifact."""

    def propose(
        self,
        eligibility: EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2,
        *,
        proposal_id: str,
        proposal_payload: Mapping[str, Any] | None = None,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2:
        if type(eligibility) is not EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2:
            raise TypeError(
                "eligibility must be EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2"
            )
        if not isinstance(proposal_id, str) or not proposal_id.strip():
            raise ValueError("proposal_id must be a non-empty string")

        if eligibility.eligibility_status == EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.ELIGIBLE:
            if proposal_payload is None or not isinstance(proposal_payload, Mapping):
                raise ValueError("ELIGIBLE evidence requires an explicit proposal payload mapping")
            proposal_status = EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.PROPOSED
            proposal_kind = "ADAPTATION_CANDIDATE"
            default_reason = "eligible learning evidence supports an advisory adaptation proposal"
        elif eligibility.eligibility_status == EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.INELIGIBLE:
            proposal_status = EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.BLOCKED
            proposal_kind = "BLOCKED_ADAPTATION_CANDIDATE"
            default_reason = "learning evidence is ineligible; adaptation proposal is blocked"
            proposal_payload = None
        else:
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Error(
                "unsupported learning eligibility status"
            )

        return EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2(
            proposal_id=proposal_id,
            eligibility_id=eligibility.eligibility_id,
            integrity_id=eligibility.integrity_id,
            signal_id=eligibility.signal_id,
            evaluation_id=eligibility.evaluation_id,
            feedback_id=eligibility.feedback_id,
            outcome_id=eligibility.outcome_id,
            execution_id=eligibility.execution_id,
            preparation_id=eligibility.preparation_id,
            decision_id=eligibility.decision_id,
            source_proposal_id=proposal_id,
            assessment_id=eligibility.assessment_id,
            environment_id=eligibility.environment_id,
            expected_model_id=eligibility.expected_model_id,
            observed_model_id=eligibility.observed_model_id,
            eligibility_status=eligibility.eligibility_status,
            signal_status=eligibility.signal_status,
            confidence=eligibility.confidence,
            signal_fingerprint=eligibility.signal_fingerprint,
            proposal_kind=proposal_kind,
            proposal_status=proposal_status,
            proposal_payload=proposal_payload,
            reasons=reasons or {"status": default_reason},
            lineage=lineage or {
                "proposal_id": proposal_id,
                "eligibility_id": eligibility.eligibility_id,
                "integrity_id": eligibility.integrity_id,
                "signal_id": eligibility.signal_id,
                "evaluation_id": eligibility.evaluation_id,
                "feedback_id": eligibility.feedback_id,
                "outcome_id": eligibility.outcome_id,
                "execution_id": eligibility.execution_id,
                "preparation_id": eligibility.preparation_id,
                "decision_id": eligibility.decision_id,
                "assessment_id": eligibility.assessment_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Service",
]
