"""M16.2 controlled self-development change impact assessment.

A ChangeImpactAssessment describes the expected scope and risk of a
SelfDevelopmentProposal. It does not authorize, approve, execute, or reject
the proposed change.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.self_development import SelfDevelopmentProposal, SelfDevelopmentValidationError


class ChangeImpactValidationError(ValueError):
    """Raised when a change impact assessment violates the M16.2 boundary."""


class ImpactLevel(str, Enum):
    """Descriptive impact magnitude; not an authorization decision."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class ImpactDomain(str, Enum):
    """Domains that a self-development change may affect."""

    CODE = "code"
    DATA = "data"
    CONFIGURATION = "configuration"
    INTERFACE = "interface"
    DEPENDENCY = "dependency"
    RUNTIME = "runtime"
    AUTHORITY = "authority"
    IDENTITY = "identity"
    UNKNOWN = "unknown"


MAX_ID_LENGTH = 256
MAX_REASON_LENGTH = 512
MAX_LIST_ITEMS = 64
MAX_METADATA_ITEMS = 32


def _text(value: str, field_name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ChangeImpactValidationError(f"{field_name} must be a non-empty string")
    if len(value) > maximum:
        raise ChangeImpactValidationError(
            f"{field_name} exceeds maximum length of {maximum}"
        )
    return value


def _freeze(value: Any, path: str = "metadata") -> Any:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if value != value or abs(value) == float("inf"):
            raise ChangeImpactValidationError(f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise ChangeImpactValidationError(
                    f"{path} keys must be non-empty strings"
                )
            frozen[key] = _freeze(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item, f"{path}[]") for item in value)
    raise ChangeImpactValidationError(
        f"{path} contains unsupported value type: {type(value).__name__}"
    )


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


def _enum_list(values: tuple[ImpactDomain, ...], field_name: str) -> None:
    if not isinstance(values, tuple):
        raise ChangeImpactValidationError(f"{field_name} must be a tuple")
    if len(values) > MAX_LIST_ITEMS:
        raise ChangeImpactValidationError(
            f"{field_name} exceeds maximum count of {MAX_LIST_ITEMS}"
        )
    if len(set(values)) != len(values):
        raise ChangeImpactValidationError(f"{field_name} must be unique")
    for index, value in enumerate(values):
        if not isinstance(value, ImpactDomain):
            raise ChangeImpactValidationError(
                f"{field_name}[{index}] must be an ImpactDomain"
            )


@dataclass(frozen=True)
class ChangeImpactAssessment:
    """Immutable descriptive assessment for a self-development proposal."""

    assessment_id: str
    proposal: SelfDevelopmentProposal
    overall_impact: ImpactLevel
    affected_domains: tuple[ImpactDomain, ...] = ()
    reasons: tuple[str, ...] = ()
    dependency_impact: ImpactLevel = ImpactLevel.UNKNOWN
    compatibility_impact: ImpactLevel = ImpactLevel.UNKNOWN
    rollback_feasibility: ImpactLevel = ImpactLevel.UNKNOWN
    confidence: float = 0.0
    authority_scope_impact: bool = False
    identity_scope_impact: bool = False
    requires_authority_review: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _text(self.assessment_id, "assessment_id", MAX_ID_LENGTH)
        if not isinstance(self.proposal, SelfDevelopmentProposal):
            raise ChangeImpactValidationError("proposal must be a SelfDevelopmentProposal")
        for name, value in (
            ("overall_impact", self.overall_impact),
            ("dependency_impact", self.dependency_impact),
            ("compatibility_impact", self.compatibility_impact),
            ("rollback_feasibility", self.rollback_feasibility),
        ):
            if not isinstance(value, ImpactLevel):
                raise ChangeImpactValidationError(f"{name} must be an ImpactLevel")
        _enum_list(self.affected_domains, "affected_domains")
        if not isinstance(self.reasons, tuple):
            raise ChangeImpactValidationError("reasons must be a tuple")
        if len(self.reasons) > MAX_LIST_ITEMS:
            raise ChangeImpactValidationError(
                f"reasons exceeds maximum count of {MAX_LIST_ITEMS}"
            )
        if len(set(self.reasons)) != len(self.reasons):
            raise ChangeImpactValidationError("reasons must be unique")
        for index, reason in enumerate(self.reasons):
            _text(reason, f"reasons[{index}]", MAX_REASON_LENGTH)
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise ChangeImpactValidationError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ChangeImpactValidationError("confidence must be between 0 and 1")
        for name, value in (
            ("authority_scope_impact", self.authority_scope_impact),
            ("identity_scope_impact", self.identity_scope_impact),
            ("requires_authority_review", self.requires_authority_review),
        ):
            if not isinstance(value, bool):
                raise ChangeImpactValidationError(f"{name} must be a bool")
        if self.authority_scope_impact and ImpactDomain.AUTHORITY not in self.affected_domains:
            raise ChangeImpactValidationError(
                "authority_scope_impact requires the authority domain"
            )
        if self.identity_scope_impact and ImpactDomain.IDENTITY not in self.affected_domains:
            raise ChangeImpactValidationError(
                "identity_scope_impact requires the identity domain"
            )
        if (self.authority_scope_impact or self.identity_scope_impact) and not self.requires_authority_review:
            raise ChangeImpactValidationError(
                "authority or identity impact requires authority review"
            )
        if not isinstance(self.metadata, Mapping):
            raise ChangeImpactValidationError("metadata must be a mapping")
        if len(self.metadata) > MAX_METADATA_ITEMS:
            raise ChangeImpactValidationError(
                f"metadata exceeds maximum item count of {MAX_METADATA_ITEMS}"
            )
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    @property
    def proposal_id(self) -> str:
        """Stable lineage back to the M16.1 self-development proposal."""

        return self.proposal.proposal_id

    @property
    def change_is_authorized(self) -> bool:
        """Always false: assessment never grants permission."""

        return False

    @property
    def execution_requested(self) -> bool:
        """Always false: assessment never requests execution."""

        return False

    def with_reason(self, reason: str) -> "ChangeImpactAssessment":
        _text(reason, "reason", MAX_REASON_LENGTH)
        if reason in self.reasons:
            raise ChangeImpactValidationError("reason already exists")
        return ChangeImpactAssessment(
            assessment_id=self.assessment_id,
            proposal=self.proposal,
            overall_impact=self.overall_impact,
            affected_domains=self.affected_domains,
            reasons=self.reasons + (reason,),
            dependency_impact=self.dependency_impact,
            compatibility_impact=self.compatibility_impact,
            rollback_feasibility=self.rollback_feasibility,
            confidence=self.confidence,
            authority_scope_impact=self.authority_scope_impact,
            identity_scope_impact=self.identity_scope_impact,
            requires_authority_review=self.requires_authority_review,
            metadata=self.metadata,
        )

    def with_domain(self, domain: ImpactDomain) -> "ChangeImpactAssessment":
        if not isinstance(domain, ImpactDomain):
            raise ChangeImpactValidationError("domain must be an ImpactDomain")
        if domain in self.affected_domains:
            raise ChangeImpactValidationError("domain already exists")
        return ChangeImpactAssessment(
            assessment_id=self.assessment_id,
            proposal=self.proposal,
            overall_impact=self.overall_impact,
            affected_domains=self.affected_domains + (domain,),
            reasons=self.reasons,
            dependency_impact=self.dependency_impact,
            compatibility_impact=self.compatibility_impact,
            rollback_feasibility=self.rollback_feasibility,
            confidence=self.confidence,
            authority_scope_impact=self.authority_scope_impact,
            identity_scope_impact=self.identity_scope_impact,
            requires_authority_review=self.requires_authority_review,
            metadata=self.metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "assessment_id": self.assessment_id,
            "proposal_id": self.proposal_id,
            "overall_impact": self.overall_impact.value,
            "affected_domains": [domain.value for domain in self.affected_domains],
            "reasons": list(self.reasons),
            "dependency_impact": self.dependency_impact.value,
            "compatibility_impact": self.compatibility_impact.value,
            "rollback_feasibility": self.rollback_feasibility.value,
            "confidence": self.confidence,
            "authority_scope_impact": self.authority_scope_impact,
            "identity_scope_impact": self.identity_scope_impact,
            "requires_authority_review": self.requires_authority_review,
            "metadata": _thaw(self.metadata),
            "impact_assessment": True,
            "change_is_authorized": False,
            "instruction_granted": False,
            "execution_requested": False,
            "policy_authority": False,
            "authority_scope_change_authorized": False,
            "identity_change_authorized": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
