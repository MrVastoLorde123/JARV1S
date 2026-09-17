"""M79: append-only, tamper-evident security audit evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from types import MappingProxyType
from typing import Any, Mapping, Sequence


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True)
class SecurityAuditEvent:
    event_id: str
    timestamp: str
    principal_id: str
    action: str
    resource: str
    outcome: str
    details: Mapping[str, Any] = field(default_factory=dict)
    previous_hash: str = ""
    event_hash: str = ""

    def __post_init__(self) -> None:
        for name in ("event_id", "timestamp", "principal_id", "action", "resource", "outcome"):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        if not isinstance(self.details, Mapping):
            raise TypeError("details must be a mapping")
        object.__setattr__(self, "details", MappingProxyType(dict(self.details)))
        if not isinstance(self.previous_hash, str) or self.previous_hash.strip() != self.previous_hash:
            raise ValueError("previous_hash must be a string")
        if not isinstance(self.event_hash, str) or self.event_hash.strip() != self.event_hash:
            raise ValueError("event_hash must be a string")

    def canonical_payload(self) -> bytes:
        payload = {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "principal_id": self.principal_id,
            "action": self.action,
            "resource": self.resource,
            "outcome": self.outcome,
            "details": dict(self.details),
            "previous_hash": self.previous_hash,
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")

    def computed_hash(self) -> str:
        return hashlib.sha256(self.canonical_payload()).hexdigest()


class SecurityAuditLedger:
    """In-memory append-only security evidence with hash-chain verification."""

    def __init__(self, events: Sequence[SecurityAuditEvent] = ()) -> None:
        self._events: list[SecurityAuditEvent] = []
        for event in events:
            self.append(event)

    @property
    def last_hash(self) -> str:
        return "" if not self._events else self._events[-1].event_hash

    def append(self, event: SecurityAuditEvent) -> SecurityAuditEvent:
        if not isinstance(event, SecurityAuditEvent):
            raise TypeError("event must be a SecurityAuditEvent")
        if any(item.event_id == event.event_id for item in self._events):
            raise ValueError(f"duplicate audit event id: {event.event_id}")
        if event.previous_hash != self.last_hash:
            raise ValueError("audit event previous_hash does not match ledger tip")
        expected_hash = event.computed_hash()
        if event.event_hash != expected_hash:
            raise ValueError("audit event hash does not match canonical content")
        self._events.append(event)
        return event

    def build_and_append(
        self,
        *,
        event_id: str,
        timestamp: str,
        principal_id: str,
        action: str,
        resource: str,
        outcome: str,
        details: Mapping[str, Any] | None = None,
    ) -> SecurityAuditEvent:
        event = SecurityAuditEvent(
            event_id=event_id,
            timestamp=timestamp,
            principal_id=principal_id,
            action=action,
            resource=resource,
            outcome=outcome,
            details=details or {},
            previous_hash=self.last_hash,
            event_hash="",
        )
        event = SecurityAuditEvent(
            event_id=event.event_id,
            timestamp=event.timestamp,
            principal_id=event.principal_id,
            action=event.action,
            resource=event.resource,
            outcome=event.outcome,
            details=event.details,
            previous_hash=event.previous_hash,
            event_hash=event.computed_hash(),
        )
        return self.append(event)

    def verify_chain(self) -> bool:
        previous = ""
        for event in self._events:
            if event.previous_hash != previous or event.event_hash != event.computed_hash():
                return False
            previous = event.event_hash
        return True

    def snapshot(self) -> tuple[SecurityAuditEvent, ...]:
        return tuple(self._events)


__all__ = ["SecurityAuditEvent", "SecurityAuditLedger"]
