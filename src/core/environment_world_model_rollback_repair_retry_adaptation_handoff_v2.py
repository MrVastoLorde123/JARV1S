"""M23.64: immutable handoff boundary after adaptation authorization."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_authorization_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind,
    EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status,
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


class EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Error(RuntimeError):
    """Raised when an authorized adaptation cannot be handed off safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status(str, Enum):
    READY = "READY"
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


def _canonical(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _canonical(value[key]) for key in sorted(value, key=lambda item: str(item))}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if isinstance(value, set):
        return sorted((_canonical(item) for item in value), key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")))
    return value


def _handoff_fingerprint(authorization: EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2) -> str:
    evidence = {
        "authorization_id": authorization.authorization_id,
        "validation_id": authorization.validation_id,
        "proposal_id": authorization.proposal_id,
        "proposal_fingerprint": authorization.proposal_fingerprint,
        "authority_principal_id": authorization.authority_principal_id,
        "authority_kind": authorization.authority_kind,
        "authorization_scope": authorization.authorization_scope,
        "proposal_payload": authorization.proposal_payload,
        "proposal_kind": authorization.proposal_kind,
        "confidence": authorization.confidence,
        "signal_fingerprint": authorization.signal_fingerprint,
    }
    canonical = json.dumps(_canonical(evidence), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2:
    """Immutable execution-ready representation for one already-authorized proposal."""

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
    execution_id: str
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
    confidence: float
    signal_fingerprint: str
    proposal_kind: str
    proposal_payload: Mapping[str, Any] | None
    proposal_fingerprint: str
    authority_principal_id: str | None
    authority_kind: EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind | None
    authorization_scope: Mapping[str, str] | None
    handoff_payload: Mapping[str, Any] | None
    handoff_fingerprint: str
    handoff_status: EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "handoff_id", "authorization_id", "validation_id", "proposal_id", "eligibility_id", "integrity_id",
            "signal_id", "evaluation_id", "feedback_id", "outcome_id", "execution_id", "preparation_id",
            "decision_id", "source_proposal_id", "environment_id", "expected_model_id", "observed_model_id",
            "signal_fingerprint", "proposal_kind", "proposal_fingerprint", "handoff_fingerprint",
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
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)) or not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.authority_principal_id is not None and (not isinstance(self.authority_principal_id, str) or not self.authority_principal_id.strip()):
            raise ValueError("authority_principal_id must be None or a non-empty string")
        if self.authority_kind is not None and not isinstance(self.authority_kind, EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind):
            raise TypeError("authority_kind must be an adaptation-authorization v2 authority kind")
        if self.authorization_scope is not None and not isinstance(self.authorization_scope, Mapping):
            raise TypeError("authorization_scope must be None or a mapping")
        for name, value in (("proposal_payload", self.proposal_payload), ("handoff_payload", self.handoff_payload)):
            if value is not None and not isinstance(value, Mapping):
                raise TypeError(f"{name} must be None or a mapping")
        if not isinstance(self.handoff_status, EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status):
            raise TypeError("handoff_status must be an adaptation-handoff v2 status")
        if not isinstance(self.reasons, Mapping) or not isinstance(self.lineage, Mapping):
            raise TypeError("reasons and lineage must be mappings")

        if self.handoff_status == EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status.READY:
            if self.authorization_status != EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.AUTHORIZED:
                raise ValueError("READY requires AUTHORIZED adaptation evidence")
            if self.validation_status != EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status.VALID:
                raise ValueError("READY requires VALID adaptation-proposal validation")
            if self.proposal_status != EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.PROPOSED:
                raise ValueError("READY requires PROPOSED adaptation-proposal status")
            if self.eligibility_status != EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.ELIGIBLE:
                raise ValueError("READY requires ELIGIBLE learning evidence")
            if self.authority_kind != EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind.USER:
                raise ValueError("READY requires USER authority kind")
            if not self.authority_principal_id or not self.authority_principal_id.lower().startswith("user:"):
                raise ValueError("READY requires an explicit user: authority principal")
            if self.authorization_scope != {"proposal_id": self.proposal_id, "proposal_fingerprint": self.proposal_fingerprint}:
                raise ValueError("READY requires exact proposal-scoped authorization")
            if self.proposal_payload is None or not self.proposal_payload or self.handoff_payload != self.proposal_payload:
                raise ValueError("READY requires the exact non-empty authorized proposal payload")
            if len(self.proposal_fingerprint) != 64 or len(self.handoff_fingerprint) != 64:
                raise ValueError("READY requires SHA-256 fingerprints")
        elif self.handoff_status == EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status.BLOCKED:
            if self.authorization_status != EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.DENIED:
                raise ValueError("BLOCKED requires DENIED authorization evidence")
            if self.proposal_status != EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.BLOCKED:
                raise ValueError("BLOCKED requires BLOCKED proposal status")
            if self.handoff_payload is not None or self.authority_principal_id is not None or self.authority_kind is not None or self.authorization_scope is not None:
                raise ValueError("BLOCKED handoff cannot contain executable payload or authority")
            if self.handoff_fingerprint != "0" * 64:
                raise ValueError("BLOCKED handoff requires zero fingerprint")
        else:
            raise ValueError("unsupported handoff status")

        object.__setattr__(self, "proposal_payload", None if self.proposal_payload is None else _freeze(self.proposal_payload))
        object.__setattr__(self, "authorization_scope", None if self.authorization_scope is None else _freeze(self.authorization_scope))
        object.__setattr__(self, "handoff_payload", None if self.handoff_payload is None else _freeze(self.handoff_payload))
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_execution_ready(self) -> bool:
        return self.handoff_status == EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status.READY

    @property
    def is_advisory_only(self) -> bool:
        return True

    @property
    def executes(self) -> bool:
        return False

    @property
    def schedules_work(self) -> bool:
        return False

    @property
    def mutates_persistence(self) -> bool:
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
    def grants_authority(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Service:
    """Prepare a bounded handoff from one exact authorization without executing it."""

    def prepare(
        self,
        authorization: EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2,
        *,
        handoff_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2:
        if type(authorization) is not EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2:
            raise TypeError("authorization must be EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2")
        if not isinstance(handoff_id, str) or not handoff_id.strip():
            raise ValueError("handoff_id must be a non-empty string")
        if authorization.authorization_status == EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.DENIED:
            return self._build(authorization, handoff_id=handoff_id, status=EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status.BLOCKED, reasons=reasons, lineage=lineage)
        if authorization.authorization_status != EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.AUTHORIZED:
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Error("unsupported authorization status")
        if authorization.proposal_payload is None or not authorization.proposal_payload:
            raise ValueError("AUTHORIZED evidence requires a non-empty proposal payload")
        return self._build(authorization, handoff_id=handoff_id, status=EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status.READY, reasons=reasons, lineage=lineage)

    @staticmethod
    def _build(
        authorization: EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2,
        *,
        handoff_id: str,
        status: EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status,
        reasons: Mapping[str, str] | None,
        lineage: Mapping[str, Any] | None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2:
        ready = status == EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status.READY
        return EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2(
            handoff_id=handoff_id,
            authorization_id=authorization.authorization_id,
            validation_id=authorization.validation_id,
            proposal_id=authorization.proposal_id,
            eligibility_id=authorization.eligibility_id,
            integrity_id=authorization.integrity_id,
            signal_id=authorization.signal_id,
            evaluation_id=authorization.evaluation_id,
            feedback_id=authorization.feedback_id,
            outcome_id=authorization.outcome_id,
            execution_id=authorization.execution_id,
            preparation_id=authorization.preparation_id,
            decision_id=authorization.decision_id,
            source_proposal_id=authorization.source_proposal_id,
            assessment_id=authorization.assessment_id,
            environment_id=authorization.environment_id,
            expected_model_id=authorization.expected_model_id,
            observed_model_id=authorization.observed_model_id,
            eligibility_status=authorization.eligibility_status,
            proposal_status=authorization.proposal_status,
            validation_status=authorization.validation_status,
            authorization_status=authorization.authorization_status,
            confidence=authorization.confidence,
            signal_fingerprint=authorization.signal_fingerprint,
            proposal_kind=authorization.proposal_kind,
            proposal_payload=authorization.proposal_payload,
            proposal_fingerprint=authorization.proposal_fingerprint,
            authority_principal_id=authorization.authority_principal_id,
            authority_kind=authorization.authority_kind,
            authorization_scope=authorization.authorization_scope,
            handoff_payload=authorization.proposal_payload if ready else None,
            handoff_fingerprint=_handoff_fingerprint(authorization) if ready else "0" * 64,
            handoff_status=status,
            reasons=reasons or {"status": "authorized adaptation is prepared for a separate future execution boundary" if ready else "denied authorization is blocked from handoff"},
            lineage=lineage or {"handoff_id": handoff_id, "authorization_id": authorization.authorization_id, "proposal_id": authorization.proposal_id},
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationHandoffV2Service",
]
