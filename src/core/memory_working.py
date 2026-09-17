"""M88: bounded working memory.

Working memory is a contextual snapshot, not durable truth and not execution
authority. It may reference durable memories but does not mutate them.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkingMemorySnapshot:
    session_id: str
    version: int
    focus: str | None = None
    memory_ids: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    open_questions: tuple[str, ...] = ()
    created_at: str = ""
    expires_at: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.session_id, str) or not self.session_id.strip():
            raise ValueError("session_id must be a non-empty string")
        if not isinstance(self.version, int) or isinstance(self.version, bool) or self.version < 1:
            raise ValueError("version must be a positive integer")
        if self.focus is not None and (not isinstance(self.focus, str) or not self.focus.strip()):
            raise ValueError("focus must be non-empty when provided")
        for name, values in (
            ("memory_ids", self.memory_ids),
            ("assumptions", self.assumptions),
            ("open_questions", self.open_questions),
        ):
            if not isinstance(values, tuple) or any(not isinstance(item, str) or not item.strip() for item in values):
                raise TypeError(f"{name} must be a tuple of non-empty strings")
        if len(set(self.memory_ids)) != len(self.memory_ids):
            raise ValueError("memory_ids must not contain duplicates")
        if not isinstance(self.created_at, str) or not self.created_at.strip():
            raise ValueError("created_at must be a non-empty string")
        if self.expires_at is not None and (not isinstance(self.expires_at, str) or not self.expires_at.strip()):
            raise ValueError("expires_at must be non-empty when provided")

    def to_context(self) -> dict[str, object]:
        return {
            "session_id": self.session_id,
            "version": self.version,
            "focus": self.focus,
            "memory_ids": tuple(self.memory_ids),
            "assumptions": tuple(self.assumptions),
            "open_questions": tuple(self.open_questions),
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "durable_mutation_performed": False,
            "authority_granted": False,
            "execution_requested": False,
        }


__all__ = ["WorkingMemorySnapshot"]
