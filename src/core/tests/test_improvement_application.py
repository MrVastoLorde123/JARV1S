import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.improvement_application import (
    ImprovementApplicationService,
    ImprovementApplicationStatus,
)
from src.core.improvement_decision import ImprovementDecisionStatus
from src.core.tests.test_improvement_decision import M24_3ImprovementDecisionTests


class M24_4ImprovementApplicationTests(unittest.TestCase):
    def _make_decision(self):
        return M24_3ImprovementDecisionTests()._decide()

    def _apply(self, decision=None, **kwargs):
        values = {
            "applicator_id": "improvement-application-engine",
            "application_scope": "bounded-self-improvement-target",
            "application_purpose": "apply-approved-candidate",
            "application_result": {
                "outcome": "reported-applied",
                "target": {"component": "demo", "version": "v1"},
            },
            "status": ImprovementApplicationStatus.APPLIED,
        }
        values.update(kwargs)
        if decision is None:
            decision = self._make_decision()
        return ImprovementApplicationService().apply(decision, **values)

    def test_approved_decision_forms_application_record(self):
        application = self._apply()
        self.assertTrue(application.is_applied)
        self.assertEqual(application.application_id, "application-162")
        self.assertEqual(application.source_status, ImprovementDecisionStatus.APPROVED)

    def test_exact_decision_type_is_required(self):
        with self.assertRaises(TypeError):
            ImprovementApplicationService().apply(
                object(),
                applicator_id="a",
                application_scope="s",
                application_purpose="p",
                application_result={"ok": True},
                status=ImprovementApplicationStatus.APPLIED,
            )

    def test_source_must_be_approved(self):
        decision = self._make_decision()
        rejected = decision.__class__(**{**decision.__dict__, "status": ImprovementDecisionStatus.REJECTED})
        application = self._apply(rejected)
        self.assertTrue(application.is_invalid)
        self.assertIn("source decision is not APPROVED", application.reasons)

    def test_anchored_lineage_is_rechecked(self):
        decision = self._make_decision()
        tampered_decision = decision.__class__(
            **{**decision.__dict__, "lineage": {**decision.lineage, "candidate_id": "tampered-candidate"}}
        )
        invalid = self._apply(tampered_decision)
        self.assertTrue(invalid.is_invalid)
        self.assertIn("candidate_id lineage mismatch", invalid.reasons)

    def test_application_identity_is_preserved_from_upstream_chain(self):
        application = self._apply()
        decision = self._make_decision()
        self.assertEqual(application.application_id, decision.application_id)
        self.assertEqual(application.application_id, "application-162")

    def test_required_application_metadata_is_enforced(self):
        with self.assertRaises(ValueError):
            self._apply(applicator_id=" ")
        with self.assertRaises(ValueError):
            self._apply(application_scope="")
        with self.assertRaises(ValueError):
            self._apply(application_purpose=" ")

    def test_application_result_and_status_are_required_and_typed(self):
        with self.assertRaises(ValueError):
            self._apply(application_result=None)
        with self.assertRaises(TypeError):
            self._apply(status="APPLIED")

    def test_result_is_recursively_immutable(self):
        application = self._apply(application_result={"outer": {"items": ["x"]}})
        self.assertIsInstance(application.application_result, MappingProxyType)
        self.assertIsInstance(application.application_result["outer"], MappingProxyType)
        self.assertEqual(application.application_result["outer"]["items"], ("x",))
        with self.assertRaises(TypeError):
            application.application_result["new"] = "value"

    def test_lineage_is_recursively_immutable(self):
        application = self._apply()
        self.assertIsInstance(application.lineage, MappingProxyType)
        with self.assertRaises(TypeError):
            application.lineage["new"] = "value"

    def test_application_is_immutable(self):
        application = self._apply()
        with self.assertRaises(FrozenInstanceError):
            application.status = ImprovementApplicationStatus.FAILED

    def test_source_decision_is_not_mutated(self):
        decision = self._make_decision()
        before = decision
        self._apply(decision)
        self.assertEqual(decision, before)
        self.assertTrue(decision.is_approved)

    def test_failed_application_remains_bounded(self):
        application = self._apply(status=ImprovementApplicationStatus.FAILED, application_result={"outcome": "failed"})
        self.assertTrue(application.is_failed)
        self.assertFalse(application.executes_improvement)
        self.assertFalse(application.authorizes_execution)

    def test_all_application_statuses_are_bounded(self):
        for status in ImprovementApplicationStatus:
            application = self._apply(status=status)
            self.assertEqual(application.status, status)
            self.assertFalse(application.executes_improvement)
            self.assertFalse(application.authorizes_execution)

    def test_execution_and_mutation_walls_are_closed(self):
        application = self._apply()
        for attribute in (
            "executes_improvement", "authorizes_execution", "mutates_model", "mutates_memory",
            "mutates_policy", "mutates_state", "persists_state", "learns_from_application",
            "establishes_truth", "establishes_correctness", "establishes_certainty", "establishes_usefulness",
        ):
            self.assertFalse(getattr(application, attribute))

    def test_custom_reasons_require_tuple_of_non_empty_strings(self):
        with self.assertRaises(TypeError):
            self._apply(reasons=["x"])
        with self.assertRaises(TypeError):
            self._apply(reasons=("",))

    def test_custom_reasons_and_lineage_are_preserved_and_frozen(self):
        reasons = ("change window approved", "scope constrained")
        lineage = {"source": {"id": "decision-243"}}
        application = self._apply(reasons=reasons, lineage=lineage)
        self.assertEqual(application.reasons, reasons)
        self.assertIsInstance(application.lineage, MappingProxyType)
        self.assertIsInstance(application.lineage["source"], MappingProxyType)

    def test_invalid_application_fails_closed(self):
        decision = self._make_decision()
        tampered = decision.__class__(
            **{**decision.__dict__, "status": ImprovementDecisionStatus.INVALID}
        )
        application = self._apply(tampered)
        self.assertEqual(application.status, ImprovementApplicationStatus.INVALID)
        self.assertFalse(application.authorizes_execution)

    def test_provenance_is_preserved(self):
        decision = self._make_decision()
        application = self._apply(decision)
        for name in (
            "decision_id", "evaluation_id", "candidate_id", "consumption_id", "integrity_id",
            "validation_id", "transition_id", "evidence_id", "application_id", "proposal_id",
            "eligibility_id", "source_integrity_id", "source_validation_id", "state_key",
        ):
            self.assertEqual(getattr(application, name), getattr(decision, name))

    def test_status_properties_are_stable(self):
        applied = self._apply(status=ImprovementApplicationStatus.APPLIED)
        failed = self._apply(status=ImprovementApplicationStatus.FAILED, application_result={"outcome": "failed"})
        self.assertTrue(applied.is_applied)
        self.assertFalse(applied.is_failed)
        self.assertFalse(applied.is_invalid)
        self.assertTrue(failed.is_failed)
        self.assertFalse(failed.is_applied)
        self.assertFalse(failed.is_invalid)


if __name__ == "__main__":
    unittest.main()
