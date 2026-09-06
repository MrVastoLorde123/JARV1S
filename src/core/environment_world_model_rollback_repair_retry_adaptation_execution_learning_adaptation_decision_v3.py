"""M23.74: immutable adaptation decision evidence derived from a v3 proposal."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_proposal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Error(RuntimeError):
    """Raised when a safe adaptation decision cannot be formed."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(k): _freeze(v) for k, v in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(v) for v in value)
    if isinstance(value, tuple):
        return tuple(_freeze(v) for v in value)
    if isinstance(value, set):
        return frozenset(_freeze(v) for v in value)
    return value


@dataclass(frozen=True)
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3:
    """Immutable decision evidence; it does not authorize or execute adaptation."""

    decision_id: str
    proposal_id: str
    source_proposal_id: str
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
    source_integrity_id: str
    assessment_id: str | None
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    execution_status: Any
    feedback_status: Any
    evaluation_status: Any
    integrity_status: Any
    eligibility_status: Any
    signal_status: Any
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
    decision_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status
    decision_basis: Mapping[str, Any]
    reasons: Mapping[str, Any] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = (
            "decision_id", "proposal_id", "source_proposal_id", "eligibility_id", "integrity_id", "signal_id",
            "evaluation_id", "feedback_id", "classification_id", "execution_id", "handoff_id",
            "authorization_id", "validation_id", "source_signal_id", "outcome_id", "preparation_id",
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
        if not isinstance(self.proposal_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status):
            raise TypeError("proposal_status must be an adaptation-proposal v3 status")
        if not isinstance(self.decision_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status):
            raise TypeError("decision_status must be an adaptation-decision v3 status")
        if not isinstance(self.decision_basis, Mapping):
            raise TypeError("decision_basis must be a mapping")
        if self.proposal_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.BLOCKED:
            if self.decision_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.BLOCKED:
                raise ValueError("blocked proposals must produce BLOCKED decisions")
        elif self.decision_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.BLOCKED:
            raise ValueError("proposed adaptations cannot produce a BLOCKED decision")
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
    def requests_adaptation_execution(self) -> bool:
        return False

    @property
    def grants_authority(self) -> bool:
        return False

    @property
    def executes(self) -> bool:
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


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Service:
    """Turn one adaptation proposal into inert decision evidence."""

    def decide(
        self,
        proposal: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3,
        *,
        decision_id: str,
        accept: bool = False,
        decision_basis: Mapping[str, Any] | None = None,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3:
        if type(proposal) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3:
            raise TypeError("proposal must be an adaptation-proposal v3 artifact")
        if not isinstance(decision_id, str) or not decision_id.strip():
            raise ValueError("decision_id must be a non-empty string")
        if proposal.proposal_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationProposalV3Status.BLOCKED:
            status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.BLOCKED
            default_basis = {"source_status": "BLOCKED", "decision": "adaptation candidate remains blocked"}
        else:
            status = (
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.ACCEPTED
                if accept else
                EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.REJECTED
            )
            default_basis = {"source_status": "PROPOSED", "decision": status.value}
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3(
            decision_id=decision_id,
            proposal_id=proposal.proposal_id,
            source_proposal_id=proposal.source_proposal_id,
            eligibility_id=proposal.eligibility_id,
            integrity_id=proposal.integrity_id,
            signal_id=proposal.signal_id,
            evaluation_id=proposal.evaluation_id,
            feedback_id=proposal.feedback_id,
            classification_id=proposal.classification_id,
            execution_id=proposal.execution_id,
            handoff_id=proposal.handoff_id,
            authorization_id=proposal.authorization_id,
            validation_id=proposal.validation_id,
            source_signal_id=proposal.source_signal_id,
            outcome_id=proposal.outcome_id,
            preparation_id=proposal.preparation_id,
            source_integrity_id=proposal.source_integrity_id,
            assessment_id=proposal.assessment_id,
            environment_id=proposal.environment_id,
            expected_model_id=proposal.expected_model_id,
            observed_model_id=proposal.observed_model_id,
            execution_status=proposal.execution_status,
            feedback_status=proposal.feedback_status,
            evaluation_status=proposal.evaluation_status,
            integrity_status=proposal.integrity_status,
            eligibility_status=proposal.eligibility_status,
            signal_status=proposal.signal_status,
            confidence=proposal.confidence,
            signal_fingerprint=proposal.signal_fingerprint,
            upstream_proposal_fingerprint=proposal.upstream_proposal_fingerprint,
            handoff_fingerprint=proposal.handoff_fingerprint,
            result_fingerprint=proposal.result_fingerprint,
            authority_principal_id=proposal.authority_principal_id,
            executor_id=proposal.executor_id,
            failure_reason=proposal.failure_reason,
            proposal_kind=proposal.proposal_kind,
            proposal_status=proposal.proposal_status,
            decision_status=status,
            decision_basis=decision_basis if decision_basis is not None else default_basis,
            reasons=reasons if reasons is not None else {"decision": status.value},
            lineage=lineage if lineage is not None else {"decision_id": decision_id, "proposal_id": proposal.proposal_id, "source_proposal_id": proposal.source_proposal_id},
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Service",
]
