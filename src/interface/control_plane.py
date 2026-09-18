"""Runtime-owned control-plane projection for the JARVIS cockpit."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from types import MappingProxyType
from typing import Any, Callable, Mapping

from src.core.interface_backend import InterfaceOperation, InterfaceResponseStatus
from src.core.runtime_activity_stream import RuntimeActivityEvent, RuntimeActivityKind, RuntimeActivityStream

from .control_plane_store import ControlPlaneActivityStore


class ControlPlaneError(RuntimeError):
    """Raised when a control-plane snapshot cannot be constructed safely."""


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(k): _freeze(v) for k, v in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(v) for v in value)
    if isinstance(value, tuple):
        return tuple(_freeze(v) for v in value)
    return value


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    if hasattr(value, "value"):
        try:
            return value.value
        except Exception:
            pass
    return value


@dataclass(frozen=True)
class ControlPlaneSnapshot:
    """One immutable, UI-safe representation of current JARVIS operations."""

    schema: str
    generated_at: str
    runtime: Mapping[str, Any]
    task: Mapping[str, Any]
    agents: tuple[Mapping[str, Any], ...]
    approvals: tuple[Mapping[str, Any], ...]
    tools: tuple[Mapping[str, Any], ...]
    model: Mapping[str, Any]
    blockers: tuple[Mapping[str, Any], ...]
    verification: Mapping[str, Any]
    events: tuple[Mapping[str, Any], ...]
    cursor: int
    metadata: Mapping[str, Any] = field(default_factory=dict)
    autonomous: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.schema != "control-plane.v1":
            raise ValueError("unsupported control-plane schema")
        if not isinstance(self.generated_at, str) or not self.generated_at.strip():
            raise ValueError("generated_at must be a non-empty string")
        if type(self.cursor) is not int or self.cursor < 0:
            raise ValueError("cursor must be a non-negative integer")
        for name in ("runtime", "task", "model", "verification", "metadata"):
            value = getattr(self, name)
            if not isinstance(value, Mapping):
                raise TypeError(f"{name} must be a mapping")
        for name in ("agents", "approvals", "tools", "blockers", "events"):
            value = getattr(self, name)
            if not isinstance(value, tuple):
                raise TypeError(f"{name} must be a tuple")
            if not all(isinstance(item, Mapping) for item in value):
                raise TypeError(f"{name} entries must be mappings")
        object.__setattr__(self, "runtime", _freeze(self.runtime))
        object.__setattr__(self, "task", _freeze(self.task))
        object.__setattr__(self, "agents", tuple(_freeze(item) for item in self.agents))
        object.__setattr__(self, "approvals", tuple(_freeze(item) for item in self.approvals))
        object.__setattr__(self, "tools", tuple(_freeze(item) for item in self.tools))
        object.__setattr__(self, "model", _freeze(self.model))
        object.__setattr__(self, "blockers", tuple(_freeze(item) for item in self.blockers))
        object.__setattr__(self, "verification", _freeze(self.verification))
        object.__setattr__(self, "events", tuple(_freeze(item) for item in self.events))
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "generated_at": self.generated_at,
            "runtime": _plain(self.runtime),
            "task": _plain(self.task),
            "agents": [_plain(item) for item in self.agents],
            "approvals": [_plain(item) for item in self.approvals],
            "tools": [_plain(item) for item in self.tools],
            "model": _plain(self.model),
            "blockers": [_plain(item) for item in self.blockers],
            "verification": _plain(self.verification),
            "autonomous": [_plain(item) for item in self.autonomous],
            "events": [_plain(item) for item in self.events],
            "cursor": self.cursor,
            "metadata": _plain(self.metadata),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)


class ControlPlaneActivityRecorder:
    """Translate browser command lifecycle into the shared runtime activity stream."""

    _OBSERVABLE_RESPONSE_KEYS = frozenset({
        "route",
        "stage",
        "success",
        "task_id",
        "operation_id",
        "plan_fingerprint",
        "edit_count",
        "verification_runner",
        "verification_arguments",
        "coding_status",
        "edits_attempted",
        "edits_applied",
        "blocked_tool",
        "verification",
        "operation_status",
    })

    def __init__(
        self,
        stream: RuntimeActivityStream,
        *,
        durable_store: ControlPlaneActivityStore | None = None,
    ) -> None:
        if type(stream) is not RuntimeActivityStream:
            raise TypeError("stream must be a RuntimeActivityStream")
        if durable_store is not None and type(durable_store) is not ControlPlaneActivityStore:
            raise TypeError("durable_store must be a ControlPlaneActivityStore or None")
        self._stream = stream
        self._durable_store = durable_store
        self._lock = RLock()
        if durable_store is not None and stream.size == 0:
            for event in durable_store.load_events():
                stream.publish(event)
        self._event_counter = stream.size

    def record_request(self, *, request_id: str, session_id: str) -> RuntimeActivityEvent:
        return self._publish(
            session_id=session_id,
            request_id=request_id,
            kind=RuntimeActivityKind.REQUEST_RECEIVED,
            status=None,
            stage="COMMAND_HTTP",
            summary="UI command request received",
            metadata={"event_source": "command_http"},
        )

    def record_response(
        self,
        *,
        request_id: str,
        session_id: str,
        status: InterfaceResponseStatus,
        metadata: Mapping[str, Any] | None = None,
    ) -> RuntimeActivityEvent:
        kind = (
            RuntimeActivityKind.RESPONSE_EMITTED
            if status is InterfaceResponseStatus.ACCEPTED
            else RuntimeActivityKind.REQUEST_REJECTED
            if status is InterfaceResponseStatus.REJECTED
            else RuntimeActivityKind.REQUEST_FAILED
        )
        safe_metadata = {"event_source": "command_http", **self._sanitize_response_metadata(metadata or {})}
        return self._publish(
            session_id=session_id,
            request_id=request_id,
            kind=kind,
            status=status,
            stage=str(safe_metadata.get("stage", "COMMAND_HTTP")),
            summary=f"UI command {status.value.lower()}",
            metadata=safe_metadata,
        )

    @classmethod
    def _sanitize_response_metadata(cls, metadata: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        sanitized: dict[str, Any] = {}
        for key in cls._OBSERVABLE_RESPONSE_KEYS:
            if key not in metadata:
                continue
            value = metadata[key]
            if isinstance(value, (str, int, float, bool)) or value is None:
                sanitized[key] = value
            elif isinstance(value, (list, tuple)):
                sanitized[key] = tuple(item for item in value if isinstance(item, (str, int, float, bool)) or item is None)
            elif key == "verification" and isinstance(value, Mapping):
                safe_verification = {}
                for verification_key in ("state", "status", "success", "runner", "exit_code", "passed", "error"):
                    if verification_key in value:
                        item = value[verification_key]
                        if isinstance(item, (str, int, float, bool)) or item is None:
                            safe_verification[verification_key] = item
                sanitized[key] = safe_verification
        return sanitized

    def _publish(self, *, session_id: str, request_id: str, kind: RuntimeActivityKind, status: InterfaceResponseStatus | None, stage: str, summary: str, metadata: Mapping[str, Any]) -> RuntimeActivityEvent:
        with self._lock:
            self._event_counter += 1
            event = RuntimeActivityEvent(
                event_id=f"control-event-{self._event_counter}",
                sequence=self._stream.size + 1,
                session_id=session_id,
                actor_id="ui",
                request_id=request_id,
                operation=InterfaceOperation.PROPOSE,
                kind=kind,
                status=status,
                stage=stage,
                summary=summary,
                metadata=metadata,
            )
            if self._durable_store is not None:
                self._durable_store.append(event)
            self._stream.publish(event)
            return event


WorldSupplier = Callable[[], Mapping[str, Any]]


class ControlPlaneSnapshotBuilder:
    """Compose deterministic runtime sources into one read-only snapshot."""

    def __init__(
        self,
        *,
        world_supplier: WorldSupplier,
        activity_stream: RuntimeActivityStream,
        task_supplier: Callable[[], Mapping[str, Any]] | None = None,
        agents_supplier: Callable[[], tuple[Mapping[str, Any], ...]] | None = None,
        approvals_supplier: Callable[[], tuple[Mapping[str, Any], ...]] | None = None,
        tools_supplier: Callable[[], tuple[Mapping[str, Any], ...]] | None = None,
        model_supplier: Callable[[], Mapping[str, Any]] | None = None,
        blockers_supplier: Callable[[], tuple[Mapping[str, Any], ...]] | None = None,
        verification_supplier: Callable[[], Mapping[str, Any]] | None = None,
        autonomous_supplier: Callable[[], tuple[Mapping[str, Any], ...]] | None = None,
        clock: Callable[[], str] | None = None,
    ) -> None:
        if not callable(world_supplier):
            raise TypeError("world_supplier must be callable")
        if type(activity_stream) is not RuntimeActivityStream:
            raise TypeError("activity_stream must be a RuntimeActivityStream")
        self._world_supplier = world_supplier
        self._activity_stream = activity_stream
        self._task_supplier = task_supplier or (lambda: {})
        self._agents_supplier = agents_supplier or (lambda: ())
        self._approvals_supplier = approvals_supplier or (lambda: ())
        self._tools_supplier = tools_supplier or (lambda: ())
        self._model_supplier = model_supplier or (lambda: {})
        self._blockers_supplier = blockers_supplier or (lambda: ())
        self._verification_supplier = verification_supplier or (lambda: {})
        self._autonomous_supplier = autonomous_supplier or (lambda: ())
        self._clock = clock or (lambda: datetime.now(timezone.utc).isoformat())

    def build(self, *, after_cursor: int = 0, limit: int = 50) -> ControlPlaneSnapshot:
        if type(after_cursor) is not int or after_cursor < 0:
            raise ValueError("after_cursor must be a non-negative integer")
        if type(limit) is not int or not 1 <= limit <= 500:
            raise ValueError("limit must be an integer from 1 to 500")

        world = self._world_supplier()
        if not isinstance(world, Mapping):
            raise ControlPlaneError("world supplier must return a mapping")
        events = self._activity_stream.since(after_cursor)
        event_views = tuple(self._event_view(event) for event in events[-limit:])
        cursor = self._activity_stream.size
        return ControlPlaneSnapshot(
            schema="control-plane.v1",
            generated_at=self._clock(),
            runtime={
                "available": True,
                "world": dict(world),
                "read_only": True,
            },
            task=self._require_mapping("task", self._task_supplier()),
            agents=self._require_records("agents", self._agents_supplier()),
            approvals=self._require_records("approvals", self._approvals_supplier()),
            tools=self._require_records("tools", self._tools_supplier()),
            model=self._require_mapping("model", self._model_supplier()),
            blockers=self._require_records("blockers", self._blockers_supplier()),
            verification=self._require_mapping("verification", self._verification_supplier()),
            autonomous=self._require_records("autonomous", self._autonomous_supplier()),
            events=event_views,
            cursor=cursor,
            metadata={"event_count": len(event_views), "after_cursor": after_cursor},
        )

    @staticmethod
    def _require_mapping(name: str, value: Mapping[str, Any]) -> Mapping[str, Any]:
        if not isinstance(value, Mapping):
            raise ControlPlaneError(f"{name} supplier must return a mapping")
        return value

    @staticmethod
    def _require_records(name: str, value: tuple[Mapping[str, Any], ...]) -> tuple[Mapping[str, Any], ...]:
        if not isinstance(value, tuple):
            raise ControlPlaneError(f"{name} supplier must return a tuple")
        if not all(isinstance(item, Mapping) for item in value):
            raise ControlPlaneError(f"{name} entries must be mappings")
        return value

    @staticmethod
    def _event_view(event: RuntimeActivityEvent) -> Mapping[str, Any]:
        return {
            "event_id": event.event_id,
            "sequence": event.sequence,
            "session_id": event.session_id,
            "actor_id": event.actor_id,
            "request_id": event.request_id,
            "operation": event.operation.value,
            "kind": event.kind.value,
            "status": event.status.value if event.status is not None else None,
            "stage": event.stage,
            "summary": event.summary,
            "metadata": dict(event.metadata),
        }


__all__ = ["ControlPlaneActivityRecorder", "ControlPlaneActivityStore", "ControlPlaneError", "ControlPlaneSnapshot", "ControlPlaneSnapshotBuilder"]
