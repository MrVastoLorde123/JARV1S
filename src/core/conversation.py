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
    Active working state for a JARVIS conversation.

    Persistent storage is handled by ConversationStore.

    ConversationState itself remains responsible for:
        - active turns
        - active topic
        - active task
        - session metadata
    """

    def __init__(
        self,
        conversation_id=None,
        created_at=None,
        updated_at=None,
    ):
        timestamp = (
            created_at
            or self._timestamp()
        )

        self._conversation_id = (
            conversation_id
            or str(uuid4())
        )

        self._created_at = timestamp
        self._updated_at = (
            updated_at
            or timestamp
        )

        self._turns = []

        self._active_topic = None
        self._active_task = None

        self._metadata = {}

    @staticmethod
    def _timestamp():
        return (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

    @classmethod
    def restore(
        cls,
        conversation_id,
        created_at,
        updated_at,
        turns=(),
        active_topic=None,
        active_task=None,
        metadata=None,
    ):
        """
        Restore a ConversationState from persistent storage.

        This is intentionally a classmethod so persistence logic
        does not need to mutate private state fields externally.
        """

        state = cls(
            conversation_id=conversation_id,
            created_at=created_at,
            updated_at=updated_at,
        )

        state._turns = list(turns)

        state._active_topic = (
            active_topic
        )

        state._active_task = (
            active_task
        )

        state._metadata = dict(
            metadata or {}
        )

        return state

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
        self._updated_at = self._timestamp()

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
            str,
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
            timestamp=self._timestamp(),
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
            str,
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
            str,
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
            str,
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