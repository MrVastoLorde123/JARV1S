"""M11.2 bounded session and conversation runtime.

Sessions provide continuity for interface interactions without interpreting intent,
granting authority, authorizing execution, or mutating JARVIS policy.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.interface.boundary import InterfaceRequest, InterfaceResponse


class SessionConflictError(ValueError):
    """Raised when session identity or conversation lineage conflicts."""


@dataclass(frozen=True)
class ConversationTurn:
    """Immutable request/response pair correlated by request identity."""

    request: InterfaceRequest
    response: InterfaceResponse | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.request, InterfaceRequest):
            raise TypeError("request must be an InterfaceRequest")
        if self.response is not None:
            if not isinstance(self.response, InterfaceResponse):
                raise TypeError("response must be an InterfaceResponse or None")
            if self.response.request_id != self.request.request_id:
                raise ValueError("response must reference the same request_id")

    @property
    def complete(self) -> bool:
        return self.response is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "request": self.request.to_dict(),
            "response": self.response.to_dict() if self.response else None,
        }


@dataclass(frozen=True)
class ConversationSession:
    """Immutable bounded conversation state for one interface session."""

    session_id: str
    turns: tuple[ConversationTurn, ...] = ()
    max_turns: int = 50
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.session_id, str) or not self.session_id.strip():
            raise ValueError("session_id must be a non-empty string")
        if not isinstance(self.turns, tuple):
            raise TypeError("turns must be a tuple")
        if not isinstance(self.max_turns, int) or isinstance(self.max_turns, bool) or self.max_turns <= 0:
            raise ValueError("max_turns must be a positive integer")
        if len(self.turns) > self.max_turns:
            raise ValueError("turn history exceeds max_turns")
        if any(not isinstance(turn, ConversationTurn) for turn in self.turns):
            raise TypeError("turns must contain ConversationTurn values")
        request_ids = [turn.request.request_id for turn in self.turns]
        if len(set(request_ids)) != len(request_ids):
            raise SessionConflictError("request_id must be unique within a session")
        if any(turn.request.session_id not in (None, self.session_id) for turn in self.turns):
            raise ValueError("turn request session_id must match the session")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "session_id", self.session_id.strip())
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def append_request(self, request: InterfaceRequest) -> "ConversationSession":
        if not isinstance(request, InterfaceRequest):
            raise TypeError("request must be an InterfaceRequest")
        if request.session_id not in (None, self.session_id):
            raise ValueError("request session_id must match the session")
        if any(turn.request.request_id == request.request_id for turn in self.turns):
            raise SessionConflictError(f"request '{request.request_id}' is already in the session")
        if len(self.turns) >= self.max_turns:
            raise ValueError("session turn bound has been reached")
        normalized_request = request
        if request.session_id is None:
            normalized_request = InterfaceRequest(
                request_id=request.request_id,
                channel=request.channel,
                content=request.content,
                session_id=self.session_id,
                metadata=request.metadata,
            )
        return ConversationSession(
            session_id=self.session_id,
            turns=self.turns + (ConversationTurn(request=normalized_request),),
            max_turns=self.max_turns,
            metadata=self.metadata,
        )

    def append_response(self, response: InterfaceResponse) -> "ConversationSession":
        if not isinstance(response, InterfaceResponse):
            raise TypeError("response must be an InterfaceResponse")
        if not self.turns:
            raise ValueError("cannot append a response without a request")
        latest = self.turns[-1]
        if latest.response is not None:
            raise SessionConflictError("latest session turn already has a response")
        if response.request_id != latest.request.request_id:
            raise ValueError("response must correlate to the latest pending request")
        completed = ConversationTurn(request=latest.request, response=response)
        return ConversationSession(
            session_id=self.session_id,
            turns=self.turns[:-1] + (completed,),
            max_turns=self.max_turns,
            metadata=self.metadata,
        )

    def latest(self) -> ConversationTurn | None:
        return self.turns[-1] if self.turns else None

    def pending_request(self) -> InterfaceRequest | None:
        latest = self.latest()
        if latest is None or latest.complete:
            return None
        return latest.request

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "turns": [turn.to_dict() for turn in self.turns],
            "max_turns": self.max_turns,
            "metadata": dict(self.metadata),
            "truth_guaranteed": False,
            "intent_interpreted": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "policy_mutation": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)


@dataclass(frozen=True)
class SessionStore:
    """Immutable provider-neutral session registry."""

    sessions: tuple[ConversationSession, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.sessions, tuple):
            raise TypeError("sessions must be a tuple")
        ids: set[str] = set()
        for session in self.sessions:
            if not isinstance(session, ConversationSession):
                raise TypeError("sessions must contain ConversationSession values")
            if session.session_id in ids:
                raise SessionConflictError(f"session '{session.session_id}' is already stored")
            ids.add(session.session_id)

    def open(self, session_id: str, *, max_turns: int = 50, metadata: Mapping[str, Any] | None = None) -> ConversationSession:
        if any(item.session_id == session_id for item in self.sessions):
            raise SessionConflictError(f"session '{session_id}' is already stored")
        return ConversationSession(
            session_id=session_id,
            max_turns=max_turns,
            metadata=metadata or {},
        )

    def append(self, session: ConversationSession) -> "SessionStore":
        if not isinstance(session, ConversationSession):
            raise TypeError("session must be a ConversationSession")
        existing = next((item for item in self.sessions if item.session_id == session.session_id), None)
        if existing is not None:
            raise SessionConflictError(f"session '{session.session_id}' is already stored")
        return SessionStore(self.sessions + (session,))

    def replace(self, session: ConversationSession) -> "SessionStore":
        if not isinstance(session, ConversationSession):
            raise TypeError("session must be a ConversationSession")
        if not any(item.session_id == session.session_id for item in self.sessions):
            raise SessionConflictError(f"session '{session.session_id}' does not exist")
        return SessionStore(
            tuple(session if item.session_id == session.session_id else item for item in self.sessions)
        )

    def get(self, session_id: str) -> ConversationSession | None:
        return next((item for item in self.sessions if item.session_id == session_id), None)

    def list(self) -> tuple[ConversationSession, ...]:
        return self.sessions


class SessionRuntime:
    """Manage bounded conversation continuity without interpreting the conversation."""

    def receive(self, session: ConversationSession, request: InterfaceRequest) -> ConversationSession:
        return session.append_request(request)

    def respond(self, session: ConversationSession, response: InterfaceResponse) -> ConversationSession:
        return session.append_response(response)
