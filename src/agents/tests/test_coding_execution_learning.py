from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from src.agents.coding_execution_learning import (
    CodingExecutionLearningRecord,
    CodingExecutionLearningService,
)
from src.agents.coding_worker import (
    CodingAgentEdit,
    CodingAgentPlan,
    CodingAgentResult,
    CodingAgentTask,
    CodingAgentVerification,
)
from src.core.coding_agent_jarvis import CodingAgentJARVIS
from src.core.persistent_intelligence import PersistentMemoryRepository
from src.core.persistent_memory import MemoryLifecycle, PersistentMemoryKind
from src.learning.evaluation import EvaluationState
from src.learning.experience import Experience
from src.tools.models import ToolResult
from src.agents.coding_confirmation import coding_plan_fingerprint


class CodingExecutionLearningServiceTests(unittest.TestCase):
    def _fixtures(self):
        task = CodingAgentTask(
            objective="execute bounded coding change",
            task_id="cs3-task",
            metadata={"coding_operation_id": "cs3-operation"},
        )
        plan = CodingAgentPlan(
            edits=(CodingAgentEdit(path="src/example.py", content="updated"),),
            verification=CodingAgentVerification(runner="python_unittest"),
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
                    invocation_id="cs3-edit",
                ),
            ),
            verification=ToolResult(
                success=True,
                tool_name="run_test",
                content={"exit_code": 0},
                invocation_id="cs3-test",
            ),
            message="verification passed",
        )
        return task, plan, result

    def test_record_observes_completed_execution_and_persists_candidate_learning(self):
        with tempfile.TemporaryDirectory() as tmp:
            repository = PersistentMemoryRepository(Path(tmp) / "jarvis.db")
            service = CodingExecutionLearningService(repository)
            task, plan, result = self._fixtures()

            record = service.record(task, plan, result)

            self.assertIsInstance(record, CodingExecutionLearningRecord)
            self.assertTrue(record.persisted)
            self.assertEqual(record.evaluation.state, EvaluationState.SUCCESS)
            self.assertEqual(record.claim_evaluation_state, "VERIFIED")
            self.assertFalse(record.experience.provenance["authority_granted"])
            self.assertFalse(record.experience.provenance["execution_repeated"])
            memory = repository.get(record.memory_id)
            self.assertIsNotNone(memory)
            self.assertEqual(memory.kind, PersistentMemoryKind.EPISODIC)
            self.assertEqual(memory.status, MemoryLifecycle.CANDIDATE)
            self.assertFalse(memory.to_context()["truth_established"])
            self.assertFalse(memory.to_context()["authority_granted"])

    def test_record_is_idempotent_for_same_execution_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            repository = PersistentMemoryRepository(Path(tmp) / "jarvis.db")
            service = CodingExecutionLearningService(repository)
            task, plan, result = self._fixtures()

            first = service.record(task, plan, result)
            second = service.record(task, plan, result)

            self.assertTrue(first.persisted)
            self.assertFalse(second.persisted)
            self.assertEqual(first.memory_id, second.memory_id)
            self.assertEqual(first.experience.experience_id, second.experience.experience_id)
            self.assertEqual(len(repository.list_records(kind=PersistentMemoryKind.EPISODIC)), 1)

    def test_persistence_failure_is_reported_without_repeating_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            repository = PersistentMemoryRepository(Path(tmp) / "jarvis.db")
            service = CodingExecutionLearningService(repository)
            task, plan, result = self._fixtures()

            with patch.object(repository, "persist", side_effect=RuntimeError("disk unavailable")):
                record = service.record(task, plan, result)

            self.assertFalse(record.persisted)
            self.assertEqual(record.persistence_error, "RuntimeError: disk unavailable")
            self.assertEqual(record.evaluation.state, EvaluationState.SUCCESS)


class CodingAgentJARVISLearningIntegrationTests(unittest.TestCase):
    def test_confirm_observes_the_actual_result_once_and_exposes_learning_receipt(self):
        task = CodingAgentTask(
            objective="execute approved change",
            task_id="jarvis-cs3-task",
            metadata={},
        )
        plan = CodingAgentPlan(
            edits=(CodingAgentEdit(path="src/example.py", content="updated"),),
            verification=CodingAgentVerification(runner="python_unittest"),
        )
        operation = SimpleNamespace(
            operation_id="jarvis-cs3-operation",
            task=task,
            plan=plan,
            metadata={"plan_fingerprint": coding_plan_fingerprint(task, plan)},
            is_pending=True,
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
                    invocation_id="jarvis-cs3-edit",
                ),
            ),
            verification=ToolResult(
                success=True,
                tool_name="run_test",
                content={"exit_code": 0},
                invocation_id="jarvis-cs3-test",
            ),
            message="verification passed",
        )

        confirmation = Mock()
        confirmation.get_pending.return_value = None
        confirmation.get.return_value = operation
        confirmation.confirm.return_value = operation
        learning = Mock()
        learning.record.return_value = SimpleNamespace(
            to_metadata=lambda: {
                "learning_persisted": True,
                "learning_memory_id": "memory-cs3",
                "learning_evaluation_state": "SUCCESS",
                "truth_established": False,
                "certainty_established": False,
                "authority_granted": False,
                "execution_requested": False,
            }
        )
        service = Mock(spec=["execute"])
        service.execute.return_value = result

        jarvis = object.__new__(CodingAgentJARVIS)
        jarvis.coding_confirmation_service = confirmation
        jarvis.coding_agent_service = service
        jarvis.coding_execution_learning_service = learning

        response = jarvis._confirm_coding((operation.operation_id,))

        service.execute.assert_called_once_with(
            task.__class__(
                objective=task.objective,
                task_id=task.task_id,
                metadata={"coding_operation_id": operation.operation_id},
            ),
            plan,
        )
        learning.record.assert_called_once()
        observed_task, observed_plan, observed_result = learning.record.call_args.args
        self.assertEqual(observed_task.task_id, task.task_id)
        self.assertIs(observed_plan, plan)
        self.assertIs(observed_result, result)
        self.assertTrue(response.metadata["learning_persisted"])
        self.assertEqual(response.metadata["learning_memory_id"], "memory-cs3")
        self.assertFalse(response.metadata["authority_granted"])
        self.assertFalse(response.metadata["execution_requested"])


if __name__ == "__main__":
    unittest.main()
