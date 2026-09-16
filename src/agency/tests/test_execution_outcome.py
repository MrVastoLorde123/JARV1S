from unittest import TestCase

from src.agency.controlled_agency import ControlledAgency
from src.agency.execution_bridge import run_execution_handoff
from src.agency.execution_handoff import create_execution_handoff
from src.agency.execution_outcome import (
    AgencyOutcomeStatus,
    VerificationDecision,
    VerificationDisposition,
    build_verification_input,
    classify_agency_outcome,
)
from src.agency.execution_runtime import ExecutionOutcome, ExecutionRuntime
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


class M37ExecutionOutcomeTests(TestCase):
    def _handoff(self):
        work = WorkState(
            work_id="work-37",
            objective="classify bounded execution",
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

    def _result(self):
        agency = ControlledAgency(
            ExecutionRuntime(_SuccessfulAdapter()),
            ExecutionObservationContextIntegrator(),
            max_steps=2,
        )
        context = WorkingContext(
            request="deploy change",
            context_package=ContextPackage(request="deploy change", items=(), instructions=()),
        )
        return run_execution_handoff(agency, self._handoff(), context)

    def test_execution_observation_is_classified_without_claiming_verification(self):
        outcome = classify_agency_outcome(self._result())
        self.assertEqual(AgencyOutcomeStatus.SUCCEEDED, outcome.status)
        self.assertTrue(outcome.succeeded)
        self.assertEqual(1, outcome.observation_count)
        self.assertIsNone(outcome.error)
        self.assertFalse(outcome.to_context()["verification_guaranteed"])

    def test_verification_input_is_bounded_and_requires_external_decision(self):
        outcome = classify_agency_outcome(self._result())
        verification_input = build_verification_input(outcome, expected_request="deploy change")
        self.assertEqual("deploy change", verification_input.expected_request)
        decision = VerificationDecision(
            execution_id="exec-1",
            disposition=VerificationDisposition.VERIFIED,
            reason="independent verifier confirmed expected state",
            evidence_id="evidence-37-1",
        )
        self.assertEqual(VerificationDisposition.VERIFIED, decision.disposition)
        self.assertEqual("evidence-37-1", decision.evidence_id)

    def test_verified_requires_evidence_and_invalid_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            VerificationDecision(
                execution_id="exec-1",
                disposition=VerificationDisposition.VERIFIED,
                reason="missing evidence",
            )
        with self.assertRaises(TypeError):
            build_verification_input(object(), expected_request="deploy change")
        with self.assertRaises(ValueError):
            build_verification_input(classify_agency_outcome(self._result()), expected_request="")
