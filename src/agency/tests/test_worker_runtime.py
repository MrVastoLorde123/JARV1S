import unittest

from src.agency.execution_runtime import ExecutionOutcome, ExecutionRuntime
from src.agency.observation_integration import ExecutionObservationContextIntegrator
from src.agency.workforce import WorkerAssignment, WorkerDefinition, WorkerRegistry, WorkerReportStatus
from src.agency.worker_runtime import BoundedWorkerRuntime
from src.context.execution_semantics import ExecutionPreparation, ExecutionPreparationStatus, ExecutionRequest
from src.context.models import ContextPackage
from src.context.working_context import WorkingContext


class FakeAdapter:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return self.outcomes.pop(0)


class MappingResolver:
    def __init__(self, mapping):
        self.mapping = dict(mapping)

    def resolve_capability(self, operation):
        return self.mapping[operation]


class SequenceProvider:
    def __init__(self, preparations):
        self.preparations = list(preparations)

    def next_preparation(self, working_context, previous_observation):
        if not self.preparations:
            return None
        return self.preparations.pop(0)


class WorkerRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.context = WorkingContext(
            request="research a topic",
            context_package=ContextPackage(request="research a topic", items=(), instructions=()),
        )
        self.worker = WorkerDefinition(
            worker_id="researcher",
            name="Research Worker",
            capabilities=("search", "summarize"),
            max_steps=3,
        )
        self.assignment = WorkerAssignment(
            assignment_id="assignment-1",
            worker_id="researcher",
            objective="research a topic",
            allowed_capabilities=("search", "summarize"),
            input_scope=("request",),
            output_scope=("findings",),
            max_steps=2,
        )

    @staticmethod
    def preparation(execution_id, operation):
        request = ExecutionRequest(
            execution_id=execution_id,
            request="research a topic",
            proposal_id=f"proposal-{execution_id}",
            validation_id=f"validation-{execution_id}",
            policy_decision_id=f"policy-{execution_id}",
            confirmation_id=None,
            authorization_id=f"authorization-{execution_id}",
            operation=operation,
            arguments={},
        )
        return ExecutionPreparation(
            request="research a topic",
            execution_id=execution_id,
            status=ExecutionPreparationStatus.READY,
            execution_request=request,
        )

    def runtime(self, adapter, resolver=None):
        registry = WorkerRegistry()
        registry.register(self.worker)
        return BoundedWorkerRuntime(
            registry,
            ExecutionRuntime(adapter),
            ExecutionObservationContextIntegrator(),
            capability_resolver=resolver,
        )

    def test_runs_one_authorized_worker_step(self):
        adapter = FakeAdapter([ExecutionOutcome(success=True, content="result")])
        runtime = self.runtime(adapter)
        result = runtime.run(self.assignment, self.context, self.preparation("exec-1", "search"))
        self.assertEqual(result.report.status, WorkerReportStatus.COMPLETED)
        self.assertEqual(result.steps_executed if hasattr(result, "steps_executed") else len(result.observations), 1)
        self.assertEqual(len(adapter.requests), 1)

    def test_missing_preparation_never_executes(self):
        adapter = FakeAdapter([])
        runtime = self.runtime(adapter)
        result = runtime.run(self.assignment, self.context)
        self.assertEqual(result.report.status, WorkerReportStatus.BLOCKED)
        self.assertEqual(len(adapter.requests), 0)

    def test_initial_operation_is_checked_against_assignment(self):
        adapter = FakeAdapter([ExecutionOutcome(success=True)])
        runtime = self.runtime(adapter)
        with self.assertRaises(ValueError):
            runtime.run(self.assignment, self.context, self.preparation("exec-1", "publish"))
        self.assertEqual(len(adapter.requests), 0)

    def test_provider_never_bypasses_worker_capability_boundary(self):
        first = self.preparation("exec-1", "search")
        second = self.preparation("exec-2", "publish")
        adapter = FakeAdapter([ExecutionOutcome(success=True)])
        provider = SequenceProvider([second])
        runtime = self.runtime(adapter)
        result = runtime.run(self.assignment, self.context, first, provider)
        self.assertEqual(result.report.status, WorkerReportStatus.PARTIAL)
        self.assertEqual(len(adapter.requests), 1)

    def test_operation_can_map_to_capability_without_string_identity(self):
        adapter = FakeAdapter([ExecutionOutcome(success=True)])
        resolver = MappingResolver({"web.search": "search"})
        runtime = self.runtime(adapter, resolver)
        result = runtime.run(self.assignment, self.context, self.preparation("exec-1", "web.search"))
        self.assertEqual(result.report.status, WorkerReportStatus.COMPLETED)

    def test_worker_step_bound_is_never_exceeded(self):
        adapter = FakeAdapter([ExecutionOutcome(success=True), ExecutionOutcome(success=True), ExecutionOutcome(success=True)])
        runtime = self.runtime(adapter)
        first = self.preparation("exec-1", "search")
        second = self.preparation("exec-2", "summarize")
        third = self.preparation("exec-3", "search")
        result = runtime.run(self.assignment, self.context, first, SequenceProvider([second, third]))
        self.assertEqual(len(result.observations), 2)
        self.assertEqual(len(adapter.requests), 2)


if __name__ == "__main__":
    unittest.main()
