import unittest

from src.agency.execution_runtime import ExecutionOutcome, ExecutionObservation, ExecutionStatus
from src.agency.observation_integration import (
    ExecutionObservationContextIntegrator,
    ExecutionObservationStore,
    ObservationConflictError,
)
from src.context.models import OBSERVATION, ContextPackage
from src.context.working_context import WorkingContext


class ObservationIntegrationTests(unittest.TestCase):
    def observation(self, execution_id="execution:1", status=ExecutionStatus.SUCCEEDED):
        outcome = ExecutionOutcome(success=True, content={"value": 42}) if status is ExecutionStatus.SUCCEEDED else None
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
            completed=status.completed,
            succeeded=status.succeeded,
            outcome=outcome,
            error=None if outcome is not None else {"code": "failed"},
            metadata={"source": "test"},
        )

    def context(self):
        return WorkingContext(
            request="inspect file",
            context_package=ContextPackage(
                request="inspect file",
                items=(),
                instructions=(),
            ),
        )

    def test_store_appends_and_retrieves_by_execution_identity(self):
        first = self.observation()
        store = ExecutionObservationStore().append(first)

        self.assertIs(store.get("execution:1"), first)
        self.assertEqual(store.list(), (first,))

    def test_store_rejects_duplicate_execution_identity(self):
        observation = self.observation()
        store = ExecutionObservationStore().append(observation)

        with self.assertRaises(ObservationConflictError):
            store.append(observation)

    def test_context_projection_preserves_execution_identity_and_status(self):
        observation = self.observation()
        item = ExecutionObservationContextIntegrator.to_context_item(observation)

        self.assertEqual(item.source_type, OBSERVATION)
        self.assertEqual(item.provenance["source_id"], "execution:1")
        self.assertEqual(item.provenance["status"], "succeeded")
        self.assertNotIn("authorized", item.provenance)

    def test_context_projection_is_deterministic(self):
        observation = self.observation()

        first = ExecutionObservationContextIntegrator.to_context_item(observation)
        second = ExecutionObservationContextIntegrator.to_context_item(observation)

        self.assertEqual(first.content, second.content)

    def test_integrate_returns_new_working_context_with_observation(self):
        original = self.context()
        observation = self.observation()

        integrator = ExecutionObservationContextIntegrator()
        updated = integrator.integrate(original, [observation])

        self.assertIsNot(updated, original)
        self.assertEqual(len(original.observations), 0)
        self.assertEqual(len(updated.observations), 1)
        self.assertEqual(updated.observations[0].source_type, OBSERVATION)
        self.assertEqual(updated.observations[0].provenance["execution_id"], "execution:1")
        self.assertEqual(updated.metadata["execution_observation_integration"], "m8.3")

    def test_integration_keeps_existing_observations(self):
        original = self.context()
        existing = ExecutionObservationContextIntegrator.to_context_item(self.observation("execution:existing"))
        original = WorkingContext(
            request=original.request,
            context_package=original.context_package,
            observations=(existing,),
        )

        updated = ExecutionObservationContextIntegrator().integrate(
            original,
            [self.observation("execution:new")],
        )

        self.assertEqual(
            [item.provenance["execution_id"] for item in updated.observations],
            ["execution:existing", "execution:new"],
        )

    def test_failed_observation_remains_failure_in_context_projection(self):
        observation = self.observation("execution:failed", ExecutionStatus.FAILED)
        item = ExecutionObservationContextIntegrator.to_context_item(observation)

        self.assertEqual(item.provenance["status"], "failed")
        self.assertIn("failed", item.content)

    def test_not_attempted_observation_remains_not_attempted(self):
        observation = self.observation("execution:blocked", ExecutionStatus.NOT_ATTEMPTED)
        item = ExecutionObservationContextIntegrator.to_context_item(observation)

        self.assertEqual(item.provenance["status"], "not_attempted")
        self.assertIn("not_attempted", item.content)

    def test_integrator_rejects_invalid_working_context(self):
        with self.assertRaises(TypeError):
            ExecutionObservationContextIntegrator().integrate(object())

    def test_integrator_rejects_invalid_observation(self):
        with self.assertRaises(TypeError):
            ExecutionObservationContextIntegrator.to_context_item(object())


if __name__ == "__main__":
    unittest.main()
