import unittest

from src.core.execution_plan_models import ExecutionPlan, PlanStatus, PlanStep, StepStatus
from src.core.execution_progress import ExecutionProgress
from src.core.execution_state import ExecutionState
from src.core.multi_step_planner import MultiStepExecutionPlanner
from src.core.task_models import TaskRequest, TaskType


class RecordingStepPlanner:
    def __init__(self):
        self.calls = []

    def plan(self, task, progress=None):
        self.calls.append((task, progress))
        return ExecutionPlan(
            plan_id=f"plan-{len(self.calls)}",
            task_description=task.content,
            steps=(
                PlanStep(
                    step_id="source-step",
                    description=task.content,
                    action=None,
                    order=0,
                    status=StepStatus.READY,
                    depends_on=(),
                ),
            ),
            status=PlanStatus.READY,
        )


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

    def test_progress_is_not_forwarded_to_child_subtask_planning(self):
        step_planner = RecordingStepPlanner()
        planner = MultiStepExecutionPlanner(step_planner=step_planner)
        progress = ExecutionProgress.from_state(
            ExecutionState(
                goal="inspect project then summarize",
                plan_id="attempt-1",
                status=ExecutionState.__annotations__["status"].__args__[0].FAILED
                if False
                else __import__("src.core.execution_plan_models", fromlist=["PlanExecutionStatus"]).PlanExecutionStatus.FAILED,
                completed_steps=("inspect project",),
                unresolved_requirements=("summarize",),
            )
        )

        planner.plan(
            TaskRequest("inspect project then summarize", TaskType.INFORMATION),
            progress=progress,
        )

        self.assertEqual(len(step_planner.calls), 2)
        self.assertIsNone(step_planner.calls[0][1])
        self.assertIsNone(step_planner.calls[1][1])

    def test_planner_does_not_execute(self):
        result = self.planner.plan(TaskRequest("inspect project then summarize", TaskType.INFORMATION))
        self.assertEqual(result.status.value, "READY")

    def test_invalid_task_is_rejected(self):
        with self.assertRaises(TypeError):
            self.planner.plan("inspect project")


if __name__ == "__main__":
    unittest.main()
