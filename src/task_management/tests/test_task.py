import unittest

from src.task_management.goals import Provenance
from src.task_management.task import Task, TaskState, TaskStore, TaskTransitionError


class TaskModelLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provenance = Provenance(source="objective", reference_id="objective-1")
        self.task = Task(
            task_id="task-1",
            objective_id="objective-1",
            title="Research target customers",
            description="Identify the initial customer segment.",
            provenance=self.provenance,
            priority=10,
        )

    def test_task_is_immutable(self) -> None:
        with self.assertRaises(AttributeError):
            self.task.title = "changed"
        with self.assertRaises(TypeError):
            self.task.metadata["x"] = "y"

    def test_task_requires_valid_identity_and_text(self) -> None:
        with self.assertRaises(ValueError):
            Task("", "objective-1", "Title", "Description", self.provenance)
        with self.assertRaises(ValueError):
            Task("task-1", "", "Title", "Description", self.provenance)
        with self.assertRaises(ValueError):
            Task("task-1", "objective-1", "", "Description", self.provenance)
        with self.assertRaises(ValueError):
            Task("task-1", "objective-1", "Title", "", self.provenance)

    def test_task_context_is_non_authoritative(self) -> None:
        context = self.task.to_context()
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertEqual(context["task_id"], "task-1")
        self.assertEqual(context["objective_id"], "objective-1")

    def test_full_operational_lifecycle_is_explicit(self) -> None:
        ready = self.task.transition(TaskState.READY, reference_id="ready-1")
        started = ready.transition(TaskState.IN_PROGRESS, reference_id="start-1")
        blocked = started.transition(TaskState.BLOCKED, reference_id="block-1")
        resumed = blocked.transition(TaskState.IN_PROGRESS, reference_id="resume-1")
        completed = resumed.transition(TaskState.COMPLETED, reference_id="complete-1")

        self.assertEqual(completed.state, TaskState.COMPLETED)
        self.assertEqual(completed.metadata["last_transition_reference"], "complete-1")
        self.assertEqual(completed.objective_id, "objective-1")

    def test_proposed_tasks_can_be_cancelled_or_superseded(self) -> None:
        cancelled = self.task.transition(TaskState.CANCELLED, reference_id="cancel-1")
        superseded = self.task.transition(TaskState.SUPERSEDED, reference_id="replace-1")
        self.assertEqual(cancelled.state, TaskState.CANCELLED)
        self.assertEqual(superseded.state, TaskState.SUPERSEDED)

    def test_invalid_transition_is_rejected(self) -> None:
        with self.assertRaises(TaskTransitionError):
            self.task.transition(TaskState.COMPLETED, reference_id="complete-1")
        with self.assertRaises(TaskTransitionError):
            self.task.transition(TaskState.IN_PROGRESS, reference_id="start-1")

    def test_transition_requires_reference(self) -> None:
        with self.assertRaises(ValueError):
            self.task.transition(TaskState.READY, reference_id="")

    def test_terminal_tasks_cannot_transition(self) -> None:
        terminal_candidates = (
            self.task.transition(TaskState.READY, reference_id="ready-1").transition(
                TaskState.IN_PROGRESS, reference_id="start-1"
            ).transition(TaskState.COMPLETED, reference_id="complete-1"),
            self.task.transition(TaskState.CANCELLED, reference_id="cancel-1"),
            self.task.transition(TaskState.SUPERSEDED, reference_id="replace-1"),
        )
        for terminal in terminal_candidates:
            with self.subTest(state=terminal.state):
                with self.assertRaises(TaskTransitionError):
                    terminal.transition(TaskState.READY, reference_id="reopen-1")

    def test_task_store_rejects_unknown_objective_when_registry_is_bound(self) -> None:
        store = TaskStore(objective_ids={"objective-2"})
        with self.assertRaises(ValueError):
            store.put_task(self.task)

    def test_task_store_allows_registration_and_idempotent_put(self) -> None:
        store = TaskStore()
        store.register_objective("objective-1")
        store.put_task(self.task)
        store.put_task(self.task)
        self.assertEqual(store.get_task("task-1"), self.task)

    def test_task_identity_conflicts_are_rejected(self) -> None:
        store = TaskStore()
        store.register_objective("objective-1")
        store.put_task(self.task)
        conflicting = Task(
            task_id="task-1",
            objective_id="objective-1",
            title="Different",
            description="Different",
            provenance=self.provenance,
        )
        with self.assertRaises(ValueError):
            store.put_task(conflicting)

    def test_task_objective_identity_cannot_change(self) -> None:
        store = TaskStore()
        store.register_objective("objective-1")
        store.register_objective("objective-2")
        store.put_task(self.task)
        replacement = Task(
            task_id="task-1",
            objective_id="objective-2",
            title=self.task.title,
            description=self.task.description,
            provenance=self.task.provenance,
        )
        with self.assertRaises(ValueError):
            store.replace_task(replacement)

    def test_task_listing_is_deterministic_and_can_exclude_terminal(self) -> None:
        store = TaskStore()
        store.register_objective("objective-1")
        store.put_task(self.task)
        store.put_task(
            Task(
                task_id="task-2",
                objective_id="objective-1",
                title="Higher priority",
                description="Do this first.",
                provenance=self.provenance,
                priority=20,
                state=TaskState.READY,
            )
        )
        store.replace_task(self.task.transition(TaskState.CANCELLED, reference_id="cancel-1"))

        current = store.list_tasks("objective-1", include_terminal=False)
        self.assertEqual(tuple(task.task_id for task in current), ("task-2",))
        self.assertEqual(tuple(task.task_id for task in store.list_tasks("objective-1")), ("task-2", "task-1"))

    def test_task_has_no_dependency_or_scheduling_contract(self) -> None:
        self.assertFalse(hasattr(self.task, "depends_on"))
        self.assertFalse(hasattr(self.task, "scheduled_at"))
        self.assertFalse(hasattr(self.task, "worker_id"))
        self.assertFalse(hasattr(self.task, "execution_request"))


if __name__ == "__main__":
    unittest.main()
