"""M23.94: immutable advisory decision evidence for application-learning adaptation proposals v4."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_proposal_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Error(RuntimeError):
    """Raised when application-learning adaptation decision evidence cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
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
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4:
    """Immutable advisory decision evidence derived from one M23.93 proposal."""

    decision_id: str
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
    eligibility_status: Any
    proposal_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status
    proposal_kind: str
    decision_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status
    decision_basis: Mapping[str, Any]
    reasons: Mapping[str, Any] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = (
            "decision_id", "proposal_id", "eligibility_id", "integrity_id", "signal_id", "evaluation_id", "feedback_id",
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
        if not isinstance(self.proposal_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status):
            raise TypeError("proposal_status must be an application-learning adaptation proposal v4 status")
        if not isinstance(self.decision_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status):
            raise TypeError("decision_status must be an application-learning adaptation decision v4 status")
        if self.proposal_status is EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status.BLOCKED and self.decision_status is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status.BLOCKED:
            raise ValueError("BLOCKED proposals must produce BLOCKED decisions")
        if self.proposal_status is EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status.PROPOSED and self.decision_status is EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status.BLOCKED:
            raise ValueError("PROPOSED proposals cannot produce BLOCKED decisions")
        if not isinstance(self.decision_basis, Mapping):
            raise TypeError("decision_basis must be a mapping")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        for name in ("signal_fingerprint", "source_signal_fingerprint", "result_fingerprint", "application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("decision evidence requires SHA-256 fingerprints")
        object.__setattr__(self, "decision_basis", _freeze(self.decision_basis))
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


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Service:
    """Turn one proposal into bounded decision evidence without authorizing adaptation."""

    def decide(
        self,
        proposal: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4,
        *,
        decision_id: str,
        accept: bool = False,
        decision_basis: Mapping[str, Any] | None = None,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4:
        if type(proposal) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4:
            raise TypeError("proposal must be an application-learning adaptation proposal v4 artifact")
        if not isinstance(decision_id, str) or not decision_id.strip():
            raise ValueError("decision_id must be a non-empty string")
        if proposal.proposal_status is EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status.BLOCKED:
            status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status.BLOCKED
            default_basis = {"source_status": "BLOCKED", "decision": "adaptation candidate remains blocked"}
        else:
            status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status.ACCEPTED if accept else EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status.REJECTED
            default_basis = {"source_status": "PROPOSED", "decision": status.value}
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4(
            decision_id=decision_id,
            proposal_id=proposal.proposal_id,
            eligibility_id=proposal.eligibility_id,
            integrity_id=proposal.integrity_id,
            signal_id=proposal.signal_id,
            evaluation_id=proposal.evaluation_id,
            feedback_id=proposal.feedback_id,
            feedback_source_id=proposal.feedback_source_id,
            classification_id=proposal.classification_id,
            source_integrity_id=proposal.source_integrity_id,
            application_id=proposal.application_id,
            source_decision_id=proposal.source_decision_id,
            source_proposal_id=proposal.source_proposal_id,
            outcome_id=proposal.outcome_id,
            outcome_status=proposal.outcome_status,
            feedback_status=proposal.feedback_status,
            confidence=proposal.confidence,
            signal_fingerprint=proposal.signal_fingerprint,
            source_signal_fingerprint=proposal.source_signal_fingerprint,
            result_fingerprint=proposal.result_fingerprint,
            application_fingerprint=proposal.application_fingerprint,
            failure_reason=proposal.failure_reason,
            evaluation_status=proposal.evaluation_status,
            signal_status=proposal.signal_status,
            integrity_status=proposal.integrity_status,
            eligibility_status=proposal.eligibility_status,
            proposal_status=proposal.proposal_status,
            proposal_kind=proposal.proposal_kind,
            decision_status=status,
            decision_basis=decision_basis if decision_basis is not None else default_basis,
            reasons=reasons if reasons is not None else {"decision": status.value},
            lineage=lineage if lineage is not None else {
                "decision_id": decision_id,
                "proposal_id": proposal.proposal_id,
                "eligibility_id": proposal.eligibility_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Service",
]
