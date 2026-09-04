import json
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

from src.database import get_connection

from src.core.conversation_models import (
    ASSISTANT,
    USER,
    StateSnapshot,
    Turn,
)

from src.core.conversation import (
    ConversationState,
)


class ConversationRecord:
    """
    Persistent conversation metadata.
    """

    def __init__(
        self,
        conversation_id,
        title,
        created_at,
        updated_at,
        is_archived,
        is_starred,
    ):
        self.conversation_id = conversation_id
        self.title = title
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_archived = bool(is_archived)
        self.is_starred = bool(is_starred)


class ConversationStore:
    """
    Persistence boundary for JARVIS conversations.

    Responsibilities:

        - create conversations
        - store messages
        - retrieve conversations
        - restore ConversationState
        - persist active conversation state

    This class does not perform AI operations and does not
    perform memory formation.
    """

    def __init__(self):
        self.ensure_schema()

    def ensure_schema(self):
        """
        Ensure persistent conversation-state storage exists.

        The base conversations/messages tables may be created by an
        earlier schema component. ConversationStore must therefore not
        make construction fail merely because the messages table is not
        present yet. Auxiliary indexes are created only when their base
        table exists.
        """

        connection = get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_state (
                    conversation_id TEXT PRIMARY KEY,

                    active_topic TEXT,
                    active_task TEXT,

                    metadata TEXT NOT NULL
                        DEFAULT '{}',

                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,

                    FOREIGN KEY (
                        conversation_id
                    )
                    REFERENCES conversations(id)
                    ON DELETE CASCADE
                )
                """
            )

            messages_exists = cursor.execute(
                """
                SELECT 1
                FROM sqlite_master
                WHERE type = 'table'
                  AND name = 'messages'
                LIMIT 1
                """
            ).fetchone()

            if messages_exists is not None:
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_messages_conversation_created
                    ON messages(
                        conversation_id,
                        created_at
                    )
                    """
                )

            connection.commit()
        finally:
            connection.close()

    @staticmethod
    def _timestamp():
        return (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

    def create_conversation(
        self,
        title=None,
        conversation_id=None,
    ):
        """
        Create a new persistent conversation.

        Returns:
            ConversationRecord
        """

        conversation_id = (
            conversation_id
            or str(uuid4())
        )

        timestamp = self._timestamp()

        title = (
            title.strip()
            if isinstance(title, str)
            else None
        )

        if not title:
            title = "JARVIS Conversation"

        connection = get_connection()

        try:

            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO conversations (
                    id,
                    title,
                    created_at,
                    updated_at,
                    is_archived,
                    is_starred
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    conversation_id,
                    title,
                    timestamp,
                    timestamp,
                    0,
                    0,
                ),
            )

            cursor.execute(
                """
                INSERT INTO conversation_state (
                    conversation_id,
                    active_topic,
                    active_task,
                    metadata,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    conversation_id,
                    None,
                    None,
                    "{}",
                    timestamp,
                    timestamp,
                ),
            )

            connection.commit()

        except sqlite3.IntegrityError:

            connection.rollback()
            raise

        finally:

            connection.close()

        return ConversationRecord(
            conversation_id=conversation_id,
            title=title,
            created_at=timestamp,
            updated_at=timestamp,
            is_archived=False,
            is_starred=False,
        )

    def conversation_exists(
        self,
        conversation_id,
    ):
        connection = get_connection()

        row = connection.execute(
            """
            SELECT 1
            FROM conversations
            WHERE id = ?
            LIMIT 1
            """,
            (conversation_id,),
        ).fetchone()

        connection.close()

        return row is not None

    def get_conversation(
        self,
        conversation_id,
    ):
        """
        Retrieve persistent conversation metadata.

        Returns:
            ConversationRecord | None
        """

        connection = get_connection()

        row = connection.execute(
            """
            SELECT
                id,
                title,
                created_at,
                updated_at,
                is_archived,
                is_starred
            FROM conversations
            WHERE id = ?
            LIMIT 1
            """,
            (conversation_id,),
        ).fetchone()

        connection.close()

        if row is None:
            return None

        return ConversationRecord(
            conversation_id=row[0],
            title=row[1],
            created_at=row[2],
            updated_at=row[3],
            is_archived=row[4],
            is_starred=row[5],
        )

    def append_message(
        self,
        conversation_id,
        role,
        content,
        parent_id=None,
        message_id=None,
        created_at=None,
    ):
        """
        Persist one conversation message.

        Returns:
            dict containing message_id and created_at.
        """

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
                "Message content must be a string."
            )

        content = content.strip()

        if not content:
            raise ValueError(
                "Message content cannot be empty."
            )

        if not self.conversation_exists(
            conversation_id
        ):
            raise ValueError(
                "Conversation does not exist."
            )

        message_id = (
            message_id
            or str(uuid4())
        )

        created_at = (
            created_at
            or self._timestamp()
        )

        connection = get_connection()

        try:

            connection.execute(
                """
                INSERT INTO messages (
                    id,
                    conversation_id,
                    role,
                    content,
                    created_at,
                    parent_id
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    message_id,
                    conversation_id,
                    role,
                    content,
                    created_at,
                    parent_id,
                ),
            )

            connection.execute(
                """
                UPDATE conversations
                SET updated_at = ?
                WHERE id = ?
                """,
                (
                    created_at,
                    conversation_id,
                ),
            )

            connection.commit()

        except sqlite3.IntegrityError:

            connection.rollback()
            raise

        finally:

            connection.close()

        return {
            "message_id": message_id,
            "created_at": created_at,
        }

    def get_messages(
        self,
        conversation_id,
    ):
        """
        Retrieve all messages belonging to a conversation.
        """

        connection = get_connection()

        rows = connection.execute(
            """
            SELECT
                id,
                conversation_id,
                role,
                content,
                created_at,
                parent_id
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at, rowid
            """,
            (
                conversation_id,
            ),
        ).fetchall()

        connection.close()

        return rows

    def save_state(
        self,
        snapshot: StateSnapshot,
    ):
        """
        Persist the current active conversation state.
        """

        metadata_json = json.dumps(
            snapshot.metadata,
            ensure_ascii=False,
        )

        connection = get_connection()

        connection.execute(
            """
            INSERT INTO conversation_state (
                conversation_id,
                active_topic,
                active_task,
                metadata,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)

            ON CONFLICT(conversation_id)
            DO UPDATE SET
                active_topic = excluded.active_topic,
                active_task = excluded.active_task,
                metadata = excluded.metadata,
                updated_at = excluded.updated_at
            """,
            (
                snapshot.conversation_id,
                snapshot.active_topic,
                snapshot.active_task,
                metadata_json,
                snapshot.created_at,
                snapshot.updated_at,
            ),
        )

        connection.execute(
            """
            UPDATE conversations
            SET updated_at = ?
            WHERE id = ?
            """,
            (
                snapshot.updated_at,
                snapshot.conversation_id,
            ),
        )

        connection.commit()
        connection.close()

    def load_state(
        self,
        conversation_id,
    ):
        """
        Reconstruct a ConversationState from persistent storage.

        Returns:
            ConversationState | None
        """

        conversation = self.get_conversation(
            conversation_id
        )

        if conversation is None:
            return None

        connection = get_connection()

        state_row = connection.execute(
            """
            SELECT
                active_topic,
                active_task,
                metadata,
                created_at,
                updated_at
            FROM conversation_state
            WHERE conversation_id = ?
            LIMIT 1
            """,
            (
                conversation_id,
            ),
        ).fetchone()

        message_rows = connection.execute(
            """
            SELECT
                role,
                content,
                created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at, rowid
            """,
            (
                conversation_id,
            ),
        ).fetchall()

        connection.close()

        turns = tuple(
            Turn(
                role=row[0],
                content=row[1],
                timestamp=str(row[2]),
            )
            for row in message_rows
        )

        if state_row is None:

            active_topic = None
            active_task = None
            metadata = {}
            created_at = str(
                conversation.created_at
            )
            updated_at = str(
                conversation.updated_at
            )

        else:

            active_topic = state_row[0]
            active_task = state_row[1]

            try:
                metadata = json.loads(
                    state_row[2]
                )

            except (
                TypeError,
                json.JSONDecodeError,
            ):
                metadata = {}

            created_at = str(
                state_row[3]
            )

            updated_at = str(
                state_row[4]
            )

        return ConversationState.restore(
            conversation_id=conversation_id,
            created_at=created_at,
            updated_at=updated_at,
            turns=turns,
            active_topic=active_topic,
            active_task=active_task,
            metadata=metadata,
        )
