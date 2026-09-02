import unittest

from src.agency.controlled_agency import AgencyStopReason, ControlledAgency
from src.agency.execution_runtime import ExecutionOutcome, ExecutionRuntime
from src.agency.observation_integration import ExecutionObservationContextIntegrator
from src.context.execution_semantics import (
    ExecutionPreparation,
    ExecutionPreparationStatus,
    ExecutionPreparationViolation,
    ExecutionRequest,
)
from src.context.models import ContextPackage
from src.context.working_context import WorkingContext


class FakeAdapter:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return self.outcomes.pop(0)


class SequenceProvider:
    def __init__(self, preparations):
        self.preparations = list(preparations)
        self.calls = []

    def next_preparation(self, working_context, previous_observation):
        self.calls.append((working_context, previous_observation))
        if not self.preparations:
            return None
        return self.preparations.pop(0)


class ControlledAgencyTests(unittest.TestCase):
    def setUp(self):
        self.context = WorkingContext(
            request="run a bounded sequence",
            context_package=ContextPackage(
                request="run a bounded sequence",
                items=(),
                instructions=(),
            ),
        )

    @staticmethod
    def preparation(execution_id):
        request = ExecutionRequest(
            execution_id=execution_id,
            request="run a bounded sequence",
            proposal_id=f"proposal-{execution_id}",
            validation_id=f"validation-{execution_id}",
            policy_decision_id=f"policy-{execution_id}",
            confirmation_id=None,
            authorization_id=f"authorization-{execution_id}",
            operation="test.operation",
            arguments={"value": execution_id},
        )
        return ExecutionPreparation(
            request="run a bounded sequence",
            execution_id=execution_id,
            status=ExecutionPreparationStatus.READY,
            execution_request=request,
        )

    def test_runs_two_independently_authorized_steps_in_order(self):
        first = self.preparation("exec-1")
        second = self.preparation("exec-2")
        provider = SequenceProvider([second])
        adapter = FakeAdapter([
            ExecutionOutcome(success=True, content="one"),
            ExecutionOutcome(success=True, content="two"),
        ])

        result = ControlledAgency(
            ExecutionRuntime(adapter),
            ExecutionObservationContextIntegrator(),
            max_steps=3,
            next_step_provider=provider,
        ).run(self.context, first)

        self.assertEqual(result.stop_reason, AgencyStopReason.COMPLETED)
        self.assertEqual(result.steps_executed, 2)
        self.assertEqual(
            tuple(item.execution_id for item in result.observations),
            ("exec-1", "exec-2"),
        )
        self.assertEqual(
            tuple(item.execution_id for item in adapter.requests),
            ("exec-1", "exec-2"),
        )
        self.assertEqual(len(result.working_context.observations), 2)
        self.assertEqual(len(provider.calls), 2)
        self.assertEqual(provider.calls[0][1].execution_id, "exec-1")
        self.assertEqual(provider.calls[1][1].execution_id, "exec-2")
        self.assertEqual(provider.calls[0][0].observations[-1].provenance["source_id"], "exec-1")
        self.assertEqual(provider.calls[1][0].observations[-1].provenance["source_id"], "exec-2")

    def test_step_limit_prevents_unbounded_agency(self):
        first = self.preparation("exec-1")
        second = self.preparation("exec-2")
        third = self.preparation("exec-3")
        provider = SequenceProvider([second, third])
        adapter = FakeAdapter([
            ExecutionOutcome(success=True),
            ExecutionOutcome(success=True),
            ExecutionOutcome(success=True),
        ])

        result = ControlledAgency(
            ExecutionRuntime(adapter),
            ExecutionObservationContextIntegrator(),
            max_steps=2,
            next_step_provider=provider,
        ).run(self.context, first)

        self.assertEqual(result.stop_reason, AgencyStopReason.STEP_LIMIT_REACHED)
        self.assertEqual(result.steps_executed, 2)
        self.assertEqual(len(adapter.requests), 2)

    def test_blocked_next_preparation_is_never_executed(self):
        first = self.preparation("exec-1")
        blocked = ExecutionPreparation(
            request="run a bounded sequence",
            execution_id="exec-2",
            status=ExecutionPreparationStatus.BLOCKED,
            violations=(ExecutionPreparationViolation("blocked", "not authorized"),),
        )
        provider = SequenceProvider([blocked])
        adapter = FakeAdapter([ExecutionOutcome(success=True)])

        result = ControlledAgency(
            ExecutionRuntime(adapter),
            ExecutionObservationContextIntegrator(),
            max_steps=3,
            next_step_provider=provider,
        ).run(self.context, first)

        self.assertEqual(result.stop_reason, AgencyStopReason.NEXT_PREPARATION_BLOCKED)
        self.assertEqual(result.steps_executed, 1)
        self.assertEqual(len(adapter.requests), 1)

    def test_duplicate_execution_identity_is_rejected(self):
        first = self.preparation("exec-1")
        duplicate = self.preparation("exec-1")
        provider = SequenceProvider([duplicate])
        adapter = FakeAdapter([ExecutionOutcome(success=True)])

        result = ControlledAgency(
            ExecutionRuntime(adapter),
            ExecutionObservationContextIntegrator(),
            max_steps=3,
            next_step_provider=provider,
        ).run(self.context, first)

        self.assertEqual(result.stop_reason, AgencyStopReason.DUPLICATE_EXECUTION_ID)
        self.assertEqual(result.steps_executed, 1)
        self.assertEqual(len(adapter.requests), 1)

    def test_failed_step_stops_without_implicit_retry_when_no_provider_exists(self):
        first = self.preparation("exec-1")
        adapter = FakeAdapter([
            ExecutionOutcome(
                success=False,
                error={"code": "failed", "message": "test failure"},
            )
        ])

        result = ControlledAgency(
            ExecutionRuntime(adapter),
            ExecutionObservationContextIntegrator(),
            max_steps=3,
        ).run(self.context, first)

        self.assertEqual(result.stop_reason, AgencyStopReason.EXECUTION_FAILED)
        self.assertEqual(result.steps_executed, 1)
        self.assertFalse(result.succeeded)

    def test_non_preparation_from_step_provider_cannot_bypass_boundary(self):
        first = self.preparation("exec-1")

        class InvalidProvider:
            def next_preparation(self, working_context, previous_observation):
                return object()

        adapter = FakeAdapter([ExecutionOutcome(success=True)])
        result = ControlledAgency(
            ExecutionRuntime(adapter),
            ExecutionObservationContextIntegrator(),
            max_steps=3,
            next_step_provider=InvalidProvider(),
        ).run(self.context, first)

        self.assertEqual(result.stop_reason, AgencyStopReason.INVALID_PREPARATION)
        self.assertEqual(result.steps_executed, 1)
        self.assertEqual(len(adapter.requests), 1)


if __name__ == "__main__":
    unittest.main()
