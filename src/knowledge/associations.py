"""M13.4 evidence-backed association boundary.

An EvidenceBackedAssociation ties an existing relationship to explicit
provenance references. The evidence is a basis for the association, not a
truth claim, fact guarantee, policy, authorization, or execution permission.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .relationships import Relationship, RelationshipType


class AssociationEvidenceValidationError(ValueError):
    """Raised when an evidence-backed association violates its boundary."""


MAX_ASSOCIATION_EVIDENCE_REFS = 64
MAX_EVIDENCE_REF_LENGTH = 256
MAX_SOURCE_LENGTH = 256


def _validate_text(value: str, field_name: str, max_length: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AssociationEvidenceValidationError(
            f"{field_name} must be a non-empty string"
        )
    if len(value) > max_length:
        raise AssociationEvidenceValidationError(
            f"{field_name} exceeds maximum length of {max_length}"
        )
    return value


@dataclass(frozen=True)
class AssociationEvidence:
    """Immutable provenance reference for an association."""

    evidence_ref: str
    source: str

    def __post_init__(self) -> None:
        _validate_text(self.evidence_ref, "evidence_ref", MAX_EVIDENCE_REF_LENGTH)
        _validate_text(self.source, "source", MAX_SOURCE_LENGTH)

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_ref": self.evidence_ref,
            "source": self.source,
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class EvidenceBackedAssociation:
    """An existing relationship explicitly grounded in provenance references."""

    relationship: Relationship
    evidence: tuple[AssociationEvidence, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.relationship, Relationship):
            raise AssociationEvidenceValidationError(
                "relationship must be a Relationship"
            )
        if not isinstance(self.evidence, tuple):
            raise AssociationEvidenceValidationError("evidence must be a tuple")
        if not self.evidence:
            raise AssociationEvidenceValidationError(
                "an evidence-backed association requires at least one evidence item"
            )
        if len(self.evidence) > MAX_ASSOCIATION_EVIDENCE_REFS:
            raise AssociationEvidenceValidationError(
                "evidence exceeds maximum count of "
                f"{MAX_ASSOCIATION_EVIDENCE_REFS}"
            )
        for item in self.evidence:
            if not isinstance(item, AssociationEvidence):
                raise AssociationEvidenceValidationError(
                    "evidence must contain AssociationEvidence values"
                )
        evidence_refs = tuple(item.evidence_ref for item in self.evidence)
        if len(set(evidence_refs)) != len(evidence_refs):
            raise AssociationEvidenceValidationError(
                "evidence references must be unique"
            )
        relationship_refs = set(self.relationship.evidence_refs)
        missing = [ref for ref in evidence_refs if ref not in relationship_refs]
        if missing:
            raise AssociationEvidenceValidationError(
                "evidence references must already be attached to the relationship: "
                + ", ".join(missing)
            )

    @property
    def relationship_id(self) -> str:
        return self.relationship.relationship_id

    @property
    def relationship_type(self) -> RelationshipType:
        return self.relationship.relationship_type

    @property
    def evidence_refs(self) -> tuple[str, ...]:
        return tuple(item.evidence_ref for item in self.evidence)

    def to_dict(self) -> dict[str, Any]:
        return {
            "relationship": self.relationship.to_dict(),
            "evidence": [item.to_dict() for item in self.evidence],
            "evidence_backed": True,
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "intent_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
