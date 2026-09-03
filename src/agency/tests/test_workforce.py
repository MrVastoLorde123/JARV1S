import unittest

from src.agency.workforce import (
    WorkerAssignment,
    WorkerDefinition,
    WorkerRegistry,
    WorkerReport,
    WorkerReportStatus,
)


class WorkerContractTests(unittest.TestCase):
    def worker(self):
        return WorkerDefinition(
            worker_id="researcher",
            name="Research Worker",
            capabilities=("search", "summarize"),
            max_steps=5,
        )

    def assignment(self, **overrides):
        values = {
            "assignment_id": "assignment-1",
            "worker_id": "researcher",
            "objective": "research a topic",
            "allowed_capabilities": ("search",),
            "input_scope": ("request",),
            "output_scope": ("findings",),
            "max_steps": 3,
        }
        values.update(overrides)
        return WorkerAssignment(**values)

    def test_worker_accepts_assignment_within_bounds(self):
        self.assertTrue(self.worker().accepts(self.assignment()))

    def test_worker_rejects_capability_escalation(self):
        assignment = self.assignment(allowed_capabilities=("search", "summarize", "execute"))
        with self.assertRaises(ValueError):
            self.worker().accepts(assignment)

    def test_worker_rejects_step_bound_escalation(self):
        assignment = self.assignment(max_steps=6)
        self.assertFalse(self.worker().accepts(assignment))

    def test_registry_rejects_duplicate_worker_identity(self):
        registry = WorkerRegistry()
        registry.register(self.worker())
        with self.assertRaises(ValueError):
            registry.register(self.worker())

    def test_registry_validates_assignment_against_registered_worker(self):
        registry = WorkerRegistry()
        registry.register(self.worker())
        resolved = registry.validate_assignment(self.assignment())
        self.assertEqual(resolved.worker_id, "researcher")

    def test_registry_rejects_unknown_worker(self):
        registry = WorkerRegistry()
        with self.assertRaises(KeyError):
            registry.validate_assignment(self.assignment(worker_id="missing"))

    def test_assignment_serialization_does_not_grant_authority(self):
        context = self.assignment().to_context()
        self.assertFalse(context["authorization_granted"])
        self.assertEqual(context["assignment_id"], "assignment-1")

    def test_report_preserves_worker_and_assignment_identity(self):
        report = WorkerReport(
            assignment_id="assignment-1",
            worker_id="researcher",
            status=WorkerReportStatus.COMPLETED,
            outputs={"findings": ("a", "b")},
            summary="completed bounded work",
        )
        context = report.to_context()
        self.assertEqual(context["assignment_id"], "assignment-1")
        self.assertEqual(context["worker_id"], "researcher")
        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["truth_guaranteed"])

    def test_assignment_forbids_authority_and_execution_metadata(self):
        with self.assertRaises(ValueError):
            self.assignment(metadata={"authorization": "granted"})


if __name__ == "__main__":
    unittest.main()
