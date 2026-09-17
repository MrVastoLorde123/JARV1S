from unittest import TestCase

from src.agency.authorized_execution_admission import create_authorized_execution_admission
from src.agency.authorized_execution_outcome import build_authorized_execution_outcome
from src.agency.authorized_execution_runtime_admission import create_authorized_execution_runtime_admission
from src.agency.authorization_decision import AuthorizationDecision, AuthorizationDisposition
from src.agency.authorization_execution_bridge import create_authorization_execution_bridge
from src.agency.controlled_agency import ControlledAgencyResult
from src.agency.execution_bridge import AgencyExecutionBridgeResult
from src.agency.execution_handoff import create_execution_handoff
from src.agency.work_dispatch import DispatchRequest, WorkDispatcher
from src.agency.work_planning import PlanStepKind, WorkPlanStep, build_work_plan
from src.agency.work_state import WorkRole, WorkStage, WorkState, WorkStatus
from src.agency.workforce import WorkerDefinition, WorkerRegistry
from src.context.authorization_integrity_semantics import AuthorizationIntegrity, AuthorizationIntegrityStatus
from src.context.authorization_semantics import AuthorizationDecision as LegacyAuthorizationDecision, AuthorizationStatus
from src.context.execution_semantics import ExecutionGate
from src.context.working_context import WorkingContext
from unittest.mock import Mock


class _M56Fixture(TestCase):
    def _authorization(self):
        return AuthorizationDecision(
            "auth-56",
            "confirm-result-56",
            "confirmation-56",
            AuthorizationDisposition.GRANTED,
            "explicitly granted",
        )

    def _preparation(self):
        decision = LegacyAuthorizationDecision(
            request="deploy change",
            authorization_id="auth-56",
            proposal_id="proposal-56",
            validation_id="validation-56",
            policy_decision_id="policy-56",
            confirmation_id="confirmation-56",
            status=AuthorizationStatus.AUTHORIZED,
            rationale="approved",
        )
        integrity = AuthorizationIntegrity(
            request="deploy change",
            authorization_id="auth-56",
            proposal_id="proposal-56",
            validation_id="validation-56",
            policy_decision_id="policy-56",
            confirmation_id="confirmation-56",
            status=AuthorizationIntegrityStatus.VALID,
        )
        return ExecutionGate().prepare(decision, integrity, "exec-56", "deploy")

    def _handoff(self):
        work = WorkState(
            work_id="work-56",
            objective="build authorized execution outcome",
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
        return create_execution_handoff(dispatch, self._preparation())

    def _runtime_admission(self):
        preparation = self._preparation()
        bridge = create_authorization_execution_bridge(self._authorization(), preparation)
        admission = create_authorized_execution_admission(bridge, self._handoff())
        agency_result = ControlledAgencyResult(
            observations=(),
            lifecycles=(),
            working_context=Mock(spec=WorkingContext),
            stop_reason="completed",
        )
        execution_result = AgencyExecutionBridgeResult(
            handoff=admission.execution_handoff,
            agency_result=agency_result,
        )
        return create_authorized_execution_runtime_admission(admission, execution_result)


class M56AuthorizedExecutionOutcomeTests(_M56Fixture):
    def test_exact_runtime_result_becomes_m37_outcome_and_verifier_input(self):
        result = build_authorized_execution_outcome(self._runtime_admission())
        self.assertEqual("exec-56", result.execution_id)
        self.assertEqual("deploy change", result.outcome.request)
        self.assertEqual(result.outcome, result.verification_input.outcome)
        self.assertEqual("deploy change", result.verification_input.expected_request)
        self.assertFalse(result.to_context()["verification_performed"])

    def test_mismatched_expected_request_is_rejected(self):
        with self.assertRaises(ValueError):
            build_authorized_execution_outcome(
                self._runtime_admission(),
                expected_request="different request",
            )

    def test_non_runtime_admission_is_rejected(self):
        with self.assertRaises(TypeError):
            build_authorized_execution_outcome(object())

    def test_outcome_bridge_exposes_no_authority_or_execution_controls(self):
        result = build_authorized_execution_outcome(self._runtime_admission())
        payload = result.to_context()
        self.assertFalse(payload["authorization_created"])
        self.assertFalse(payload["execution_requested"])
        self.assertNotIn("authorize", payload)
        self.assertNotIn("execute", payload)
        self.assertNotIn("provider", payload)
