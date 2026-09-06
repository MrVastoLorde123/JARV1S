"""M23.62: validation boundary for v2 adaptation proposals."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.core.environment_world_model_rollback_repair_retry_adaptation_proposal_v2 import (
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2,
    EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_learning_eligibility_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status,
)
from src.core.environment_world_model_rollback_repair_retry_learning_signal_v2 import (
    EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status,
)


class EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Error(RuntimeError):
    """Raised when adaptation-proposal validation evidence cannot be formed safely."""


class EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status(str, Enum):
    VALID = "VALID"
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
        return sorted(
            (_canonical(item) for item in value),
            key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")),
        )
    return value


def _proposal_fingerprint(proposal: EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2) -> str:
    payload = {
        "proposal_id": proposal.proposal_id,
        "eligibility_id": proposal.eligibility_id,
        "integrity_id": proposal.integrity_id,
        "signal_id": proposal.signal_id,
        "evaluation_id": proposal.evaluation_id,
        "feedback_id": proposal.feedback_id,
        "outcome_id": proposal.outcome_id,
        "execution_id": proposal.execution_id,
        "preparation_id": proposal.preparation_id,
        "decision_id": proposal.decision_id,
        "source_proposal_id": proposal.source_proposal_id,
        "assessment_id": proposal.assessment_id,
        "environment_id": proposal.environment_id,
        "expected_model_id": proposal.expected_model_id,
        "observed_model_id": proposal.observed_model_id,
        "eligibility_status": proposal.eligibility_status,
        "signal_status": proposal.signal_status,
        "confidence": proposal.confidence,
        "signal_fingerprint": proposal.signal_fingerprint,
        "proposal_kind": proposal.proposal_kind,
        "proposal_status": proposal.proposal_status,
        "proposal_payload": proposal.proposal_payload,
        "reasons": proposal.reasons,
        "lineage": proposal.lineage,
    }
    canonical = json.dumps(_canonical(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2:
    """Immutable structural validation evidence over one v2 adaptation proposal."""

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
    signal_status: EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status
    confidence: float
    signal_fingerprint: str
    proposal_kind: str
    proposal_status: EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status
    proposal_payload: Mapping[str, Any] | None
    proposal_fingerprint: str
    validation_status: EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status
    reasons: Mapping[str, str] = field(default_factory=dict)
    lineage: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "validation_id", "proposal_id", "eligibility_id", "integrity_id", "signal_id",
            "evaluation_id", "feedback_id", "outcome_id", "execution_id", "preparation_id",
            "decision_id", "source_proposal_id", "environment_id", "expected_model_id",
            "observed_model_id", "signal_fingerprint", "proposal_kind", "proposal_fingerprint",
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
        if not isinstance(self.signal_status, EnvironmentWorldModelRollbackRepairRetryLearningSignalV2Status):
            raise TypeError("signal_status must be a learning-signal v2 status")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not isinstance(self.proposal_status, EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status):
            raise TypeError("proposal_status must be an adaptation-proposal v2 status")
        if not isinstance(self.validation_status, EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status):
            raise TypeError("validation_status must be an adaptation-proposal validation v2 status")
        if not isinstance(self.proposal_payload, Mapping) and self.proposal_payload is not None:
            raise TypeError("proposal_payload must be None or a mapping")
        if self.validation_status == EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status.VALID:
            if self.proposal_status != EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.PROPOSED:
                raise ValueError("VALID validation requires PROPOSED proposal status")
            if self.eligibility_status != EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.ELIGIBLE:
                raise ValueError("VALID validation requires ELIGIBLE learning evidence")
            if self.proposal_payload is None or not self.proposal_payload:
                raise ValueError("VALID validation requires a non-empty proposal payload")
            if len(self.proposal_fingerprint) != 64:
                raise ValueError("VALID validation requires a SHA-256 proposal fingerprint")
        elif self.validation_status == EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status.BLOCKED:
            if self.proposal_status != EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.BLOCKED:
                raise ValueError("BLOCKED validation requires BLOCKED proposal status")
            if self.eligibility_status != EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.INELIGIBLE:
                raise ValueError("BLOCKED validation requires INELIGIBLE learning evidence")
            if self.proposal_payload is not None:
                raise ValueError("BLOCKED validation cannot contain a proposal payload")
        else:
            raise ValueError("unsupported validation status")
        if not isinstance(self.reasons, Mapping):
            raise TypeError("reasons must be a mapping")
        if not isinstance(self.lineage, Mapping):
            raise TypeError("lineage must be a mapping")
        object.__setattr__(self, "proposal_payload", None if self.proposal_payload is None else _freeze(self.proposal_payload))
        object.__setattr__(self, "reasons", _freeze(self.reasons))
        object.__setattr__(self, "lineage", _freeze(self.lineage))

    @property
    def is_advisory_only(self) -> bool:
        return True

    @property
    def validates_representation_only(self) -> bool:
        return True

    @property
    def authorizes_adaptation(self) -> bool:
        return False

    @property
    def permits_adaptation(self) -> bool:
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
    def executes(self) -> bool:
        return False


class EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Service:
    """Validate one exact adaptation proposal without approving or applying it."""

    def validate(
        self,
        proposal: EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2,
        *,
        validation_id: str,
        reasons: Mapping[str, str] | None = None,
        lineage: Mapping[str, Any] | None = None,
    ) -> EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2:
        if type(proposal) is not EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2:
            raise TypeError(
                "proposal must be EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2"
            )
        if not isinstance(validation_id, str) or not validation_id.strip():
            raise ValueError("validation_id must be a non-empty string")
        if proposal.proposal_status == EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.PROPOSED:
            if proposal.eligibility_status != EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.ELIGIBLE:
                raise EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Error(
                    "PROPOSED proposal requires ELIGIBLE learning evidence"
                )
            if proposal.proposal_payload is None or not isinstance(proposal.proposal_payload, Mapping) or not proposal.proposal_payload:
                raise ValueError("PROPOSED proposal requires a non-empty payload mapping")
            status = EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status.VALID
            default_reason = "adaptation proposal representation is structurally valid for later authorization review"
            fingerprint = _proposal_fingerprint(proposal)
        elif proposal.proposal_status == EnvironmentWorldModelRollbackRepairRetryAdaptationProposalV2Status.BLOCKED:
            if proposal.eligibility_status != EnvironmentWorldModelRollbackRepairRetryLearningEligibilityV2Status.INELIGIBLE:
                raise EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Error(
                    "BLOCKED proposal requires INELIGIBLE learning evidence"
                )
            if proposal.proposal_payload is not None:
                raise ValueError("BLOCKED proposal cannot contain a payload")
            status = EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status.BLOCKED
            default_reason = "blocked adaptation proposal cannot proceed to authorization review"
            fingerprint = "0" * 64
        else:
            raise EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Error(
                "unsupported adaptation proposal status"
            )
        return EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2(
            validation_id=validation_id,
            proposal_id=proposal.proposal_id,
            eligibility_id=proposal.eligibility_id,
            integrity_id=proposal.integrity_id,
            signal_id=proposal.signal_id,
            evaluation_id=proposal.evaluation_id,
            feedback_id=proposal.feedback_id,
            outcome_id=proposal.outcome_id,
            execution_id=proposal.execution_id,
            preparation_id=proposal.preparation_id,
            decision_id=proposal.decision_id,
            source_proposal_id=proposal.source_proposal_id,
            assessment_id=proposal.assessment_id,
            environment_id=proposal.environment_id,
            expected_model_id=proposal.expected_model_id,
            observed_model_id=proposal.observed_model_id,
            eligibility_status=proposal.eligibility_status,
            signal_status=proposal.signal_status,
            confidence=proposal.confidence,
            signal_fingerprint=proposal.signal_fingerprint,
            proposal_kind=proposal.proposal_kind,
            proposal_status=proposal.proposal_status,
            proposal_payload=proposal.proposal_payload,
            proposal_fingerprint=fingerprint,
            validation_status=status,
            reasons=reasons or {"status": default_reason},
            lineage=lineage or {
                "validation_id": validation_id,
                "proposal_id": proposal.proposal_id,
                "eligibility_id": proposal.eligibility_id,
                "integrity_id": proposal.integrity_id,
                "signal_id": proposal.signal_id,
                "evaluation_id": proposal.evaluation_id,
                "feedback_id": proposal.feedback_id,
                "outcome_id": proposal.outcome_id,
                "execution_id": proposal.execution_id,
                "preparation_id": proposal.preparation_id,
                "decision_id": proposal.decision_id,
                "assessment_id": proposal.assessment_id,
            },
        )


__all__ = [
    "EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Error",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Status",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2",
    "EnvironmentWorldModelRollbackRepairRetryAdaptationProposalValidationV2Service",
]
