from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
from time import monotonic
from typing import Mapping


class TraceEventKind(str, Enum):
    RUN_STARTED = "run_started"
    CASE_STARTED = "case_started"
    REQUEST_CREATED = "request_created"
    PROVIDER_SELECTED = "provider_selected"
    RESPONSE_RECEIVED = "response_received"
    SCORE_CALCULATED = "score_calculated"
    CASE_COMPLETED = "case_completed"
    ERROR = "error"
    RUN_COMPLETED = "run_completed"


class EvaluationOutcome(str, Enum):
    PASS = "pass"
    MODEL_FAILURE = "model_failure"
    INFRASTRUCTURE_ERROR = "infrastructure_error"
    TIMEOUT = "timeout"
    INVALID_PROVIDER_RESPONSE = "invalid_provider_response"
    REQUEST_ERROR = "request_error"
    EVALUATION_ERROR = "evaluation_error"


def _json_safe(value: object) -> object:
    """Convert trace evidence into values accepted by JSON encoders."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return _json_safe(value.value)
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _json_safe(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    raise TypeError(
        f"trace data contains unsupported non-JSON value: {type(value).__name__}"
    )


@dataclass(frozen=True)
class TraceEvent:
    sequence: int
    kind: TraceEventKind
    message: str
    case_id: str | None = None
    model_id: str | None = None
    provider_name: str | None = None
    outcome: EvaluationOutcome | None = None
    data: Mapping[str, object] = field(default_factory=dict)
    elapsed_ms: float | None = None

    def __post_init__(self) -> None:
        if self.sequence < 0:
            raise ValueError("trace sequence cannot be negative")
        if not self.message.strip():
            raise ValueError("trace message cannot be empty")
        object.__setattr__(self, "data", dict(self.data))


class ExecutionTrace:
    """In-memory, UI-ready record of JARVIS evaluation execution."""

    def __init__(self, run_id: str) -> None:
        if not run_id.strip():
            raise ValueError("run_id cannot be empty")
        self.run_id = run_id
        self._started = monotonic()
        self._events: list[TraceEvent] = []

    @property
    def events(self) -> tuple[TraceEvent, ...]:
        return tuple(self._events)

    def add(
        self,
        kind: TraceEventKind,
        message: str,
        *,
        case_id: str | None = None,
        model_id: str | None = None,
        provider_name: str | None = None,
        outcome: EvaluationOutcome | None = None,
        data: Mapping[str, object] | None = None,
    ) -> TraceEvent:
        event = TraceEvent(
            sequence=len(self._events),
            kind=kind,
            message=message,
            case_id=case_id,
            model_id=model_id,
            provider_name=provider_name,
            outcome=outcome,
            data=data or {},
            elapsed_ms=round((monotonic() - self._started) * 1000.0, 3),
        )
        self._events.append(event)
        return event

    def as_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "events": [
                {
                    "sequence": event.sequence,
                    "kind": event.kind.value,
                    "message": event.message,
                    "case_id": event.case_id,
                    "model_id": event.model_id,
                    "provider_name": event.provider_name,
                    "outcome": event.outcome.value if event.outcome else None,
                    "data": _json_safe(event.data),
                    "elapsed_ms": event.elapsed_ms,
                }
                for event in self._events
            ],
        }
