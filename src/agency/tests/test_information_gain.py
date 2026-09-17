from unittest import TestCase

from src.agency.information_gain import (
    InformationGainOpportunity,
    build_information_gain_assessment,
)
from src.agency.initiative_evaluation import InitiativeEvaluation, InitiativeEvaluationSet


class M48InformationGainTests(TestCase):
    def _evaluation_set(self):
        return InitiativeEvaluationSet(
            "eval-set",
            "candidate-set",
            evaluations=(
                InitiativeEvaluation(
                    "candidate-1",
                    "candidate-set",
                    0.8,
                    0.7,
                    0.6,
                    "bounded descriptive evaluation",
                ),
            ),
            unresolved_uncertainties=("need confirmation", "need current evidence"),
        )

    def test_opportunity_must_reference_supplied_uncertainty(self):
        evaluation_set = self._evaluation_set()
        opportunity = InformationGainOpportunity(
            "op-1", "eval-set", "unknown uncertainty", 0.8, "test"
        )
        with self.assertRaises(ValueError):
            build_information_gain_assessment(
                evaluation_set, assessment_id="assessment", opportunities=(opportunity,)
            )

    def test_opportunity_must_reference_supplied_evaluation_set(self):
        evaluation_set = self._evaluation_set()
        opportunity = InformationGainOpportunity(
            "op-1", "other-set", "need confirmation", 0.8, "test"
        )
        with self.assertRaises(ValueError):
            build_information_gain_assessment(
                evaluation_set, assessment_id="assessment", opportunities=(opportunity,)
            )

    def test_gain_is_bounded_and_output_is_not_authority(self):
        evaluation_set = self._evaluation_set()
        opportunity = InformationGainOpportunity(
            "op-1", "eval-set", "need confirmation", 0.8, "confirmation would reduce uncertainty", "candidate-1"
        )
        assessment = build_information_gain_assessment(
            evaluation_set, assessment_id="assessment", opportunities=(opportunity,)
        )
        payload = assessment.to_context()
        self.assertEqual(payload["opportunity_count"], 1)
        self.assertEqual(payload["unresolved_uncertainties"], evaluation_set.unresolved_uncertainties)
        self.assertFalse(payload["truth_established"])
        self.assertFalse(payload["intent_established"])
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["scheduling_requested"])
        self.assertFalse(payload["execution_requested"])

    def test_unresolved_uncertainty_is_carried_forward(self):
        evaluation_set = self._evaluation_set()
        assessment = build_information_gain_assessment(evaluation_set, assessment_id="assessment")
        self.assertEqual(assessment.unresolved_uncertainties, evaluation_set.unresolved_uncertainties)
        self.assertEqual(assessment.opportunity_count, 0)
