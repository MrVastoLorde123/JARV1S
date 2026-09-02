import unittest

from src.agency.execution_runtime import (
    ExecutionObservation,
    ExecutionOutcome,
    ExecutionStatus,
)
from src.agency.reliability import (
    RecoveryAction,
    RecoveryPlanner,
    ReliabilityClass,
    ReliabilityClassifier,
    ReliabilitySignal,
)


class ReliabilityTests(unittest.TestCase):
    @staticmethod
    def observation(
        status=ExecutionStatus.SUCCEEDED,
        execution_id="exec-1",
    ):
        outcome = None
        error = None
        attempted = status is not ExecutionStatus.NOT_ATTEMPTED
        completed = status in {ExecutionStatus.SUCCEEDED, ExecutionStatus.FAILED}
        succeeded = status is ExecutionStatus.SUCCEEDED

        if status is ExecutionStatus.SUCCEEDED:
            outcome = ExecutionOutcome(success=True, content="ok")
        elif status is ExecutionStatus.FAILED:
            outcome = ExecutionOutcome(
                success=False,
                error={"code": "failed", "message": "boom"},
            )
        elif status is ExecutionStatus.NOT_ATTEMPTED:
            error = {"code": "blocked", "message": "not attempted"}

        return ExecutionObservation(
            execution_id=execution_id,
            request="do the operation",
            proposal_id="proposal-1" if attempted else None,
            validation_id="validation-1" if attempted else None,
            policy_decision_id="policy-1" if attempted else None,
            confirmation_id=None,
            authorization_id="authorization-1" if attempted else None,
            operation="test.operation" if attempted else None,
            status=status,
            attempted=attempted,
            completed=completed,
            succeeded=succeeded,
            outcome=outcome,
            error=error,
        )

    def test_success_is_healthy_with_no_recovery(self):
        assessment = ReliabilityClassifier().assess(self.observation())
        decision = RecoveryPlanner().plan(assessment)

        self.assertEqual(assessment.classification, ReliabilityClass.HEALTHY)
        self.assertEqual(decision.request.action, RecoveryAction.NONE)

    def test_failed_execution_is_terminal_without_explicit_retryable_signal(self):
        assessment = ReliabilityClassifier().assess(
            self.observation(ExecutionStatus.FAILED)
        )

        self.assertEqual(assessment.classification, ReliabilityClass.FAILED_TERMINAL)

    def test_failed_execution_requires_explicit_retryable_signal(self):
        assessment = ReliabilityClassifier().assess(
            self.observation(ExecutionStatus.FAILED),
            ReliabilitySignal(retryable_failure=True),
        )

        self.assertEqual(assessment.classification, ReliabilityClass.FAILED_RETRYABLE)

    def test_retryable_failure_requests_fresh_authorization(self):
        assessment = ReliabilityClassifier().assess(
            self.observation(ExecutionStatus.FAILED),
            ReliabilitySignal(retryable_failure=True),
        )
        decision = RecoveryPlanner().plan(assessment, recovery_count=0)

        self.assertEqual(
            decision.request.action,
            RecoveryAction.REQUEST_FRESH_AUTHORIZATION,
        )
        self.assertTrue(decision.request.metadata["authority_required_for_new_action"])

    def test_recovery_budget_exhaustion_stops(self):
        assessment = ReliabilityClassifier().assess(
            self.observation(ExecutionStatus.FAILED),
            ReliabilitySignal(retryable_failure=True),
        )
        decision = RecoveryPlanner(max_recovery_requests=2).plan(
            assessment,
            recovery_count=2,
        )

        self.assertEqual(decision.request.action, RecoveryAction.STOP)

    def test_blocked_execution_stops(self):
        observation = self.observation(ExecutionStatus.NOT_ATTEMPTED)
        assessment = ReliabilityClassifier().assess(observation)
        decision = RecoveryPlanner().plan(assessment)

        self.assertEqual(assessment.classification, ReliabilityClass.BLOCKED)
        self.assertEqual(decision.request.action, RecoveryAction.STOP)

    def test_interruption_requires_reconciliation(self):
        assessment = ReliabilityClassifier().assess(
            self.observation(ExecutionStatus.FAILED),
            ReliabilitySignal(interrupted=True, reason="operator stopped execution"),
        )
        decision = RecoveryPlanner().plan(assessment)

        self.assertEqual(assessment.classification, ReliabilityClass.INTERRUPTED)
        self.assertEqual(decision.request.action, RecoveryAction.RECONCILE)

    def test_partial_completion_requires_reconciliation(self):
        assessment = ReliabilityClassifier().assess(
            self.observation(ExecutionStatus.SUCCEEDED),
            ReliabilitySignal(partial_completion=True),
        )
        decision = RecoveryPlanner().plan(assessment)

        self.assertEqual(assessment.classification, ReliabilityClass.PARTIAL_COMPLETION)
        self.assertEqual(decision.request.action, RecoveryAction.RECONCILE)

    def test_explicit_reconciliation_has_priority(self):
        assessment = ReliabilityClassifier().assess(
            self.observation(ExecutionStatus.FAILED),
            ReliabilitySignal(
                requires_reconciliation=True,
                retryable_failure=True,
            ),
        )

        self.assertEqual(
            assessment.classification,
            ReliabilityClass.REQUIRES_RECONCILIATION,
        )

    def test_recovery_request_never_grants_authorization(self):
        assessment = ReliabilityClassifier().assess(
            self.observation(ExecutionStatus.FAILED),
            ReliabilitySignal(retryable_failure=True),
        )
        decision = RecoveryPlanner().plan(assessment)
        context = decision.request.to_context()

        self.assertFalse(context["authorization_granted"])
        self.assertEqual(
            decision.request.action,
            RecoveryAction.REQUEST_FRESH_AUTHORIZATION,
        )

    def test_execution_identity_is_preserved(self):
        assessment = ReliabilityClassifier().assess(
            self.observation(ExecutionStatus.FAILED, execution_id="exec-99"),
            ReliabilitySignal(retryable_failure=True),
        )
        decision = RecoveryPlanner().plan(assessment)

        self.assertEqual(assessment.execution_id, "exec-99")
        self.assertEqual(decision.request.execution_id, "exec-99")


if __name__ == "__main__":
    unittest.main()
