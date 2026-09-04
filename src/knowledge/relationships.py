"""M13.3 relationship boundary.

A Relationship records a bounded association between two entity identities.
It does not establish truth, fact, intent, policy, authorization, or execution.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class RelationshipValidationError(ValueError):
    """Raised when a relationship violates the knowledge boundary."""


class RelationshipType(str, Enum):
    WORKS_ON = "works_on"
    OWNS = "owns"
    KNOWS = "knows"
    DEPENDS_ON = "depends_on"
    USES = "uses"
    LOCATED_AT = "located_at"
    RELATED_TO = "related_to"
    PART_OF = "part_of"
    LEARNED_FROM = "learned_from"
    SUPPORTS = "supports"
    CONFLICTS_WITH = "conflicts_with"


MAX_RELATIONSHIP_ID_LENGTH = 256
MAX_RELATIONSHIP_METADATA_ITEMS = 32
MAX_RELATIONSHIP_EVIDENCE_REFS = 64


def _validate_text(value: str, field_name: str, max_length: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RelationshipValidationError(f"{field_name} must be a non-empty string")
    if len(value) > max_length:
        raise RelationshipValidationError(
            f"{field_name} exceeds maximum length of {max_length}"
        )
    return value


def _freeze_metadata(value: Any, path: str = "metadata") -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        if isinstance(value, float) and not (value == value and abs(value) != float("inf")):
            raise RelationshipValidationError(f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise RelationshipValidationError(f"{path} keys must be non-empty strings")
            frozen[key] = _freeze_metadata(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_metadata(item, f"{path}[]") for item in value)
    raise RelationshipValidationError(
        f"{path} contains unsupported metadata type: {type(value).__name__}"
    )


def _thaw_metadata(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw_metadata(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_metadata(item) for item in value]
    return value


@dataclass(frozen=True)
class Relationship:
    """Immutable bounded association between two entity identities."""

    relationship_id: str
    relationship_type: RelationshipType
    source_entity_id: str
    target_entity_id: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _validate_text(self.relationship_id, "relationship_id", MAX_RELATIONSHIP_ID_LENGTH)
        _validate_text(self.source_entity_id, "source_entity_id", MAX_RELATIONSHIP_ID_LENGTH)
        _validate_text(self.target_entity_id, "target_entity_id", MAX_RELATIONSHIP_ID_LENGTH)
        if not isinstance(self.relationship_type, RelationshipType):
            try:
                object.__setattr__(self, "relationship_type", RelationshipType(self.relationship_type))
            except (TypeError, ValueError) as exc:
                raise RelationshipValidationError(
                    "relationship_type must be a supported RelationshipType"
                ) from exc
        if not isinstance(self.metadata, Mapping):
            raise RelationshipValidationError("metadata must be a mapping")
        if len(self.metadata) > MAX_RELATIONSHIP_METADATA_ITEMS:
            raise RelationshipValidationError(
                f"metadata exceeds maximum item count of {MAX_RELATIONSHIP_METADATA_ITEMS}"
            )
        object.__setattr__(self, "metadata", _freeze_metadata(self.metadata))
        if not isinstance(self.evidence_refs, tuple):
            raise RelationshipValidationError("evidence_refs must be a tuple")
        if len(self.evidence_refs) > MAX_RELATIONSHIP_EVIDENCE_REFS:
            raise RelationshipValidationError(
                f"evidence_refs exceeds maximum count of {MAX_RELATIONSHIP_EVIDENCE_REFS}"
            )
        if len(set(self.evidence_refs)) != len(self.evidence_refs):
            raise RelationshipValidationError("evidence_refs must be unique")
        for index, reference in enumerate(self.evidence_refs):
            _validate_text(reference, f"evidence_refs[{index}]", MAX_RELATIONSHIP_ID_LENGTH)

    def to_dict(self) -> dict[str, Any]:
        return {
            "relationship_id": self.relationship_id,
            "relationship_type": self.relationship_type.value,
            "source_entity_id": self.source_entity_id,
            "target_entity_id": self.target_entity_id,
            "metadata": _thaw_metadata(self.metadata),
            "evidence_refs": list(self.evidence_refs),
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "intent_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
