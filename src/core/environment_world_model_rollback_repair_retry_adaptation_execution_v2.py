"""M23.65: bounded execution of one exact authorized adaptation handoff."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Callable, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_authorization_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind,
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_handoff_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2,
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


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Error(RuntimeError):
    """Raised when an adaptation execution cannot be safely formed."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status(str, Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"


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
    if isinstance(value, set):
        return sorted(
            (_canonical(item) for item in value),
            key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")),
        )
    return value


def _result_fingerprint(value: Mapping[str, Any]) -> str:
    canonical = json.dumps(_canonical(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2:
    """Immutable result of one bounded adaptation execution attempt."""

    execution_id: str
    handoff_id: str
    authorization_id: str
    validation_id: str
    proposal_id: str
    eligibility_id: str
    integrity_id: str
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
    execution_status: EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "execution_id", "handoff_id", "authorization_id", "validation_id", "proposal_id", "eligibility_id",
            "integrity_id", "signal_id", "evaluation_id", "feedback_id", "outcome_id", "preparation_id",
            "decision_id", "source_proposal_id", "environment_id", "expected_model_id", "observed_model_id",
            "signal_fingerprint", "proposal_kind", "proposal_fingerprint", "handoff_fingerprint", "result_fingerprint",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.assessment_id is not None and (not isinstance(self.assessment_id, str) or not self.assessment_id.strip()):
            raise ValueError("assessment_id must be None or a non-empty string")
        if not isinstance(self.eligibility_status, EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status):
            raise TypeError("eligibility_status must be a learning-eligibility v2 status")
        if not isinstance(self.proposal_status, EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status):
            raise TypeError("proposal_status must be an adaptation-proposal v2 status")
        if not isinstance(self.validation_status, EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status):
            raise TypeError("validation_status must be an adaptation-proposal validation v2 status")
        if not isinstance(self.authorization_status, EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status):
            raise TypeError("authorization_status must be an adaptation-authorization v2 status")
        if not isinstance(self.handoff_status, EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status):
            raise TypeError("handoff_status must be an adaptation-handoff v2 status")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.authority_principal_id is not None and (not isinstance(self.authority_principal_id, str) or not self.authority_principal_id.strip()):
            raise ValueError("authority_principal_id must be None or a non-empty string")
        if self.authority_kind is not None and not isinstance(self.authority_kind, EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind):
            raise TypeError("authority_kind must be an adaptation-authorization v2 authority kind")
        if self.authorization_scope is not None and not isinstance(self.authorization_scope, Mapping):
            raise TypeError("authorization_scope must be None or a mapping")
        if self.executor_id is not None and (not isinstance(self.executor_id, str) or not self.executor_id.strip()):
            raise ValueError("executor_id must be None or a non-empty string")
        if self.observed_result is not None and not isinstance(self.observed_result, Mapping):
            raise TypeError("observed_result must be None or a mapping")
        if self.failure_reason is not None and (not isinstance(self.failure_reason, str) or not self.failure_reason.strip()):
            raise ValueError("failure_reason must be None or a non-empty string")
        if not isinstance(self.execution_status, EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status):
            raise TypeError("execution_status must be an adaptation-execution v2 status")

        if self.execution_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.COMPLETED:
            self._validate_ready_base()
            self._validate_executor()
            if self.observed_result is None:
                raise ValueError("COMPLETED requires observed_result evidence")
            if self.failure_reason is not None:
                raise ValueError("COMPLETED cannot contain failure_reason")
            if len(self.result_fingerprint) != 64:
                raise ValueError("COMPLETED requires a SHA-256 result fingerprint")
            if _result_fingerprint(self.observed_result) != self.result_fingerprint:
                raise ValueError("COMPLETED result_fingerprint must match observed_result")
        elif self.execution_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.FAILED:
            self._validate_ready_base()
            self._validate_executor()
            if self.observed_result is not None:
                raise ValueError("FAILED cannot contain observed_result evidence")
            if not self.failure_reason or not self.failure_reason.strip():
                raise ValueError("FAILED requires a non-empty failure_reason")
            if self.result_fingerprint != "0" * 64:
                raise ValueError("FAILED requires zero result fingerprint")
        elif self.execution_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.REJECTED:
            if self.handoff_status != EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status.BLOCKED:
                raise ValueError("REJECTED requires BLOCKED handoff")
            if self.authorization_status != EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.DENIED:
                raise ValueError("REJECTED requires DENIED authorization")
            if self.handoff_fingerprint != "0" * 64:
                raise ValueError("REJECTED requires zero handoff fingerprint")
            if self.executor_id is not None or self.observed_result is not None:
                raise ValueError("REJECTED cannot invoke or report an executor")
            if self.result_fingerprint != "0" * 64:
                raise ValueError("REJECTED requires zero result fingerprint")
            if not self.failure_reason or not self.failure_reason.strip():
                raise ValueError("REJECTED requires a rejection reason")
        else:
            raise ValueError("unsupported execution status")

        if self.authorization_scope is not None:
            expected_scope = {"proposal_id": self.proposal_id, "proposal_fingerprint": self.proposal_fingerprint}
            if dict(self.authorization_scope) != expected_scope:
                raise ValueError("execution evidence requires exact proposal-scoped authorization")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")
        object.__setattr__(self, "authorization_scope", None if self.authorization_scope is None else _freeze(self.authorization_scope))
        object.__setattr__(self, "observed_result", None if self.observed_result is None else _freeze(self.observed_result))
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    def _validate_ready_base(self) -> None:
        if self.handoff_status != EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status.READY:
            raise ValueError("executable result requires READY handoff")
        if self.authorization_status != EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.AUTHORIZED:
            raise ValueError("executable result requires AUTHORIZED adaptation")
        if self.validation_status != EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status.VALID:
            raise ValueError("executable result requires VALID proposal validation")
        if self.proposal_status != EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.PROPOSED:
            raise ValueError("executable result requires PROPOSED proposal")
        if self.eligibility_status != EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.ELIGIBLE:
            raise ValueError("executable result requires ELIGIBLE learning evidence")
        if self.authority_kind != EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind.USER:
            raise ValueError("executable result requires USER authority kind")
        if not self.authority_principal_id or not self.authority_principal_id.lower().startswith("user:"):
            raise ValueError("executable result requires explicit user: authority")
        if len(self.proposal_fingerprint) != 64 or len(self.handoff_fingerprint) != 64:
            raise ValueError("executable result requires SHA-256 proposal and handoff fingerprints")

    def _validate_executor(self) -> None:
        if not self.executor_id or not self.executor_id.strip().lower().startswith("executor:"):
            raise ValueError("executable result requires an explicit executor: identity")

    @property
    def completed(self) -> bool:
        return self.execution_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.COMPLETED

    @property
    def failed(self) -> bool:
        return self.execution_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.FAILED

    @property
    def rejected(self) -> bool:
        return self.execution_status == EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.REJECTED

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


class EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Service:
    """Execute one exact READY handoff through an explicit external executor capability."""

    def execute(
        self,
        handoff: EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2,
        *,
        execution_id: str,
        executor_id: str,
        executor: Callable[[Mapping[str, Any], str], Mapping[str, Any]],
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2:
        if type(handoff) is not EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2:
            raise TypeError("handoff must be EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2")
        if not isinstance(execution_id, str) or not execution_id.strip():
            raise ValueError("execution_id must be a non-empty string")
        if not isinstance(executor_id, str) or not executor_id.strip():
            raise ValueError("executor_id must be a non-empty string")
        if not executor_id.strip().lower().startswith("executor:"):
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Error(
                "executor identity must use the explicit executor: namespace"
            )
        if not callable(executor):
            raise TypeError("executor must be callable")

        common = dict(
            execution_id=execution_id,
            handoff_id=handoff.handoff_id,
            authorization_id=handoff.authorization_id,
            validation_id=handoff.validation_id,
            proposal_id=handoff.proposal_id,
            eligibility_id=handoff.eligibility_id,
            integrity_id=handoff.integrity_id,
            signal_id=handoff.signal_id,
            evaluation_id=handoff.evaluation_id,
            feedback_id=handoff.feedback_id,
            outcome_id=handoff.outcome_id,
            preparation_id=handoff.preparation_id,
            decision_id=handoff.decision_id,
            source_proposal_id=handoff.source_proposal_id,
            assessment_id=handoff.assessment_id,
            environment_id=handoff.environment_id,
            expected_model_id=handoff.expected_model_id,
            observed_model_id=handoff.observed_model_id,
            eligibility_status=handoff.eligibility_status,
            proposal_status=handoff.proposal_status,
            validation_status=handoff.validation_status,
            authorization_status=handoff.authorization_status,
            handoff_status=handoff.handoff_status,
            confidence=handoff.confidence,
            signal_fingerprint=handoff.signal_fingerprint,
            proposal_kind=handoff.proposal_kind,
            proposal_fingerprint=handoff.proposal_fingerprint,
            handoff_fingerprint=handoff.handoff_fingerprint,
            authority_principal_id=handoff.authority_principal_id,
            authority_kind=handoff.authority_kind,
            authorization_scope=handoff.authorization_scope,
            reasons=reasons or {},
            lineage=lineage or {"execution_id": execution_id, "handoff_id": handoff.handoff_id, "authorization_id": handoff.authorization_id},
        )

        if handoff.handoff_status == EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status.BLOCKED:
            return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2(
                **common,
                executor_id=None,
                observed_result=None,
                result_fingerprint="0" * 64,
                failure_reason="blocked handoff cannot be executed",
                execution_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.REJECTED,
            )
        if handoff.handoff_status != EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status.READY:
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Error("unsupported handoff status")
        if handoff.proposal_payload is None or not handoff.proposal_payload:
            raise ValueError("READY handoff requires a non-empty proposal payload")
        if handoff.handoff_payload != handoff.proposal_payload:
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Error(
                "handoff payload must exactly equal the authorized proposal payload"
            )
        if handoff.authorization_scope != {"proposal_id": handoff.proposal_id, "proposal_fingerprint": handoff.proposal_fingerprint}:
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Error(
                "handoff authorization scope is not exact"
            )

        try:
            observed = executor(handoff.handoff_payload, handoff.environment_id)
        except Exception as exc:  # bounded failure evidence; no automatic retry
            return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2(
                **common,
                executor_id=executor_id,
                observed_result=None,
                result_fingerprint="0" * 64,
                failure_reason=f"executor failure: {type(exc).__name__}: {exc}",
                execution_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.FAILED,
            )
        if not isinstance(observed, Mapping):
            raise TypeError("executor must return an observed-result mapping")
        return EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2(
            **common,
            executor_id=executor_id,
            observed_result=dict(observed),
            result_fingerprint=_result_fingerprint(observed),
            failure_reason=None,
            execution_status=EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status.COMPLETED,
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationExecutionV2Service",
]
