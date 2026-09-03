"""M12.4 durable session lifecycle boundary.

This module adds persistence to session identity and lifecycle while reusing the
existing SessionRuntime, ConversationStore, and JARVIS processor contracts.
Persistence changes continuity only; it does not create semantic or authority
state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from src.core.conversation_store import ConversationStore
from src.core.session_runtime import SessionRuntime, SessionRuntimeResult, SessionProcessor
from src.interface.request import JARVISRequest


class DurableProcessorFactory(Protocol):
    """Construct a core processor bound to a persistent conversation."""

    def __call__(self, session_id: str, conversation_id: str) -> SessionProcessor: ...


@dataclass(frozen=True)
class DurableSessionRecord:
    """Stable mapping between interface session identity and conversation identity."""

    session_id: str
    conversation_id: str


class DurableSessionRuntime:
    """Persist session identity while delegating request processing to SessionRuntime."""

    def __init__(
        self,
        default_processor: SessionProcessor,
        conversation_store: ConversationStore,
        processor_factory: DurableProcessorFactory | None = None,
    ) -> None:
        if not callable(getattr(default_processor, "ask", None)):
            raise TypeError("default_processor must provide an ask(query) method")
        if not isinstance(conversation_store, ConversationStore):
            raise TypeError("conversation_store must be a ConversationStore")
        if processor_factory is not None and not callable(processor_factory):
            raise TypeError("processor_factory must be callable or None")

        self._default_processor = default_processor
        self._conversation_store = conversation_store
        self._processor_factory = processor_factory
        self._session_runtime = SessionRuntime(
            default_processor=default_processor,
            session_processor_factory=self._bind_processor,
        )
        self._records: dict[str, DurableSessionRecord] = {}

    @property
    def conversation_store(self) -> ConversationStore:
        return self._conversation_store

    @property
    def session_runtime(self) -> SessionRuntime:
        return self._session_runtime

    def process(self, request: JARVISRequest) -> SessionRuntimeResult:
        if not isinstance(request, JARVISRequest):
            raise TypeError("request must be a JARVISRequest")
        return self._session_runtime.process(request)

    def session_count(self) -> int:
        return self._session_runtime.session_count()

    def session_record(self, session_id: str) -> DurableSessionRecord | None:
        return self._records.get(self._normalize_session_id(session_id))

    def clear_session_binding(self, session_id: str) -> None:
        normalized = self._normalize_session_id(session_id)
        self._records.pop(normalized, None)
        self._session_runtime.clear_session(normalized)

    def clear_all_session_bindings(self) -> None:
        self._records.clear()
        self._session_runtime.clear_all_sessions()

    def _bind_processor(self, session_id: str) -> SessionProcessor:
        normalized = self._normalize_session_id(session_id)
        record = self._ensure_record(normalized)

        if self._processor_factory is None:
            return self._default_processor

        processor = self._processor_factory(normalized, record.conversation_id)
        if not callable(getattr(processor, "ask", None)):
            raise TypeError("durable session processor must provide an ask(query) method")
        return processor

    def _ensure_record(self, session_id: str) -> DurableSessionRecord:
        record = self._records.get(session_id)
        if record is not None:
            return record

        if self._conversation_store.conversation_exists(session_id):
            conversation_id = session_id
        else:
            created = self._conversation_store.create_conversation(
                conversation_id=session_id,
            )
            conversation_id = created.conversation_id

        record = DurableSessionRecord(
            session_id=session_id,
            conversation_id=conversation_id,
        )
        self._records[session_id] = record
        return record

    @staticmethod
    def _normalize_session_id(session_id: str) -> str:
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id must be a non-empty string")
        return session_id.strip()


__all__ = ["DurableProcessorFactory", "DurableSessionRecord", "DurableSessionRuntime"]
