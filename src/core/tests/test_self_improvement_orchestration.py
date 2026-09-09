import unittest

from src.core.continuous_self_improvement_candidate import ContinuousSelfImprovementCandidate
from src.core.improvement_application import ImprovementApplication
from src.core.improvement_decision import ImprovementDecision
from src.core.improvement_evaluation import ImprovementEvaluation
from src.core.improvement_verification import ImprovementVerification
from src.core.interface_backend import InterfaceOperation, InterfaceRequest, InterfaceResponseStatus, SelfImprovementInterfaceBackend
from src.core.self_improvement_orchestration import SelfImprovementOrchestration
from src.core.tests.test_continuous_self_improvement_candidate import M24_1ContinuousSelfImprovementCandidateTests
from src.core.tests.test_improvement_application import M24_4ImprovementApplicationTests
from src.core.tests.test_improvement_decision import M24_3ImprovementDecisionTests
from src.core.tests.test_improvement_evaluation import M24_2ImprovementEvaluationTests
from src.core.tests.test_improvement_verification import M24_5ImprovementVerificationRollbackTests


class M25_2SelfImprovementOrchestrationTests(unittest.TestCase):
    def setUp(self):
        candidate_tests = M24_1ContinuousSelfImprovementCandidateTests()
        self.consumption = candidate_tests._make_consumption()
        self.candidate = candidate_tests._propose(self.consumption)
        self.evaluation = M24_2ImprovementEvaluationTests()._evaluate(self.candidate)
        self.decision = M24_3ImprovementDecisionTests()._decide(self.evaluation)
        self.application = M24_4ImprovementApplicationTests()._apply(self.decision)
        self.verification = M24_5ImprovementVerificationRollbackTests()._verify(self.application)
        self.calls = []

        class CandidateService:
            def propose(inner, *args, **kwargs):
                self.calls.append(("propose", args, kwargs))
                return self.candidate

        class EvaluationService:
            def evaluate(inner, *args, **kwargs):
                self.calls.append(("evaluate", args, kwargs))
                return self.evaluation

        class DecisionService:
            def decide(inner, *args, **kwargs):
                self.calls.append(("decide", args, kwargs))
                return self.decision

        class ApplicationService:
            def apply(inner, *args, **kwargs):
                self.calls.append(("apply", args, kwargs))
                return self.application

        class VerificationService:
            def verify(inner, *args, **kwargs):
                self.calls.append(("verify", args, kwargs))
                return self.verification

        self.orchestrator = SelfImprovementOrchestration(
            candidate_service=CandidateService(), evaluation_service=EvaluationService(),
            decision_service=DecisionService(), application_service=ApplicationService(),
            verification_service=VerificationService(),
        )

    def req(self, operation, payload):
        return InterfaceRequest(
            request_id=f"request-{operation.value.lower()}", session_id="session-1", actor_id="actor-1",
            operation=operation, payload=payload, metadata={"channel": "test"},
        )

    def test_full_m25_backend_to_m24_route(self):
        backend = SelfImprovementInterfaceBackend(self.orchestrator)
        response = backend.handle(self.req(InterfaceOperation.DECIDE, {
            "evaluation": self.evaluation, "decision_id": "decision", "decider_id": "decider",
            "decision_purpose": "purpose", "decision_scope": "scope",
            "disposition": self.decision.disposition, "rationale": {"basis": "evaluation"},
            "factors": {"risk": "bounded"},
        }))
        self.assertIs(response.status, InterfaceResponseStatus.ACCEPTED)
        self.assertIs(response.payload["artifact"], self.decision)
        self.assertEqual(response.request_id, "request-decide")
        self.assertIs(response.operation, InterfaceOperation.DECIDE)

    def test_all_five_live_routes_dispatch(self):
        payloads = {
            InterfaceOperation.PROPOSE: {
                "consumption": self.consumption, "candidate_id": "candidate", "proposer_id": "proposer",
                "candidate_purpose": "purpose", "improvement_scope": "scope",
                "proposed_improvement": {"x": 1}, "rationale": {"basis": "test"},
            },
            InterfaceOperation.EVALUATE: {
                "candidate": self.candidate, "evaluation_id": "evaluation", "evaluator_id": "evaluator",
                "evaluation_purpose": "purpose", "evaluation_scope": "scope", "criteria": ("criterion",),
                "observations": {"criterion": "observed"}, "assessment": self.evaluation.assessment,
            },
            InterfaceOperation.DECIDE: {
                "evaluation": self.evaluation, "decision_id": "decision", "decider_id": "decider",
                "decision_purpose": "purpose", "decision_scope": "scope", "disposition": self.decision.disposition,
                "rationale": {"basis": "evaluation"}, "factors": {"risk": "bounded"},
            },
            InterfaceOperation.APPLY: {
                "decision": self.decision, "applicator_id": "applicator", "application_scope": "scope",
                "application_purpose": "purpose", "application_result": {"result": "recorded"}, "status": self.application.status,
            },
            InterfaceOperation.VERIFY: {
                "application": self.application, "verification_id": "verification", "verifier_id": "verifier",
                "verification_purpose": "purpose", "verification_scope": "scope", "observed_result": {"actual": True},
                "expected_result": {"expected": True}, "verification_status": self.verification.verification_status,
                "rollback_status": self.verification.rollback_status, "rollback_result": {"recorded": False},
            },
        }
        expected_names = ["propose", "evaluate", "decide", "apply", "verify"]
        for operation, payload in payloads.items():
            response = self.orchestrator.dispatch(self.req(operation, payload))
            self.assertIs(response.status, InterfaceResponseStatus.ACCEPTED)
        self.assertEqual([call[0] for call in self.calls], expected_names)

    def test_provenance_artifact_is_passed_through_not_rebuilt(self):
        response = self.orchestrator.dispatch(self.req(InterfaceOperation.VERIFY, {
            "application": self.application, "verification_id": "verification", "verifier_id": "verifier",
            "verification_purpose": "purpose", "verification_scope": "scope", "observed_result": {"actual": True},
            "expected_result": {"expected": True}, "verification_status": self.verification.verification_status,
            "rollback_status": self.verification.rollback_status, "rollback_result": {"recorded": False},
        }))
        artifact = response.payload["artifact"]
        self.assertIs(type(artifact), ImprovementVerification)
        self.assertEqual(artifact.application_id, self.application.application_id)
        self.assertEqual(artifact.lineage, self.application.lineage | {"verification_id": artifact.verification_id})

    def test_missing_required_payload_is_rejected_before_service(self):
        response = self.orchestrator.dispatch(self.req(InterfaceOperation.DECIDE, {"evaluation": self.evaluation}))
        self.assertIs(response.status, InterfaceResponseStatus.REJECTED)
        self.assertIn("missing payload field: decision_id", response.payload["error"])
        self.assertEqual(self.calls, [])

    def test_m24_input_type_error_is_rejected(self):
        response = self.orchestrator.dispatch(self.req(InterfaceOperation.EVALUATE, {
            "candidate": object(), "evaluation_id": "evaluation", "evaluator_id": "evaluator",
            "evaluation_purpose": "purpose", "evaluation_scope": "scope", "criteria": ("criterion",),
            "observations": {"criterion": "observed"}, "assessment": self.evaluation.assessment,
        }))
        self.assertIs(response.status, InterfaceResponseStatus.REJECTED)
        self.assertIn("candidate must be a ContinuousSelfImprovementCandidate", response.payload["error"])
        self.assertEqual(self.calls, [])

    def test_wrong_stage_result_fails_closed(self):
        class BadDecisionService:
            def decide(inner, *args, **kwargs):
                return self.evaluation
        orchestrator = SelfImprovementOrchestration(
            candidate_service=self.orchestrator._candidate_service, evaluation_service=self.orchestrator._evaluation_service,
            decision_service=BadDecisionService(), application_service=self.orchestrator._application_service,
            verification_service=self.orchestrator._verification_service,
        )
        response = orchestrator.dispatch(self.req(InterfaceOperation.DECIDE, {
            "evaluation": self.evaluation, "decision_id": "decision", "decider_id": "decider",
            "decision_purpose": "purpose", "decision_scope": "scope", "disposition": self.decision.disposition,
            "rationale": {"basis": "evaluation"}, "factors": {"risk": "bounded"},
        }))
        self.assertIs(response.status, InterfaceResponseStatus.FAILED)
        self.assertIn("wrong stage result", response.payload["error"])

    def test_rollback_is_not_an_execution_path(self):
        response = self.orchestrator.dispatch(self.req(InterfaceOperation.ROLLBACK, {"verification": self.verification}))
        self.assertIs(response.status, InterfaceResponseStatus.REJECTED)
        self.assertIn("rollback execution is not part of M25.2", response.payload["error"])

    def test_status_is_deferred_to_runtime_state_contract(self):
        response = self.orchestrator.dispatch(self.req(InterfaceOperation.STATUS, {"state_key": "planner"}))
        self.assertIs(response.status, InterfaceResponseStatus.REJECTED)
        self.assertIn("runtime state contract", response.payload["error"])

    def test_constructor_requires_all_five_stage_services(self):
        with self.assertRaises(TypeError):
            SelfImprovementOrchestration(
                candidate_service=None, evaluation_service=self.orchestrator._evaluation_service,
                decision_service=self.orchestrator._decision_service, application_service=self.orchestrator._application_service,
                verification_service=self.orchestrator._verification_service,
            )

    def test_exact_request_type_is_required(self):
        with self.assertRaises(TypeError):
            self.orchestrator.dispatch(object())

    def test_orchestration_authority_walls_remain_closed(self):
        for name in (
            "authorizes_execution", "executes_capability", "mutates_state", "persists_state",
            "establishes_truth", "establishes_certainty", "is_ai_provider",
        ):
            self.assertFalse(getattr(self.orchestrator, name))

    def test_response_metadata_preserves_session_actor_and_stage(self):
        response = self.orchestrator.dispatch(self.req(InterfaceOperation.APPLY, {
            "decision": self.decision, "applicator_id": "applicator", "application_scope": "scope",
            "application_purpose": "purpose", "application_result": {"result": "recorded"}, "status": self.application.status,
        }))
        self.assertEqual(response.metadata["session_id"], "session-1")
        self.assertEqual(response.metadata["actor_id"], "actor-1")
        self.assertEqual(response.metadata["artifact_type"], "ImprovementApplication")

    def test_optional_lineage_and_reasons_are_forwarded(self):
        lineage = {"candidate_id": "candidate"}
        reasons = ("caller supplied",)
        self.orchestrator.dispatch(self.req(InterfaceOperation.EVALUATE, {
            "candidate": self.candidate, "evaluation_id": "evaluation", "evaluator_id": "evaluator",
            "evaluation_purpose": "purpose", "evaluation_scope": "scope", "criteria": ("criterion",),
            "observations": {"criterion": "observed"}, "assessment": self.evaluation.assessment,
            "lineage": lineage, "reasons": reasons,
        }))
        _, _, kwargs = self.calls[0]
        self.assertEqual(kwargs["lineage"], lineage)
        self.assertEqual(kwargs["reasons"], reasons)


if __name__ == "__main__":
    unittest.main()
