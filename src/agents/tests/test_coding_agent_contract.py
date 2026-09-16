from __future__ import annotations

import unittest

from src.agents.coding_agent_contract import (
    CodingAgentStage,
    CodingAgentState,
    can_transition,
)


class M28CodingAgentContractTests(unittest.TestCase):
    def test_state_requires_safe_identity_and_bounds(self) -> None:
        state = CodingAgentState(
            task_id="coding-1",
            stage=CodingAgentStage.PLANNING,
            objective="Improve the interface",
            edits_total=2,
            edits_applied=1,
        )
        self.assertEqual(state.task_id, "coding-1")
        self.assertEqual(state.edits_applied, 1)

        with self.assertRaises(ValueError):
            CodingAgentState(
                task_id="coding-1",
                stage=CodingAgentStage.PLANNING,
                objective="Improve the interface",
                edits_total=1,
                edits_applied=2,
            )

    def test_authority_lifecycle_is_explicit(self) -> None:
        self.assertTrue(can_transition(CodingAgentStage.IDLE, CodingAgentStage.UNDERSTANDING))
        self.assertTrue(can_transition(CodingAgentStage.PLANNING, CodingAgentStage.AWAITING_CONFIRMATION))
        self.assertTrue(can_transition(CodingAgentStage.AWAITING_CONFIRMATION, CodingAgentStage.EXECUTING))
        self.assertTrue(can_transition(CodingAgentStage.EXECUTING, CodingAgentStage.VERIFYING))
        self.assertTrue(can_transition(CodingAgentStage.VERIFYING, CodingAgentStage.COMPLETE))
        self.assertFalse(can_transition(CodingAgentStage.IDLE, CodingAgentStage.EXECUTING))
        self.assertFalse(can_transition(CodingAgentStage.PLANNING, CodingAgentStage.COMPLETE))

    def test_terminal_states_cannot_transition(self) -> None:
        for stage in (CodingAgentStage.COMPLETE, CodingAgentStage.BLOCKED, CodingAgentStage.FAILED):
            self.assertFalse(can_transition(stage, CodingAgentStage.EXECUTING))
            self.assertFalse(can_transition(stage, CodingAgentStage.COMPLETE))


if __name__ == "__main__":
    unittest.main()
