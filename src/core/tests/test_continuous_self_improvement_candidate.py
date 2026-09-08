import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.continuous_self_improvement_candidate import (
    ContinuousSelfImprovementCandidateService,
    ContinuousSelfImprovementCandidateStatus,
)
from src.core.learning_state_execution_learning_state_validation_integrity_consumption import (
    LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus,
)
from src.core.tests.test_learning_state_execution_learning_state_validation_integrity_consumption import (
    M23_169LearningStateValidationIntegrityConsumptionTests,
)


class M24_1ContinuousSelfImprovementCandidateTests(unittest.TestCase):
    def _make_consumption(self):
        return M23_169LearningStateValidationIntegrityConsumptionTests()._consume()

    def _propose(self, consumption=None, **kwargs):
        values = {
            "candidate_id": "improvement-candidate-241",
            "proposer_id": "self-improvement-engine",
            "candidate_purpose": "bounded-behavior-improvement",
            "improvement_scope": "planner-response-selection",
            "proposed_improvement": {"strategy": "prefer-verified-path", "weight": 0.8},
            "rationale": {"basis": "consumed-learning-evidence"},
        }
        values.update(kwargs)
        return ContinuousSelfImprovementCandidateService().propose(consumption or self._make_consumption(), **values)

    def test_consumed_evidence_forms_proposed_candidate(self):
        result = self._propose()
        self.assertIs(result.status, ContinuousSelfImprovementCandidateStatus.PROPOSED)
        self.assertTrue(result.is_proposed)
        self.assertTrue(result.proposes_adaptation)
        self.assertEqual(result.consumption_id, "validation-integrity-consumption-169")

    def test_exact_consumption_type_is_required(self):
        with self.assertRaises(TypeError):
            self._propose(consumption=object())

    def test_source_must_be_consumed(self):
        source = self._make_consumption()
        object.__setattr__(source, "status", LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus.REJECTED)
        result = self._propose(source)
        self.assertIs(result.status, ContinuousSelfImprovementCandidateStatus.REJECTED)
        self.assertFalse(result.is_proposed)
        self.assertIn("source consumption is not CONSUMED", result.reasons)

    def test_candidate_identity_must_be_distinct(self):
        source = self._make_consumption()
        with self.assertRaises(ValueError):
            self._propose(source, candidate_id=source.consumption_id)
        with self.assertRaises(ValueError):
            self._propose(source, candidate_id=source.integrity_id)

    def test_required_candidate_metadata_is_enforced(self):
        source = self._make_consumption()
        service = ContinuousSelfImprovementCandidateService()
        common = {
            "proposer_id": "proposer",
            "candidate_purpose": "purpose",
            "improvement_scope": "scope",
            "proposed_improvement": {"x": 1},
            "rationale": {"basis": "evidence"},
        }
        for field in ("candidate_id", "proposer_id", "candidate_purpose", "improvement_scope"):
            values = dict(common, candidate_id="candidate-241")
            values[field] = " "
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    service.propose(source, **values)
        with self.assertRaises(ValueError):
            service.propose(source, candidate_id="candidate-241", proposer_id="proposer", candidate_purpose="purpose", improvement_scope="scope", proposed_improvement=None, rationale={"basis": "evidence"})
        with self.assertRaises(ValueError):
            service.propose(source, candidate_id="candidate-241", proposer_id="proposer", candidate_purpose="purpose", improvement_scope="scope", proposed_improvement={"x": 1}, rationale=None)

    def test_anchored_lineage_is_rechecked(self):
        source = self._make_consumption()
        original = source.lineage
        expected = {
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
            result = self._propose(source)
            self.assertIs(result.status, ContinuousSelfImprovementCandidateStatus.REJECTED, msg=field)
            self.assertIn(reason, result.reasons, msg=field)
            object.__setattr__(source, "lineage", original)

    def test_custom_reasons_and_lineage_are_preserved_and_frozen(self):
        lineage = {"candidate_id": "candidate-custom", "chain": ["a", {"depth": 2}]}
        result = self._propose(candidate_id="candidate-custom", reasons=("caller-reason",), lineage=lineage)
        self.assertEqual(result.reasons, ("caller-reason",))
        self.assertIsInstance(result.lineage, MappingProxyType)
        self.assertIsInstance(result.lineage["chain"], tuple)
        self.assertIsInstance(result.lineage["chain"][1], MappingProxyType)
        with self.assertRaises(TypeError):
            result.lineage["x"] = "y"

    def test_candidate_preserves_consumed_provenance(self):
        result = self._propose()
        source = self._make_consumption()
        source_fields = {
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
            "source_integrity_fingerprint": "integrity_fingerprint",
            "computed_integrity_fingerprint": "computed_integrity_fingerprint",
        }
        for candidate_field, source_field in source_fields.items():
            self.assertEqual(getattr(result, candidate_field), getattr(source, source_field))

    def test_source_is_not_mutated(self):
        source = self._make_consumption()
        before = source
        self._propose(source)
        self.assertEqual(source, before)

    def test_candidate_evidence_is_recursive_and_immutable(self):
        result = self._propose(
            proposed_improvement={"steps": ["one", {"bounded": True}]},
            rationale={"signals": ["validated", {"confidence": "preserved"}]},
        )
        self.assertIsInstance(result.proposed_improvement, MappingProxyType)
        self.assertIsInstance(result.proposed_improvement["steps"], tuple)
        self.assertIsInstance(result.proposed_improvement["steps"][1], MappingProxyType)
        self.assertIsInstance(result.rationale, MappingProxyType)
        with self.assertRaises(TypeError):
            result.proposed_improvement["x"] = "y"
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            result.status = ContinuousSelfImprovementCandidateStatus.REJECTED

    def test_custom_reasons_require_tuple_of_non_empty_strings(self):
        source = self._make_consumption()
        service = ContinuousSelfImprovementCandidateService()
        values = dict(
            candidate_id="candidate-241",
            proposer_id="proposer",
            candidate_purpose="purpose",
            improvement_scope="scope",
            proposed_improvement={"x": 1},
            rationale={"basis": "evidence"},
        )
        with self.assertRaises(TypeError):
            service.propose(source, **values, reasons=["x"])
        with self.assertRaises(TypeError):
            service.propose(source, **values, reasons=(" ",))

    def test_rejected_candidate_is_not_learning_or_authoritative(self):
        source = self._make_consumption()
        object.__setattr__(source, "status", LearningStateExecutionLearningStateValidationIntegrityConsumptionStatus.REJECTED)
        result = self._propose(source)
        for name in (
            "is_learning", "applies_learning", "authorizes_learning", "authorizes_execution", "authorizes_retry",
            "invokes_learner", "invokes_executor", "updates_model", "mutates_memory", "mutates_policy",
            "mutates_state", "persists_state", "schedules_work", "plans_work", "establishes_truth",
            "establishes_correctness", "establishes_certainty", "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))

    def test_proposed_candidate_remains_non_authoritative(self):
        result = self._propose()
        for name in (
            "is_learning", "applies_learning", "authorizes_learning", "authorizes_execution", "authorizes_retry",
            "invokes_learner", "invokes_executor", "updates_model", "mutates_memory", "mutates_policy",
            "mutates_state", "persists_state", "schedules_work", "plans_work", "establishes_truth",
            "establishes_correctness", "establishes_certainty", "establishes_usefulness",
        ):
            self.assertFalse(getattr(result, name))

    def test_candidate_status_is_stable(self):
        result = self._propose()
        self.assertEqual(result.status.value, "PROPOSED")
        self.assertFalse(result.is_rejected)

    def test_source_fingerprints_are_preserved(self):
        source = self._make_consumption()
        result = self._propose(source)
        self.assertEqual(result.source_integrity_fingerprint, source.integrity_fingerprint)
        self.assertEqual(result.computed_integrity_fingerprint, source.computed_integrity_fingerprint)


if __name__ == "__main__":
    unittest.main()
