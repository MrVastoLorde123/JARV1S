"""M74: explicit, session-bound security identity."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class PrincipalKind(str, Enum):
    USER = "USER"
    SERVICE = "SERVICE"
    WORKER = "WORKER"
    MODEL = "MODEL"
    SYSTEM = "SYSTEM"


class SecurityLevel(str, Enum):
    UNAUTHENTICATED = "UNAUTHENTICATED"
    AUTHENTICATED = "AUTHENTICATED"
    ELEVATED = "ELEVATED"


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True)
class SecurityIdentity:
    principal_id: str
    display_name: str
    kind: PrincipalKind
    attributes: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "principal_id", _text(self.principal_id, "principal_id"))
        object.__setattr__(self, "display_name", _text(self.display_name, "display_name"))
        if not isinstance(self.kind, PrincipalKind):
            raise TypeError("kind must be a PrincipalKind")
        if not isinstance(self.attributes, Mapping):
            raise TypeError("attributes must be a mapping")
        object.__setattr__(self, "attributes", MappingProxyType(dict(self.attributes)))

    def to_context(self) -> dict[str, Any]:
        return {
            "principal_id": self.principal_id,
            "display_name": self.display_name,
            "kind": self.kind.value,
            "attributes": dict(self.attributes),
            "authority_granted": False,
            "permissions_granted": False,
        }


@dataclass(frozen=True)
class SecuritySession:
    session_id: str
    identity: SecurityIdentity
    level: SecurityLevel
    active: bool = True
    authentication_method: str = "explicit"

    def __post_init__(self) -> None:
        object.__setattr__(self, "session_id", _text(self.session_id, "session_id"))
        if not isinstance(self.identity, SecurityIdentity):
            raise TypeError("identity must be a SecurityIdentity")
        if not isinstance(self.level, SecurityLevel):
            raise TypeError("level must be a SecurityLevel")
        if not isinstance(self.active, bool):
            raise TypeError("active must be a bool")
        object.__setattr__(self, "authentication_method", _text(self.authentication_method, "authentication_method"))

    @property
    def authenticated(self) -> bool:
        return self.active and self.level is not SecurityLevel.UNAUTHENTICATED

    def require_authenticated(self) -> None:
        if not self.authenticated:
            raise PermissionError(f"security session '{self.session_id}' is not authenticated")

    def to_context(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "identity": self.identity.to_context(),
            "level": self.level.value,
            "active": self.active,
            "authenticated": self.authenticated,
            "authentication_method": self.authentication_method,
            "authority_granted": False,
        }


class SecurityIdentityRegistry:
    """Immutable registry-like snapshot for explicitly supplied identities."""

    def __init__(self, sessions: tuple[SecuritySession, ...] = ()) -> None:
        if any(not isinstance(item, SecuritySession) for item in sessions):
            raise TypeError("sessions must contain SecuritySession values")
        ids = tuple(item.session_id for item in sessions)
        if len(ids) != len(set(ids)):
            raise ValueError("session IDs must be unique")
        self._sessions = MappingProxyType({item.session_id: item for item in sessions})

    def get(self, session_id: str) -> SecuritySession:
        normalized = _text(session_id, "session_id")
        try:
            return self._sessions[normalized]
        except KeyError as exc:
            raise KeyError(normalized) from exc

    def snapshot(self) -> tuple[SecuritySession, ...]:
        return tuple(self._sessions.values())


__all__ = ["PrincipalKind", "SecurityLevel", "SecurityIdentity", "SecuritySession", "SecurityIdentityRegistry"]
