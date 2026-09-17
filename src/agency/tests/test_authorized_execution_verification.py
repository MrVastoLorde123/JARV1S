from unittest import TestCase
from unittest.mock import Mock

from src.agency.authorized_execution_admission import create_authorized_execution_admission
from src.agency.authorized_execution_outcome import build_authorized_execution_outcome
from src.agency.authorized_execution_runtime_admission import create_authorized_execution_runtime_admission
from src.agency.authorized_execution_verification import bind_authorized_execution_verification
from src.agency.authorization_decision import AuthorizationDecision, AuthorizationDisposition
from src.agency.authorization_execution_bridge import create_authorization_execution_bridge
from src.agency.controlled_agency import AgencyStopReason, ControlledAgencyResult
from src.agency.execution_bridge import AgencyExecutionBridgeResult
from src.agency.execution_handoff import create_execution_handoff
from src.agency.execution_outcome import VerificationDecision, VerificationDisposition
from src.agency.execution_runtime import ExecutionObservation, ExecutionOutcome, ExecutionStatus
from src.agency.work_dispatch import DispatchRequest, WorkDispatcher
from src.agency.work_planning import PlanStepKind, WorkPlanStep, build_work_plan
from src.agency.work_state import WorkRole, WorkStage, WorkState, WorkStatus
from src.agency.workforce import WorkerDefinition, WorkerRegistry
from src.context.authorization_integrity_semantics import AuthorizationIntegrity, AuthorizationIntegrityStatus
from src.context.authorization_semantics import AuthorizationDecision as LegacyAuthorizationDecision, AuthorizationStatus
from src.context.execution_semantics import ExecutionGate
from src.context.working_context import WorkingContext


class _M57Fixture(TestCase):
    def _authorization(self):
        return AuthorizationDecision("auth-57", "confirm-result-57", "confirmation-57", AuthorizationDisposition.GRANTED, "explicitly granted")

    def _preparation(self):
        decision = LegacyAuthorizationDecision(
            request="deploy change", authorization_id="auth-57", proposal_id="proposal-57",
            validation_id="validation-57", policy_decision_id="policy-57",
            confirmation_id="confirmation-57", status=AuthorizationStatus.AUTHORIZED, rationale="approved",
        )
        integrity = AuthorizationIntegrity(
            request="deploy change", authorization_id="auth-57", proposal_id="proposal-57",
            validation_id="validation-57", policy_decision_id="policy-57", confirmation_id="confirmation-57",
            status=AuthorizationIntegrityStatus.VALID,
        )
        return ExecutionGate().prepare(decision, integrity, "exec-57", "deploy")

    def _handoff(self):
        work = WorkState(work_id="work-57", objective="verify authorized execution", stage=WorkStage.EXECUTING,
                         status=WorkStatus.ACTIVE, role=WorkRole.TECHNICAL_LEAD)
        plan = build_work_plan(work, (WorkPlanStep("step-1", "deploy change", PlanStepKind.IMPLEMENT, WorkRole.TECHNICAL_LEAD),))
        registry = WorkerRegistry()
        registry.register(WorkerDefinition("worker-1", "Worker", ("deploy",), 2))
        dispatch = WorkDispatcher(registry).dispatch(
            DispatchRequest(plan, "step-1", "worker-1", input_scope=("repo",), output_scope=("result",))
        )
        return create_execution_handoff(dispatch, self._preparation())

    def _authorized_outcome(self):
        preparation = self._preparation()
        bridge = create_authorization_execution_bridge(self._authorization(), preparation)
        admission = create_authorized_execution_admission(bridge, self._handoff())
        observation = ExecutionObservation(
            execution_id="exec-57", request="deploy change", proposal_id="proposal-57",
            validation_id="validation-57", policy_decision_id="policy-57", confirmation_id="confirmation-57",
            authorization_id="auth-57", operation="deploy", status=ExecutionStatus.SUCCEEDED,
            attempted=True, completed=True, succeeded=True,
            outcome=ExecutionOutcome(success=True, content={"result": "ok"}),
        )
        agency_result = ControlledAgencyResult(
            observations=(observation,), lifecycles=(), working_context=Mock(spec=WorkingContext),
            stop_reason=AgencyStopReason.COMPLETED,
        )
        execution_result = AgencyExecutionBridgeResult(handoff=admission.execution_handoff, agency_result=agency_result)
        runtime = create_authorized_execution_runtime_admission(admission, execution_result)
        return build_authorized_execution_outcome(runtime)


class M57AuthorizedExecutionVerificationTests(_M57Fixture):
    def test_exact_external_verification_binds_to_authorized_outcome(self):
        outcome = self._authorized_outcome()
        verification = VerificationDecision(
            execution_id="exec-57", disposition=VerificationDisposition.VERIFIED,
            reason="independent verifier confirmed expected state", evidence_id="evidence-57",
        )
        result = bind_authorized_execution_verification(outcome, verification)
        self.assertEqual("exec-57", result.execution_id)
        self.assertEqual("evidence-57", result.evidence_id)
        self.assertEqual(VerificationDisposition.VERIFIED, result.disposition)
        self.assertTrue(result.to_context()["verification_performed"])

    def test_mismatched_verification_identity_is_rejected(self):
        outcome = self._authorized_outcome()
        verification = VerificationDecision(
            execution_id="exec-other", disposition=VerificationDisposition.REJECTED,
            reason="verification refers to a different execution",
        )
        with self.assertRaises(ValueError):
            bind_authorized_execution_verification(outcome, verification)

    def test_non_verification_input_is_rejected(self):
        with self.assertRaises(TypeError):
            bind_authorized_execution_verification(self._authorized_outcome(), object())

    def test_verification_bridge_does_not_create_authority_or_execution(self):
        outcome = self._authorized_outcome()
        verification = VerificationDecision(
            execution_id="exec-57", disposition=VerificationDisposition.VERIFIED,
            reason="independent verification", evidence_id="evidence-57",
        )
        payload = bind_authorized_execution_verification(outcome, verification).to_context()
        self.assertFalse(payload["authorization_created"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["execution_performed"])
        self.assertFalse(payload["recovery_derived"])
        self.assertNotIn("authorize", payload)
        self.assertNotIn("execute", payload)
