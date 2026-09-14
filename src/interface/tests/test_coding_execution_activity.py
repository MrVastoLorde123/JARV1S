import unittest

from src.core.interface_backend import InterfaceOperation
from src.core.runtime_activity_stream import RuntimeActivityKind, RuntimeActivityStream
from src.interface.coding_execution_activity import CodingExecutionActivityRecorder, ObservingToolInvoker
from src.tools.models import ToolError, ToolRequest, ToolResult


class FakeToolInvoker:
    def __init__(self, result: ToolResult) -> None:
        self.result = result
        self.requests = []

    def invoke(self, request: ToolRequest) -> ToolResult:
        self.requests.append(request)
        return self.result


class CodingExecutionActivityTests(unittest.TestCase):
    def test_tool_execution_lifecycle_is_observed_without_arguments(self):
        stream = RuntimeActivityStream()
        recorder = CodingExecutionActivityRecorder(stream)
        delegate = FakeToolInvoker(
            ToolResult(
                success=True,
                tool_name="write_file",
                invocation_id="invoke-1",
            )
        )
        invoker = ObservingToolInvoker(delegate, recorder)
        request = ToolRequest(
            tool_name="write_file",
            arguments={"path": "secret.txt", "content": "PRIVATE"},
            metadata={
                "task_id": "task-1",
                "coding_operation_id": "op-1",
                "edit_index": 0,
            },
            invocation_id="invoke-1",
        )

        result = invoker.invoke(request)

        self.assertTrue(result.success)
        self.assertEqual([event.kind for event in stream.snapshot()], [
            RuntimeActivityKind.TOOL_EXECUTION_STARTED,
            RuntimeActivityKind.TOOL_EXECUTION_COMPLETED,
        ])
        completed = stream.snapshot()[1]
        self.assertEqual(completed.operation, InterfaceOperation.APPLY)
        self.assertEqual(completed.metadata["tool_name"], "write_file")
        self.assertNotIn("arguments", completed.metadata)
        self.assertNotIn("content", completed.metadata)
        self.assertNotIn("path", completed.metadata)

    def test_verification_lifecycle_is_observed_with_bounded_error(self):
        stream = RuntimeActivityStream()
        recorder = CodingExecutionActivityRecorder(stream)
        delegate = FakeToolInvoker(
            ToolResult(
                success=False,
                tool_name="run_test",
                invocation_id="verify-1",
                error=ToolError(code="test_failed", message="verification failed"),
            )
        )
        invoker = ObservingToolInvoker(delegate, recorder)
        request = ToolRequest(
            tool_name="run_test",
            arguments={"runner": "python_unittest", "arguments": ["private-test"]},
            metadata={"task_id": "task-2", "phase": "verification"},
            invocation_id="verify-1",
        )

        result = invoker.invoke(request)

        self.assertFalse(result.success)
        events = stream.snapshot()
        self.assertEqual([event.kind for event in events], [
            RuntimeActivityKind.VERIFICATION_STARTED,
            RuntimeActivityKind.VERIFICATION_COMPLETED,
        ])
        completed = events[1]
        self.assertEqual(completed.operation, InterfaceOperation.VERIFY)
        self.assertFalse(completed.metadata["success"])
        self.assertEqual(completed.metadata["error_code"], "test_failed")
        self.assertNotIn("arguments", completed.metadata)


if __name__ == "__main__":
    unittest.main()
