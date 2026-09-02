import unittest

from src.agency.execution_lifecycle import (
    ContinuationRequest,
    ExecutionLifecycle,
    ExecutionLifecycleStatus,
)
from src.agency.execution_runtime import ExecutionObservation, ExecutionOutcome, ExecutionStatus


class ExecutionLifecycleTests(unittest.TestCase):
    def observation(self, execution_id="execution:1", status=ExecutionStatus.SUCCEEDED):
        success = status is ExecutionStatus.SUCCEEDED
        return ExecutionObservation(
            execution_id=execution_id,
            request="inspect file",
            proposal_id="proposal:1",
            validation_id="validation:1",
            policy_decision_id="policy:1",
            confirmation_id=None,
            authorization_id="authorization:1",
            operation="inspect_file",
            status=status,
            attempted=status is not ExecutionStatus.NOT_ATTEMPTED,
            completed=status in {ExecutionStatus.SUCCEEDED, ExecutionStatus.FAILED},
            succeeded=success,
            outcome=ExecutionOutcome(success=True, content={"value": 42}) if success else None,
            error=None if success else {"code": "failed", "message": "execution failed"},
        )

    def test_starts_pending_with_stable_identity(self):
        lifecycle = ExecutionLifecycle.start("execution:1")
        self.assertEqual(lifecycle.status, ExecutionLifecycleStatus.PENDING)
        self.assertEqual(lifecycle.execution_id, "execution:1")
        self.assertFalse(lifecycle.terminal)

    def test_pending_transitions_to_running_immutably(self):
        pending = ExecutionLifecycle.start("execution:1")
        running = pending.start_running()
        self.assertIsNot(pending, running)
        self.assertEqual(pending.status, ExecutionLifecycleStatus.PENDING)
        self.assertEqual(running.status, ExecutionLifecycleStatus.RUNNING)

    def test_success_observation_completes_lifecycle(self):
        lifecycle = ExecutionLifecycle.start("execution:1").start_running()
        observed = self.observation()
        completed = lifecycle.apply_observation(observed)
        self.assertEqual(completed.status, ExecutionLifecycleStatus.SUCCEEDED)
        self.assertTrue(completed.terminal)
        self.assertIs(completed.observation, observed)

    def test_failed_observation_completes_as_failed(self):
        lifecycle = ExecutionLifecycle.start("execution:1").start_running()
        failed = lifecycle.apply_observation(self.observation(status=ExecutionStatus.FAILED))
        self.assertEqual(failed.status, ExecutionLifecycleStatus.FAILED)
        self.assertTrue(failed.terminal)
        self.assertFalse(failed.observation.succeeded)

    def test_not_attempted_observation_becomes_blocked_not_success(self):
        lifecycle = ExecutionLifecycle.start("execution:1").start_running()
        blocked = lifecycle.apply_observation(self.observation(status=ExecutionStatus.NOT_ATTEMPTED))
        self.assertEqual(blocked.status, ExecutionLifecycleStatus.BLOCKED)
        self.assertTrue(blocked.terminal)
        self.assertFalse(blocked.observation.succeeded)

    def test_mismatched_observation_identity_is_rejected(self):
        lifecycle = ExecutionLifecycle.start("execution:1").start_running()
        with self.assertRaises(ValueError):
            lifecycle.apply_observation(self.observation("execution:2"))

    def test_continuation_request_is_explicit_and_identity_bound(self):
        lifecycle = ExecutionLifecycle.start("execution:1").start_running()
        continued = lifecycle.request_continuation("await external result")
        self.assertEqual(continued.status, ExecutionLifecycleStatus.CONTINUATION_REQUIRED)
        self.assertTrue(continued.may_continue)
        self.assertIsInstance(continued.continuation, ContinuationRequest)
        self.assertEqual(continued.continuation.execution_id, "execution:1")

    def test_continuation_does_not_appear_in_terminal_lifecycle(self):
        lifecycle = ExecutionLifecycle.start("execution:1").start_running()
        completed = lifecycle.apply_observation(self.observation())
        with self.assertRaises(ValueError):
            completed.request_continuation("do more")

    def test_consuming_continuation_returns_to_pending_without_authorizing(self):
        lifecycle = ExecutionLifecycle.start("execution:1").start_running()
        pending_again = lifecycle.request_continuation("await external result").consume_continuation()
        self.assertEqual(pending_again.status, ExecutionLifecycleStatus.PENDING)
        self.assertIsNone(pending_again.continuation)
        self.assertIsNone(pending_again.observation)
        self.assertEqual(pending_again.execution_id, "execution:1")

    def test_terminal_lifecycle_cannot_be_cancelled(self):
        lifecycle = ExecutionLifecycle.start("execution:1").start_running()
        completed = lifecycle.apply_observation(self.observation())
        with self.assertRaises(ValueError):
            completed.cancel()

    def test_context_projection_contains_no_authority_grant(self):
        lifecycle = ExecutionLifecycle.start("execution:1").start_running().request_continuation("await result")
        context = lifecycle.to_context()
        self.assertEqual(context["status"], "continuation_required")
        self.assertTrue(context["may_continue"])
        self.assertNotIn("authorized", context)
        self.assertNotIn("authorization_granted", context)
        self.assertNotIn("permission", context)


if __name__ == "__main__":
    unittest.main()
