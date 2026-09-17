from unittest import TestCase

from src.agency.adaptation_application import LearningProfile, apply_adaptation
from src.agency.adaptation_outcome import AdaptationOutcomeDisposition, evaluate_adaptation_outcome
from src.agency.adaptation_proposal import propose_adaptation
from src.agency.adaptation_validation import AdaptationValidationDisposition, validate_adaptation
from src.agency.authorized_execution_reconciliation import build_authorized_execution_reconciliation
from src.agency.experience_feedback import build_experience_feedback
from src.agency.experience_record import build_experience_record
from src.agency.learning_evaluation import LearningEvaluationDisposition, evaluate_learning_signal
from src.agency.learning_signal import build_learning_signal
from src.agency.tests.test_authorized_execution_recovery import _M58Fixture
from src.agency.work_state import WorkRole, WorkStage, WorkState, WorkStatus


class Phase2ExperienceLearningAdaptationTests(_M58Fixture):
    def _reconciliation(self):
        return build_authorized_execution_reconciliation(
            self._verification_recovery(),
            WorkState(
                work_id="work-58",
                objective="recover bounded work",
                stage=WorkStage.EXECUTING,
                status=WorkStatus.ACTIVE,
                role=WorkRole.TECHNICAL_LEAD,
                current_step="deploy change",
            ),
        )

    def _verification_recovery(self):
        from src.agency.authorized_execution_recovery import build_authorized_execution_recovery
        return build_authorized_execution_recovery(self._verification(), self._objective(), self._cycle())

    def _feedback(self):
        return build_experience_feedback(self._reconciliation(), experience_id="experience-phase2", value_delta=1.0)

    def _record(self, learning_candidate=True):
        return build_experience_record(
            self._feedback(),
            situation="bounded deployment",
            action="deploy change",
            result="verified completion",
            evidence_ids=("evidence-58",),
            tags=("deployment", "verified"),
            learning_candidate=learning_candidate,
        )

    def _signal(self):
        return build_learning_signal(
            self._record(),
            signal_id="signal-phase2",
            hypothesis="verified deployment benefits from this bounded workflow",
            strength=0.9,
            generalization_scope="same workflow family",
            value_relevance=0.8,
        )

    def _evaluation(self):
        return evaluate_learning_signal(
            self._signal(),
            evaluation_id="evaluation-phase2",
            disposition=LearningEvaluationDisposition.SUPPORTED,
            confidence=0.9,
            reason="supported by verified experience evidence",
            evidence_ids=("evidence-58",),
        )

    def _proposal(self):
        return propose_adaptation(
            self._evaluation(),
            proposal_id="proposal-phase2",
            target="planning.workflow.deployment",
            change_type="PREFERENCE",
            description="prefer the verified bounded deployment workflow",
            expected_benefit=0.8,
            risk=0.1,
        )

    def _validation(self):
        return validate_adaptation(
            self._proposal(),
            validation_id="validation-phase2",
            disposition=AdaptationValidationDisposition.VALID,
            reason="bounded, compatible, evidence-backed preference change",
        )

    def _application(self):
        return apply_adaptation(
            self._validation(),
            LearningProfile(version=4, entries={"planning.workflow.network": "existing"}),
            application_id="application-phase2",
        )

    def test_m60_feedback_preserves_reconciled_identity(self):
        feedback = self._feedback()
        self.assertEqual("exec-58", feedback.execution_id)
        self.assertEqual("auth-58", feedback.authorization_id)
        self.assertEqual("deploy change", feedback.request)
        self.assertFalse(feedback.to_context()["authority_created"])

    def test_m61_record_can_be_marked_non_learning(self):
        record = self._record(learning_candidate=False)
        self.assertFalse(record.learning_candidate)
        with self.assertRaises(ValueError):
            build_learning_signal(
                record,
                signal_id="blocked-signal",
                hypothesis="do not learn",
                strength=0.9,
                generalization_scope="none",
                value_relevance=0.1,
            )

    def test_m62_and_m63_produce_adoptable_learning(self):
        evaluation = self._evaluation()
        self.assertTrue(evaluation.adoptable)
        self.assertEqual(LearningEvaluationDisposition.SUPPORTED, evaluation.disposition)

    def test_m63_rejected_learning_is_not_adoptable(self):
        evaluation = evaluate_learning_signal(
            self._signal(),
            evaluation_id="evaluation-rejected",
            disposition=LearningEvaluationDisposition.REJECTED,
            confidence=0.95,
            reason="contradicted by evidence",
        )
        self.assertFalse(evaluation.adoptable)
        with self.assertRaises(ValueError):
            propose_adaptation(
                evaluation,
                proposal_id="proposal-rejected",
                target="x",
                change_type="PREFERENCE",
                description="invalid",
                expected_benefit=0.5,
                risk=0.1,
            )

    def test_m64_and_m65_preserve_bounded_adaptation(self):
        proposal = self._proposal()
        validation = self._validation()
        self.assertEqual("signal-phase2", proposal.learning_signal_id)
        self.assertTrue(validation.applicable)
        self.assertFalse(proposal.to_context()["authorization_granted"])
        self.assertFalse(validation.to_context()["execution_requested"])

    def test_m66_applies_only_validated_learning_as_new_profile_version(self):
        application = self._application()
        self.assertEqual(5, application.after.version)
        self.assertEqual(
            "prefer the verified bounded deployment workflow",
            application.after.entries["planning.workflow.deployment"],
        )
        self.assertFalse(application.to_context()["external_mutation_performed"])
        blocked = validate_adaptation(
            self._proposal(),
            validation_id="validation-blocked",
            disposition=AdaptationValidationDisposition.BLOCKED,
            reason="requires review",
        )
        with self.assertRaises(ValueError):
            apply_adaptation(blocked, application.after, application_id="blocked-application")

    def test_m67_measures_improvement(self):
        outcome = evaluate_adaptation_outcome(
            self._application(),
            outcome_id="outcome-improved",
            disposition=AdaptationOutcomeDisposition.IMPROVED,
            value_delta=2.5,
            reason="subsequent measured value improved",
        )
        self.assertEqual(AdaptationOutcomeDisposition.IMPROVED, outcome.disposition)
        self.assertGreater(outcome.value_delta, 0)

    def test_end_to_end_phase2_chain_remains_authority_free(self):
        payloads = [
            self._feedback().to_context(),
            self._record().to_context(),
            self._signal().to_context(),
            self._evaluation().to_context(),
            self._proposal().to_context(),
            self._validation().to_context(),
            self._application().to_context(),
            evaluate_adaptation_outcome(
                self._application(),
                outcome_id="outcome-unmeasured",
                disposition=AdaptationOutcomeDisposition.UNMEASURED,
                reason="no subsequent measurement yet",
            ).to_context(),
        ]
        for payload in payloads:
            self.assertFalse(payload.get("authorization_created", False))
            self.assertFalse(payload.get("authorization_granted", False))
            self.assertFalse(payload.get("execution_requested", False))
            self.assertNotIn("authorize", payload)
            self.assertNotIn("execute", payload)
