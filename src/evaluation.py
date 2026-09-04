"""M15.3 initiative evaluation boundary.

Evaluation compares an initiative candidate using explicit bounded criteria.
It produces a descriptive judgment, not an approval, instruction,
authorization, policy decision, or execution request.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .initiative import InitiativeCandidate


class InitiativeEvaluationValidationError(ValueError):
    """Raised when initiative evaluation violates the M15.3 boundary."""


MAX_ID_LENGTH = 256
MAX_REASON_LENGTH = 512
MAX_REASONS = 16
MAX_METADATA_ITEMS = 32


def _text(value: str, field_name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InitiativeEvaluationValidationError(f"{field_name} must be a non-empty string")
    if len(value) > maximum:
        raise InitiativeEvaluationValidationError(f"{field_name} exceeds maximum length of {maximum}")
    return value


def _score(value: float, field_name: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise InitiativeEvaluationValidationError(f"{field_name} must be a number")
    number = float(value)
    if number != number or number in (float("inf"), float("-inf")):
        raise InitiativeEvaluationValidationError(f"{field_name} must be finite")
    if not 0.0 <= number <= 1.0:
        raise InitiativeEvaluationValidationError(f"{field_name} must be between 0.0 and 1.0")
    return number


def _freeze(value: Any, path: str = "metadata") -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        if isinstance(value, float) and not (value == value and abs(value) != float("inf")):
            raise InitiativeEvaluationValidationError(f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise InitiativeEvaluationValidationError(f"{path} keys must be non-empty strings")
            frozen[key] = _freeze(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item, f"{path}[]") for item in value)
    raise InitiativeEvaluationValidationError(
        f"{path} contains unsupported value type: {type(value).__name__}"
    )


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True)
class InitiativeEvaluation:
    """Immutable bounded evaluation of one initiative candidate."""

    evaluation_id: str
    candidate: InitiativeCandidate
    value_score: float
    urgency_score: float
    confidence_score: float
    effort_score: float
    risk_score: float
    reasons: tuple[str, ...] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _text(self.evaluation_id, "evaluation_id", MAX_ID_LENGTH)
        if not isinstance(self.candidate, InitiativeCandidate):
            raise InitiativeEvaluationValidationError("candidate must be an InitiativeCandidate")
        for name in ("value_score", "urgency_score", "confidence_score", "effort_score", "risk_score"):
            object.__setattr__(self, name, _score(getattr(self, name), name))
        if not isinstance(self.reasons, tuple):
            raise InitiativeEvaluationValidationError("reasons must be a tuple")
        if len(self.reasons) > MAX_REASONS:
            raise InitiativeEvaluationValidationError(f"reasons exceeds maximum count of {MAX_REASONS}")
        if len(set(self.reasons)) != len(self.reasons):
            raise InitiativeEvaluationValidationError("reasons must be unique")
        for index, reason in enumerate(self.reasons):
            _text(reason, f"reasons[{index}]", MAX_REASON_LENGTH)
        if not isinstance(self.metadata, Mapping):
            raise InitiativeEvaluationValidationError("metadata must be a mapping")
        if len(self.metadata) > MAX_METADATA_ITEMS:
            raise InitiativeEvaluationValidationError(
                f"metadata exceeds maximum item count of {MAX_METADATA_ITEMS}"
            )
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    @property
    def net_signal(self) -> float:
        """Return a bounded descriptive signal, not a permission decision."""
        return (self.value_score + self.urgency_score + self.confidence_score + (1.0 - self.effort_score) + (1.0 - self.risk_score)) / 5.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "evaluation_id": self.evaluation_id,
            "initiative_id": self.candidate.initiative_id,
            "value_score": self.value_score,
            "urgency_score": self.urgency_score,
            "confidence_score": self.confidence_score,
            "effort_score": self.effort_score,
            "risk_score": self.risk_score,
            "net_signal": self.net_signal,
            "reasons": list(self.reasons),
            "metadata": _thaw(self.metadata),
            "evaluation_is_authorization": False,
            "initiative_is_instruction": False,
            "obligation_created": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
            "truth_guaranteed": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
