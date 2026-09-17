from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.agents.coding_execution_learning import CodingExecutionLearningService
from src.agents.coding_worker import (
    CodingAgentEdit,
    CodingAgentPlan,
    CodingAgentResult,
    CodingAgentTask,
    CodingAgentVerification,
)
from src.core.persistent_intelligence import PersistentMemoryRepository
from src.core.persistent_memory import MemoryLifecycle, PersistentMemoryKind
from src.tools.models import ToolResult


class CS4DurableRestartLearningTests(unittest.TestCase):
    def _fixtures(self):
        task = CodingAgentTask(
            objective="prove durable restart continuity",
            task_id="cs4-restart-task",
            metadata={"coding_operation_id": "cs4-restart-operation"},
        )
        plan = CodingAgentPlan(
            edits=(
                CodingAgentEdit(
                    path="src/example.py",
                    content="restart proof",
                    overwrite=True,
                ),
            ),
            verification=CodingAgentVerification(runner="python_unittest"),
            rationale="Record one completed execution and reopen the same store.",
        )
        result = CodingAgentResult(
            task_id=task.task_id,
            status="verified",
            edits_attempted=1,
            edits_applied=1,
            edit_results=(
                ToolResult(
                    success=True,
                    tool_name="write_file",
                    content={"written": True},
                    invocation_id="cs4-edit",
                ),
            ),
            verification=ToolResult(
                success=True,
                tool_name="run_test",
                content={"exit_code": 0},
                invocation_id="cs4-test",
            ),
            message="verification passed",
        )
        return task, plan, result

    def test_learning_record_survives_repository_recreation(self):
        with tempfile.TemporaryDirectory() as tmp:
            database_path = Path(tmp) / "jarvis.db"

            first_repository = PersistentMemoryRepository(database_path)
            first_service = CodingExecutionLearningService(first_repository)
            task, plan, result = self._fixtures()

            first_record = first_service.record(task, plan, result)
            self.assertTrue(first_record.persisted)

            original = first_repository.get(first_record.memory_id)
            self.assertIsNotNone(original)
            self.assertEqual(original.kind, PersistentMemoryKind.EPISODIC)
            self.assertEqual(original.status, MemoryLifecycle.CANDIDATE)

            del first_service
            del first_repository

            restarted_repository = PersistentMemoryRepository(database_path)
            restarted_service = CodingExecutionLearningService(restarted_repository)

            restored = restarted_repository.get(first_record.memory_id)
            self.assertIsNotNone(restored)
            self.assertEqual(restored.kind, PersistentMemoryKind.EPISODIC)
            self.assertEqual(restored.status, MemoryLifecycle.CANDIDATE)
            self.assertEqual(restored.content, original.content)
            self.assertEqual(restored.provenance_ids, original.provenance_ids)

            provenance = restarted_repository.provenance_for(restored.memory_id)
            self.assertEqual(
                tuple(reference.provenance_id for reference in provenance.refs),
                restored.provenance_ids,
            )

            second_record = restarted_service.record(task, plan, result)
            self.assertFalse(second_record.persisted)
            self.assertEqual(second_record.memory_id, first_record.memory_id)
            self.assertEqual(
                len(
                    restarted_repository.list_records(
                        kind=PersistentMemoryKind.EPISODIC,
                    )
                ),
                1,
            )


if __name__ == "__main__":
    unittest.main()
