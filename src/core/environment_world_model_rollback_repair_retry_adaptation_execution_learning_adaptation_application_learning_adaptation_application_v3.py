"""M23.85: bounded application of learning-adaptation decisions to internal learning state."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_decision_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_proposal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Error(RuntimeError):
    """Raised when bounded learning-adaptation application cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status(str, Enum):
    APPLIED = "APPLIED"
    NOT_APPLIED = "NOT_APPLIED"
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


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationLearningApplierV3(Protocol):
    """Replaceable adapter for the bounded internal learning-state target."""

    def apply(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        ...


@dataclass(frozen=True)
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3:
    """Immutable evidence of one bounded learning-adaptation application."""

    application_id: str
    decision_id: str
    proposal_id: str
    source_proposal_id: str
    eligibility_id: str
    eligibility_source_id: str
    integrity_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    classification_id: str
    application_source_id: str
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
    decision_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status
    application_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status
    applied_learning_update: Mapping[str, Any] | None
    application_result: Mapping[str, Any] | None
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
    reasons: Mapping[str, Any] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = (
            "application_id", "decision_id", "proposal_id", "source_proposal_id", "eligibility_id", "eligibility_source_id",
            "integrity_id", "signal_id", "evaluation_id", "feedback_id", "classification_id", "application_source_id",
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
        if not isinstance(self.decision_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status):
            raise TypeError("decision_status must be an application-learning adaptation decision v3 status")
        if not isinstance(self.application_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status):
            raise TypeError("application_status must be an application-learning adaptation application v3 status")
        if self.decision_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.BLOCKED and self.application_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.BLOCKED:
            raise ValueError("blocked decisions must produce BLOCKED applications")
        if self.decision_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.REJECTED and self.application_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.NOT_APPLIED:
            raise ValueError("rejected decisions must produce NOT_APPLIED applications")
        if self.application_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.APPLIED:
            if not isinstance(self.applied_learning_update, Mapping) or not isinstance(self.application_result, Mapping):
                raise ValueError("APPLIED applications require learning update and result mappings")
            if self.failure_reason is not None:
                raise ValueError("APPLIED applications cannot carry a failure reason")
        else:
            if self.applied_learning_update is not None or self.application_result is not None:
                raise ValueError("non-applied applications cannot carry learning update or result")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "applied_learning_update", None if self.applied_learning_update is None else _freeze(self.applied_learning_update))
        object.__setattr__(self, "application_result", None if self.application_result is None else _freeze(self.application_result))
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def mutates_learning_state(self) -> bool:
        return self.application_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.APPLIED

    @property
    def authorizes_adaptation(self) -> bool:
        return False

    @property
    def grants_authority(self) -> bool:
        return False

    @property
    def executes_capability(self) -> bool:
        return False

    @property
    def schedules_work(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Service:
    """Apply only accepted learning-adaptation proposals through a bounded internal applier."""

    def apply(
        self,
        decision: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3,
        proposal: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3,
        *,
        application_id: str,
        learning_applier: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationLearningApplierV3 | None = None,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3:
        if type(decision) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3:
            raise TypeError("decision must be an application-learning adaptation decision v3 artifact")
        if type(proposal) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3:
            raise TypeError("proposal must be an application-learning adaptation proposal v3 artifact")
        if not isinstance(application_id, str) or not application_id.strip():
            raise ValueError("application_id must be a non-empty string")
        if decision.proposal_id != proposal.proposal_id or decision.source_proposal_id != proposal.source_proposal_id:
            raise ValueError("decision and proposal identities must match")
        if decision.proposal_status != proposal.proposal_status:
            raise ValueError("decision and proposal statuses must match")
        if decision.proposal_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Status.PROPOSED and proposal.proposal_payload is None:
            raise ValueError("proposed learning adaptation must carry a proposal payload")
        if decision.decision_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.BLOCKED:
            return self._result(decision, proposal, application_id, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.BLOCKED, None, None, None, reasons, lineage)
        if decision.decision_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.REJECTED:
            return self._result(decision, proposal, application_id, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.NOT_APPLIED, None, None, None, reasons, lineage)
        if learning_applier is None:
            raise ValueError("accepted learning adaptation requires a learning_applier")
        try:
            result = learning_applier.apply(proposal.proposal_payload)
            if not isinstance(result, Mapping):
                raise TypeError("learning applier result must be a mapping")
        except Exception as exc:
            return self._result(decision, proposal, application_id, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.NOT_APPLIED, None, None, str(exc), reasons, lineage)
        return self._result(decision, proposal, application_id, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status.APPLIED, proposal.proposal_payload, result, None, reasons, lineage)

    @staticmethod
    def _result(
        decision: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3,
        proposal: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3,
        application_id: str,
        status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status,
        applied_learning_update: Mapping[str, Any] | None,
        application_result: Mapping[str, Any] | None,
        failure_reason: str | None,
        reasons: Mapping[str, Any] | None,
        lineage: Mapping[str, Any] | None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3:
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3(
            application_id=application_id,
            decision_id=decision.decision_id,
            proposal_id=proposal.proposal_id,
            source_proposal_id=proposal.source_proposal_id,
            eligibility_id=proposal.eligibility_id,
            eligibility_source_id=proposal.eligibility_source_id,
            integrity_id=proposal.integrity_id,
            signal_id=proposal.signal_id,
            evaluation_id=proposal.evaluation_id,
            feedback_id=proposal.feedback_id,
            classification_id=proposal.classification_id,
            application_source_id=proposal.proposal_id,
            source_integrity_id=proposal.source_integrity_id,
            feedback_signal_id=proposal.feedback_signal_id,
            feedback_source_id=proposal.feedback_source_id,
            source_evaluation_id=proposal.source_evaluation_id,
            execution_id=proposal.execution_id,
            handoff_id=proposal.handoff_id,
            authorization_id=proposal.authorization_id,
            validation_id=proposal.validation_id,
            source_signal_id=proposal.source_signal_id,
            outcome_id=proposal.outcome_id,
            preparation_id=proposal.preparation_id,
            assessment_id=proposal.assessment_id,
            environment_id=proposal.environment_id,
            expected_model_id=proposal.expected_model_id,
            observed_model_id=proposal.observed_model_id,
            proposal_kind=proposal.proposal_kind,
            proposal_status=proposal.proposal_status,
            decision_status=decision.decision_status,
            application_status=status,
            applied_learning_update=applied_learning_update,
            application_result=application_result,
            source_signal_status=proposal.source_signal_status,
            confidence=proposal.confidence,
            signal_fingerprint=proposal.signal_fingerprint,
            upstream_proposal_fingerprint=proposal.upstream_proposal_fingerprint,
            handoff_fingerprint=proposal.handoff_fingerprint,
            result_fingerprint=proposal.result_fingerprint,
            application_fingerprint=proposal.application_fingerprint,
            authority_principal_id=proposal.authority_principal_id,
            executor_id=proposal.executor_id,
            failure_reason=failure_reason,
            reasons=reasons if reasons is not None else {"application": status.value},
            lineage=lineage if lineage is not None else {"application_id": application_id, "decision_id": decision.decision_id, "proposal_id": proposal.proposal_id},
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationLearningApplierV3",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationV3Service",
]
