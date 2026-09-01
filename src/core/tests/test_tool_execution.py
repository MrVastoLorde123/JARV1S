import unittest

from src.core.execution_plan_models import PlanStep
from src.core.execution_planner import ExecutionPlanner
from src.core.task_models import TaskRequest, TaskType
from src.core.tool_execution import ToolPlanStepHandler
from src.tools.models import ToolError, ToolRequest, ToolResult


class FakeToolInvoker:
    def __init__(self, result):
        self.result = result
        self.requests = []

    def invoke(self, request):
        self.requests.append(request)
        return self.result


class ToolExecutionBridgeTests(unittest.TestCase):
    def test_tool_task_plan_preserves_explicit_tool_invocation_data(self):
        task = TaskRequest(
            content="Read the project README",
            task_type=TaskType.TOOL,
            metadata={
                "tool_name": "read_file",
                "arguments": {"path": "README.md"},
                "invocation_id": "read-readme-1",
            },
        )

        plan = ExecutionPlanner().plan(task)
        step = plan.steps[0]

        self.assertEqual("USE_TOOL", step.action)
        self.assertEqual("read_file", step.metadata["tool_name"])
        self.assertEqual({"path": "README.md"}, step.metadata["arguments"])
        self.assertEqual("read-readme-1", step.metadata["invocation_id"])

    def test_tool_task_requires_tool_name(self):
        task = TaskRequest(
            content="Do something with a tool",
            task_type=TaskType.TOOL,
        )

        with self.assertRaises(ValueError):
            ExecutionPlanner().plan(task)

    def test_tool_task_requires_dictionary_arguments(self):
        task = TaskRequest(
            content="Read something",
            task_type=TaskType.TOOL,
            metadata={
                "tool_name": "read_file",
                "arguments": ["README.md"],
            },
        )

        with self.assertRaises(ValueError):
            ExecutionPlanner().plan(task)

    def test_handler_builds_tool_request_and_returns_content(self):
        invoker = FakeToolInvoker(
            ToolResult(
                success=True,
                tool_name="read_file",
                content={"path": "README.md", "content": "hello"},
            )
        )
        handler = ToolPlanStepHandler(invoker)
        step = PlanStep(
            step_id="step-1",
            description="Read README",
            action="USE_TOOL",
            order=0,
            metadata={
                "tool_name": "read_file",
                "arguments": {"path": "README.md"},
            },
        )

        output = handler(step)

        self.assertEqual(
            {"path": "README.md", "content": "hello"},
            output,
        )
        self.assertEqual(1, len(invoker.requests))
        self.assertIsInstance(invoker.requests[0], ToolRequest)
        self.assertEqual("read_file", invoker.requests[0].tool_name)
        self.assertEqual({"path": "README.md"}, invoker.requests[0].arguments)
        self.assertEqual("step-1", invoker.requests[0].invocation_id)

    def test_explicit_invocation_id_is_preserved(self):
        invoker = FakeToolInvoker(
            ToolResult(
                success=True,
                tool_name="read_file",
                content="ok",
            )
        )
        handler = ToolPlanStepHandler(invoker)
        step = PlanStep(
            step_id="step-1",
            description="Read README",
            action="USE_TOOL",
            order=0,
            metadata={
                "tool_name": "read_file",
                "arguments": {"path": "README.md"},
                "invocation_id": "custom-id",
            },
        )

        handler(step)

        self.assertEqual("custom-id", invoker.requests[0].invocation_id)

    def test_failed_tool_result_becomes_execution_failure(self):
        invoker = FakeToolInvoker(
            ToolResult(
                success=False,
                tool_name="read_file",
                error=ToolError(
                    code="file_not_found",
                    message="no such file: missing.txt",
                ),
            )
        )
        handler = ToolPlanStepHandler(invoker)
        step = PlanStep(
            step_id="step-1",
            description="Read missing file",
            action="USE_TOOL",
            order=0,
            metadata={
                "tool_name": "read_file",
                "arguments": {"path": "missing.txt"},
            },
        )

        with self.assertRaisesRegex(
            RuntimeError,
            "file_not_found: no such file: missing.txt",
        ):
            handler(step)

    def test_handler_rejects_wrong_action(self):
        invoker = FakeToolInvoker(
            ToolResult(
                success=True,
                tool_name="read_file",
                content="ok",
            )
        )
        handler = ToolPlanStepHandler(invoker)
        step = PlanStep(
            step_id="step-1",
            description="Not a tool action",
            action="PERFORM_ACTION",
            order=0,
        )

        with self.assertRaises(ValueError):
            handler(step)

    def test_handler_rejects_missing_tool_name(self):
        invoker = FakeToolInvoker(
            ToolResult(
                success=True,
                tool_name="read_file",
                content="ok",
            )
        )
        handler = ToolPlanStepHandler(invoker)
        step = PlanStep(
            step_id="step-1",
            description="Read something",
            action="USE_TOOL",
            order=0,
            metadata={"arguments": {"path": "README.md"}},
        )

        with self.assertRaises(ValueError):
            handler(step)

    def test_handler_rejects_non_mapping_arguments(self):
        invoker = FakeToolInvoker(
            ToolResult(
                success=True,
                tool_name="read_file",
                content="ok",
            )
        )
        handler = ToolPlanStepHandler(invoker)
        step = PlanStep(
            step_id="step-1",
            description="Read something",
            action="USE_TOOL",
            order=0,
            metadata={
                "tool_name": "read_file",
                "arguments": ["README.md"],
            },
        )

        with self.assertRaises(ValueError):
            handler(step)


if __name__ == "__main__":
    unittest.main()
