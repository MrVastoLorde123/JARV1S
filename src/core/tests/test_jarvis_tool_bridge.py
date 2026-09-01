import unittest
from unittest.mock import Mock

from src.core.jarvis import JARVIS
from src.core.task_models import TaskRequest, TaskType
from src.core.tool_execution import ToolInvoker
from src.tools.models import ToolResult


class RecordingToolInvoker:
    def __init__(self):
        self.requests = []

    def invoke(self, request):
        self.requests.append(request)
        return ToolResult(
            success=True,
            tool_name=request.tool_name,
            content={
                "tool": request.tool_name,
                "arguments": dict(request.arguments),
            },
            invocation_id=request.invocation_id,
        )


class JARVISToolBridgeTests(unittest.TestCase):
    def test_jarvis_accepts_one_tool_invoker_dependency(self):
        invoker = RecordingToolInvoker()
        jarvis = JARVIS(ai_service=Mock(), tool_invoker=invoker)

        self.assertIs(jarvis.tool_invoker, invoker)
        self.assertTrue(jarvis.plan_executor.has_handler("USE_TOOL"))

    def test_tool_task_flows_through_jarvis_without_tool_specific_dependencies(self):
        invoker = RecordingToolInvoker()
        jarvis = JARVIS(ai_service=Mock(), tool_invoker=invoker)

        response = jarvis.ask_task(
            TaskRequest(
                content="Inspect the README",
                task_type=TaskType.TOOL,
                metadata={
                    "tool_name": "read_file",
                    "arguments": {"path": "README.md"},
                },
            )
        )

        self.assertEqual("TASK", response.metadata["route"])
        self.assertEqual("EXECUTION", response.metadata["stage"])
        self.assertEqual("COMPLETED", response.metadata["execution_status"])
        self.assertEqual(1, len(invoker.requests))
        self.assertEqual("read_file", invoker.requests[0].tool_name)
        self.assertEqual({"path": "README.md"}, invoker.requests[0].arguments)

    def test_jarvis_without_tool_invoker_does_not_construct_one(self):
        jarvis = JARVIS(ai_service=Mock())

        self.assertIsNone(jarvis.tool_invoker)
        self.assertFalse(jarvis.plan_executor.has_handler("USE_TOOL"))


if __name__ == "__main__":
    unittest.main()
