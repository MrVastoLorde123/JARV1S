"""M23.95: explicit application boundary for accepted adaptation decisions v4."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_decision_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_learning_adaptation_application_learning_adaptation_proposal_v4 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Error(RuntimeError):
    """Raised when adaptation application evidence cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Status(str, Enum):
    APPLIED = "APPLIED"
    NOT_APPLIED = "NOT_APPLIED"
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
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4:
    """Immutable evidence emitted by the explicit adaptation-application boundary."""

    application_id: str
    decision_id: str
    proposal_id: str
    source_proposal_id: str
    eligibility_id: str
    integrity_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    feedback_source_id: str
    classification_id: str
    source_integrity_id: str
    source_decision_id: str
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
    proposal_status: Any
    proposal_kind: str
    decision_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status
    application_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Status
    application_result: Mapping[str, Any] | None = None
    reasons: Mapping[str, Any] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = (
            "application_id", "decision_id", "proposal_id", "source_proposal_id", "eligibility_id", "integrity_id",
            "signal_id", "evaluation_id", "feedback_id", "feedback_source_id", "classification_id",
            "source_integrity_id", "source_decision_id", "outcome_id", "signal_fingerprint",
            "source_signal_fingerprint", "result_fingerprint", "application_fingerprint", "proposal_kind",
        )
        for name in required:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be numeric and between 0.0 and 1.0")
        if self.failure_reason is not None and (not isinstance(self.failure_reason, str) or not self.failure_reason.strip()):
            raise ValueError("failure_reason must be None or a non-empty string")
        if not isinstance(self.decision_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status):
            raise TypeError("decision_status must be an application-learning adaptation decision v4 status")
        if not isinstance(self.application_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Status):
            raise TypeError("application_status must be an application-learning adaptation application v4 status")
        if self.decision_status is EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status.BLOCKED and self.application_status is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Status.BLOCKED:
            raise ValueError("BLOCKED decisions must produce BLOCKED application evidence")
        if self.decision_status is EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status.REJECTED and self.application_status is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Status.REJECTED:
            raise ValueError("REJECTED decisions must produce REJECTED application evidence")
        if self.application_status is EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Status.APPLIED:
            if self.decision_status is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status.ACCEPTED:
                raise ValueError("APPLIED evidence requires an ACCEPTED decision")
            if self.proposal_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status.PROPOSED:
                raise ValueError("APPLIED evidence requires a PROPOSED source proposal")
            if not isinstance(self.application_result, Mapping):
                raise TypeError("APPLIED evidence requires a mapping application_result")
        elif self.application_status is EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Status.NOT_APPLIED and self.decision_status is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status.ACCEPTED:
            raise ValueError("NOT_APPLIED evidence is reserved for accepted decisions that failed to apply")
        if self.application_status is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Status.APPLIED and self.application_result is not None:
            raise ValueError("non-APPLIED evidence cannot carry an application result")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        for name in ("signal_fingerprint", "source_signal_fingerprint", "result_fingerprint", "application_fingerprint"):
            if len(getattr(self, name)) != 64:
                raise ValueError("application evidence requires SHA-256 fingerprints")
        object.__setattr__(self, "application_result", None if self.application_result is None else _freeze(self.application_result))
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


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Service:
    """Apply accepted adaptation candidates only through an explicitly injected callable."""

    def apply(
        self,
        decision: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4,
        *,
        application_id: str,
        learning_applier: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4:
        if type(decision) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4:
            raise TypeError("decision must be an application-learning adaptation decision v4 artifact")
        if not isinstance(application_id, str) or not application_id.strip():
            raise ValueError("application_id must be a non-empty string")
        if decision.decision_status is EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status.BLOCKED:
            status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Status.BLOCKED
            result = None
            failure = "blocked adaptation decision cannot be applied"
        elif decision.decision_status is EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationDecisionV4Status.REJECTED:
            status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Status.REJECTED
            result = None
            failure = "rejected adaptation decision cannot be applied"
        elif decision.proposal_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationProposalV4Status.PROPOSED:
            status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Status.NOT_APPLIED
            result = None
            failure = "accepted decision requires a PROPOSED source proposal"
        elif learning_applier is None:
            status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Status.NOT_APPLIED
            result = None
            failure = "accepted adaptation decision requires an injected learning applier"
        else:
            try:
                source_payload = {
                    "decision_id": decision.decision_id,
                    "proposal_id": decision.proposal_id,
                    "eligibility_id": decision.eligibility_id,
                }
                applied = learning_applier(source_payload)
                if not isinstance(applied, Mapping):
                    raise TypeError("learning applier must return a mapping result")
                status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Status.APPLIED
                result = applied
                failure = None
            except Exception as exc:
                status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Status.NOT_APPLIED
                result = None
                failure = f"learning applier failed: {exc}"
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4(
            application_id=application_id, decision_id=decision.decision_id, proposal_id=decision.proposal_id,
            source_proposal_id=decision.source_proposal_id, eligibility_id=decision.eligibility_id, integrity_id=decision.integrity_id,
            signal_id=decision.signal_id, evaluation_id=decision.evaluation_id, feedback_id=decision.feedback_id,
            feedback_source_id=decision.feedback_source_id, classification_id=decision.classification_id,
            source_integrity_id=decision.source_integrity_id, source_decision_id=decision.source_decision_id,
            outcome_id=decision.outcome_id, outcome_status=decision.outcome_status, feedback_status=decision.feedback_status,
            confidence=decision.confidence, signal_fingerprint=decision.signal_fingerprint,
            source_signal_fingerprint=decision.source_signal_fingerprint, result_fingerprint=decision.result_fingerprint,
            application_fingerprint=decision.application_fingerprint, failure_reason=failure if failure is not None else decision.failure_reason,
            evaluation_status=decision.evaluation_status, signal_status=decision.signal_status, integrity_status=decision.integrity_status,
            eligibility_status=decision.eligibility_status, proposal_status=decision.proposal_status, proposal_kind=decision.proposal_kind,
            decision_status=decision.decision_status, application_status=status, application_result=result,
            reasons=reasons if reasons is not None else {"application_status": status.value},
            lineage=lineage if lineage is not None else {"application_id": application_id, "decision_id": decision.decision_id, "proposal_id": decision.proposal_id},
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationLearningAdaptationApplicationLearningAdaptationApplicationV4Service",
]