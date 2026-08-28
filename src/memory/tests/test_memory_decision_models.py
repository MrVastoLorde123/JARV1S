import unittest

from src.memory.memory_decision_models import (
    CREATE,
    CONFIRM,
    UPDATE,
    CONTRADICT,
    IGNORE,
    MemoryDecision,
    MemoryDecisionContext,
)

from src.memory.memory_models import (
    CandidateMemory,
)

class MemoryDecisionModelTests(
    unittest.TestCase
):

    def setUp(
        self,
    ):

        self.candidate = CandidateMemory(
            content=(
                "User is learning PCVUE v17."
            ),
            category="SKILL",
            memory_key="pcvue_v17_skill",
            subject="PCVUE v17",
            evidence_text=(
                "I'm learning PCVUE v17."
            ),
        )

    def test_decision_context_can_be_created(
        self,
    ):

        context = MemoryDecisionContext(
            candidate=self.candidate,
        )

        self.assertEqual(
            context.candidate,
            self.candidate,
        )

        self.assertIsNone(
            context.existing_memory,
        )

    def test_decision_requires_valid_action(
        self,
    ):

        with self.assertRaises(
            ValueError
        ):

            MemoryDecision(
                action="INVALID",
                candidate=self.candidate,
                memory_id=None,
                reason="Invalid",
                confidence=0.5,
            )

    def test_decision_requires_valid_confidence(
        self,
    ):

        with self.assertRaises(
            ValueError
        ):

            MemoryDecision(
                action=CREATE,
                candidate=self.candidate,
                memory_id=None,
                reason="Test",
                confidence=2.0,
            )

    def test_valid_create_decision_can_be_created(
        self,
    ):

        decision = MemoryDecision(
            action=CREATE,
            candidate=self.candidate,
            memory_id=None,
            reason="No matching memory.",
            confidence=0.9,
        )

        self.assertEqual(
            decision.action,
            CREATE,
        )

    def test_all_decision_actions_are_recognized(
        self,
    ):

        actions = (
            CREATE,
            CONFIRM,
            UPDATE,
            CONTRADICT,
            IGNORE,
        )

        for action in actions:

            decision = MemoryDecision(
                action=action,
                candidate=self.candidate,
                memory_id=None,
                reason="Test",
                confidence=0.5,
            )

            self.assertEqual(
                decision.action,
                action,
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2,
    )