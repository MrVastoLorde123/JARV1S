import unittest

from src.agency.delegation import DelegationPlan
from src.agency.workforce import WorkerAssignment
from src.agency.workforce_recovery import (
    WorkerRecoveryAssessment,
    WorkerRecoveryState,
    WorkerRecoveryStore,
    WorkforceRecoveryConflictError,
    WorkforceRecoveryPlanner,
)


class WorkforceRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.assignment = WorkerAssignment(
            assignment_id="a1", worker_id="researcher", objective="research",
            allowed_capabilities=("search",), input_scope=("request",),
            output_scope=("findings",), max_steps=2,
        )
        self.plan = DelegationPlan(plan_id="plan-1", assignments=(self.assignment,))

    def assessment(self, *, state=WorkerRecoveryState.RETRYABLE, attempt_count=0, retryable=False):
        return WorkerRecoveryAssessment(
            plan_id="plan-1", assignment_id="a1", worker_id="researcher", state=state,
            attempt_count=attempt_count, retryable=retryable, evidence={"source": "test"},
            execution_id="exec-1", result_id="result-1",
        )

    def test_assessment_preserves_worker_assignment_and_execution_identity(self):
        assessment = self.assessment()
        self.assertEqual((assessment.plan_id, assessment.assignment_id, assessment.worker_id), ("plan-1", "a1", "researcher"))
        self.assertEqual((assessment.execution_id, assessment.result_id), ("exec-1", "result-1"))

    def test_retry_requires_explicit_bound_and_fresh_authorization(self):
        assessment = self.assessment(retryable=True)
        intent = WorkforceRecoveryPlanner(default_max_retries=2).plan_retry(assessment)
        self.assertTrue(intent.should_retry)
        self.assertTrue(intent.fresh_authorization_required)
        self.assertFalse(intent.to_context()["authorization_granted"])

    def test_retry_bound_is_hard(self):
        assessment = self.assessment(retryable=True, attempt_count=2)
        intent = WorkforceRecoveryPlanner(default_max_retries=2).plan_retry(assessment)
        self.assertFalse(intent.should_retry)

    def test_non_retryable_assessment_cannot_request_retries(self):
        assessment = self.assessment(state=WorkerRecoveryState.BLOCKED, retryable=False)
        with self.assertRaises(ValueError):
            WorkforceRecoveryPlanner().plan_retry(assessment, max_retries=1)

    def test_store_is_idempotent_for_identical_assessment(self):
        store = WorkerRecoveryStore()
        assessment = self.assessment()
        self.assertIs(store.record(assessment), assessment)
        self.assertIs(store.record(assessment), assessment)
        self.assertEqual(store.snapshot(), (assessment,))

    def test_store_rejects_conflicting_assessment_identity(self):
        store = WorkerRecoveryStore()
        store.record(self.assessment())
        with self.assertRaises(WorkforceRecoveryConflictError):
            store.record(self.assessment(state=WorkerRecoveryState.TERMINAL))

    def test_recovery_cannot_bypass_dependencies(self):
        second = WorkerAssignment(
            assignment_id="a2", worker_id="researcher", objective="follow up",
            allowed_capabilities=("search",), input_scope=("findings",),
            output_scope=("followup",), max_steps=1,
        )
        plan = DelegationPlan(plan_id="plan-2", assignments=(self.assignment, second), dependencies={"a2": ("a1",)})
        planner = WorkforceRecoveryPlanner()
        with self.assertRaises(WorkforceRecoveryConflictError):
            planner.ensure_dependency_ready(plan, "a2", set())
        planner.ensure_dependency_ready(plan, "a2", {"a1"})

    def test_serialization_does_not_grant_authority_or_global_context(self):
        context = self.assessment().to_context()
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["capability_escalation"])
        self.assertFalse(context["global_context_access"])


if __name__ == "__main__":
    unittest.main()
