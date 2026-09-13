import unittest

from src.runtime.autonomous_tool_result_feedback import (
    AutonomousToolResultFeedbackAdapter,
)
from src.tools.models import ToolError, ToolResult


class M62Tests(unittest.TestCase):
    def test_success_feedback(self):
        result = ToolResult(
            success=True,
            tool_name="inspect",
            content={"state": "healthy"},
            metadata={"source": "test"},
            invocation_id="a1",
        )
        feedback = AutonomousToolResultFeedbackAdapter().adapt(result)
        self.assertTrue(feedback.success)
        self.assertEqual(feedback.tool_name, "inspect")
        self.assertIn("healthy", feedback.observation)
        self.assertEqual(feedback.context_delta["tool_result"]["invocation_id"], "a1")

    def test_failure_feedback(self):
        result = ToolResult(
            success=False,
            tool_name="inspect",
            error=ToolError(
                code="timeout",
                message="device did not respond",
                details={"attempt": 1},
            ),
            invocation_id="a2",
        )
        feedback = AutonomousToolResultFeedbackAdapter().adapt(result)
        self.assertFalse(feedback.success)
        self.assertIn("timeout", feedback.observation)
        self.assertEqual(
            feedback.context_delta["tool_result"]["error"]["code"],
            "timeout",
        )

    def test_invalid_result_rejected(self):
        with self.assertRaises(TypeError):
            AutonomousToolResultFeedbackAdapter().adapt("not a result")

    def test_does_not_mutate_result(self):
        result = ToolResult(
            success=True,
            tool_name="inspect",
            content={"x": 1},
            invocation_id="a3",
        )
        adapter = AutonomousToolResultFeedbackAdapter()
        first = adapter.adapt(result)
        second = adapter.adapt(result)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
