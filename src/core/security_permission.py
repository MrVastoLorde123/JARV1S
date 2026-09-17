"""M75: explicit principal-to-capability permission policy."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Sequence


class PermissionAction(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    INVOKE = "INVOKE"
    DELETE = "DELETE"
    ADMIN = "ADMIN"


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True)
class PermissionGrant:
    principal_id: str
    capability_id: str
    actions: tuple[PermissionAction, ...]
    constraints: Mapping[str, Any] = field(default_factory=dict)
    enabled: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "principal_id", _text(self.principal_id, "principal_id"))
        object.__setattr__(self, "capability_id", _text(self.capability_id, "capability_id"))
        if not isinstance(self.actions, tuple) or not self.actions:
            raise ValueError("actions must be a non-empty tuple")
        if any(not isinstance(item, PermissionAction) for item in self.actions):
            raise TypeError("actions must contain PermissionAction values")
        if len(set(self.actions)) != len(self.actions):
            raise ValueError("actions must be unique")
        if not isinstance(self.constraints, Mapping):
            raise TypeError("constraints must be a mapping")
        if not isinstance(self.enabled, bool):
            raise TypeError("enabled must be a bool")
        object.__setattr__(self, "constraints", MappingProxyType(dict(self.constraints)))

    def allows(self, action: PermissionAction) -> bool:
        return self.enabled and action in self.actions


@dataclass(frozen=True)
class PermissionRequest:
    principal_id: str
    capability_id: str
    action: PermissionAction
    context: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "principal_id", _text(self.principal_id, "principal_id"))
        object.__setattr__(self, "capability_id", _text(self.capability_id, "capability_id"))
        if not isinstance(self.action, PermissionAction):
            raise TypeError("action must be a PermissionAction")
        if not isinstance(self.context, Mapping):
            raise TypeError("context must be a mapping")
        object.__setattr__(self, "context", MappingProxyType(dict(self.context)))


@dataclass(frozen=True)
class PermissionEvaluation:
    request: PermissionRequest
    allowed: bool
    reason: str
    matched_grant: PermissionGrant | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.request, PermissionRequest):
            raise TypeError("request must be a PermissionRequest")
        if not isinstance(self.allowed, bool):
            raise TypeError("allowed must be a bool")
        object.__setattr__(self, "reason", _text(self.reason, "reason"))
        if self.matched_grant is not None and not isinstance(self.matched_grant, PermissionGrant):
            raise TypeError("matched_grant must be a PermissionGrant or None")

    def to_context(self) -> dict[str, Any]:
        return {
            "principal_id": self.request.principal_id,
            "capability_id": self.request.capability_id,
            "action": self.request.action.value,
            "allowed": self.allowed,
            "reason": self.reason,
            "matched": self.matched_grant is not None,
            "authority_granted": False,
        }


class PermissionModel:
    def __init__(self, grants: Sequence[PermissionGrant] = ()) -> None:
        values = tuple(grants)
        if any(not isinstance(item, PermissionGrant) for item in values):
            raise TypeError("grants must contain PermissionGrant values")
        keys = [(item.principal_id, item.capability_id) for item in values]
        if len(keys) != len(set(keys)):
            raise ValueError("one grant per principal/capability pair is required")
        self._grants = MappingProxyType({key: value for key, value in zip(keys, values)})

    def evaluate(self, request: PermissionRequest) -> PermissionEvaluation:
        if not isinstance(request, PermissionRequest):
            raise TypeError("request must be a PermissionRequest")
        grant = self._grants.get((request.principal_id, request.capability_id))
        if grant is None:
            return PermissionEvaluation(request, False, "no matching permission grant")
        if not grant.enabled:
            return PermissionEvaluation(request, False, "permission grant is disabled", grant)
        if not grant.allows(request.action):
            return PermissionEvaluation(request, False, "requested action is outside the grant", grant)
        return PermissionEvaluation(request, True, "permission granted by explicit security policy", grant)

    def snapshot(self) -> tuple[PermissionGrant, ...]:
        return tuple(self._grants.values())


__all__ = ["PermissionAction", "PermissionGrant", "PermissionRequest", "PermissionEvaluation", "PermissionModel"]
