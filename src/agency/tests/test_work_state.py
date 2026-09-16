from __future__ import annotations

import unittest

from src.agency.work_state import (
    WorkBlocker,
    WorkRole,
    WorkStage,
    WorkState,
    WorkStatus,
    infer_work_role,
)


class M31WorkStateTests(unittest.TestCase):
    def test_work_state_is_immutable_and_bounded(self) -> None:
        state = WorkState(
            work_id="work-1",
            objective="Build the next JARVIS boundary",
            stage=WorkStage.PLANNING,
            status=WorkStatus.ACTIVE,
            role=WorkRole.TECHNICAL_LEAD,
            progress=0.5,
            required_capabilities=("filesystem", "tests"),
            assigned_agent_ids=("agent-1",),
            evidence_cursor=12,
        )
        self.assertEqual(state.work_id, "work-1")
        self.assertEqual(state.progress, 0.5)
        with self.assertRaises(TypeError):
            state.metadata["authority"] = True
        with self.assertRaises(ValueError):
            WorkState(work_id="work-1", objective="bad", progress=1.2)

    def test_blockers_are_first_class_work_state(self) -> None:
        blocker = WorkBlocker(
            blocker_id="block-1",
            message="Waiting for repository evidence",
            severity="HIGH",
            stage=WorkStage.GATHERING_EVIDENCE,
        )
        state = WorkState(
            work_id="work-2",
            objective="Investigate missing evidence",
            stage=WorkStage.BLOCKED,
            status=WorkStatus.BLOCKED,
            blockers=(blocker,),
        )
        self.assertTrue(state.is_blocked)
        self.assertEqual(state.blockers[0].severity, "HIGH")

    def test_dynamic_role_inference_uses_work_state_signals(self) -> None:
        self.assertEqual(
            infer_work_role(stage=WorkStage.GATHERING_EVIDENCE, has_unknowns=True),
            WorkRole.RESEARCHER,
        )
        self.assertEqual(
            infer_work_role(stage=WorkStage.PLANNING, implementation_ready=True),
            WorkRole.TECHNICAL_LEAD,
        )
        self.assertEqual(
            infer_work_role(stage=WorkStage.VERIFYING, has_failed_verification=True),
            WorkRole.DEBUGGER,
        )
        self.assertEqual(
            infer_work_role(stage=WorkStage.COMPLETE, verification_passed=True),
            WorkRole.RELEASE_COORDINATOR,
        )

    def test_role_is_not_authority(self) -> None:
        state = WorkState(
            work_id="work-3",
            objective="Review proposed change",
            stage=WorkStage.PROPOSING_ACTION,
            status=WorkStatus.ACTIVE,
            role=WorkRole.REVIEWER,
        )
        self.assertNotIn("authority", state.metadata)
        self.assertNotIn("permission", state.metadata)


if __name__ == "__main__":
    unittest.main()
