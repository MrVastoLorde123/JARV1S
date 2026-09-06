"""M23.63: explicit external authorization boundary for v2 adaptation proposals."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_proposal_validation_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_adaptation_proposal_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_learning_eligibility_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Error(RuntimeError):
    """Raised when an adaptation authorization cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status(str, Enum):
    AUTHORIZED = "AUTHORIZED"
    DENIED = "DENIED"


class EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind(str, Enum):
    USER = "USER"


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
class EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2:
    """Immutable, proposal-scoped authorization evidence from one explicit user principal."""

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
    confidence: float
    signal_fingerprint: str
    proposal_kind: str
    proposal_payload: Mapping[str, Any] | None
    proposal_fingerprint: str
    authority_principal_id: str | None
    authority_kind: EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind | None
    authorization_scope: Mapping[str, str] | None
    authorization_status: EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "authorization_id", "validation_id", "proposal_id", "eligibility_id", "integrity_id",
            "signal_id", "evaluation_id", "feedback_id", "outcome_id", "execution_id",
            "preparation_id", "decision_id", "source_proposal_id", "environment_id",
            "expected_model_id", "observed_model_id", "signal_fingerprint", "proposal_kind",
            "proposal_fingerprint",
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
        if not isinstance(self.proposal_status, EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status):
            raise TypeError("proposal_status must be an adaptation-proposal v2 status")
        if not isinstance(self.validation_status, EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status):
            raise TypeError("validation_status must be an adaptation-proposal validation v2 status")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not isinstance(self.proposal_payload, Mapping) and self.proposal_payload is not None:
            raise TypeError("proposal_payload must be None or a mapping")
        if self.authority_principal_id is not None and (
            not isinstance(self.authority_principal_id, str) or not self.authority_principal_id.strip()
        ):
            raise ValueError("authority_principal_id must be None or a non-empty string")
        if self.authority_kind is not None and not isinstance(
            self.authority_kind, EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind
        ):
            raise TypeError("authority_kind must be an adaptation-authorization v2 authority kind")
        if self.authorization_scope is not None:
            if not isinstance(self.authorization_scope, Mapping):
                raise TypeError("authorization_scope must be None or a mapping")
            for key, value in self.authorization_scope.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise TypeError("authorization_scope keys and values must be strings")
        if not isinstance(self.authorization_status, EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status):
            raise TypeError("authorization_status must be an adaptation-authorization v2 status")
        if not isinstance(self.reasons, Mapping):
            raise TypeError("reasons must be a mapping")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        if self.authorization_status == EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.AUTHORIZED:
            if self.validation_status != EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status.VALID:
                raise ValueError("AUTHORIZED requires VALID adaptation-proposal validation")
            if self.proposal_status != EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.PROPOSED:
                raise ValueError("AUTHORIZED requires PROPOSED adaptation-proposal status")
            if self.eligibility_status != EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.ELIGIBLE:
                raise ValueError("AUTHORIZED requires ELIGIBLE learning evidence")
            if self.proposal_payload is None or not self.proposal_payload:
                raise ValueError("AUTHORIZED requires a non-empty proposal payload")
            if len(self.proposal_fingerprint) != 64:
                raise ValueError("AUTHORIZED requires a SHA-256 proposal fingerprint")
            if not self.authority_principal_id or not self.authority_principal_id.strip().lower().startswith("user:"):
                raise ValueError("AUTHORIZED requires an explicit external USER principal")
            if self.authority_kind != EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind.USER:
                raise ValueError("AUTHORIZED requires an explicit USER authority kind")
            if self.authorization_scope is None:
                raise ValueError("AUTHORIZED requires an explicit authorization scope")
            expected_scope = {
                "proposal_id": self.proposal_id,
                "proposal_fingerprint": self.proposal_fingerprint,
            }
            if dict(self.authorization_scope) != expected_scope:
                raise ValueError("AUTHORIZED scope must bind exactly to proposal_id and proposal_fingerprint")
        elif self.authorization_status == EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.DENIED:
            if self.validation_status != EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status.BLOCKED:
                raise ValueError("DENIED authorization evidence requires BLOCKED validation")
            if self.proposal_status != EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.BLOCKED:
                raise ValueError("DENIED authorization evidence requires BLOCKED proposal status")
            if self.eligibility_status != EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.INELIGIBLE:
                raise ValueError("DENIED authorization evidence requires INELIGIBLE learning evidence")
            if self.proposal_payload is not None:
                raise ValueError("DENIED authorization evidence cannot contain a proposal payload")
            if self.authority_principal_id is not None or self.authority_kind is not None or self.authorization_scope is not None:
                raise ValueError("DENIED authorization evidence cannot contain an authority grant")
            if self.proposal_fingerprint != "0" * 64:
                raise ValueError("DENIED authorization evidence for BLOCKED validation requires a zero fingerprint")
        else:
            raise ValueError("unsupported authorization status")
        object.__setattr__(self, "proposal_payload", None if self.proposal_payload is None else _freeze(self.proposal_payload))
        object.__setattr__(self, "authorization_scope", None if self.authorization_scope is None else _freeze(self.authorization_scope))
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_authorized(self) -> bool:
        return self.authorization_status == EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.AUTHORIZED

    @property
    def authorizes_adaptation(self) -> bool:
        return self.is_authorized

    @property
    def permits_adaptation(self) -> bool:
        return self.is_authorized

    @property
    def grants_broader_authority(self) -> bool:
        return False

    @property
    def is_external_user_authorized(self) -> bool:
        return self.is_authorized and self.authority_kind == EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind.USER

    @property
    def self_authorizes(self) -> bool:
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


class EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Service:
    """Authorize one exact validated proposal only from an explicit external user principal."""

    def authorize(
        self,
        validation: EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2,
        *,
        authorization_id: str,
        authority_principal_id: str,
        authority_kind: EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind,
        authorization_scope: Mapping[str, str],
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2:
        if type(validation) is not EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2:
            raise TypeError("validation must be EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2")
        if not isinstance(authorization_id, str) or not authorization_id.strip():
            raise ValueError("authorization_id must be a non-empty string")
        if not isinstance(authority_principal_id, str) or not authority_principal_id.strip():
            raise ValueError("authority_principal_id must be a non-empty string")
        if not isinstance(authority_kind, EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind):
            raise TypeError("authority_kind must be an adaptation-authorization v2 authority kind")
        if authority_kind != EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind.USER:
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Error(
                "only an explicit USER principal may authorize adaptation"
            )
        if not authority_principal_id.strip().lower().startswith("user:"):
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Error(
                "authority principal must use the explicit user: namespace"
            )
        if not isinstance(authorization_scope, Mapping):
            raise TypeError("authorization_scope must be a mapping")
        expected_scope = {
            "proposal_id": validation.proposal_id,
            "proposal_fingerprint": validation.proposal_fingerprint,
        }
        if dict(authorization_scope) != expected_scope:
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Error(
                "authorization scope must bind exactly to the validated proposal_id and proposal_fingerprint"
            )
        if validation.validation_status == EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status.BLOCKED:
            return EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2(
                authorization_id=authorization_id,
                validation_id=validation.validation_id,
                proposal_id=validation.proposal_id,
                eligibility_id=validation.eligibility_id,
                integrity_id=validation.integrity_id,
                signal_id=validation.signal_id,
                evaluation_id=validation.evaluation_id,
                feedback_id=validation.feedback_id,
                outcome_id=validation.outcome_id,
                execution_id=validation.execution_id,
                preparation_id=validation.preparation_id,
                decision_id=validation.decision_id,
                source_proposal_id=validation.source_proposal_id,
                assessment_id=validation.assessment_id,
                environment_id=validation.environment_id,
                expected_model_id=validation.expected_model_id,
                observed_model_id=validation.observed_model_id,
                eligibility_status=validation.eligibility_status,
                proposal_status=validation.proposal_status,
                validation_status=validation.validation_status,
                confidence=validation.confidence,
                signal_fingerprint=validation.signal_fingerprint,
                proposal_kind=validation.proposal_kind,
                proposal_payload=None,
                proposal_fingerprint="0" * 64,
                authority_principal_id=None,
                authority_kind=None,
                authorization_scope=None,
                authorization_status=EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.DENIED,
                reasons=reasons or {"status": "blocked validation cannot receive authorization"},
                lineage=lineage or {"authorization_id": authorization_id, "validation_id": validation.validation_id},
            )
        if validation.validation_status != EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status.VALID:
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Error(
                "unsupported validation status for authorization"
            )
        return EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2(
            authorization_id=authorization_id,
            validation_id=validation.validation_id,
            proposal_id=validation.proposal_id,
            eligibility_id=validation.eligibility_id,
            integrity_id=validation.integrity_id,
            signal_id=validation.signal_id,
            evaluation_id=validation.evaluation_id,
            feedback_id=validation.feedback_id,
            outcome_id=validation.outcome_id,
            execution_id=validation.execution_id,
            preparation_id=validation.preparation_id,
            decision_id=validation.decision_id,
            source_proposal_id=validation.source_proposal_id,
            assessment_id=validation.assessment_id,
            environment_id=validation.environment_id,
            expected_model_id=validation.expected_model_id,
            observed_model_id=validation.observed_model_id,
            eligibility_status=validation.eligibility_status,
            proposal_status=validation.proposal_status,
            validation_status=validation.validation_status,
            confidence=validation.confidence,
            signal_fingerprint=validation.signal_fingerprint,
            proposal_kind=validation.proposal_kind,
            proposal_payload=validation.proposal_payload,
            proposal_fingerprint=validation.proposal_fingerprint,
            authority_principal_id=authority_principal_id,
            authority_kind=authority_kind,
            authorization_scope=dict(authorization_scope),
            authorization_status=EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status.AUTHORIZED,
            reasons=reasons or {"status": "explicit user authorization recorded for this exact validated proposal"},
            lineage=lineage or {
                "authorization_id": authorization_id,
                "validation_id": validation.validation_id,
                "proposal_id": validation.proposal_id,
                "proposal_fingerprint": validation.proposal_fingerprint,
                "authority_principal_id": authority_principal_id,
                "authority_kind": authority_kind,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2AuthorityKind",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationAuthorizationV2Service",
]