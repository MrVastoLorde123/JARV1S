import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.continuous_self_improvement_candidate import ContinuousSelfImprovementCandidateStatus
from src.core.improvement_decision import (
    ImprovementDecisionService,
    ImprovementDecisionStatus,
    ImprovementDisposition,
)
from src.core.improvement_evaluation import ImprovementAssessment
from src.core.tests.test_improvement_evaluation import M24_2ImprovementEvaluationTests


class M24_3ImprovementDecisionTests(unittest.TestCase):
    def _make_evaluation(self):
        return M24_2ImprovementEvaluationTests()._evaluate()

    def _decide(self, evaluation=None, **kwargs):
        values = {
            "decision_id": "improvement-decision-243",
            "decider_id": "improvement-decision-engine",
            "decision_purpose": "bounded-candidate-disposition",
            "decision_scope": "planner-response-selection",
            "disposition": ImprovementDisposition.APPROVE,
            "rationale": {"basis": "supportive-evaluation"},
            "factors": {"risk": "bounded", "traceability": "present"},
        }
        values.update(kwargs)
        return ImprovementDecisionService().decide(evaluation or self._make_evaluation(), **values)

    def test_evaluated_source_forms_bounded_decision(self):
        result = self._decide()
        self.assertIs(result.status, ImprovementDecisionStatus.APPROVED)
        self.assertTrue(result.is_approved)
        self.assertTrue(result.approves_candidate)
        self.assertEqual(result.evaluation_id, "improvement-evaluation-242")

    def test_exact_evaluation_type_is_required(self):
        with self.assertRaises(TypeError):
            self._decide(evaluation=object())

    def test_source_must_be_evaluated(self):
        source = self._make_evaluation()
        object.__setattr__(source, "status", source.status.REJECTED)
        result = self._decide(source)
        self.assertIs(result.status, ImprovementDecisionStatus.INVALID)
        self.assertFalse(result.is_approved)
        self.assertTrue(result.is_invalid)
        self.assertIn("source evaluation is not EVALUATED", result.reasons)

    def test_decision_identity_must_be_distinct(self):
        source = self._make_evaluation()
        with self.assertRaises(ValueError):
            self._decide(source, decision_id=source.evaluation_id)
        with self.assertRaises(ValueError):
            self._decide(source, decision_id=source.candidate_id)

    def test_required_decision_metadata_is_enforced(self):
        service = ImprovementDecisionService()
        source = self._make_evaluation()
        common = {
            "decider_id": "decider",
            "decision_purpose": "purpose",
            "decision_scope": "scope",
            "disposition": ImprovementDisposition.DEFER,
            "rationale": {"basis": "evaluation"},
            "factors": {"x": 1},
        }
        for field in ("decision_id", "decider_id", "decision_purpose", "decision_scope"):
            values = dict(common, decision_id="decision-243")
            values[field] = " "
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    service.decide(source, **values)

    def test_disposition_is_explicitly_typed(self):
        with self.assertRaises(TypeError):
            self._decide(disposition="APPROVE")

    def test_rationale_and_factors_are_required(self):
        with self.assertRaises(ValueError):
            self._decide(rationale=None)
        with self.assertRaises(ValueError):
            self._decide(factors=None)

    def test_anchored_lineage_is_rechecked(self):
        source = self._make_evaluation()
        original = source.lineage
        expected = {
            "evaluation_id": "evaluation_id lineage mismatch",
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
            result = self._decide(source)
            self.assertIs(result.status, ImprovementDecisionStatus.INVALID, msg=field)
            self.assertIn(reason, result.reasons, msg=field)
            object.__setattr__(source, "lineage", original)

    def test_decision_preserves_evaluation_provenance(self):
        source = self._make_evaluation()
        result = self._decide(source)
        fields = {
            "evaluation_id": "evaluation_id",
            "candidate_id": "candidate_id",
            "consumption_id": "consumption_id",
            "integrity_id": "integrity_id",
            "validation_id": "validation_id",
            "transition_id": "transition_id",
            "evidence_id": "evidence_id",
            "application_id": "application_id",
            "proposal_id": "proposal_id",
            "eligibility_id": "eligibility_id",
            "source_integrity_id": "source_integrity_id",
            "source_validation_id": "source_validation_id",
            "state_key": "state_key",
            "candidate_scope": "candidate_scope",
            "candidate_source_fingerprint": "candidate_source_fingerprint",
            "candidate_computed_fingerprint": "candidate_computed_fingerprint",
        }
        for decision_field, evaluation_field in fields.items():
            self.assertEqual(getattr(result, decision_field), getattr(source, evaluation_field))

    def test_custom_rationale_factors_and_lineage_are_frozen(self):
        result = self._decide(
            rationale={"reasons": ["one", {"bounded": True}]},
            factors={"checks": [{"risk": "low"}]},
            lineage={"decision_id": "decision-custom", "chain": ["a", {"depth": 2}]},
            decision_id="decision-custom",
        )
        self.assertIsInstance(result.rationale, MappingProxyType)
        self.assertIsInstance(result.rationale["reasons"], tuple)
        self.assertIsInstance(result.rationale["reasons"][1], MappingProxyType)
        self.assertIsInstance(result.factors, MappingProxyType)
        self.assertIsInstance(result.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            result.factors["x"] = "y"

    def test_decision_is_immutable(self):
        result = self._decide()
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = ImprovementDecisionStatus.REJECTED

    def test_source_is_not_mutated(self):
        source = self._make_evaluation()
        before = source
        self._decide(source)
        self.assertEqual(source, before)

    def test_all_dispositions_are_bounded(self):
        expected = {
            ImprovementDisposition.APPROVE: ImprovementDecisionStatus.APPROVED,
            ImprovementDisposition.REJECT: ImprovementDecisionStatus.REJECTED,
            ImprovementDisposition.DEFER: ImprovementDecisionStatus.DEFERRED,
        }
        for disposition, status in expected.items():
            result = self._decide(disposition=disposition)
            self.assertIs(result.status, status)
            self.assertFalse(result.authorizes_application)
            self.assertFalse(result.authorizes_execution)
            self.assertFalse(result.applies_improvement)
            self.assertFalse(result.executes_improvement)

    def test_approved_decision_is_not_application_authority(self):
        result = self._decide()
        for name in (
            "authorizes_application", "authorizes_execution", "applies_improvement", "executes_improvement",
            "is_learning", "updates_model", "mutates_memory", "mutates_policy", "mutates_state",
            "persists_state", "establishes_truth", "establishes_correctness", "establishes_certainty",
            "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))

    def test_invalid_decision_is_not_authoritative(self):
        source = self._make_evaluation()
        object.__setattr__(source, "status", source.status.REJECTED)
        result = self._decide(source)
        for name in (
            "authorizes_application", "authorizes_execution", "applies_improvement", "executes_improvement",
            "is_learning", "updates_model", "mutates_memory", "mutates_policy", "mutates_state",
            "persists_state", "establishes_truth", "establishes_correctness", "establishes_certainty",
            "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))

    def test_custom_reasons_require_tuple_of_non_empty_strings(self):
        source = self._make_evaluation()
        with self.assertRaises(TypeError):
            self._decide(source, reasons=["x"])
        with self.assertRaises(TypeError):
            self._decide(source, reasons=(" ",))

    def test_status_properties_are_stable(self):
        self.assertTrue(self._decide(disposition=ImprovementDisposition.APPROVE).is_approved)
        self.assertTrue(self._decide(disposition=ImprovementDisposition.REJECT).is_rejected)
        self.assertTrue(self._decide(disposition=ImprovementDisposition.DEFER).is_deferred)


if __name__ == "__main__":
    unittest.main()
