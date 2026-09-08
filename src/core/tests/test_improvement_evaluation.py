import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.continuous_self_improvement_candidate import ContinuousSelfImprovementCandidateStatus
from src.core.improvement_evaluation import (
    ImprovementAssessment,
    ImprovementEvaluationService,
    ImprovementEvaluationStatus,
)
from src.core.tests.test_continuous_self_improvement_candidate import (
    M24_1ContinuousSelfImprovementCandidateTests,
)


class M24_2ImprovementEvaluationTests(unittest.TestCase):
    def _make_candidate(self):
        return M24_1ContinuousSelfImprovementCandidateTests()._propose()

    def _evaluate(self, candidate=None, **kwargs):
        values = {
            "evaluation_id": "improvement-evaluation-242",
            "evaluator_id": "improvement-evaluator",
            "evaluation_purpose": "bounded-candidate-assessment",
            "evaluation_scope": "planner-response-selection",
            "criteria": ("bounded-scope", "traceable-evidence"),
            "observations": {"bounded-scope": "preserved", "traceable-evidence": "present"},
            "assessment": ImprovementAssessment.SUPPORTIVE,
        }
        values.update(kwargs)
        return ImprovementEvaluationService().evaluate(candidate or self._make_candidate(), **values)

    def test_proposed_candidate_forms_evaluation(self):
        result = self._evaluate()
        self.assertIs(result.status, ImprovementEvaluationStatus.EVALUATED)
        self.assertTrue(result.is_evaluated)
        self.assertFalse(result.is_rejected)
        self.assertEqual(result.candidate_id, "improvement-candidate-241")
        self.assertIs(result.assessment, ImprovementAssessment.SUPPORTIVE)

    def test_exact_candidate_type_is_required(self):
        with self.assertRaises(TypeError):
            self._evaluate(candidate=object())

    def test_source_must_be_proposed(self):
        source = self._make_candidate()
        object.__setattr__(source, "status", ContinuousSelfImprovementCandidateStatus.REJECTED)
        result = self._evaluate(source)
        self.assertIs(result.status, ImprovementEvaluationStatus.REJECTED)
        self.assertFalse(result.is_evaluated)
        self.assertIn("source candidate is not PROPOSED", result.reasons)

    def test_evaluation_identity_must_be_distinct(self):
        source = self._make_candidate()
        with self.assertRaises(ValueError):
            self._evaluate(source, evaluation_id=source.candidate_id)
        with self.assertRaises(ValueError):
            self._evaluate(source, evaluation_id=source.consumption_id)

    def test_required_evaluation_metadata_is_enforced(self):
        service = ImprovementEvaluationService()
        source = self._make_candidate()
        common = {
            "evaluator_id": "evaluator",
            "evaluation_purpose": "purpose",
            "evaluation_scope": "scope",
            "criteria": ("criterion",),
            "observations": {"criterion": "observed"},
            "assessment": ImprovementAssessment.MIXED,
        }
        for field in ("evaluation_id", "evaluator_id", "evaluation_purpose", "evaluation_scope"):
            values = dict(common, evaluation_id="evaluation-242")
            values[field] = " "
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    service.evaluate(source, **values)

    def test_criteria_must_be_non_empty_tuple_of_strings(self):
        source = self._make_candidate()
        values = {
            "evaluation_id": "evaluation-242",
            "evaluator_id": "evaluator",
            "evaluation_purpose": "purpose",
            "evaluation_scope": "scope",
            "observations": {"criterion": "observed"},
            "assessment": ImprovementAssessment.INCONCLUSIVE,
        }
        with self.assertRaises(TypeError):
            self._evaluate(source, **values, criteria=["criterion"])
        with self.assertRaises(TypeError):
            self._evaluate(source, **values, criteria=(" ",))
        with self.assertRaises(ValueError):
            self._evaluate(source, **values, criteria=())

    def test_observations_and_assessment_are_required_and_typed(self):
        with self.assertRaises(ValueError):
            self._evaluate(observations=None)
        with self.assertRaises(TypeError):
            self._evaluate(assessment="SUPPORTIVE")

    def test_anchored_lineage_is_rechecked(self):
        source = self._make_candidate()
        original = source.lineage
        expected = {
            "candidate_id": "candidate_id lineage mismatch",
            "consumption_id": "consumption_id lineage mismatch",
            "integrity_id": "integrity_id lineage mismatch",
            "validation_id": "validation_id lineage mismatch",
            "transition_id": "transition_id lineage mismatch",
            "evidence_id": "evidence_id lineage mismatch",
            "application_id": "application_id lineage mismatch",
            "source_integrity_id": "source_integrity_id lineage mismatch",
            "source_validation_id": "source_validation_id lineage mismatch",
        }
        for field, reason in expected.items():
            tampered = dict(original)
            tampered[field] = "tampered"
            object.__setattr__(source, "lineage", MappingProxyType(tampered))
            result = self._evaluate(source)
            self.assertIs(result.status, ImprovementEvaluationStatus.REJECTED, msg=field)
            self.assertIn(reason, result.reasons, msg=field)
            object.__setattr__(source, "lineage", original)

    def test_evaluation_preserves_candidate_provenance(self):
        source = self._make_candidate()
        result = self._evaluate(source)
        fields = {
            "candidate_id": "candidate_id",
            "consumption_id": "consumption_id",
            "integrity_id": "integrity_id",
            "validation_id": "validation_id",
            "transition_id": "transition_id",
            "evidence_id": "evidence_id",
            "application_id": "application_id",
            "decision_id": "decision_id",
            "proposal_id": "proposal_id",
            "eligibility_id": "eligibility_id",
            "source_integrity_id": "source_integrity_id",
            "source_validation_id": "source_validation_id",
            "state_key": "state_key",
            "candidate_scope": "improvement_scope",
            "candidate_source_fingerprint": "source_integrity_fingerprint",
            "candidate_computed_fingerprint": "computed_integrity_fingerprint",
        }
        for evaluation_field, candidate_field in fields.items():
            self.assertEqual(getattr(result, evaluation_field), getattr(source, candidate_field))

    def test_custom_reasons_and_lineage_are_preserved_and_frozen(self):
        lineage = {"evaluation_id": "evaluation-custom", "chain": ["a", {"depth": 2}]}
        result = self._evaluate(evaluation_id="evaluation-custom", reasons=("reviewed",), lineage=lineage)
        self.assertEqual(result.reasons, ("reviewed",))
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertIsInstance(result.lineage["chain"], tuple)
        self.assertIsInstance(result.lineage["chain"][1], MappingProxyType)
        with self.assertRaises(TypeError):
            result.lineage["x"] = "y"

    def test_observations_are_recursively_immutable(self):
        result = self._evaluate(observations={"checks": ["one", {"bounded": True}]})
        self.assertIsInstance(result.observations, MappingProxyType)
        self.assertIsInstance(result.observations["checks"], tuple)
        self.assertIsInstance(result.observations["checks"][1], MappingProxyType)
        with self.assertRaises(TypeError):
            result.observations["x"] = "y"

    def test_evaluation_is_immutable(self):
        result = self._evaluate()
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = ImprovementEvaluationStatus.REJECTED

    def test_source_is_not_mutated(self):
        source = self._make_candidate()
        before = source
        self._evaluate(source)
        self.assertEqual(source, before)

    def test_assessment_is_observation_not_decision(self):
        for assessment in ImprovementAssessment:
            result = self._evaluate(assessment=assessment)
            self.assertIs(result.assessment, assessment)
            self.assertFalse(result.decides_improvement)
            self.assertFalse(result.authorizes_application)
            self.assertFalse(result.applies_improvement)

    def test_evaluation_remains_non_authoritative(self):
        result = self._evaluate()
        for name in (
            "authorizes_application", "authorizes_execution", "applies_improvement", "decides_improvement",
            "is_learning", "updates_model", "mutates_memory", "mutates_policy", "mutates_state",
            "persists_state", "establishes_truth", "establishes_correctness", "establishes_certainty",
            "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))

    def test_rejected_evaluation_remains_non_authoritative(self):
        source = self._make_candidate()
        object.__setattr__(source, "status", ContinuousSelfImprovementCandidateStatus.REJECTED)
        result = self._evaluate(source)
        for name in (
            "authorizes_application", "authorizes_execution", "applies_improvement", "decides_improvement",
            "is_learning", "updates_model", "mutates_memory", "mutates_policy", "mutates_state",
            "persists_state", "establishes_truth", "establishes_correctness", "establishes_certainty",
            "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))

    def test_custom_reasons_require_tuple_of_non_empty_strings(self):
        source = self._make_candidate()
        with self.assertRaises(TypeError):
            self._evaluate(source, reasons=["x"])
        with self.assertRaises(TypeError):
            self._evaluate(source, reasons=(" ",))

    def test_status_is_stable(self):
        result = self._evaluate()
        self.assertEqual(result.status.value, "EVALUATED")
        self.assertFalse(result.is_rejected)


if __name__ == "__main__":
    unittest.main()
