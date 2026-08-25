import unittest

from src.core.conversation import (
    ConversationState,
)

from src.core.conversation_models import (
    ASSISTANT,
    USER,
    StateSnapshot,
)


class ConversationStateTests(
    unittest.TestCase
):

    def setUp(self):

        self.conversation = (
            ConversationState()
        )

    def test_conversation_has_id(self):

        self.assertIsNotNone(
            self.conversation.conversation_id
        )

        self.assertTrue(
            self.conversation.conversation_id
        )

    def test_custom_conversation_id_is_preserved(self):

        conversation = ConversationState(
            conversation_id="test-001"
        )

        self.assertEqual(
            conversation.conversation_id,
            "test-001"
        )

    def test_turn_can_be_added(self):

        self.conversation.add_turn(
            USER,
            "Hello JARVIS."
        )

        turns = (
            self.conversation
            .get_recent_turns()
        )

        self.assertEqual(
            len(turns),
            1
        )

        self.assertEqual(
            turns[0].role,
            USER
        )

        self.assertEqual(
            turns[0].content,
            "Hello JARVIS."
        )

    def test_multiple_turns_preserve_order(self):

        self.conversation.add_turn(
            USER,
            "Hello."
        )

        self.conversation.add_turn(
            ASSISTANT,
            "Hello."
        )

        turns = (
            self.conversation
            .get_recent_turns()
        )

        self.assertEqual(
            len(turns),
            2
        )

        self.assertEqual(
            turns[0].role,
            USER
        )

        self.assertEqual(
            turns[1].role,
            ASSISTANT
        )

    def test_recent_turn_limit(self):

        for number in range(5):

            self.conversation.add_turn(
                USER,
                f"Message {number}"
            )

        turns = (
            self.conversation
            .get_recent_turns(
                limit=2
            )
        )

        self.assertEqual(
            len(turns),
            2
        )

        self.assertEqual(
            turns[0].content,
            "Message 3"
        )

        self.assertEqual(
            turns[1].content,
            "Message 4"
        )

    def test_zero_turn_limit_returns_empty(self):

        self.conversation.add_turn(
            USER,
            "Hello."
        )

        self.assertEqual(
            self.conversation
            .get_recent_turns(0),
            ()
        )

    def test_invalid_role_is_rejected(self):

        with self.assertRaises(
            ValueError
        ):

            self.conversation.add_turn(
                "system",
                "Not allowed yet."
            )

    def test_empty_turn_is_rejected(self):

        with self.assertRaises(
            ValueError
        ):

            self.conversation.add_turn(
                USER,
                "   "
            )

    def test_non_string_turn_is_rejected(self):

        with self.assertRaises(
            TypeError
        ):

            self.conversation.add_turn(
                USER,
                123
            )

    def test_topic_can_be_set(self):

        self.conversation.set_topic(
            "Modbus troubleshooting"
        )

        self.assertEqual(
            self.conversation.active_topic,
            "Modbus troubleshooting"
        )

    def test_task_can_be_set(self):

        self.conversation.set_task(
            "Determine why P04 scaling is incorrect."
        )

        self.assertEqual(
            self.conversation.active_task,
            "Determine why P04 scaling is incorrect."
        )

    def test_task_can_be_cleared(self):

        self.conversation.set_task(
            "Temporary task"
        )

        self.conversation.clear_task()

        self.assertIsNone(
            self.conversation.active_task
        )

    def test_none_topic_clears_topic(self):

        self.conversation.set_topic(
            "Temporary topic"
        )

        self.conversation.set_topic(
            None
        )

        self.assertIsNone(
            self.conversation.active_topic
        )

    def test_snapshot_is_created(self):

        self.conversation.add_turn(
            USER,
            "Hello JARVIS."
        )

        self.conversation.set_topic(
            "JARVIS"
        )

        snapshot = (
            self.conversation.snapshot()
        )

        self.assertIsInstance(
            snapshot,
            StateSnapshot
        )

        self.assertEqual(
            snapshot.conversation_id,
            self.conversation.conversation_id
        )

        self.assertEqual(
            len(snapshot.turns),
            1
        )

        self.assertEqual(
            snapshot.active_topic,
            "JARVIS"
        )

    def test_snapshot_is_immutable(self):

        snapshot = (
            self.conversation.snapshot()
        )

        with self.assertRaises(
            AttributeError
        ):

            snapshot.active_topic = (
                "Changed"
            )

    def test_metadata_is_stored_in_snapshot(self):

        self.conversation.set_metadata(
            "test_key",
            "test_value"
        )

        snapshot = (
            self.conversation.snapshot()
        )

        self.assertEqual(
            snapshot.metadata["test_key"],
            "test_value"
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )