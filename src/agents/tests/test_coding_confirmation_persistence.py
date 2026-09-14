import tempfile
import unittest
from pathlib import Path

from src.agents.coding_confirmation import CodingAgentConfirmationService
from src.agents.coding_confirmation_models import CodingConfirmationStatus
from src.agents.coding_confirmation_store import CodingConfirmationStore
from src.agents.coding_worker import CodingAgentEdit, CodingAgentPlan, CodingAgentTask, CodingAgentVerification
from src.tools.models import ToolRequest


class CodingConfirmationPersistenceTests(unittest.TestCase):
    def test_pending_operation_survives_service_restart_with_exact_plan(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "jarvis.db"
            store = CodingConfirmationStore(database_path)
            service = CodingAgentConfirmationService(store)
            task = CodingAgentTask(
                objective="Persist the exact approved proposal",
                task_id="task-persist-1",
                metadata={"repository_context": "repo-state"},
            )
            plan = CodingAgentPlan(
                edits=(CodingAgentEdit(path="example.txt", content="hello", overwrite=True),),
                verification=CodingAgentVerification(
                    runner="python_unittest",
                    arguments=("example_test",),
                    timeout_seconds=30,
                ),
                rationale="private planning context",
            )

            staged = service.stage(task, plan, metadata={"ui": "desktop"})
            restarted = CodingAgentConfirmationService(CodingConfirmationStore(database_path))
            restored = restarted.get(staged.operation_id)

            self.assertIsNotNone(restored)
            self.assertEqual(restored.status, CodingConfirmationStatus.PENDING)
            self.assertEqual(restored.task, task)
            self.assertEqual(restored.plan, plan)
            self.assertEqual(restored.metadata["ui"], "desktop")

    def test_consumed_invocation_remains_consumed_after_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "jarvis.db"
            store = CodingConfirmationStore(database_path)
            service = CodingAgentConfirmationService(store)
            task = CodingAgentTask(objective="Run one exact verification", task_id="task-persist-2")
            plan = CodingAgentPlan(
                edits=(),
                verification=CodingAgentVerification(runner="python_unittest", arguments=("tests",)),
            )
            operation = service.stage(task, plan)
            self.assertIsNotNone(service.confirm(operation.operation_id))

            request = ToolRequest(
                tool_name="run_test",
                arguments={"runner": "python_unittest", "arguments": ["tests"]},
                metadata={
                    "coding_operation_id": operation.operation_id,
                    "task_id": task.task_id,
                    "phase": "verification",
                },
                invocation_id="task-persist-2-verification",
            )

            self.assertTrue(service.authorize_tool_request(operation.operation_id, request))

            restarted = CodingAgentConfirmationService(CodingConfirmationStore(database_path))
            self.assertFalse(restarted.authorize_tool_request(operation.operation_id, request))


if __name__ == "__main__":
    unittest.main()
