"""M15.1 bounded initiative candidate boundary.

An InitiativeCandidate records a descriptive opportunity or need that JARVIS
may surface from existing context. It is a proposal seed, not an instruction,
authorization, policy decision, or execution request.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


class InitiativeValidationError(ValueError):
    """Raised when an initiative candidate violates the M15.1 boundary."""


MAX_ID_LENGTH = 256
MAX_TITLE_LENGTH = 512
MAX_DESCRIPTION_LENGTH = 2048
MAX_REFERENCE_LENGTH = 256
MAX_REFERENCES = 64
MAX_TAG_LENGTH = 128
MAX_TAGS = 32
MAX_METADATA_ITEMS = 32


def _text(value: str, field_name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InitiativeValidationError(f"{field_name} must be a non-empty string")
    if len(value) > maximum:
        raise InitiativeValidationError(
            f"{field_name} exceeds maximum length of {maximum}"
        )
    return value


def _freeze(value: Any, path: str = "metadata") -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        if isinstance(value, float) and not (value == value and abs(value) != float("inf")):
            raise InitiativeValidationError(f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise InitiativeValidationError(f"{path} keys must be non-empty strings")
            frozen[key] = _freeze(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item, f"{path}[]") for item in value)
    raise InitiativeValidationError(
        f"{path} contains unsupported value type: {type(value).__name__}"
    )


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True)
class InitiativeCandidate:
    """Immutable bounded description of a possible initiative."""

    initiative_id: str
    title: str
    description: str
    context_refs: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _text(self.initiative_id, "initiative_id", MAX_ID_LENGTH)
        _text(self.title, "title", MAX_TITLE_LENGTH)
        _text(self.description, "description", MAX_DESCRIPTION_LENGTH)

        if not isinstance(self.context_refs, tuple):
            raise InitiativeValidationError("context_refs must be a tuple")
        if len(self.context_refs) > MAX_REFERENCES:
            raise InitiativeValidationError(
                f"context_refs exceeds maximum count of {MAX_REFERENCES}"
            )
        if len(set(self.context_refs)) != len(self.context_refs):
            raise InitiativeValidationError("context_refs must be unique")
        for index, reference in enumerate(self.context_refs):
            _text(reference, f"context_refs[{index}]", MAX_REFERENCE_LENGTH)

        if not isinstance(self.tags, tuple):
            raise InitiativeValidationError("tags must be a tuple")
        if len(self.tags) > MAX_TAGS:
            raise InitiativeValidationError(f"tags exceeds maximum count of {MAX_TAGS}")
        if len(set(self.tags)) != len(self.tags):
            raise InitiativeValidationError("tags must be unique")
        for index, tag in enumerate(self.tags):
            _text(tag, f"tags[{index}]", MAX_TAG_LENGTH)

        if not isinstance(self.metadata, Mapping):
            raise InitiativeValidationError("metadata must be a mapping")
        if len(self.metadata) > MAX_METADATA_ITEMS:
            raise InitiativeValidationError(
                f"metadata exceeds maximum item count of {MAX_METADATA_ITEMS}"
            )
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    def with_context_ref(self, reference: str) -> "InitiativeCandidate":
        _text(reference, "reference", MAX_REFERENCE_LENGTH)
        if reference in self.context_refs:
            raise InitiativeValidationError("context reference already exists")
        return InitiativeCandidate(
            initiative_id=self.initiative_id,
            title=self.title,
            description=self.description,
            context_refs=self.context_refs + (reference,),
            tags=self.tags,
            metadata=self.metadata,
        )

    def with_tag(self, tag: str) -> "InitiativeCandidate":
        _text(tag, "tag", MAX_TAG_LENGTH)
        if tag in self.tags:
            raise InitiativeValidationError("tag already exists")
        return InitiativeCandidate(
            initiative_id=self.initiative_id,
            title=self.title,
            description=self.description,
            context_refs=self.context_refs,
            tags=self.tags + (tag,),
            metadata=self.metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "initiative_id": self.initiative_id,
            "title": self.title,
            "description": self.description,
            "context_refs": list(self.context_refs),
            "tags": list(self.tags),
            "metadata": _thaw(self.metadata),
            "initiative_is_instruction": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
            "user_intent_guaranteed": False,
            "truth_guaranteed": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
