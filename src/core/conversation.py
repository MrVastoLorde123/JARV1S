from datetime import datetime, timezone
from uuid import uuid4

from src.core.conversation_models import (
    ASSISTANT,
    USER,
    StateSnapshot,
    Turn,
)


class ConversationState:
    """
    Temporary working state for an active JARVIS conversation.

    This object is intentionally separate from:
        - long-term memory
        - historical conversation storage
        - AI provider state
    """

    def __init__(
        self,
        conversation_id=None,
    ):

        timestamp = (
            datetime.now(timezone.utc)
            .isoformat()
        )

        self._conversation_id = (
            conversation_id
            or str(uuid4())
        )

        self._created_at = timestamp
        self._updated_at = timestamp

        self._turns = []

        self._active_topic = None
        self._active_task = None

        self._metadata = {}

    @property
    def conversation_id(self):

        return self._conversation_id

    @property
    def active_topic(self):

        return self._active_topic

    @property
    def active_task(self):

        return self._active_task

    def _touch(self):

        self._updated_at = (
            datetime.now(timezone.utc)
            .isoformat()
        )

    def add_turn(
        self,
        role,
        content,
    ):

        if role not in (
            USER,
            ASSISTANT,
        ):
            raise ValueError(
                f"Invalid conversation role: {role}"
            )

        if not isinstance(
            content,
            str
        ):
            raise TypeError(
                "Turn content must be a string."
            )

        content = content.strip()

        if not content:
            raise ValueError(
                "Turn content cannot be empty."
            )

        turn = Turn(
            role=role,
            content=content,
            timestamp=(
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
        )

        self._turns.append(turn)

        self._touch()

    def get_recent_turns(
        self,
        limit=10,
    ):

        if limit < 0:
            raise ValueError(
                "Turn limit cannot be negative."
            )

        if limit == 0:
            return ()

        return tuple(
            self._turns[-limit:]
        )

    def set_topic(
        self,
        topic,
    ):

        if topic is None:
            self._active_topic = None
            self._touch()
            return

        if not isinstance(
            topic,
            str
        ):
            raise TypeError(
                "Conversation topic must be a string."
            )

        topic = topic.strip()

        self._active_topic = (
            topic or None
        )

        self._touch()

    def set_task(
        self,
        task,
    ):

        if task is None:
            self._active_task = None
            self._touch()
            return

        if not isinstance(
            task,
            str
        ):
            raise TypeError(
                "Conversation task must be a string."
            )

        task = task.strip()

        self._active_task = (
            task or None
        )

        self._touch()

    def clear_task(self):

        self._active_task = None

        self._touch()

    def set_metadata(
        self,
        key,
        value,
    ):

        if not isinstance(
            key,
            str
        ):
            raise TypeError(
                "Metadata key must be a string."
            )

        self._metadata[key] = value

        self._touch()

    def snapshot(self):

        return StateSnapshot(
            conversation_id=(
                self._conversation_id
            ),
            created_at=self._created_at,
            updated_at=self._updated_at,
            turns=tuple(
                self._turns
            ),
            active_topic=(
                self._active_topic
            ),
            active_task=(
                self._active_task
            ),
            metadata=dict(
                self._metadata
            ),
        )
    