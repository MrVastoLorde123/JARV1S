"""M23.84: immutable decision evidence for application-learning adaptation proposals v3."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_proposal_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Error(RuntimeError):
    """Raised when application-learning adaptation decision evidence cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status(str, Enum):
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
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3:
    """Immutable advisory decision evidence; no authorization or execution is created."""

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
    application_id: str
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
    decision_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status
    decision_basis: Mapping[str, Any]
    reasons: Mapping[str, Any] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required=(
            "decision_id","proposal_id","source_proposal_id","eligibility_id","eligibility_source_id","integrity_id",
            "signal_id","evaluation_id","feedback_id","classification_id","application_id","source_integrity_id",
            "feedback_signal_id","feedback_source_id","source_evaluation_id","execution_id","handoff_id","authorization_id",
            "validation_id","source_signal_id","outcome_id","preparation_id","environment_id","expected_model_id",
            "observed_model_id","proposal_kind","signal_fingerprint","upstream_proposal_fingerprint","handoff_fingerprint",
            "result_fingerprint","application_fingerprint",
        )
        for name in required:
            value=getattr(self,name)
            if not isinstance(value,str) or not value.strip(): raise ValueError(f"{name} must be a non-empty string")
        for name in ("assessment_id","authority_principal_id","executor_id"):
            value=getattr(self,name)
            if value is not None and (not isinstance(value,str) or not value.strip()): raise ValueError(f"{name} must be None or a non-empty string")
        if isinstance(self.confidence,bool) or not isinstance(self.confidence,(int,float)) or not 0.0 <= float(self.confidence) <= 1.0: raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        if self.failure_reason is not None and (not isinstance(self.failure_reason,str) or not self.failure_reason.strip()): raise ValueError("failure_reason must be None or a non-empty string")
        if not isinstance(self.proposal_status,EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Status): raise TypeError("proposal_status must be an application-learning adaptation proposal v3 status")
        if not isinstance(self.decision_status,EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status): raise TypeError("decision_status must be an application-learning adaptation decision v3 status")
        expected=(EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.BLOCKED if self.proposal_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Status.BLOCKED else self.decision_status)
        if self.proposal_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Status.BLOCKED and expected != self.decision_status: raise ValueError("blocked proposals must produce BLOCKED decisions")
        if self.proposal_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Status.PROPOSED and self.decision_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.BLOCKED: raise ValueError("proposed adaptations cannot produce BLOCKED decisions")
        if not isinstance(self.decision_basis,Mapping): raise TypeError("decision_basis must be a mapping")
        if not isinstance(self.reasons,Mapping) or not isinstance(self.lineage,Mapping): raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self,"decision_basis",_freeze(self.decision_basis))
        object.__setattr__(self,"reasons",_freeze(self.reasons))
        object.__setattr__(self,"lineage",_freeze(self.lineage))

    @property
    def is_advisory_only(self)->bool: return True
    @property
    def authorizes_adaptation(self)->bool: return False
    @property
    def grants_authority(self)->bool: return False
    @property
    def updates_model(self)->bool: return False
    @property
    def mutates_memory(self)->bool: return False
    @property
    def mutates_policy(self)->bool: return False
    @property
    def mutates_persistence(self)->bool: return False
    @property
    def schedules_work(self)->bool: return False
    @property
    def executes_action(self)->bool: return False


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Service:
    """Turn one proposal into bounded decision evidence without authorizing adaptation."""

    def decide(self, proposal: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3, *, decision_id: str, accept: bool=False, decision_basis: Mapping[str,Any]|None=None, reasons: Mapping[str,Any]|None=None, lineage: Mapping[str,Any]|None=None) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3:
        if type(proposal) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3: raise TypeError("proposal must be an application-learning adaptation proposal v3 artifact")
        if not isinstance(decision_id,str) or not decision_id.strip(): raise ValueError("decision_id must be a non-empty string")
        if proposal.proposal_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationProposalV3Status.BLOCKED:
            status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.BLOCKED
            basis={"source_status":"BLOCKED","decision":"adaptation candidate remains blocked"}
        else:
            status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.ACCEPTED if accept else EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status.REJECTED
            basis={"source_status":"PROPOSED","decision":status.value}
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3(
            decision_id=decision_id, proposal_id=proposal.proposal_id, source_proposal_id=proposal.source_proposal_id,
            eligibility_id=proposal.eligibility_id, eligibility_source_id=proposal.eligibility_source_id, integrity_id=proposal.integrity_id,
            signal_id=proposal.signal_id, evaluation_id=proposal.evaluation_id, feedback_id=proposal.feedback_id,
            classification_id=proposal.classification_id, application_id=proposal.application_id, source_integrity_id=proposal.source_integrity_id,
            feedback_signal_id=proposal.feedback_signal_id, feedback_source_id=proposal.feedback_source_id, source_evaluation_id=proposal.source_evaluation_id,
            execution_id=proposal.execution_id, handoff_id=proposal.handoff_id, authorization_id=proposal.authorization_id, validation_id=proposal.validation_id,
            source_signal_id=proposal.source_signal_id, outcome_id=proposal.outcome_id, preparation_id=proposal.preparation_id, assessment_id=proposal.assessment_id,
            environment_id=proposal.environment_id, expected_model_id=proposal.expected_model_id, observed_model_id=proposal.observed_model_id,
            proposal_kind=proposal.proposal_kind, proposal_status=proposal.proposal_status, source_application_status=proposal.source_application_status,
            source_decision_status=proposal.source_decision_status, source_outcome_status=proposal.source_outcome_status, source_feedback_status=proposal.source_feedback_status,
            source_evaluation_status=proposal.source_evaluation_status, source_signal_status=proposal.source_signal_status, confidence=proposal.confidence,
            signal_fingerprint=proposal.signal_fingerprint, upstream_proposal_fingerprint=proposal.upstream_proposal_fingerprint,
            handoff_fingerprint=proposal.handoff_fingerprint, result_fingerprint=proposal.result_fingerprint, application_fingerprint=proposal.application_fingerprint,
            authority_principal_id=proposal.authority_principal_id, executor_id=proposal.executor_id, failure_reason=proposal.failure_reason,
            decision_status=status, decision_basis=decision_basis if decision_basis is not None else basis,
            reasons=reasons if reasons is not None else {"decision":status.value},
            lineage=lineage if lineage is not None else {"decision_id":decision_id,"proposal_id":proposal.proposal_id,"eligibility_id":proposal.eligibility_id},
        )


__all__=[
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationDecisionV3Service",
]
