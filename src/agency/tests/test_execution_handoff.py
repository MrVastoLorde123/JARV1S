from unittest import TestCase

from src.agency.execution_handoff import ExecutionHandoff, create_execution_handoff
from src.agency.work_dispatch import DispatchRequest, WorkDispatcher
from src.agency.work_planning import PlanStepKind, WorkPlanStep, build_work_plan
from src.agency.work_state import WorkRole, WorkStage, WorkState, WorkStatus
from src.agency.workforce import WorkerAssignment, WorkerDefinition, WorkerRegistry
from src.context.authorization_integrity_semantics import (
    AuthorizationIntegrity,
    AuthorizationIntegrityStatus,
    AuthorizationIntegrityViolation,
)
from src.context.authorization_semantics import AuthorizationDecision, AuthorizationStatus
from src.context.execution_semantics import ExecutionGate, ExecutionPreparationStatus


class M35ExecutionHandoffTests(TestCase):
    def _dispatch(self):
        work = WorkState(
            work_id="work-35",
            objective="handoff bounded work",
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

    def _ready_preparation(self):
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
        return ExecutionGate().prepare(decision, integrity, "exec-1", "deploy")

    def test_handoff_requires_ready_preparation_and_matching_request(self):
        dispatch = self._dispatch()
        preparation = self._ready_preparation()
        self.assertEqual(ExecutionPreparationStatus.READY, preparation.status)
        handoff = create_execution_handoff(dispatch, preparation)
        self.assertIsInstance(handoff, ExecutionHandoff)
        self.assertEqual("exec-1", handoff.execution_id)
        self.assertEqual(dispatch.assignment.assignment_id, handoff.assignment_id)

    def test_blocked_preparation_is_rejected_without_creating_authority(self):
        dispatch = self._dispatch()
        blocked = ExecutionGate().prepare(
            AuthorizationDecision(
                request="deploy change",
                authorization_id="auth-2",
                proposal_id="proposal-2",
                validation_id="validation-2",
                policy_decision_id="policy-2",
                confirmation_id=None,
                status=AuthorizationStatus.DENIED,
                rationale="policy denied the consequence.",
            ),
            AuthorizationIntegrity(
                request="deploy change",
                authorization_id="auth-2",
                proposal_id="proposal-2",
                validation_id="validation-2",
                policy_decision_id="policy-2",
                confirmation_id=None,
                status=AuthorizationIntegrityStatus.INVALID,
                violations=(
                    AuthorizationIntegrityViolation(
                        "test_invalid_integrity",
                        "synthetic invalid integrity for the blocked-preparation test.",
                    ),
                ),
            ),
            "exec-2",
            "deploy",
        )
        self.assertEqual(ExecutionPreparationStatus.BLOCKED, blocked.status)
        with self.assertRaises(ValueError):
            create_execution_handoff(dispatch, blocked)

    def test_mismatched_step_is_rejected(self):
        dispatch = self._dispatch()
        preparation = self._ready_preparation()
        with self.assertRaises(ValueError):
            ExecutionHandoff(
                dispatch=dispatch,
                preparation=type(preparation)(
                    request="different request",
                    execution_id=preparation.execution_id,
                    status=preparation.status,
                    execution_request=type(preparation.execution_request)(
                        execution_id=preparation.execution_request.execution_id,
                        request="different request",
                        proposal_id=preparation.execution_request.proposal_id,
                        validation_id=preparation.execution_request.validation_id,
                        policy_decision_id=preparation.execution_request.policy_decision_id,
                        confirmation_id=preparation.execution_request.confirmation_id,
                        authorization_id=preparation.execution_request.authorization_id,
                        operation=preparation.execution_request.operation,
                    ),
                ),
            )

    def test_handoff_does_not_expose_authorization_creation_or_execution(self):
        dispatch = self._dispatch()
        handoff = create_execution_handoff(dispatch, self._ready_preparation())
        context = handoff.to_context()
        self.assertFalse(context["authorization_created"])
        self.assertFalse(context["execution_performed"])
        self.assertNotIn("authorize", context)
        self.assertNotIn("execute", context)
