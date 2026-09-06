"""M23.76: integrity boundary for one bounded adaptation application."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_application_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_learning_adaptation_decision_v3 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Error(RuntimeError):
    """Raised when adaptation-application integrity evidence cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


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


def _canonical(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _canonical(value[key]) for key in sorted(value, key=lambda item: str(item))}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if isinstance(value, (set, frozenset)):
        normalized = [_canonical(item) for item in value]
        return sorted(
            normalized,
            key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False),
        )
    return value


def _fingerprint(value: Mapping[str, Any]) -> str:
    payload = json.dumps(
        _canonical(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _application_representation(application: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3) -> dict[str, Any]:
    return {
        "application_id": application.application_id,
        "decision_id": application.decision_id,
        "proposal_id": application.proposal_id,
        "source_proposal_id": application.source_proposal_id,
        "eligibility_id": application.eligibility_id,
        "integrity_id": application.integrity_id,
        "signal_id": application.signal_id,
        "evaluation_id": application.evaluation_id,
        "feedback_id": application.feedback_id,
        "classification_id": application.classification_id,
        "execution_id": application.execution_id,
        "handoff_id": application.handoff_id,
        "authorization_id": application.authorization_id,
        "validation_id": application.validation_id,
        "source_signal_id": application.source_signal_id,
        "outcome_id": application.outcome_id,
        "preparation_id": application.preparation_id,
        "source_integrity_id": application.source_integrity_id,
        "assessment_id": application.assessment_id,
        "environment_id": application.environment_id,
        "expected_model_id": application.expected_model_id,
        "observed_model_id": application.observed_model_id,
        "confidence": application.confidence,
        "signal_fingerprint": application.signal_fingerprint,
        "upstream_proposal_fingerprint": application.upstream_proposal_fingerprint,
        "handoff_fingerprint": application.handoff_fingerprint,
        "result_fingerprint": application.result_fingerprint,
        "authority_principal_id": application.authority_principal_id,
        "executor_id": application.executor_id,
        "proposal_kind": application.proposal_kind,
        "proposal_status": application.proposal_status,
        "decision_status": application.decision_status,
        "application_status": application.application_status,
        "applied_payload": application.applied_payload,
        "application_result": application.application_result,
        "failure_reason": application.failure_reason,
    }


@dataclass(frozen=True)
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3:
    """Immutable evidence describing integrity of one adaptation application."""

    integrity_id: str
    application_id: str
    decision_id: str
    proposal_id: str
    source_proposal_id: str
    eligibility_id: str
    source_integrity_id: str
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
    assessment_id: str | None
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    confidence: float
    signal_fingerprint: str
    upstream_proposal_fingerprint: str
    handoff_fingerprint: str
    result_fingerprint: str
    authority_principal_id: str | None
    executor_id: str | None
    proposal_kind: str
    proposal_status: Any
    decision_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status
    application_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status
    applied_payload: Mapping[str, Any] | None
    application_result: Mapping[str, Any] | None
    failure_reason: str | None
    application_fingerprint: str
    integrity_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status
    reasons: Mapping[str, Any] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = (
            "integrity_id", "application_id", "decision_id", "proposal_id", "source_proposal_id", "eligibility_id",
            "source_integrity_id", "signal_id", "evaluation_id", "feedback_id", "classification_id", "execution_id",
            "handoff_id", "authorization_id", "validation_id", "source_signal_id", "outcome_id", "preparation_id",
            "environment_id", "expected_model_id", "observed_model_id", "signal_fingerprint",
            "upstream_proposal_fingerprint", "handoff_fingerprint", "result_fingerprint", "proposal_kind",
            "application_fingerprint",
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
        if not isinstance(self.decision_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status):
            raise TypeError("decision_status must be an adaptation-decision v3 status")
        if not isinstance(self.application_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status):
            raise TypeError("application_status must be an adaptation-application v3 status")
        if not isinstance(self.applied_payload, (Mapping, type(None))) or not isinstance(self.application_result, (Mapping, type(None))):
            raise TypeError("applied_payload and application_result must be mappings or None")
        if self.failure_reason is not None and (not isinstance(self.failure_reason, str) or not self.failure_reason.strip()):
            raise ValueError("failure_reason must be None or a non-empty string")
        if not isinstance(self.integrity_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status):
            raise TypeError("integrity_status must be an application-integrity v3 status")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        if self.integrity_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status.VALID:
            self._validate_valid_evidence()
        object.__setattr__(self, "applied_payload", None if self.applied_payload is None else _freeze(self.applied_payload))
        object.__setattr__(self, "application_result", None if self.application_result is None else _freeze(self.application_result))
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    def _validate_valid_evidence(self) -> None:
        if self.application_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.APPLIED:
            if self.decision_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.ACCEPTED:
                raise ValueError("VALID APPLIED integrity requires ACCEPTED decision")
            if self.applied_payload is None or self.application_result is None or self.failure_reason is not None:
                raise ValueError("VALID APPLIED integrity requires payload/result and no failure")
        elif self.application_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.NOT_APPLIED:
            if self.applied_payload is not None or self.application_result is not None:
                raise ValueError("VALID NOT_APPLIED integrity cannot carry applied payload or result")
            if self.decision_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.REJECTED:
                if self.failure_reason is not None:
                    raise ValueError("VALID REJECTED NOT_APPLIED integrity cannot carry failure evidence")
            elif self.decision_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.ACCEPTED:
                if not self.failure_reason:
                    raise ValueError("VALID ACCEPTED NOT_APPLIED integrity requires failure evidence")
            else:
                raise ValueError("VALID NOT_APPLIED integrity requires ACCEPTED or REJECTED decision")
        elif self.application_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.BLOCKED:
            if self.decision_status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.BLOCKED:
                raise ValueError("VALID BLOCKED integrity requires BLOCKED decision")
            if self.applied_payload is not None or self.application_result is not None or self.failure_reason is not None:
                raise ValueError("VALID BLOCKED integrity cannot carry action evidence")
        else:
            raise ValueError("unsupported application status")

        if len(self.application_fingerprint) != 64 or any(character not in "0123456789abcdef" for character in self.application_fingerprint.lower()):
            raise ValueError("application_fingerprint must be a 64-character hexadecimal SHA-256 fingerprint")

    @property
    def application_integrity(self) -> bool:
        return self.integrity_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status.VALID

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
    def schedules_work(self) -> bool:
        return False

    @property
    def mutates_persistence(self) -> bool:
        return False

    @property
    def mutates_policy(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Service:
    """Verify one bounded adaptation application as immutable integrity evidence."""

    def verify(
        self,
        application: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3,
        *,
        integrity_id: str,
        reasons: Mapping[str, Any] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3:
        if type(application) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3:
            raise TypeError("application must be an adaptation-application v3 artifact")
        if not isinstance(integrity_id, str) or not integrity_id.strip():
            raise ValueError("integrity_id must be a non-empty string")

        integrity_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status.VALID
        failure_reason = None
        try:
            self._validate_application(application)
        except (TypeError, ValueError) as exc:
            integrity_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status.INVALID
            failure_reason = str(exc)
        else:
            failure_reason = application.failure_reason

        application_fingerprint = _fingerprint(_application_representation(application))
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3(
            integrity_id=integrity_id,
            application_id=application.application_id,
            decision_id=application.decision_id,
            proposal_id=application.proposal_id,
            source_proposal_id=application.source_proposal_id,
            eligibility_id=application.eligibility_id,
            source_integrity_id=application.source_integrity_id,
            signal_id=application.signal_id,
            evaluation_id=application.evaluation_id,
            feedback_id=application.feedback_id,
            classification_id=application.classification_id,
            execution_id=application.execution_id,
            handoff_id=application.handoff_id,
            authorization_id=application.authorization_id,
            validation_id=application.validation_id,
            source_signal_id=application.source_signal_id,
            outcome_id=application.outcome_id,
            preparation_id=application.preparation_id,
            assessment_id=application.assessment_id,
            environment_id=application.environment_id,
            expected_model_id=application.expected_model_id,
            observed_model_id=application.observed_model_id,
            confidence=application.confidence,
            signal_fingerprint=application.signal_fingerprint,
            upstream_proposal_fingerprint=application.upstream_proposal_fingerprint,
            handoff_fingerprint=application.handoff_fingerprint,
            result_fingerprint=application.result_fingerprint,
            authority_principal_id=application.authority_principal_id,
            executor_id=application.executor_id,
            proposal_kind=application.proposal_kind,
            proposal_status=application.proposal_status,
            decision_status=application.decision_status,
            application_status=application.application_status,
            applied_payload=application.applied_payload,
            application_result=application.application_result,
            failure_reason=failure_reason,
            application_fingerprint=application_fingerprint,
            integrity_status=integrity_status,
            reasons=reasons if reasons is not None else {"integrity": integrity_status.value},
            lineage=lineage if lineage is not None else {"integrity_id": integrity_id, "application_id": application.application_id},
        )

    @staticmethod
    def _validate_application(application: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3) -> None:
        status = application.application_status
        decision = application.decision_status
        if status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.APPLIED:
            if decision != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.ACCEPTED:
                raise ValueError("APPLIED application requires ACCEPTED decision")
            if application.applied_payload is None or application.application_result is None:
                raise ValueError("APPLIED application requires payload and result")
            if application.failure_reason is not None:
                raise ValueError("APPLIED application cannot carry failure evidence")
            return
        if status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.NOT_APPLIED:
            if application.applied_payload is not None or application.application_result is not None:
                raise ValueError("NOT_APPLIED application cannot carry applied payload or result")
            if decision == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.REJECTED:
                if application.failure_reason is not None:
                    raise ValueError("REJECTED NOT_APPLIED application cannot carry failure evidence")
                return
            if decision == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.ACCEPTED:
                if not application.failure_reason:
                    raise ValueError("ACCEPTED NOT_APPLIED application requires failure evidence")
                return
            raise ValueError("NOT_APPLIED application requires ACCEPTED or REJECTED decision")
        if status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationV3Status.BLOCKED:
            if decision != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationDecisionV3Status.BLOCKED:
                raise ValueError("BLOCKED application requires BLOCKED decision")
            if application.applied_payload is not None or application.application_result is not None or application.failure_reason is not None:
                raise ValueError("BLOCKED application cannot carry action evidence")
            return
        raise ValueError("unsupported application status")


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionLearningAdaptationApplicationIntegrityV3Service",
]
