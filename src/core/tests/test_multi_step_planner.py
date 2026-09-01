import unittest

from src.core.multi_step_planner import MultiStepExecutionPlanner
from src.core.task_models import TaskRequest, TaskType


class MultiStepExecutionPlannerTests(unittest.TestCase):
    def setUp(self):
        self.planner = MultiStepExecutionPlanner()

    def test_chained_goal_becomes_ordered_dependent_steps(self):
        result = self.planner.plan(
            TaskRequest(
                "inspect the project then summarize the result",
                TaskType.INFORMATION,
            )
        )
        self.assertEqual(len(result.steps), 2)
        self.assertEqual(result.steps[0].order, 0)
        self.assertEqual(result.steps[1].order, 1)
        self.assertEqual(result.steps[0].depends_on, ())
        self.assertEqual(result.steps[1].depends_on, (result.steps[0].step_id,))

    def test_single_goal_remains_one_step(self):
        result = self.planner.plan(TaskRequest("inspect project", TaskType.INFORMATION))
        self.assertEqual(len(result.steps), 1)
        self.assertEqual(result.metadata["subtask_count"], 1)

    def test_tool_metadata_is_preserved_per_subtask(self):
        result = self.planner.plan(
            TaskRequest(
                "read README.md then read docs/JARVIS_MASTER_CONTEXT.md",
                TaskType.TOOL,
                metadata={"tool_name": "read_file", "arguments": {"path": "README.md"}},
            )
        )
        self.assertEqual(len(result.steps), 2)
        self.assertEqual(result.steps[0].metadata["tool_name"], "read_file")
        self.assertEqual(result.steps[1].metadata["tool_name"], "read_file")
        self.assertEqual(result.steps[0].metadata["subtask_index"], 1)
        self.assertEqual(result.steps[1].metadata["subtask_index"], 2)

    def test_planner_does_not_execute(self):
        result = self.planner.plan(TaskRequest("inspect project then summarize", TaskType.INFORMATION))
        self.assertEqual(result.status.value, "READY")

    def test_invalid_task_is_rejected(self):
        with self.assertRaises(TypeError):
            self.planner.plan("inspect project")


if __name__ == "__main__":
    unittest.main()
