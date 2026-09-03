import unittest

from src.agency.worker_reporting import (
    WorkerReportConflictError,
    WorkerReportIntegrator,
    WorkerReportStore,
)
from src.agency.workforce import WorkerAssignment, WorkerReport, WorkerReportStatus
from src.context.models import ContextPackage
from src.context.working_context import WorkingContext


class WorkerReportingTests(unittest.TestCase):
    def setUp(self):
        self.assignment = WorkerAssignment(
            assignment_id="assignment-1",
            worker_id="researcher",
            objective="research a topic",
            allowed_capabilities=("search", "summarize"),
            input_scope=("request",),
            output_scope=("findings", "summary"),
            max_steps=3,
        )
        self.context = WorkingContext(
            request="research a topic",
            context_package=ContextPackage(
                request="research a topic",
                items=(),
                instructions=(),
            ),
        )

    @staticmethod
    def report(**overrides):
        values = {
            "assignment_id": "assignment-1",
            "worker_id": "researcher",
            "status": WorkerReportStatus.COMPLETED,
            "outputs": {"findings": ("a", "b")},
            "summary": "completed",
        }
        values.update(overrides)
        return WorkerReport(**values)

    def test_integrates_report_as_observation_without_authority_or_truth(self):
        result = WorkerReportIntegrator().integrate(
            self.context, self.assignment, self.report()
        )
        self.assertEqual(len(result.observations), 1)
        item = result.observations[0]
        self.assertEqual(item.provenance["worker_id"], "researcher")
        self.assertEqual(item.provenance["assignment_id"], "assignment-1")
        self.assertIn("\"authority_granted\": false", item.content)
        self.assertIn("\"truth_guaranteed\": false", item.content)
        self.assertEqual(result.metadata["worker_report_integration"], "m9.4")

    def test_report_worker_identity_must_match_assignment(self):
        with self.assertRaises(ValueError):
            WorkerReportIntegrator().integrate(
                self.context,
                self.assignment,
                self.report(worker_id="coder"),
            )

    def test_report_output_scope_must_match_assignment(self):
        with self.assertRaises(ValueError):
            WorkerReportIntegrator().integrate(
                self.context,
                self.assignment,
                self.report(outputs={"secret": "nope"}),
            )

    def test_store_rejects_duplicate_worker_assignment_identity(self):
        store = WorkerReportStore()
        store = store.append(self.report())
        with self.assertRaises(WorkerReportConflictError):
            store.append(self.report(status=WorkerReportStatus.PARTIAL))

    def test_store_is_immutable(self):
        store = WorkerReportStore()
        first = self.report()
        second = self.report(assignment_id="assignment-2")
        updated = store.append(first)
        self.assertEqual(store.list(), ())
        self.assertEqual(updated.list(), (first,))
        self.assertEqual(updated.append(second).list(), (first, second))

    def test_context_projection_is_deterministic_and_traceable(self):
        item = WorkerReportIntegrator.to_context_item(self.assignment, self.report())
        self.assertEqual(
            item.provenance["source_id"],
            "worker:researcher:assignment:assignment-1",
        )
        self.assertEqual(item.provenance["observation_type"], "worker_report")
        self.assertEqual(item.privacy_level, "PRIVATE")


if __name__ == "__main__":
    unittest.main()
