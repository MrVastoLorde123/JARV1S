from dataclasses import dataclass, field
from typing import Any


USER = "user"
ASSISTANT = "assistant"


@dataclass(frozen=True)
class Turn:
    """
    One active conversation turn.
    """

    role: str
    content: str
    timestamp: str


@dataclass(frozen=True)
class StateSnapshot:
    """
    Immutable representation of the current conversation state.
    """

    conversation_id: str
    created_at: str
    updated_at: str

    turns: tuple[Turn, ...]

    active_topic: str | None
    active_task: str | None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )
