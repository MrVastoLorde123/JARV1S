"""M23.66: integrity boundary for one adaptation-execution result."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_authorization_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind,
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_execution_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_handoff_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_proposal_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_proposal_validation_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_learning_eligibility_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Error(RuntimeError):
    """Raised when adaptation-execution result integrity cannot be established safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status(str, Enum):
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


@dataclass(frozen=True)
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2:
    """Immutable evidence describing integrity of one adaptation-execution result."""

    integrity_id: str
    execution_id: str
    handoff_id: str
    authorization_id: str
    validation_id: str
    proposal_id: str
    eligibility_id: str
    source_integrity_id: str
    signal_id: str
    evaluation_id: str
    feedback_id: str
    outcome_id: str
    preparation_id: str
    decision_id: str
    source_proposal_id: str
    assessment_id: str | None
    environment_id: str
    expected_model_id: str
    observed_model_id: str
    eligibility_status: EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status
    proposal_status: EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status
    validation_status: EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status
    authorization_status: EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status
    handoff_status: EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status
    execution_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status
    confidence: float
    signal_fingerprint: str
    proposal_kind: str
    proposal_fingerprint: str
    handoff_fingerprint: str
    authority_principal_id: str | None
    authority_kind: EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind | None
    authorization_scope: Mapping[str, str] | None
    executor_id: str | None
    observed_result: Mapping[str, Any] | None
    result_fingerprint: str
    failure_reason: str | None
    integrity_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "integrity_id", "execution_id", "handoff_id", "authorization_id",
            "validation_id", "proposal_id", "eligibility_id", "source_integrity_id",
            "signal_id", "evaluation_id", "feedback_id", "outcome_id", "preparation_id",
            "decision_id", "source_proposal_id", "environment_id", "expected_model_id",
            "observed_model_id", "signal_fingerprint", "proposal_kind",
            "proposal_fingerprint", "handoff_fingerprint", "result_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.assessment_id is not None and (
            not isinstance(self.assessment_id, str) or not self.assessment_id.strip()
        ):
            raise ValueError("assessment_id must be None or a non-empty string")
        for name, enum_type in (
            ("eligibility_status", EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status),
            ("proposal_status", EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status),
            ("validation_status", EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status),
            ("authorization_status", EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status),
            ("handoff_status", EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status),
            ("execution_status", EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status),
            ("integrity_status", EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status),
        ):
            if not isinstance(getattr(self, name), enum_type):
                raise TypeError(f"{name} has an invalid enum type")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.authority_principal_id is not None and (
            not isinstance(self.authority_principal_id, str) or not self.authority_principal_id.strip()
        ):
            raise ValueError("authority_principal_id must be None or a non-empty string")
        if self.authority_kind is not None and not isinstance(
            self.authority_kind,
            EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind,
        ):
            raise TypeError("authority_kind must be an adaptation-authorization v2 authority kind")
        if self.authorization_scope is not None and not isinstance(self.authorization_scope, Mapping):
            raise TypeError("authorization_scope must be None or a mapping")
        if self.executor_id is not None and (
            not isinstance(self.executor_id, str) or not self.executor_id.strip()
        ):
            raise ValueError("executor_id must be None or a non-empty string")
        if self.observed_result is not None and not isinstance(self.observed_result, Mapping):
            raise TypeError("observed_result must be None or a mapping")
        if self.failure_reason is not None and (
            not isinstance(self.failure_reason, str) or not self.failure_reason.strip()
        ):
            raise ValueError("failure_reason must be None or a non-empty string")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")

        if self.integrity_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status.VALID:
            self._validate_valid_evidence()

        object.__setattr__(
            self, "authorization_scope",
            None if self.authorization_scope is None else _freeze(self.authorization_scope),
        )
        object.__setattr__(
            self, "observed_result",
            None if self.observed_result is None else _freeze(self.observed_result),
        )
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    def _validate_valid_evidence(self) -> None:
        if self.execution_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.COMPLETED:
            if self.handoff_status != EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status.READY:
                raise ValueError("VALID COMPLETED integrity requires READY handoff")
            if self.authorization_status != EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.AUTHORIZED:
                raise ValueError("VALID COMPLETED integrity requires AUTHORIZED adaptation")
            if self.validation_status != EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status.VALID:
                raise ValueError("VALID COMPLETED integrity requires VALID proposal validation")
            if self.proposal_status != EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.PROPOSED:
                raise ValueError("VALID COMPLETED integrity requires PROPOSED proposal")
            if self.eligibility_status != EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.ELIGIBLE:
                raise ValueError("VALID COMPLETED integrity requires ELIGIBLE learning evidence")
            if self.authority_kind != EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind.USER:
                raise ValueError("VALID COMPLETED integrity requires USER authority")
            if not self.authority_principal_id or not self.authority_principal_id.lower().startswith("user:"):
                raise ValueError("VALID COMPLETED integrity requires user: authority")
            if self.authorization_scope != {"proposal_id": self.proposal_id, "proposal_fingerprint": self.proposal_fingerprint}:
                raise ValueError("VALID COMPLETED integrity requires exact proposal scope")
            if not self.executor_id or not self.executor_id.lower().startswith("executor:"):
                raise ValueError("VALID COMPLETED integrity requires executor: identity")
            if self.observed_result is None or self.failure_reason is not None:
                raise ValueError("VALID COMPLETED integrity requires observed result and no failure")
            if len(self.result_fingerprint) != 64 or _fingerprint(self.observed_result) != self.result_fingerprint:
                raise ValueError("VALID COMPLETED integrity requires matching result fingerprint")
            return

        if self.execution_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.FAILED:
            if self.handoff_status != EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status.READY:
                raise ValueError("VALID FAILED integrity requires READY handoff")
            if self.authorization_status != EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.AUTHORIZED:
                raise ValueError("VALID FAILED integrity requires AUTHORIZED adaptation")
            if self.validation_status != EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status.VALID:
                raise ValueError("VALID FAILED integrity requires VALID proposal validation")
            if self.proposal_status != EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.PROPOSED:
                raise ValueError("VALID FAILED integrity requires PROPOSED proposal")
            if self.eligibility_status != EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.ELIGIBLE:
                raise ValueError("VALID FAILED integrity requires ELIGIBLE learning evidence")
            if self.authority_kind != EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind.USER:
                raise ValueError("VALID FAILED integrity requires USER authority")
            if not self.authority_principal_id or not self.authority_principal_id.lower().startswith("user:"):
                raise ValueError("VALID FAILED integrity requires user: authority")
            if self.authorization_scope != {"proposal_id": self.proposal_id, "proposal_fingerprint": self.proposal_fingerprint}:
                raise ValueError("VALID FAILED integrity requires exact proposal scope")
            if not self.executor_id or not self.executor_id.lower().startswith("executor:"):
                raise ValueError("VALID FAILED integrity requires executor: identity")
            if self.observed_result is not None or not self.failure_reason:
                raise ValueError("VALID FAILED integrity requires failure evidence only")
            if self.result_fingerprint != "0" * 64:
                raise ValueError("VALID FAILED integrity requires zero result fingerprint")
            return

        if self.execution_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.REJECTED:
            if self.handoff_status != EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status.BLOCKED:
                raise ValueError("VALID REJECTED integrity requires BLOCKED handoff")
            if self.authorization_status != EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.DENIED:
                raise ValueError("VALID REJECTED integrity requires DENIED authorization")
            if self.proposal_status != EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.BLOCKED:
                raise ValueError("VALID REJECTED integrity requires BLOCKED proposal")
            if self.executor_id is not None or self.observed_result is not None:
                raise ValueError("VALID REJECTED integrity cannot carry executor or observed result")
            if self.authorization_scope is not None or self.authority_principal_id is not None or self.authority_kind is not None:
                raise ValueError("VALID REJECTED integrity cannot carry authority")
            if self.handoff_fingerprint != "0" * 64 or self.result_fingerprint != "0" * 64:
                raise ValueError("VALID REJECTED integrity requires zero action fingerprints")
            if not self.failure_reason:
                raise ValueError("VALID REJECTED integrity requires a rejection reason")
            return

        raise ValueError("unsupported execution status")

    @property
    def observed_result_integrity(self) -> bool:
        return self.integrity_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status.VALID

    @property
    def is_advisory_only(self) -> bool:
        return True

    @property
    def grants_authority(self) -> bool:
        return False

    @property
    def authorizes_retry(self) -> bool:
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


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Service:
    """Verify one adaptation-execution result as immutable integrity evidence."""

    def verify(
        self,
        execution: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2,
        *,
        integrity_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2:
        if type(execution) is not EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2:
            raise TypeError(
                "execution must be EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2"
            )
        if not isinstance(integrity_id, str) or not integrity_id.strip():
            raise ValueError("integrity_id must be a non-empty string")

        status = execution.execution_status
        result_fingerprint = execution.result_fingerprint
        observed_result = execution.observed_result
        failure_reason = execution.failure_reason
        integrity_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status.VALID

        if status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.COMPLETED:
            if observed_result is None or failure_reason is not None:
                integrity_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status.INVALID
            elif len(result_fingerprint) != 64 or _fingerprint(observed_result) != result_fingerprint:
                integrity_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status.INVALID
        elif status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.FAILED:
            if observed_result is not None or not failure_reason or result_fingerprint != "0" * 64:
                integrity_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status.INVALID
        elif status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.REJECTED:
            if (
                execution.handoff_status != EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status.BLOCKED
                or execution.authorization_status != EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.DENIED
                or execution.proposal_status != EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.BLOCKED
                or execution.executor_id is not None
                or observed_result is not None
                or execution.authorization_scope is not None
                or execution.authority_principal_id is not None
                or execution.authority_kind is not None
                or execution.handoff_fingerprint != "0" * 64
                or result_fingerprint != "0" * 64
                or not failure_reason
            ):
                integrity_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status.INVALID
            result_fingerprint = "0" * 64
            observed_result = None
        else:
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Error(
                "unsupported adaptation-execution status"
            )

        if status != EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.REJECTED:
            if execution.authorization_status != EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.AUTHORIZED:
                integrity_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status.INVALID
            if execution.authorization_scope != {
                "proposal_id": execution.proposal_id,
                "proposal_fingerprint": execution.proposal_fingerprint,
            }:
                integrity_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status.INVALID
            if execution.authority_kind != EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind.USER:
                integrity_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status.INVALID
            if not execution.authority_principal_id or not execution.authority_principal_id.lower().startswith("user:"):
                integrity_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status.INVALID
            if not execution.executor_id or not execution.executor_id.lower().startswith("executor:"):
                integrity_status = EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status.INVALID

        if integrity_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status.INVALID:
            # Preserve the source evidence exactly so invalidity is itself auditable evidence.
            result_fingerprint = execution.result_fingerprint
            observed_result = execution.observed_result
            failure_reason = execution.failure_reason

        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2(
            integrity_id=integrity_id,
            execution_id=execution.execution_id,
            handoff_id=execution.handoff_id,
            authorization_id=execution.authorization_id,
            validation_id=execution.validation_id,
            proposal_id=execution.proposal_id,
            eligibility_id=execution.eligibility_id,
            source_integrity_id=execution.integrity_id,
            signal_id=execution.signal_id,
            evaluation_id=execution.evaluation_id,
            feedback_id=execution.feedback_id,
            outcome_id=execution.outcome_id,
            preparation_id=execution.preparation_id,
            decision_id=execution.decision_id,
            source_proposal_id=execution.source_proposal_id,
            assessment_id=execution.assessment_id,
            environment_id=execution.environment_id,
            expected_model_id=execution.expected_model_id,
            observed_model_id=execution.observed_model_id,
            eligibility_status=execution.eligibility_status,
            proposal_status=execution.proposal_status,
            validation_status=execution.validation_status,
            authorization_status=execution.authorization_status,
            handoff_status=execution.handoff_status,
            execution_status=execution.execution_status,
            confidence=execution.confidence,
            signal_fingerprint=execution.signal_fingerprint,
            proposal_kind=execution.proposal_kind,
            proposal_fingerprint=execution.proposal_fingerprint,
            handoff_fingerprint=execution.handoff_fingerprint,
            authority_principal_id=execution.authority_principal_id,
            authority_kind=execution.authority_kind,
            authorization_scope=execution.authorization_scope,
            executor_id=execution.executor_id,
            observed_result=observed_result,
            result_fingerprint=result_fingerprint,
            failure_reason=failure_reason,
            integrity_status=integrity_status,
            reasons=reasons or {
                "status": "adaptation execution result integrity verified"
                if integrity_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Status.VALID
                else "adaptation execution result integrity invalid"
            },
            lineage=lineage or {
                "execution_id": execution.execution_id,
                "handoff_id": execution.handoff_id,
                "authorization_id": execution.authorization_id,
                "proposal_id": execution.proposal_id,
                "source_integrity_id": execution.integrity_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionResultIntegrityV2Service",
]
