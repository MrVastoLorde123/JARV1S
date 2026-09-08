"""M25.1: provider-neutral backend contract beneath future JARVIS interfaces."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Protocol


class InterfaceBackendError(RuntimeError):
    """Raised when an interface backend request cannot be handled safely."""


class InterfaceOperation(str, Enum):
    PROPOSE = "PROPOSE"
    EVALUATE = "EVALUATE"
    DECIDE = "DECIDE"
    APPLY = "APPLY"
    VERIFY = "VERIFY"
    ROLLBACK = "ROLLBACK"
    STATUS = "STATUS"


class InterfaceResponseStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class InterfaceRequest:
    """Immutable, provider-neutral command envelope entering JARVIS."""

    request_id: str
    session_id: str
    actor_id: str
    operation: InterfaceOperation
    payload: Mapping[str, Any]
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in ("request_id", "session_id", "actor_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.operation, InterfaceOperation):
            raise TypeError("operation must be an interface operation")
        if not isinstance(self.payload, Mapping):
            raise TypeError("payload must be a mapping")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "metadata", _freeze(self.metadata))


@dataclass(frozen=True)
class InterfaceResponse:
    """Immutable, provider-neutral response envelope leaving JARVIS."""

    request_id: str
    operation: InterfaceOperation
    status: InterfaceResponseStatus
    payload: Mapping[str, Any]
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        if not isinstance(self.request_id, str) or not self.request_id.strip():
            raise ValueError("request_id must be a non-empty string")
        if not isinstance(self.operation, InterfaceOperation):
            raise TypeError("operation must be an interface operation")
        if not isinstance(self.status, InterfaceResponseStatus):
            raise TypeError("status must be an interface response status")
        if not isinstance(self.payload, Mapping):
            raise TypeError("payload must be a mapping")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "payload", _freeze(self.payload))
        object.__setattr__(self, "metadata", _freeze(self.metadata))


class InterfaceOrchestrationPort(Protocol):
    """Injected orchestration capability used by the interface backend."""

    def dispatch(self, request: InterfaceRequest) -> InterfaceResponse:
        ...


class SelfImprovementInterfaceBackend:
    """Validate interface envelopes and delegate them to orchestration."""

    def __init__(self, orchestration: InterfaceOrchestrationPort) -> None:
        if orchestration is None or not callable(getattr(orchestration, "dispatch", None)):
            raise TypeError("orchestration must provide callable dispatch")
        self._orchestration = orchestration

    def handle(self, request: InterfaceRequest) -> InterfaceResponse:
        if type(request) is not InterfaceRequest:
            raise TypeError("request must be an interface request")
        response = self._orchestration.dispatch(request)
        if type(response) is not InterfaceResponse:
            raise TypeError("orchestration must return an interface response")
        if response.request_id != request.request_id:
            raise InterfaceBackendError("response request identity mismatch")
        if response.operation is not request.operation:
            raise InterfaceBackendError("response operation identity mismatch")
        return response

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def executes_capability(self) -> bool:
        return False

    @property
    def mutates_state(self) -> bool:
        return False

    @property
    def persists_state(self) -> bool:
        return False

    @property
    def establishes_truth(self) -> bool:
        return False

    @property
    def establishes_certainty(self) -> bool:
        return False

    @property
    def is_ai_provider(self) -> bool:
        return False


__all__ = [
    "InterfaceBackendError",
    "InterfaceOperation",
    "InterfaceResponseStatus",
    "InterfaceRequest",
    "InterfaceResponse",
    "InterfaceOrchestrationPort",
    "SelfImprovementInterfaceBackend",
]
