import unittest

from src.agency.delegation import DelegationConflictError, DelegationCoordinator, DelegationPlan
from src.agency.workforce import WorkerAssignment, WorkerDefinition, WorkerRegistry


class DelegationTests(unittest.TestCase):
    def setUp(self):
        self.registry = WorkerRegistry()
        self.registry.register(
            WorkerDefinition(
                worker_id="researcher",
                name="Researcher",
                capabilities=("search", "summarize"),
                max_steps=5,
            )
        )
        self.registry.register(
            WorkerDefinition(
                worker_id="writer",
                name="Writer",
                capabilities=("compose",),
                max_steps=4,
            )
        )

    def assignment(self, assignment_id, worker_id, capability, output):
        return WorkerAssignment(
            assignment_id=assignment_id,
            worker_id=worker_id,
            objective=f"objective-{assignment_id}",
            allowed_capabilities=(capability,),
            input_scope=("request",),
            output_scope=(output,),
            max_steps=2,
        )

    def test_coordinator_accepts_bounded_assignments(self):
        plan = DelegationPlan(
            plan_id="plan-1",
            assignments=(
                self.assignment("a1", "researcher", "search", "findings"),
                self.assignment("a2", "writer", "compose", "draft"),
            ),
        )
        result = DelegationCoordinator(self.registry).coordinate(plan)
        self.assertEqual(result.assignment_ids, ("a1", "a2"))

    def test_dependencies_produce_deterministic_topological_order(self):
        plan = DelegationPlan(
            plan_id="plan-2",
            assignments=(
                self.assignment("a2", "writer", "compose", "draft"),
                self.assignment("a1", "researcher", "search", "findings"),
            ),
            dependencies={"a2": ("a1",)},
        )
        result = DelegationCoordinator(self.registry).coordinate(plan)
        self.assertEqual(result.assignment_ids, ("a1", "a2"))

    def test_rejects_duplicate_assignment_identity(self):
        assignment = self.assignment("same", "researcher", "search", "findings")
        with self.assertRaises(DelegationConflictError):
            DelegationPlan(plan_id="plan-3", assignments=(assignment, assignment))

    def test_rejects_dependency_cycle(self):
        assignments = (
            self.assignment("a1", "researcher", "search", "findings"),
            self.assignment("a2", "writer", "compose", "draft"),
        )
        plan = DelegationPlan(
            plan_id="plan-4",
            assignments=assignments,
            dependencies={"a1": ("a2",), "a2": ("a1",)},
        )
        with self.assertRaises(DelegationConflictError):
            plan.ordered_assignment_ids()

    def test_rejects_assignment_outside_registered_worker_bounds(self):
        plan = DelegationPlan(
            plan_id="plan-5",
            assignments=(self.assignment("a1", "researcher", "execute", "findings"),),
        )
        with self.assertRaises(ValueError):
            DelegationCoordinator(self.registry).coordinate(plan)

    def test_serialization_does_not_grant_authority(self):
        plan = DelegationPlan(
            plan_id="plan-6",
            assignments=(self.assignment("a1", "researcher", "search", "findings"),),
        )
        context = plan.to_context()
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["authority_escalation"])

    def test_coordinator_does_not_execute_workers(self):
        plan = DelegationPlan(
            plan_id="plan-7",
            assignments=(self.assignment("a1", "researcher", "search", "findings"),),
        )
        result = DelegationCoordinator(self.registry).coordinate(plan)
        self.assertEqual(result.assignment_ids, ("a1",))


if __name__ == "__main__":
    unittest.main()
