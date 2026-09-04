"""Tests for the M20.3 task dependency graph boundary."""

import unittest

from src.task_management.dependencies import DependencyError, TaskDependency, TaskDependencyGraph


class TaskDependencyGraphTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = TaskDependencyGraph(["t1", "t2", "t3", "t4"])

    def test_dependency_model_has_explicit_direction(self) -> None:
        dependency = TaskDependency("t1", "t2")
        self.assertEqual(dependency.edge, ("t1", "t2"))

    def test_self_dependency_is_rejected(self) -> None:
        with self.assertRaises(DependencyError):
            self.graph.add_dependency("t1", "t1")

    def test_unknown_tasks_are_rejected(self) -> None:
        with self.assertRaises(DependencyError):
            self.graph.add_dependency("missing", "t1")
        with self.assertRaises(DependencyError):
            self.graph.add_dependency("t1", "missing")

    def test_duplicate_dependency_is_idempotent(self) -> None:
        first = self.graph.add_dependency("t1", "t2")
        second = self.graph.add_dependency("t1", "t2")
        self.assertEqual(first, second)
        self.assertEqual(self.graph.dependencies(), (first,))

    def test_cycle_is_rejected(self) -> None:
        self.graph.add_dependency("t1", "t2")
        self.graph.add_dependency("t2", "t3")
        with self.assertRaises(DependencyError):
            self.graph.add_dependency("t3", "t1")

    def test_prerequisites_and_dependents_are_symmetric(self) -> None:
        self.graph.add_dependency("t1", "t3")
        self.graph.add_dependency("t2", "t3")
        self.assertEqual(self.graph.prerequisites("t3"), ("t1", "t2"))
        self.assertEqual(self.graph.dependents("t1"), ("t3",))
        self.assertEqual(self.graph.dependents("t2"), ("t3",))

    def test_dependency_removal_is_explicit_and_idempotent(self) -> None:
        self.graph.add_dependency("t1", "t2")
        self.assertTrue(self.graph.remove_dependency("t1", "t2"))
        self.assertFalse(self.graph.remove_dependency("t1", "t2"))
        self.assertEqual(self.graph.dependencies(), ())

    def test_deterministic_topological_order(self) -> None:
        self.graph.add_dependency("t1", "t3")
        self.graph.add_dependency("t2", "t3")
        self.graph.add_dependency("t3", "t4")
        self.assertEqual(self.graph.topological_order(), ("t1", "t2", "t3", "t4"))

    def test_roots_and_leaves_are_structural_only(self) -> None:
        self.graph.add_dependency("t1", "t3")
        self.graph.add_dependency("t2", "t3")
        self.graph.add_dependency("t3", "t4")
        self.assertEqual(self.graph.root_tasks(), ("t1", "t2"))
        self.assertEqual(self.graph.leaf_tasks(), ("t4",))

    def test_task_registration_is_idempotent(self) -> None:
        self.graph.register_task("t1")
        self.assertEqual(self.graph.all_task_ids(), ("t1", "t2", "t3", "t4"))

    def test_graph_has_no_scheduling_or_authority_contract(self) -> None:
        self.graph.add_dependency("t1", "t2")
        self.assertFalse(hasattr(self.graph, "schedule"))
        self.assertFalse(hasattr(self.graph, "next_step"))
        self.assertFalse(hasattr(self.graph, "authorize"))
        self.assertFalse(hasattr(self.graph, "execute"))


if __name__ == "__main__":
    unittest.main()
