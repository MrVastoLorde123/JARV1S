"""M14.1 bounded personal context state boundary.

ContextState is a structured snapshot of currently relevant world-model state.
It is derived context, not truth, user intent, authorization, policy, or
execution permission.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Any, Mapping


class ContextStateValidationError(ValueError):
    """Raised when context state violates the M14.1 boundary."""


MAX_CONTEXT_ID_LENGTH = 256
MAX_STATE_ITEMS = 128
MAX_REFERENCE_LENGTH = 256


def _validate_text(value: str, field_name: str, max_length: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContextStateValidationError(f"{field_name} must be a non-empty string")
    if len(value) > max_length:
        raise ContextStateValidationError(
            f"{field_name} exceeds maximum length of {max_length}"
        )
    return value


def _freeze_value(value: Any, path: str = "state") -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        if isinstance(value, float) and not (value == value and abs(value) != float("inf")):
            raise ContextStateValidationError(f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise ContextStateValidationError(f"{path} keys must be non-empty strings")
            frozen[key] = _freeze_value(item, f"{path}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_value(item, f"{path}[]") for item in value)
    raise ContextStateValidationError(
        f"{path} contains unsupported value type: {type(value).__name__}"
    )


def _thaw_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_value(item) for item in value]
    return value


@dataclass(frozen=True)
class ContextState:
    """Immutable snapshot of bounded current context."""

    context_id: str
    state: Mapping[str, Any] = field(default_factory=dict)
    source_refs: tuple[str, ...] = ()
    observed_at: str | None = None

    def __post_init__(self) -> None:
        _validate_text(self.context_id, "context_id", MAX_CONTEXT_ID_LENGTH)
        if not isinstance(self.state, Mapping):
            raise ContextStateValidationError("state must be a mapping")
        if len(self.state) > MAX_STATE_ITEMS:
            raise ContextStateValidationError(
                f"state exceeds maximum item count of {MAX_STATE_ITEMS}"
            )
        object.__setattr__(self, "state", _freeze_value(self.state))

        if not isinstance(self.source_refs, tuple):
            raise ContextStateValidationError("source_refs must be a tuple")
        if len(self.source_refs) > MAX_STATE_ITEMS:
            raise ContextStateValidationError(
                f"source_refs exceeds maximum count of {MAX_STATE_ITEMS}"
            )
        if len(set(self.source_refs)) != len(self.source_refs):
            raise ContextStateValidationError("source_refs must be unique")
        for index, reference in enumerate(self.source_refs):
            _validate_text(reference, f"source_refs[{index}]", MAX_REFERENCE_LENGTH)

        if self.observed_at is not None:
            _validate_text(self.observed_at, "observed_at", MAX_REFERENCE_LENGTH)
            try:
                datetime.fromisoformat(self.observed_at.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ContextStateValidationError("observed_at must be ISO-8601") from exc

    def with_state(self, **updates: Any) -> "ContextState":
        if not updates:
            return self
        combined = _thaw_value(self.state)
        combined.update(updates)
        return ContextState(
            context_id=self.context_id,
            state=combined,
            source_refs=self.source_refs,
            observed_at=self.observed_at,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "state": _thaw_value(self.state),
            "source_refs": list(self.source_refs),
            "observed_at": self.observed_at,
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "intent_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
