"""M22.2 bounded capability trust and provenance contracts.

This module records where a capability came from and what evidence supports a
trust assessment. It does not grant permission, authorization, or execution
rights.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class CapabilityTrustError(ValueError):
    """Raised when a capability trust/provenance contract is invalid."""


class TrustStatus(str, Enum):
    """Bounded trust-assessment outcomes."""

    UNASSESSED = "UNASSESSED"
    CONDITIONAL = "CONDITIONAL"
    TRUSTED = "TRUSTED"
    UNTRUSTED = "UNTRUSTED"


@dataclass(frozen=True)
class ProvenanceEvidence:
    """Immutable evidence explaining one provenance or trust claim."""

    evidence_type: str
    source: str
    detail: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field_name in ("evidence_type", "source", "detail"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise CapabilityTrustError(
                    f"{field_name} must be a non-empty string"
                )
        if not isinstance(self.metadata, Mapping):
            raise CapabilityTrustError("metadata must be a mapping")
        object.__setattr__(self, "metadata", dict(self.metadata))


@dataclass(frozen=True)
class CapabilityProvenance:
    """Immutable declaration of a capability's origin and supporting evidence."""

    capability_id: str
    source: str
    origin: str
    publisher: str | None = None
    integrity_status: str = "unknown"
    verification_method: str | None = None
    evidence: tuple[ProvenanceEvidence, ...] = ()

    def __post_init__(self) -> None:
        for field_name in ("capability_id", "source", "origin", "integrity_status"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise CapabilityTrustError(
                    f"{field_name} must be a non-empty string"
                )
        if self.publisher is not None and (
            not isinstance(self.publisher, str) or not self.publisher.strip()
        ):
            raise CapabilityTrustError("publisher must be a non-empty string or None")
        if self.verification_method is not None and (
            not isinstance(self.verification_method, str)
            or not self.verification_method.strip()
        ):
            raise CapabilityTrustError(
                "verification_method must be a non-empty string or None"
            )
        if not isinstance(self.evidence, tuple):
            raise CapabilityTrustError("evidence must be a tuple")
        if not all(isinstance(item, ProvenanceEvidence) for item in self.evidence):
            raise CapabilityTrustError(
                "evidence must contain only ProvenanceEvidence values"
            )

    def to_context(self) -> dict[str, object]:
        return {
            "capability_id": self.capability_id,
            "source": self.source,
            "origin": self.origin,
            "publisher": self.publisher,
            "integrity_status": self.integrity_status,
            "verification_method": self.verification_method,
            "evidence_count": len(self.evidence),
            "authority_granted": False,
            "permission_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class CapabilityTrustAssessment:
    """Immutable, evidence-linked trust assessment with no authority semantics."""

    capability_id: str
    status: TrustStatus
    confidence: float
    evidence: tuple[ProvenanceEvidence, ...] = ()
    rationale: tuple[str, ...] = ()
    assessor: str = "unspecified"

    def __post_init__(self) -> None:
        if not isinstance(self.capability_id, str) or not self.capability_id.strip():
            raise CapabilityTrustError("capability_id must be a non-empty string")
        if not isinstance(self.status, TrustStatus):
            raise CapabilityTrustError("status must be a TrustStatus")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise CapabilityTrustError("confidence must be a number")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise CapabilityTrustError("confidence must be bounded to [0, 1]")
        if not isinstance(self.evidence, tuple):
            raise CapabilityTrustError("evidence must be a tuple")
        if not all(isinstance(item, ProvenanceEvidence) for item in self.evidence):
            raise CapabilityTrustError(
                "evidence must contain only ProvenanceEvidence values"
            )
        if not isinstance(self.rationale, tuple) or not all(
            isinstance(item, str) and item.strip() for item in self.rationale
        ):
            raise CapabilityTrustError(
                "rationale must be a tuple of non-empty strings"
            )
        if not isinstance(self.assessor, str) or not self.assessor.strip():
            raise CapabilityTrustError("assessor must be a non-empty string")
        if self.status is TrustStatus.UNASSESSED and self.confidence != 0.0:
            raise CapabilityTrustError(
                "UNASSESSED trust must have zero confidence"
            )

    def validate_for(self, provenance: CapabilityProvenance) -> None:
        """Ensure the assessment applies to the exact capability identity."""
        if not isinstance(provenance, CapabilityProvenance):
            raise TypeError("provenance must be a CapabilityProvenance")
        if self.capability_id.strip().lower() != provenance.capability_id.strip().lower():
            raise CapabilityTrustError(
                "trust assessment capability_id does not match provenance"
            )

    def to_context(self) -> dict[str, object]:
        return {
            "capability_id": self.capability_id,
            "trust_status": self.status.value,
            "trust_confidence": float(self.confidence),
            "evidence_count": len(self.evidence),
            "rationale": tuple(self.rationale),
            "assessor": self.assessor,
            "authority_granted": False,
            "permission_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
        }
