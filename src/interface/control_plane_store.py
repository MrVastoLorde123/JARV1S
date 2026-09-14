"""Durable activity journal for the runtime-owned JARVIS control plane."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Mapping

from src.core.interface_backend import InterfaceOperation, InterfaceResponseStatus
from src.core.runtime_activity_stream import RuntimeActivityEvent, RuntimeActivityKind


class ControlPlaneActivityStore:
    """Persist sanitized control-plane activity so observation survives restart."""

    def __init__(self, database_path: str | Path) -> None:
        self._database_path = Path(database_path)
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self.ensure_schema()

    @property
    def database_path(self) -> Path:
        return self._database_path

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def ensure_schema(self) -> None:
        connection = self._connect()
        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS control_plane_activity (
                    sequence INTEGER PRIMARY KEY,
                    event_id TEXT NOT NULL UNIQUE,
                    session_id TEXT NOT NULL,
                    actor_id TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    status TEXT,
                    stage TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    metadata TEXT NOT NULL DEFAULT '{}'
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_control_plane_activity_request
                ON control_plane_activity(request_id, sequence)
                """
            )
            connection.commit()
        finally:
            connection.close()

    def append(self, event: RuntimeActivityEvent) -> None:
        if type(event) is not RuntimeActivityEvent:
            raise TypeError("event must be a RuntimeActivityEvent")
        metadata = json.dumps(dict(event.metadata), ensure_ascii=False, default=str)
        connection = self._connect()
        try:
            connection.execute(
                """
                INSERT INTO control_plane_activity (
                    sequence,
                    event_id,
                    session_id,
                    actor_id,
                    request_id,
                    operation,
                    kind,
                    status,
                    stage,
                    summary,
                    metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.sequence,
                    event.event_id,
                    event.session_id,
                    event.actor_id,
                    event.request_id,
                    event.operation.value,
                    event.kind.value,
                    event.status.value if event.status is not None else None,
                    event.stage,
                    event.summary,
                    metadata,
                ),
            )
            connection.commit()
        except sqlite3.IntegrityError:
            connection.rollback()
            raise
        finally:
            connection.close()

    def load_events(self) -> tuple[RuntimeActivityEvent, ...]:
        connection = self._connect()
        try:
            rows = connection.execute(
                """
                SELECT
                    sequence,
                    event_id,
                    session_id,
                    actor_id,
                    request_id,
                    operation,
                    kind,
                    status,
                    stage,
                    summary,
                    metadata
                FROM control_plane_activity
                ORDER BY sequence
                """
            ).fetchall()
        finally:
            connection.close()

        events: list[RuntimeActivityEvent] = []
        for row in rows:
            try:
                metadata: Mapping[str, Any] = json.loads(row[10])
            except (TypeError, json.JSONDecodeError):
                metadata = {}
            if not isinstance(metadata, Mapping):
                metadata = {}
            events.append(
                RuntimeActivityEvent(
                    event_id=str(row[1]),
                    sequence=int(row[0]),
                    session_id=str(row[2]),
                    actor_id=str(row[3]),
                    request_id=str(row[4]),
                    operation=InterfaceOperation(str(row[5])),
                    kind=RuntimeActivityKind(str(row[6])),
                    status=(InterfaceResponseStatus(str(row[7])) if row[7] is not None else None),
                    stage=str(row[8]),
                    summary=str(row[9]),
                    metadata=metadata,
                )
            )
        return tuple(events)


__all__ = ["ControlPlaneActivityStore"]
