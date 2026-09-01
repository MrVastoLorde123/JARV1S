import tempfile
import unittest
from pathlib import Path

from src.core.execution_planner import ExecutionPlanner
from src.core.execution_policy import ExecutionPolicy
from src.core.plan_executor import PlanExecutor
from src.core.task_models import TaskRequest, TaskType
from src.core.tool_execution import ToolPlanStepHandler
from src.tools.bootstrap import build_workspace_tool_stack


class ToolExecutionIntegrationTests(unittest.TestCase):
    def test_read_tool_task_passes_through_core_and_tool_layers(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README.md").write_text("JARVIS", encoding="utf-8")

            stack = build_workspace_tool_stack(root)
            handler = ToolPlanStepHandler(stack.gate)
            executor = PlanExecutor({"USE_TOOL": handler})
            task = TaskRequest(
                content="Read the README",
                task_type=TaskType.TOOL,
                metadata={
                    "tool_name": "read_file",
                    "arguments": {"path": "README.md"},
                },
            )

            plan = ExecutionPlanner().plan(task)
            policy = ExecutionPolicy().evaluate(plan)
            execution = executor.execute(plan, policy)

            self.assertEqual("ALLOW", policy.decision.value)
            self.assertEqual("COMPLETED", execution.status.value)
            self.assertEqual("JARVIS", execution.steps[0].output["content"])

    def test_write_tool_task_reaches_tool_gate_and_is_denied_without_confirmation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            stack = build_workspace_tool_stack(root)
            handler = ToolPlanStepHandler(stack.gate)
            executor = PlanExecutor({"USE_TOOL": handler})
            task = TaskRequest(
                content="Write a file",
                task_type=TaskType.TOOL,
                metadata={
                    "tool_name": "write_file",
                    "arguments": {
                        "path": "notes.txt",
                        "content": "blocked",
                    },
                },
            )

            plan = ExecutionPlanner().plan(task)
            policy = ExecutionPolicy().evaluate(plan)
            execution = executor.execute(plan, policy)

            self.assertEqual("ALLOW", policy.decision.value)
            self.assertEqual("FAILED", execution.status.value)
            self.assertIn("confirmation_denied", execution.error)
            self.assertFalse((root / "notes.txt").exists())


if __name__ == "__main__":
    unittest.main()
