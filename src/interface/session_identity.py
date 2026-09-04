"""M18 persistent operator session identity.

This module persists only the human-facing session identifier. It does not
store intent, authorization, policy, or execution state.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol
from uuid import uuid4


class SessionIdentityStore(Protocol):
    """Minimal contract consumed by the human operating layer."""

    def get_or_create(self, requested_session_id: str | None = None) -> str: ...

    def new_session(self) -> str: ...


class PersistentSessionIdentity:
    """Persist one active local session identifier in a small JSON file."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def get_or_create(self, requested_session_id: str | None = None) -> str:
        if requested_session_id is not None:
            session_id = self._normalize(requested_session_id)
            self._write(session_id)
            return session_id

        existing = self._read()
        if existing is not None:
            return existing

        return self.new_session()

    def new_session(self) -> str:
        session_id = f"local-{uuid4().hex}"
        self._write(session_id)
        return session_id

    def _read(self) -> str | None:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, json.JSONDecodeError):
            return None

        if not isinstance(data, dict):
            return None

        raw_session_id = data.get("session_id")
        if not isinstance(raw_session_id, str):
            return None

        try:
            return self._normalize(raw_session_id)
        except ValueError:
            return None

    def _write(self, session_id: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_name(f"{self.path.name}.tmp")
        payload = json.dumps(
            {"session_id": session_id},
            ensure_ascii=False,
            indent=2,
        )
        temporary_path.write_text(payload + "\n", encoding="utf-8")
        temporary_path.replace(self.path)

    @staticmethod
    def _normalize(session_id: str) -> str:
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id must be a non-empty string")
        return session_id.strip()


__all__ = ["PersistentSessionIdentity", "SessionIdentityStore"]
