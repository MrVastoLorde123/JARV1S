from unittest import TestCase

from src.agency.authorization_decision import AuthorizationDecision, AuthorizationDisposition
from src.agency.authorization_execution_bridge import create_authorization_execution_bridge
from src.agency.authorized_execution_admission import create_authorized_execution_admission
from src.agency.execution_handoff import create_execution_handoff
from src.agency.work_dispatch import DispatchRequest, WorkDispatcher
from src.agency.work_planning import PlanStepKind, WorkPlanStep, build_work_plan
from src.agency.work_state import WorkRole, WorkStage, WorkState, WorkStatus
from src.agency.workforce import WorkerDefinition, WorkerRegistry
from src.context.authorization_integrity_semantics import AuthorizationIntegrity, AuthorizationIntegrityStatus
from src.context.authorization_semantics import AuthorizationDecision as LegacyAuthorizationDecision, AuthorizationStatus
from src.context.execution_semantics import ExecutionGate, ExecutionPreparation


class M54AuthorizedExecutionAdmissionTests(TestCase):
    def _dispatch(self):
        work = WorkState(
            work_id="work-54",
            objective="admit authorized execution",
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
        return WorkDispatcher(registry).dispatch(
            DispatchRequest(plan, "step-1", "worker-1", input_scope=("repo",), output_scope=("result",))
        )

    def _authorization(self):
        return AuthorizationDecision(
            "auth-54",
            "confirm-result-54",
            "confirmation-54",
            AuthorizationDisposition.GRANTED,
            "explicitly granted",
        )

    def _preparation(self):
        decision = LegacyAuthorizationDecision(
            request="deploy change",
            authorization_id="auth-54",
            proposal_id="proposal-54",
            validation_id="validation-54",
            policy_decision_id="policy-54",
            confirmation_id="confirmation-54",
            status=AuthorizationStatus.AUTHORIZED,
            rationale="approved",
        )
        integrity = AuthorizationIntegrity(
            request="deploy change",
            authorization_id="auth-54",
            proposal_id="proposal-54",
            validation_id="validation-54",
            policy_decision_id="policy-54",
            confirmation_id="confirmation-54",
            status=AuthorizationIntegrityStatus.VALID,
        )
        return ExecutionGate().prepare(decision, integrity, "exec-54", "deploy")

    def _handoff(self, preparation):
        return create_execution_handoff(self._dispatch(), preparation)

    def test_exact_m53_bridge_can_be_admitted_to_existing_handoff(self):
        preparation = self._preparation()
        bridge = create_authorization_execution_bridge(self._authorization(), preparation)
        admission = create_authorized_execution_admission(bridge, self._handoff(preparation))
        self.assertEqual("auth-54", admission.authorization_id)
        self.assertEqual("exec-54", admission.execution_id)
        payload = admission.to_context()
        self.assertFalse(payload["authorization_created"])
        self.assertFalse(payload["execution_prepared"])
        self.assertFalse(payload["execution_requested"])
        self.assertFalse(payload["execution_performed"])

    def test_mismatched_preparation_is_rejected(self):
        first = self._preparation()
        bridge = create_authorization_execution_bridge(self._authorization(), first)
        second = ExecutionGate().prepare(
            LegacyAuthorizationDecision(
                request="deploy change",
                authorization_id="auth-54",
                proposal_id="proposal-other",
                validation_id="validation-other",
                policy_decision_id="policy-other",
                confirmation_id="confirmation-54",
                status=AuthorizationStatus.AUTHORIZED,
                rationale="approved",
            ),
            AuthorizationIntegrity(
                request="deploy change",
                authorization_id="auth-54",
                proposal_id="proposal-other",
                validation_id="validation-other",
                policy_decision_id="policy-other",
                confirmation_id="confirmation-54",
                status=AuthorizationIntegrityStatus.VALID,
            ),
            "exec-other",
            "deploy",
        )
        with self.assertRaises(ValueError):
            create_authorized_execution_admission(bridge, self._handoff(second))

    def test_execution_id_mismatch_is_rejected(self):
        preparation = self._preparation()
        bridge = create_authorization_execution_bridge(self._authorization(), preparation)
        handoff = self._handoff(preparation)
        tampered = type(handoff)(dispatch=handoff.dispatch, preparation=ExecutionPreparation(
            request=preparation.request,
            execution_id="exec-other",
            status=preparation.status,
            execution_request=type(preparation.execution_request)(
                execution_id="exec-other",
                request=preparation.execution_request.request,
                proposal_id=preparation.execution_request.proposal_id,
                validation_id=preparation.execution_request.validation_id,
                policy_decision_id=preparation.execution_request.policy_decision_id,
                confirmation_id=preparation.execution_request.confirmation_id,
                authorization_id=preparation.execution_request.authorization_id,
                operation=preparation.execution_request.operation,
            ),
        ))
        with self.assertRaises(ValueError):
            create_authorized_execution_admission(bridge, tampered)

    def test_admission_does_not_create_or_perform_execution(self):
        preparation = self._preparation()
        bridge = create_authorization_execution_bridge(self._authorization(), preparation)
        admission = create_authorized_execution_admission(bridge, self._handoff(preparation))
        payload = admission.to_context()
        self.assertNotIn("authorize", payload)
        self.assertNotIn("execute", payload)
        self.assertNotIn("provider", payload)
