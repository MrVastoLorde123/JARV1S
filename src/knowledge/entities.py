"""M13.1 entity boundary.

An Entity is a structured referent for personal knowledge. It is not a claim
of truth, fact, intent, policy, authorization, or execution.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class EntityValidationError(ValueError):
    """Raised when an entity violates the knowledge boundary."""


class EntityType(str, Enum):
    PERSON = "PERSON"
    PROJECT = "PROJECT"
    ORGANIZATION = "ORGANIZATION"
    PRODUCT = "PRODUCT"
    SYSTEM = "SYSTEM"
    DEVICE = "DEVICE"
    LOCATION = "LOCATION"
    CONCEPT = "CONCEPT"
    SKILL = "SKILL"
    GOAL = "GOAL"
    DOCUMENT = "DOCUMENT"
    EVENT = "EVENT"


MAX_ENTITY_ID_LENGTH = 256
MAX_ENTITY_NAME_LENGTH = 512
MAX_ENTITY_METADATA_ITEMS = 64
MAX_ENTITY_EVIDENCE_REFS = 128


def _validate_text(value: str, field_name: str, max_length: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EntityValidationError(f"{field_name} must be a non-empty string")
    if len(value) > max_length:
        raise EntityValidationError(
            f"{field_name} exceeds maximum length of {max_length}"
        )
    return value


def _freeze_metadata(value: Any, path: str = "metadata") -> Any:
    """Freeze JSON-like metadata so retained references cannot mutate an entity."""
    if value is None or isinstance(value, (str, int, float, bool)):
        if isinstance(value, float) and not (value == value and abs(value) != float("inf")):
            raise EntityValidationError(f"{path} contains a non-finite number")
        return value

    if isinstance(value, Mapping):
        frozen = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise EntityValidationError(f"{path} keys must be non-empty strings")
            frozen[key] = _freeze_metadata(item, f"{path}.{key}")
        return MappingProxyType(frozen)

    if isinstance(value, (list, tuple)):
        return tuple(_freeze_metadata(item, f"{path}[]") for item in value)

    raise EntityValidationError(
        f"{path} contains unsupported metadata type: {type(value).__name__}"
    )


def _thaw_metadata(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw_metadata(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_metadata(item) for item in value]
    return value


@dataclass(frozen=True)
class Entity:
    """Immutable structured referent for the personal knowledge layer."""

    entity_id: str
    entity_type: EntityType
    canonical_name: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _validate_text(self.entity_id, "entity_id", MAX_ENTITY_ID_LENGTH)
        _validate_text(self.canonical_name, "canonical_name", MAX_ENTITY_NAME_LENGTH)

        if not isinstance(self.entity_type, EntityType):
            try:
                object.__setattr__(self, "entity_type", EntityType(self.entity_type))
            except (TypeError, ValueError) as exc:
                raise EntityValidationError("entity_type must be a supported EntityType") from exc

        if not isinstance(self.metadata, Mapping):
            raise EntityValidationError("metadata must be a mapping")
        if len(self.metadata) > MAX_ENTITY_METADATA_ITEMS:
            raise EntityValidationError(
                f"metadata exceeds maximum item count of {MAX_ENTITY_METADATA_ITEMS}"
            )
        frozen_metadata = _freeze_metadata(self.metadata)
        object.__setattr__(self, "metadata", frozen_metadata)

        if not isinstance(self.evidence_refs, tuple):
            raise EntityValidationError("evidence_refs must be a tuple")
        if len(self.evidence_refs) > MAX_ENTITY_EVIDENCE_REFS:
            raise EntityValidationError(
                f"evidence_refs exceeds maximum count of {MAX_ENTITY_EVIDENCE_REFS}"
            )
        if len(set(self.evidence_refs)) != len(self.evidence_refs):
            raise EntityValidationError("evidence_refs must be unique")
        for index, reference in enumerate(self.evidence_refs):
            _validate_text(reference, f"evidence_refs[{index}]", MAX_ENTITY_ID_LENGTH)

    def to_dict(self) -> dict[str, Any]:
        """Serialize without asserting truth or authority."""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type.value,
            "canonical_name": self.canonical_name,
            "metadata": _thaw_metadata(self.metadata),
            "evidence_refs": self.evidence_refs,
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "intent_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
