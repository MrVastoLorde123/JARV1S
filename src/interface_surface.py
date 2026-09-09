"""M25.6: a thin terminal interface surface over the canonical M25 contracts."""
from __future__ import annotations

import json
from typing import Any, Callable, Mapping, TextIO

from src.core.interface_adapter import InterfaceAdapter
from src.core.interface_backend import InterfaceOperation
from src.core.interface_session_state import InterfaceSessionStateProjector
from src.core.runtime_activity_stream import RuntimeActivityEvent, RuntimeActivityStream


class TerminalInterfaceError(RuntimeError):
    """Raised when the terminal surface cannot present or submit safely."""


class TerminalInterfaceSurface:
    """Human-facing terminal surface that delegates all semantics to M25 contracts."""

    def __init__(
        self,
        *,
        adapter: InterfaceAdapter,
        activity_stream: RuntimeActivityStream,
        session_projector: InterfaceSessionStateProjector,
        session_id: str,
        actor_id: str,
        request_id_factory: Callable[[], str] | None = None,
    ) -> None:
        if type(adapter) is not InterfaceAdapter:
            raise TypeError("adapter must be an interface adapter")
        if type(activity_stream) is not RuntimeActivityStream:
            raise TypeError("activity_stream must be a runtime activity stream")
        if type(session_projector) is not InterfaceSessionStateProjector:
            raise TypeError("session_projector must be an interface session state projector")
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id must be a non-empty string")
        if not isinstance(actor_id, str) or not actor_id.strip():
            raise ValueError("actor_id must be a non-empty string")
        if request_id_factory is not None and not callable(request_id_factory):
            raise TypeError("request_id_factory must be callable")
        self._adapter = adapter
        self._activity_stream = activity_stream
        self._session_projector = session_projector
        self._session_id = session_id
        self._actor_id = actor_id
        self._request_id_factory = request_id_factory or self._default_request_id_factory
        self._request_counter = 0
        self._activity_cursor = 0
        self._refresh_projection()

    def submit(
        self,
        operation: InterfaceOperation | str,
        *,
        payload: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any]:
        request_id = self._request_id_factory()
        if not isinstance(request_id, str) or not request_id.strip():
            raise TerminalInterfaceError("request_id_factory must return a non-empty string")
        envelope = {
            "request_id": request_id,
            "session_id": self._session_id,
            "actor_id": self._actor_id,
            "operation": operation,
            "payload": {} if payload is None else payload,
            "metadata": {} if metadata is None else metadata,
        }
        response = self._adapter.handle(envelope)
        self._refresh_projection()
        return response

    def render_response(self, response: Mapping[str, Any]) -> str:
        if not isinstance(response, Mapping):
            raise TypeError("response must be a mapping")
        return json.dumps(dict(response), sort_keys=True, default=str)

    def render_status(self) -> str:
        state = self._session_projector.state(self._session_id)
        if state is None:
            return f"SESSION {self._session_id} | NO ACTIVITY"
        activity = "ACTIVE" if state.is_active else "IDLE"
        return (
            f"SESSION {state.session_id} | ACTOR {state.actor_id} | {activity} | "
            f"EVENTS {state.event_count} | LAST {state.latest_kind.value} | "
            f"OPERATION {state.latest_operation.value} | STAGE {state.latest_stage}"
        )

    def render_activity(self, *, limit: int | None = None) -> str:
        events = [event for event in self._activity_stream.snapshot() if event.session_id == self._session_id]
        if limit is not None:
            if type(limit) is not int or limit < 1:
                raise ValueError("limit must be a positive integer")
            events = events[-limit:]
        if not events:
            return "NO ACTIVITY"
        return "\n".join(self._format_event(event) for event in events)

    def handle_line(self, line: str) -> str:
        if not isinstance(line, str):
            raise TypeError("line must be a string")
        command = line.strip()
        if not command:
            return ""
        lowered = command.lower()
        if lowered in {"help", "?"}:
            return self._help_text()
        if lowered == "status":
            self._refresh_projection()
            return self.render_status()
        if lowered == "activity":
            self._refresh_projection()
            return self.render_activity()
        if lowered.startswith("submit "):
            return self._handle_submit_line(command[7:].strip())
        if lowered in {"quit", "exit"}:
            return "BYE"
        raise TerminalInterfaceError("unknown command")

    def run(self, input_stream: TextIO, output_stream: TextIO) -> None:
        if not hasattr(input_stream, "readline"):
            raise TypeError("input_stream must provide readline")
        if not hasattr(output_stream, "write"):
            raise TypeError("output_stream must provide write")
        output_stream.write("JARVIS> READY\n")
        while True:
            output_stream.write("JARVIS> ")
            line = input_stream.readline()
            if line == "":
                break
            result = self.handle_line(line)
            if result:
                output_stream.write(result + "\n")
            if result == "BYE":
                break

    def _handle_submit_line(self, command: str) -> str:
        if not command:
            raise TerminalInterfaceError("submit requires an operation")
        parts = command.split(maxsplit=1)
        operation = parts[0].upper()
        payload: Mapping[str, Any] = {}
        if len(parts) == 2 and parts[1]:
            try:
                decoded = json.loads(parts[1])
            except json.JSONDecodeError as exc:
                raise TerminalInterfaceError("submit payload must be valid JSON") from exc
            if not isinstance(decoded, Mapping):
                raise TerminalInterfaceError("submit payload must be a JSON object")
            payload = decoded
        response = self.submit(operation, payload=payload, metadata={"surface": "terminal"})
        return self.render_response(response)

    def _refresh_projection(self) -> None:
        new_events = self._activity_stream.since(self._activity_cursor)
        for event in new_events:
            self._session_projector.apply(event)
            self._activity_cursor = event.sequence

    def _format_event(self, event: RuntimeActivityEvent) -> str:
        return (
            f"#{event.sequence} {event.kind.value} {event.operation.value} "
            f"[{event.status.value if event.status else '—'}] {event.stage} — {event.summary}"
        )

    def _help_text(self) -> str:
        return "COMMANDS: status | activity | submit <OPERATION> [JSON] | help | quit"

    def _default_request_id_factory(self) -> str:
        self._request_counter += 1
        return f"terminal-request-{self._request_counter}"

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def actor_id(self) -> str:
        return self._actor_id

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


__all__ = ["TerminalInterfaceError", "TerminalInterfaceSurface"]
