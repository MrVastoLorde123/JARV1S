from unittest import TestCase
from unittest.mock import Mock

from src.agency.authorized_execution_admission import create_authorized_execution_admission
from src.agency.authorized_execution_outcome import build_authorized_execution_outcome
from src.agency.authorized_execution_recovery import build_authorized_execution_recovery
from src.agency.authorized_execution_runtime_admission import create_authorized_execution_runtime_admission
from src.agency.authorized_execution_verification import bind_authorized_execution_verification
from src.agency.authorization_decision import AuthorizationDecision, AuthorizationDisposition
from src.agency.authorization_execution_bridge import create_authorization_execution_bridge
from src.agency.controlled_agency import AgencyStopReason, ControlledAgencyResult
from src.agency.driveability import ContinuationCycle, Objective, ObjectiveState
from src.agency.execution_bridge import AgencyExecutionBridgeResult
from src.agency.execution_handoff import create_execution_handoff
from src.agency.execution_outcome import VerificationDecision, VerificationDisposition
from src.agency.work_dispatch import DispatchRequest, WorkDispatcher
from src.agency.work_planning import PlanStepKind, WorkPlanStep, build_work_plan
from src.agency.work_state import WorkRole, WorkStage, WorkState, WorkStatus
from src.agency.workforce import WorkerDefinition, WorkerRegistry
from src.context.authorization_integrity_semantics import AuthorizationIntegrity, AuthorizationIntegrityStatus
from src.context.authorization_semantics import AuthorizationDecision as LegacyAuthorizationDecision, AuthorizationStatus
from src.context.execution_semantics import ExecutionGate
from src.context.working_context import WorkingContext


class _M58Fixture(TestCase):
    def _authorization(self):
        return AuthorizationDecision(
            "auth-58",
            "confirm-result-58",
            "confirmation-58",
            AuthorizationDisposition.GRANTED,
            "explicitly granted",
        )

    def _preparation(self):
        decision = LegacyAuthorizationDecision(
            request="deploy change",
            authorization_id="auth-58",
            proposal_id="proposal-58",
            validation_id="validation-58",
            policy_decision_id="policy-58",
            confirmation_id="confirmation-58",
            status=AuthorizationStatus.AUTHORIZED,
            rationale="approved",
        )
        integrity = AuthorizationIntegrity(
            request="deploy change",
            authorization_id="auth-58",
            proposal_id="proposal-58",
            validation_id="validation-58",
            policy_decision_id="policy-58",
            confirmation_id="confirmation-58",
            status=AuthorizationIntegrityStatus.VALID,
        )
        return ExecutionGate().prepare(decision, integrity, "exec-58", "deploy")

    def _handoff(self):
        work = WorkState(
            work_id="work-58",
            objective="recover bounded work",
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

    def _verification(self, disposition=VerificationDisposition.VERIFIED):
        preparation = self._preparation()
        bridge = create_authorization_execution_bridge(self._authorization(), preparation)
        admission = create_authorized_execution_admission(bridge, self._handoff())
        agency_result = ControlledAgencyResult(
            observations=(),
            lifecycles=(),
            working_context=Mock(spec=WorkingContext),
            stop_reason=AgencyStopReason.COMPLETED,
        )
        execution_result = AgencyExecutionBridgeResult(
            handoff=admission.execution_handoff,
            agency_result=agency_result,
        )
        runtime = create_authorized_execution_runtime_admission(admission, execution_result)
        outcome = build_authorized_execution_outcome(runtime)
        evidence_id = "evidence-58" if disposition is VerificationDisposition.VERIFIED else None
        verification = VerificationDecision("exec-58", disposition, "independent verification result", evidence_id=evidence_id)
        return bind_authorized_execution_verification(outcome, verification)

    def _objective(self):
        return Objective("objective-58", "finish bounded recovery", ObjectiveState.ACTIVE)

    def _cycle(self):
        return ContinuationCycle("cycle-58", "objective-58", 0, max_cycles=3)


class M58AuthorizedExecutionRecoveryTests(_M58Fixture):
    def test_exact_verification_derives_existing_m38_recovery(self):
        result = build_authorized_execution_recovery(
            self._verification(),
            self._objective(),
            self._cycle(),
        )
        self.assertEqual("exec-58", result.execution_id)
        self.assertEqual("auth-58", result.authorization_id)
        self.assertEqual("COMPLETE", result.disposition.value)
        self.assertFalse(result.execution_requested)
        self.assertFalse(result.to_context()["execution_performed"])

    def test_rejected_verification_can_produce_bounded_continuation(self):
        verification = self._verification(VerificationDisposition.REJECTED)
        result = build_authorized_execution_recovery(
            verification,
            self._objective(),
            self._cycle(),
            next_step="inspect the failed result",
        )
        self.assertEqual("CONTINUE", result.disposition.value)
        self.assertIsNotNone(result.recovery.continuation.proposal)
        self.assertFalse(result.recovery.continuation.proposal.execution_requested)

    def test_objective_cycle_identity_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            build_authorized_execution_recovery(
                self._verification(),
                self._objective(),
                ContinuationCycle("other-cycle", "other-objective", 0, max_cycles=3),
            )

    def test_non_verification_and_no_authority_surface_are_rejected(self):
        with self.assertRaises(TypeError):
            build_authorized_execution_recovery(object(), self._objective(), self._cycle())
        payload = build_authorized_execution_recovery(
            self._verification(), self._objective(), self._cycle()
        ).to_context()
        self.assertFalse(payload["authorization_created"])
        self.assertFalse(payload["execution_requested"])
        self.assertNotIn("authorize", payload)
        self.assertNotIn("execute", payload)
