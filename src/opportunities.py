"""M15.2 bounded opportunity and need detection boundary.

Detection turns existing context signals into descriptive detections. A
Detection is evidence of a possible opportunity or need, not truth, intent,
obligation, priority, authorization, or execution permission.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping
from types import MappingProxyType


class OpportunityDetectionValidationError(ValueError):
    """Raised when opportunity/need detection violates the M15.2 boundary."""


class DetectionType(str, Enum):
    OPPORTUNITY = "opportunity"
    NEED = "need"
    RISK = "risk"
    GAP = "gap"
    CHANGE = "change"


MAX_ID_LENGTH = 256
MAX_TITLE_LENGTH = 512
MAX_DESCRIPTION_LENGTH = 2048
MAX_REFERENCE_LENGTH = 256
MAX_REFERENCES = 64
MAX_METADATA_ITEMS = 32


def _text(value: str, field_name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OpportunityDetectionValidationError(f"{field_name} must be a non-empty string")
    if len(value) > maximum:
        raise OpportunityDetectionValidationError(
            f"{field_name} exceeds maximum length of {maximum}"
        )
    return value


def _freeze(value: Any, path: str = "metadata") -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        if isinstance(value, float) and not (value == value and abs(value) != float("inf")):
            raise OpportunityDetectionValidationError(f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise OpportunityDetectionValidationError(f"{path} keys must be non-empty strings")
            frozen[key] = _freeze(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item, f"{path}[]") for item in value)
    raise OpportunityDetectionValidationError(
        f"{path} contains unsupported value type: {type(value).__name__}"
    )


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True)
class OpportunityDetection:
    """Immutable bounded description of a detected possible opportunity or need."""

    detection_id: str
    detection_type: DetectionType
    title: str
    description: str
    context_refs: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _text(self.detection_id, "detection_id", MAX_ID_LENGTH)
        if not isinstance(self.detection_type, DetectionType):
            try:
                object.__setattr__(self, "detection_type", DetectionType(self.detection_type))
            except (TypeError, ValueError) as exc:
                raise OpportunityDetectionValidationError("detection_type must be supported DetectionType") from exc
        _text(self.title, "title", MAX_TITLE_LENGTH)
        _text(self.description, "description", MAX_DESCRIPTION_LENGTH)
        if not isinstance(self.context_refs, tuple):
            raise OpportunityDetectionValidationError("context_refs must be a tuple")
        if len(self.context_refs) > MAX_REFERENCES:
            raise OpportunityDetectionValidationError(
                f"context_refs exceeds maximum count of {MAX_REFERENCES}"
            )
        if len(set(self.context_refs)) != len(self.context_refs):
            raise OpportunityDetectionValidationError("context_refs must be unique")
        for index, reference in enumerate(self.context_refs):
            _text(reference, f"context_refs[{index}]", MAX_REFERENCE_LENGTH)
        if not isinstance(self.metadata, Mapping):
            raise OpportunityDetectionValidationError("metadata must be a mapping")
        if len(self.metadata) > MAX_METADATA_ITEMS:
            raise OpportunityDetectionValidationError(
                f"metadata exceeds maximum item count of {MAX_METADATA_ITEMS}"
            )
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    def with_context_ref(self, reference: str) -> "OpportunityDetection":
        _text(reference, "reference", MAX_REFERENCE_LENGTH)
        if reference in self.context_refs:
            raise OpportunityDetectionValidationError("context reference already exists")
        return OpportunityDetection(
            detection_id=self.detection_id,
            detection_type=self.detection_type,
            title=self.title,
            description=self.description,
            context_refs=self.context_refs + (reference,),
            metadata=self.metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "detection_id": self.detection_id,
            "detection_type": self.detection_type.value,
            "title": self.title,
            "description": self.description,
            "context_refs": list(self.context_refs),
            "metadata": _thaw(self.metadata),
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "intent_guaranteed": False,
            "obligation_created": False,
            "importance_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)


@dataclass(frozen=True)
class OpportunityDetectionSet:
    """Immutable bounded collection of detections."""

    detections: tuple[OpportunityDetection, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.detections, tuple):
            raise OpportunityDetectionValidationError("detections must be a tuple")
        if len(self.detections) > MAX_REFERENCES:
            raise OpportunityDetectionValidationError(
                f"detections exceeds maximum count of {MAX_REFERENCES}"
            )
        if any(not isinstance(item, OpportunityDetection) for item in self.detections):
            raise OpportunityDetectionValidationError(
                "detections must contain OpportunityDetection values"
            )
        ids = tuple(item.detection_id for item in self.detections)
        if len(set(ids)) != len(ids):
            raise OpportunityDetectionValidationError("detection IDs must be unique")

    def by_type(self, detection_type: DetectionType) -> tuple[OpportunityDetection, ...]:
        if not isinstance(detection_type, DetectionType):
            try:
                detection_type = DetectionType(detection_type)
            except (TypeError, ValueError) as exc:
                raise OpportunityDetectionValidationError("detection_type must be supported DetectionType") from exc
        return tuple(item for item in self.detections if item.detection_type is detection_type)

    def with_detection(self, detection: OpportunityDetection) -> "OpportunityDetectionSet":
        if not isinstance(detection, OpportunityDetection):
            raise TypeError("detection must be an OpportunityDetection")
        if any(item.detection_id == detection.detection_id for item in self.detections):
            raise OpportunityDetectionValidationError("detection ID already exists")
        return OpportunityDetectionSet(self.detections + (detection,))

    def to_dict(self) -> dict[str, Any]:
        return {
            "detections": [item.to_dict() for item in self.detections],
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "intent_guaranteed": False,
            "obligation_created": False,
            "importance_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
