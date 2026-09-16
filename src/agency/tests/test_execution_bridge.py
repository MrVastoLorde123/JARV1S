from unittest import TestCase

from src.agency.controlled_agency import ControlledAgency
from src.agency.execution_bridge import AgencyExecutionBridgeResult, run_execution_handoff
from src.agency.execution_handoff import create_execution_handoff
from src.agency.execution_runtime import ExecutionOutcome, ExecutionRuntime, ExecutionStatus
from src.agency.observation_integration import ExecutionObservationContextIntegrator
from src.agency.work_dispatch import DispatchRequest, WorkDispatcher
from src.agency.work_planning import PlanStepKind, WorkPlanStep, build_work_plan
from src.agency.work_state import WorkRole, WorkStage, WorkState, WorkStatus
from src.agency.workforce import WorkerDefinition, WorkerRegistry
from src.context.authorization_integrity_semantics import AuthorizationIntegrity, AuthorizationIntegrityStatus
from src.context.authorization_semantics import AuthorizationDecision, AuthorizationStatus
from src.context.execution_semantics import ExecutionGate
from src.context.models import ContextPackage
from src.context.working_context import WorkingContext


class _SuccessfulAdapter:
    def execute(self, request):
        return ExecutionOutcome(success=True, content={"operation": request.operation})


class M36ExecutionBridgeTests(TestCase):
    def _handoff(self):
        work = WorkState(
            work_id="work-36",
            objective="bridge bounded execution",
            stage=WorkStage.EXECUTING,
            status=WorkStatus.ACTIVE,
            role=WorkRole.TECHNICAL_LEAD,
        )
        plan = build_work_plan(
            work,
            (WorkPlanStep("step-1", "deploy change", PlanStepKind.IMPLEMENT, WorkRole.TECHNICAL_LEAD),),
        )
        registry = WorkerRegistry()
        registry.register(WorkerDefinition("worker-1", "Worker", ("deploy",), 2))
        dispatch = WorkDispatcher(registry).dispatch(
            DispatchRequest(plan, "step-1", "worker-1", input_scope=("repo",), output_scope=("result",))
        )
        decision = AuthorizationDecision(
            request="deploy change",
            authorization_id="auth-1",
            proposal_id="proposal-1",
            validation_id="validation-1",
            policy_decision_id="policy-1",
            confirmation_id=None,
            status=AuthorizationStatus.AUTHORIZED,
            rationale="policy allows the consequence without a confirmation requirement.",
        )
        integrity = AuthorizationIntegrity(
            request="deploy change",
            authorization_id="auth-1",
            proposal_id="proposal-1",
            validation_id="validation-1",
            policy_decision_id="policy-1",
            confirmation_id=None,
            status=AuthorizationIntegrityStatus.VALID,
        )
        preparation = ExecutionGate().prepare(decision, integrity, "exec-1", "deploy")
        return create_execution_handoff(dispatch, preparation)

    def _agency(self):
        return ControlledAgency(
            ExecutionRuntime(_SuccessfulAdapter()),
            ExecutionObservationContextIntegrator(),
            max_steps=1,
        )

    def _context(self):
        return WorkingContext(
            request="deploy change",
            context_package=ContextPackage(request="deploy change", items=(), instructions=()),
        )

    def test_bridge_runs_exact_ready_preparation_through_existing_agency(self):
        result = run_execution_handoff(self._agency(), self._handoff(), self._context())
        self.assertIsInstance(result, AgencyExecutionBridgeResult)
        self.assertEqual("exec-1", result.execution_id)
        self.assertEqual(1, result.steps_executed)
        self.assertTrue(result.succeeded)
        self.assertEqual(ExecutionStatus.SUCCEEDED, result.agency_result.observations[0].status)

    def test_bridge_preserves_authorization_boundary(self):
        result = run_execution_handoff(self._agency(), self._handoff(), self._context())
        context = result.to_context()
        self.assertFalse(context["authorization_created"])
        self.assertEqual("exec-1", context["execution_id"])
        self.assertNotIn("authorize", context)

    def test_invalid_inputs_are_rejected(self):
        handoff = self._handoff()
        context = self._context()
        with self.assertRaises(TypeError):
            run_execution_handoff(object(), handoff, context)
        with self.assertRaises(TypeError):
            run_execution_handoff(self._agency(), object(), context)
        with self.assertRaises(TypeError):
            run_execution_handoff(self._agency(), handoff, object())
