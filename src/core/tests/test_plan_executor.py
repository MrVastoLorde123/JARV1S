import unittest

from src.core.execution_executor_models import (
    PlanExecutionStatus,
    StepExecutionStatus,
)

from src.core.execution_plan_models import (
    ExecutionPlan,
    PlanStatus,
    PlanStep,
    StepStatus,
)

from src.core.execution_policy_models import (
    ExecutionPolicyResult,
    PolicyDecision,
)

from src.core.plan_executor import (
    PlanExecutor,
)


class PlanExecutorTests(
    unittest.TestCase
):

    def setUp(
        self,
    ):
        self.calls = []

        def test_handler(step):
            self.calls.append(
                step.step_id
            )

            return {
                "step_id": step.step_id,
                "executed": True,
            }

        self.handler = test_handler

        self.executor = PlanExecutor(
            {
                "TEST": self.handler,
            }
        )

    def _step(
        self,
        step_id="step-1",
        action="TEST",
        order=0,
        depends_on=(),
    ):
        return PlanStep(
            step_id=step_id,
            description="Test step.",
            action=action,
            order=order,
            depends_on=depends_on,
            status=StepStatus.READY,
        )

    def _plan(
        self,
        *steps,
    ):
        return ExecutionPlan(
            plan_id="plan-1",
            task_description="Test plan.",
            steps=tuple(steps),
            status=PlanStatus.READY,
        )

    def _policy(
        self,
        plan,
        decision=PolicyDecision.ALLOW,
    ):
        return ExecutionPolicyResult(
            decision=decision,
            plan=plan,
        )

    def test_handler_can_be_registered(
        self,
    ):
        executor = PlanExecutor()

        executor.register_handler(
            "TEST",
            self.handler,
        )

        self.assertTrue(
            executor.has_handler(
                "TEST"
            )
        )

    def test_handler_names_are_case_insensitive(
        self,
    ):
        executor = PlanExecutor()

        executor.register_handler(
            "  test  ",
            self.handler,
        )

        self.assertTrue(
            executor.has_handler(
                "TEST"
            )
        )

    def test_invalid_action_is_rejected(
        self,
    ):
        with self.assertRaises(
            ValueError
        ):
            self.executor.register_handler(
                "   ",
                self.handler,
            )

    def test_non_callable_handler_is_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            self.executor.register_handler(
                "TEST",
                "not callable",
            )

    def test_plan_is_executed(
        self,
    ):
        plan = self._plan(
            self._step()
        )

        result = self.executor.execute(
            plan,
            self._policy(plan),
        )

        self.assertEqual(
            result.status,
            PlanExecutionStatus.COMPLETED,
        )

        self.assertEqual(
            self.calls,
            ["step-1"],
        )

    def test_handler_output_is_preserved(
        self,
    ):
        plan = self._plan(
            self._step()
        )

        result = self.executor.execute(
            plan,
            self._policy(plan),
        )

        self.assertEqual(
            result.steps[0].output,
            {
                "step_id": "step-1",
                "executed": True,
            },
        )

    def test_multiple_steps_execute_in_order(
        self,
    ):
        plan = self._plan(
            self._step(
                step_id="step-1",
                order=0,
            ),
            self._step(
                step_id="step-2",
                order=1,
            ),
            self._step(
                step_id="step-3",
                order=2,
            ),
        )

        result = self.executor.execute(
            plan,
            self._policy(plan),
        )

        self.assertTrue(
            result.success
        )

        self.assertEqual(
            self.calls,
            [
                "step-1",
                "step-2",
                "step-3",
            ],
        )

    def test_dependencies_are_enforced(
        self,
    ):
        plan = self._plan(
            self._step(
                step_id="step-1",
                order=0,
            ),
            self._step(
                step_id="step-2",
                order=1,
                depends_on=("step-1",),
            ),
        )

        result = self.executor.execute(
            plan,
            self._policy(plan),
        )

        self.assertTrue(
            result.success
        )

        self.assertEqual(
            self.calls,
            [
                "step-1",
                "step-2",
            ],
        )

    def test_missing_handler_fails_execution(
        self,
    ):
        plan = self._plan(
            self._step(
                action="UNKNOWN",
            )
        )

        result = self.executor.execute(
            plan,
            self._policy(plan),
        )

        self.assertEqual(
            result.status,
            PlanExecutionStatus.FAILED,
        )

        self.assertEqual(
            result.steps[0].status,
            StepExecutionStatus.FAILED,
        )

        self.assertIn(
            "No handler is registered",
            result.steps[0].error,
        )

    def test_handler_exception_becomes_failed_result(
        self,
    ):
        def failing_handler(step):
            raise RuntimeError(
                "handler failed"
            )

        executor = PlanExecutor(
            {
                "TEST": failing_handler,
            }
        )

        plan = self._plan(
            self._step()
        )

        result = executor.execute(
            plan,
            self._policy(plan),
        )

        self.assertEqual(
            result.status,
            PlanExecutionStatus.FAILED,
        )

        self.assertEqual(
            result.steps[0].status,
            StepExecutionStatus.FAILED,
        )

        self.assertEqual(
            result.steps[0].error,
            "handler failed",
        )

    def test_execution_stops_after_failed_step(
        self,
    ):
        def handler(step):
            self.calls.append(
                step.step_id
            )

            if step.step_id == "step-1":
                raise RuntimeError(
                    "first failed"
                )

            return "done"

        executor = PlanExecutor(
            {
                "TEST": handler,
            }
        )

        plan = self._plan(
            self._step(
                step_id="step-1",
                order=0,
            ),
            self._step(
                step_id="step-2",
                order=1,
            ),
        )

        result = executor.execute(
            plan,
            self._policy(plan),
        )

        self.assertEqual(
            result.status,
            PlanExecutionStatus.FAILED,
        )

        self.assertEqual(
            self.calls,
            ["step-1"],
        )

    def test_deny_blocks_execution(
        self,
    ):
        plan = self._plan(
            self._step()
        )

        result = self.executor.execute(
            plan,
            self._policy(
                plan,
                PolicyDecision.DENY,
            ),
        )

        self.assertEqual(
            result.status,
            PlanExecutionStatus.BLOCKED,
        )

        self.assertEqual(
            self.calls,
            [],
        )

    def test_confirmation_requirement_blocks_execution(
        self,
    ):
        plan = self._plan(
            self._step()
        )

        result = self.executor.execute(
            plan,
            self._policy(
                plan,
                PolicyDecision.REQUIRE_CONFIRMATION,
            ),
        )

        self.assertEqual(
            result.status,
            PlanExecutionStatus.BLOCKED,
        )

        self.assertEqual(
            self.calls,
            [],
        )

    def test_policy_result_must_match_plan(
        self,
    ):
        plan = self._plan(
            self._step()
        )

        other_plan = ExecutionPlan(
            plan_id="other-plan",
            task_description="Other.",
            steps=(
                self._step(),
            ),
        )

        policy = self._policy(
            other_plan
        )

        with self.assertRaises(
            ValueError
        ):
            self.executor.execute(
                plan,
                policy,
            )

    def test_non_plan_is_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            self.executor.execute(
                "not a plan",
                "not a policy",
            )

    def test_non_policy_result_is_rejected(
        self,
    ):
        plan = self._plan(
            self._step()
        )

        with self.assertRaises(
            TypeError
        ):
            self.executor.execute(
                plan,
                "not a policy",
            )

    def test_empty_plan_fails_execution(
        self,
    ):
        plan = self._plan()

        result = self.executor.execute(
            plan,
            self._policy(plan),
        )

        self.assertEqual(
            result.status,
            PlanExecutionStatus.FAILED,
        )

        self.assertEqual(
            self.calls,
            [],
        )

    def test_executor_does_not_modify_plan(
        self,
    ):
        plan = self._plan(
            self._step()
        )

        before = plan

        self.executor.execute(
            plan,
            self._policy(plan),
        )

        self.assertEqual(
            plan,
            before,
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )