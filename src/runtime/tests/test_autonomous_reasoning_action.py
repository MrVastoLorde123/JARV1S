import json
import unittest

from src.runtime.autonomous_reasoning_action import (
    AutonomousReasoningAction,
    AutonomousReasoningActionValidationError,
    AutonomousReasoningDisposition,
)


class AutonomousReasoningActionTests(unittest.TestCase):
    def test_tool_request_requires_explicit_tool(self):
        action = AutonomousReasoningAction(
            action_id="a1",
            disposition=AutonomousReasoningDisposition.TOOL_REQUEST,
            rationale="Need evidence.",
            tool_name="read_file",
            arguments={"path": "x.txt"},
        )
        self.assertEqual(action.tool_name, "read_file")
        self.assertFalse(action.to_dict()["authority_granted"])

    def test_tool_request_rejects_missing_tool(self):
        with self.assertRaisesRegex(ValueError, "tool_name is required"):
            AutonomousReasoningAction(
                action_id="a1",
                disposition=AutonomousReasoningDisposition.TOOL_REQUEST,
                rationale="Need evidence.",
            )

    def test_non_tool_disposition_rejects_tool_name(self):
        with self.assertRaisesRegex(ValueError, "only valid for TOOL_REQUEST"):
            AutonomousReasoningAction(
                action_id="a1",
                disposition=AutonomousReasoningDisposition.CONTINUE,
                rationale="Continue thinking.",
                tool_name="read_file",
            )

    def test_waiting_disposition_requires_reason(self):
        with self.assertRaisesRegex(ValueError, "wait_reason is required"):
            AutonomousReasoningAction(
                action_id="a1",
                disposition=AutonomousReasoningDisposition.WAIT_INPUT,
                rationale="Need clarification.",
            )

    def test_complete_requires_result(self):
        with self.assertRaisesRegex(ValueError, "result is required"):
            AutonomousReasoningAction(
                action_id="a1",
                disposition=AutonomousReasoningDisposition.COMPLETE,
                rationale="Done.",
            )

    def test_mapping_round_trip(self):
        action = AutonomousReasoningAction.from_mapping(
            {
                "action_id": "a2",
                "disposition": "wait_tool",
                "rationale": "Waiting on network probe.",
                "wait_reason": "probe-result",
                "metadata": {"attempt": 1},
            }
        )
        self.assertEqual(action.disposition, AutonomousReasoningDisposition.WAIT_TOOL)
        restored = AutonomousReasoningAction.from_mapping(action.to_dict())
        self.assertEqual(restored.action_id, action.action_id)
        self.assertEqual(restored.wait_reason, action.wait_reason)

    def test_json_round_trip(self):
        action = AutonomousReasoningAction(
            action_id="a3",
            disposition=AutonomousReasoningDisposition.COMPLETE,
            rationale="Investigation finished.",
            result={"answer": "confirmed"},
        )
        restored = AutonomousReasoningAction.from_json(action.to_json())
        self.assertEqual(restored.result, {"answer": "confirmed"})
        self.assertEqual(restored.disposition, AutonomousReasoningDisposition.COMPLETE)

    def test_invalid_json_is_rejected(self):
        with self.assertRaises(AutonomousReasoningActionValidationError):
            AutonomousReasoningAction.from_json("not-json")

    def test_unsupported_disposition_is_rejected(self):
        with self.assertRaises(AutonomousReasoningActionValidationError):
            AutonomousReasoningAction.from_mapping(
                {
                    "action_id": "a4",
                    "disposition": "execute_everything",
                    "rationale": "bad",
                }
            )

    def test_tool_request_does_not_grant_authority(self):
        action = AutonomousReasoningAction(
            action_id="a5",
            disposition=AutonomousReasoningDisposition.TOOL_REQUEST,
            rationale="Run safe diagnostic.",
            tool_name="ping",
        )
        payload = action.to_dict()
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["tool_request_is_authorization"])
        self.assertEqual(payload["execution_requested"], True)

    def test_serialization_is_json(self):
        action = AutonomousReasoningAction(
            action_id="a6",
            disposition=AutonomousReasoningDisposition.CONTINUE,
            rationale="Continue.",
        )
        self.assertIsInstance(json.loads(action.to_json()), dict)


if __name__ == "__main__":
    unittest.main()
