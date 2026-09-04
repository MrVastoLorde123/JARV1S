"""M14.4 situational context boundary.

SituationalContext records bounded signals about the situation surrounding a
context snapshot. Signals describe observations and relevance; they do not
become truth, user intent, policy, authorization, or execution permission.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .world_state import ContextState


class SituationalContextValidationError(ValueError):
    """Raised when situational context violates the M14.4 boundary."""


MAX_SIGNALS = 128
MAX_SIGNAL_ID_LENGTH = 256
MAX_VALUE_LENGTH = 512


def _validate_text(value: str, field_name: str, max_length: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SituationalContextValidationError(f"{field_name} must be a non-empty string")
    if len(value) > max_length:
        raise SituationalContextValidationError(
            f"{field_name} exceeds maximum length of {max_length}"
        )
    return value


def _freeze(value: Any, path: str = "value") -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        if isinstance(value, float) and not (value == value and abs(value) != float("inf")):
            raise SituationalContextValidationError(f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise SituationalContextValidationError(f"{path} keys must be non-empty strings")
            frozen[key] = _freeze(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item, f"{path}[]") for item in value)
    raise SituationalContextValidationError(
        f"{path} contains unsupported value type: {type(value).__name__}"
    )


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True)
class SituationSignal:
    """Immutable bounded observation contributing to situational context."""

    signal_id: str
    category: str
    value: Any
    source_ref: str | None = None

    def __post_init__(self) -> None:
        _validate_text(self.signal_id, "signal_id", MAX_SIGNAL_ID_LENGTH)
        _validate_text(self.category, "category", MAX_SIGNAL_ID_LENGTH)
        if self.source_ref is not None:
            _validate_text(self.source_ref, "source_ref", MAX_SIGNAL_ID_LENGTH)
        object.__setattr__(self, "value", _freeze(self.value))

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "category": self.category,
            "value": _thaw(self.value),
            "source_ref": self.source_ref,
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "intent_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class SituationalContext:
    """Immutable snapshot of bounded situational signals."""

    context: ContextState
    signals: tuple[SituationSignal, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.context, ContextState):
            raise SituationalContextValidationError("context must be a ContextState")
        if not isinstance(self.signals, tuple):
            raise SituationalContextValidationError("signals must be a tuple")
        if len(self.signals) > MAX_SIGNALS:
            raise SituationalContextValidationError(
                f"signals exceeds maximum count of {MAX_SIGNALS}"
            )
        if any(not isinstance(signal, SituationSignal) for signal in self.signals):
            raise SituationalContextValidationError(
                "signals must contain SituationSignal values"
            )
        signal_ids = tuple(signal.signal_id for signal in self.signals)
        if len(set(signal_ids)) != len(signal_ids):
            raise SituationalContextValidationError("signal IDs must be unique")

    def signal(self, signal_id: str) -> SituationSignal | None:
        _validate_text(signal_id, "signal_id", MAX_SIGNAL_ID_LENGTH)
        return next((item for item in self.signals if item.signal_id == signal_id), None)

    def by_category(self, category: str) -> tuple[SituationSignal, ...]:
        _validate_text(category, "category", MAX_SIGNAL_ID_LENGTH)
        normalized = category.casefold()
        return tuple(item for item in self.signals if item.category.casefold() == normalized)

    def with_signal(self, signal: SituationSignal) -> "SituationalContext":
        if not isinstance(signal, SituationSignal):
            raise TypeError("signal must be a SituationSignal")
        if self.signal(signal.signal_id) is not None:
            raise SituationalContextValidationError(
                f"signal '{signal.signal_id}' already exists"
            )
        return SituationalContext(context=self.context, signals=self.signals + (signal,))

    def to_dict(self) -> dict[str, Any]:
        return {
            "context": self.context.to_dict(),
            "signals": [signal.to_dict() for signal in self.signals],
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "intent_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
