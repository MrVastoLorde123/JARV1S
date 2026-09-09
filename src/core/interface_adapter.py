"""M25.5: translate external interface envelopes to and from the canonical backend contract."""
from __future__ import annotations

from types import MappingProxyType
from typing import Any, Mapping, Protocol

from src.core.interface_backend import (
    InterfaceOperation,
    InterfaceRequest,
    InterfaceResponse,
)


class InterfaceAdapterError(RuntimeError):
    """Raised when an external interface envelope cannot cross safely."""


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


class InterfaceBackendPort(Protocol):
    """Canonical backend seam consumed by an external interface adapter."""

    def handle(self, request: InterfaceRequest) -> InterfaceResponse:
        ...


class InterfaceAdapter:
    """Translate untrusted interface envelopes without changing JARVIS semantics."""

    def __init__(self, backend: InterfaceBackendPort) -> None:
        if backend is None or not callable(getattr(backend, "handle", None)):
            raise TypeError("backend must provide callable handle")
        self._backend = backend

    def to_request(self, envelope: Mapping[str, Any]) -> InterfaceRequest:
        if not isinstance(envelope, Mapping):
            raise TypeError("envelope must be a mapping")
        required = ("request_id", "session_id", "actor_id", "operation", "payload", "metadata")
        missing = [name for name in required if name not in envelope]
        if missing:
            raise InterfaceAdapterError(f"missing required fields: {', '.join(missing)}")
        operation = envelope["operation"]
        if isinstance(operation, str):
            try:
                operation = InterfaceOperation(operation)
            except ValueError as exc:
                raise InterfaceAdapterError("operation is not a supported interface operation") from exc
        if not isinstance(operation, InterfaceOperation):
            raise TypeError("operation must be an interface operation or its string value")
        return InterfaceRequest(
            request_id=envelope["request_id"],
            session_id=envelope["session_id"],
            actor_id=envelope["actor_id"],
            operation=operation,
            payload=envelope["payload"],
            metadata=envelope["metadata"],
        )

    def from_response(self, response: InterfaceResponse) -> Mapping[str, Any]:
        if type(response) is not InterfaceResponse:
            raise TypeError("response must be an interface response")
        return MappingProxyType(
            {
                "request_id": response.request_id,
                "operation": response.operation.value,
                "status": response.status.value,
                "payload": _freeze(dict(response.payload)),
                "metadata": _freeze(dict(response.metadata)),
            }
        )

    def handle(self, envelope: Mapping[str, Any]) -> Mapping[str, Any]:
        request = self.to_request(envelope)
        response = self._backend.handle(request)
        return self.from_response(response)

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


__all__ = ["InterfaceAdapterError", "InterfaceBackendPort", "InterfaceAdapter"]
