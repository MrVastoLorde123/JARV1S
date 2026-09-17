"""M52: bounded authorization decision boundary.

Authorization is a separate deterministic decision over an explicitly
confirmed scheduling/notification proposal. This module records the decision
and its rationale without selecting providers/tools or executing anything.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from .confirmation import ConfirmationDisposition, ConfirmationResult


class AuthorizationDisposition(str, Enum):
    GRANTED = "GRANTED"
    DENIED = "DENIED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class AuthorizationDecision:
    """Immutable authorization outcome for one confirmed proposal."""

    authorization_id: str
    source_confirmation_result_id: str
    confirmation_id: str
    disposition: AuthorizationDisposition
    rationale: str
    constraints: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "authorization_id",
            "source_confirmation_result_id",
            "confirmation_id",
            "rationale",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.disposition, AuthorizationDisposition):
            raise TypeError("disposition must be an AuthorizationDisposition")
        if not isinstance(self.constraints, tuple):
            raise TypeError("constraints must be a tuple")
        if len(set(self.constraints)) != len(self.constraints):
            raise ValueError("constraints must contain unique values")
        if any(not isinstance(item, str) or not item.strip() for item in self.constraints):
            raise ValueError("constraints must contain non-empty strings")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "source_confirmation_result_id": self.source_confirmation_result_id,
            "confirmation_id": self.confirmation_id,
            "disposition": self.disposition.value,
            "rationale": self.rationale,
            "constraints": self.constraints,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "intent_established": False,
            "authority_granted": self.disposition is AuthorizationDisposition.GRANTED,
            "permissions_granted": self.disposition is AuthorizationDisposition.GRANTED,
            "execution_requested": False,
            "execution_performed": False,
        }


@dataclass(frozen=True)
class AuthorizationDecisionSet:
    """Immutable authorization decisions bound to one confirmation result."""

    decision_set_id: str
    source_confirmation_result_id: str
    decisions: tuple[AuthorizationDecision, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("decision_set_id", "source_confirmation_result_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.decisions, tuple) or any(
            not isinstance(item, AuthorizationDecision) for item in self.decisions
        ):
            raise TypeError("decisions must be a tuple of AuthorizationDecision values")
        ids = tuple(item.authorization_id for item in self.decisions)
        if len(set(ids)) != len(ids):
            raise ValueError("authorization IDs must be unique")
        if any(item.source_confirmation_result_id != self.source_confirmation_result_id for item in self.decisions):
            raise ValueError("source confirmation-result identity mismatch")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def granted_ids(self) -> tuple[str, ...]:
        return tuple(item.authorization_id for item in self.decisions if item.disposition is AuthorizationDisposition.GRANTED)

    def to_context(self) -> dict[str, Any]:
        return {
            "decision_set_id": self.decision_set_id,
            "source_confirmation_result_id": self.source_confirmation_result_id,
            "decisions": tuple(item.to_context() for item in self.decisions),
            "granted_ids": self.granted_ids,
            "metadata": dict(self.metadata),
            "truth_established": False,
            "intent_established": False,
            "authority_granted": bool(self.granted_ids),
            "permissions_granted": bool(self.granted_ids),
            "execution_requested": False,
            "execution_performed": False,
        }


def build_authorization_decision_set(
    confirmation: ConfirmationResult,
    *,
    decision_set_id: str,
    decisions: tuple[AuthorizationDecision, ...] = (),
    metadata: Mapping[str, Any] | None = None,
) -> AuthorizationDecisionSet:
    """Bind authorization decisions to one exact confirmation result."""
    if not isinstance(confirmation, ConfirmationResult):
        raise TypeError("confirmation must be a ConfirmationResult")
    if not isinstance(decision_set_id, str) or not decision_set_id.strip():
        raise ValueError("decision_set_id must be a non-empty string")
    if not isinstance(decisions, tuple) or any(not isinstance(item, AuthorizationDecision) for item in decisions):
        raise TypeError("decisions must be a tuple of AuthorizationDecision values")

    requests_by_id = {item.confirmation_id: item for item in confirmation.requests}
    for decision in decisions:
        if decision.source_confirmation_result_id != confirmation.result_id:
            raise ValueError("source confirmation-result identity mismatch")
        request = requests_by_id.get(decision.confirmation_id)
        if request is None:
            raise ValueError("authorization may only reference confirmations from the supplied result")
        if request.disposition is not ConfirmationDisposition.CONFIRMED:
            raise ValueError("authorization requires explicit CONFIRMED disposition")

    return AuthorizationDecisionSet(
        decision_set_id=decision_set_id.strip(),
        source_confirmation_result_id=confirmation.result_id,
        decisions=decisions,
        metadata={"source": "M52", **dict(metadata or {})},
    )


__all__ = [
    "AuthorizationDecision",
    "AuthorizationDecisionSet",
    "AuthorizationDisposition",
    "build_authorization_decision_set",
]
