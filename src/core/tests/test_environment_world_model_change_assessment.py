import unittest

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_change_assessment import (
    EnvironmentWorldModelChangeAssessment,
    EnvironmentWorldModelChangeAssessmentService,
    WorldModelChangeAssessmentError,
)


class EnvironmentWorldModelChangeAssessmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.baseline = EnvironmentWorldModel(
            model_id="model-1",
            environment_id="env-1",
            state_by_domain={
                "hardware": {"cpu": "x86"},
                "network": {"status": "online"},
            },
            represented_domains=("hardware", "network"),
            missing_domains=("software", "models"),
            context_ids=("ctx-1", "ctx-2"),
            qualification_ids=("qual-1", "qual-2"),
            provenance_ids=("prov-1", "prov-2"),
            readiness_id="ready-1",
            source_bundle_id="bundle-1",
        )
        self.candidate = EnvironmentWorldModel(
            model_id="model-2",
            environment_id="env-1",
            state_by_domain={
                "hardware": {"cpu": "x86"},
                "network": {"status": "offline"},
                "software": {"os": "linux"},
            },
            represented_domains=("hardware", "network", "software"),
            missing_domains=("models",),
            context_ids=("ctx-3", "ctx-4", "ctx-5"),
            qualification_ids=("qual-3", "qual-4", "qual-5"),
            provenance_ids=("prov-3", "prov-4", "prov-5"),
            readiness_id="ready-2",
            source_bundle_id="bundle-2",
        )
        self.service = EnvironmentWorldModelChangeAssessmentService()

    def test_detects_changed_and_unchanged_domains(self) -> None:
        result = self.service.assess(
            self.baseline,
            self.candidate,
            assessment_id="change-1",
        )
        self.assertIsInstance(result, EnvironmentWorldModelChangeAssessment)
        self.assertEqual(result.changed_domains, ("network", "software"))
        self.assertEqual(result.unchanged_domains, ("hardware",))
        self.assertEqual(result.changes_by_domain["network"]["baseline_state"], {"status": "online"})
        self.assertEqual(result.changes_by_domain["network"]["candidate_state"], {"status": "offline"})
        self.assertFalse(result.changes_by_domain["network"]["baseline_present"] is False)
        self.assertTrue(result.changes_by_domain["software"]["baseline_present"] is False)
        self.assertTrue(result.changes_by_domain["software"]["candidate_present"])

    def test_same_environment_is_required(self) -> None:
        candidate = EnvironmentWorldModel(
            model_id="model-other",
            environment_id="env-2",
            state_by_domain={},
            represented_domains=(),
            missing_domains=("hardware",),
            context_ids=(),
            qualification_ids=(),
            provenance_ids=(),
            readiness_id="ready-other",
            source_bundle_id="bundle-other",
        )
        with self.assertRaises(WorldModelChangeAssessmentError):
            self.service.assess(
                self.baseline,
                candidate,
                assessment_id="change-env-mismatch",
            )

    def test_model_identities_must_differ(self) -> None:
        candidate = EnvironmentWorldModel(
            model_id="model-1",
            environment_id="env-1",
            state_by_domain={"hardware": {"cpu": "other"}},
            represented_domains=("hardware",),
            missing_domains=("network",),
            context_ids=("ctx-x",),
            qualification_ids=("qual-x",),
            provenance_ids=("prov-x",),
            readiness_id="ready-x",
            source_bundle_id="bundle-x",
        )
        with self.assertRaises(WorldModelChangeAssessmentError):
            self.service.assess(
                self.baseline,
                candidate,
                assessment_id="change-same-id",
            )

    def test_wrong_types_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.assess(object(), self.candidate, assessment_id="change-bad-baseline")
        with self.assertRaises(TypeError):
            self.service.assess(self.baseline, object(), assessment_id="change-bad-candidate")

    def test_missing_domain_transitions_are_detected(self) -> None:
        candidate = EnvironmentWorldModel(
            model_id="model-3",
            environment_id="env-1",
            state_by_domain={"hardware": {"cpu": "x86"}},
            represented_domains=("hardware",),
            missing_domains=("network", "software"),
            context_ids=("ctx-6",),
            qualification_ids=("qual-6",),
            provenance_ids=("prov-6",),
            readiness_id="ready-3",
            source_bundle_id="bundle-3",
        )
        result = self.service.assess(
            self.baseline,
            candidate,
            assessment_id="change-missing",
        )
        self.assertEqual(result.changed_domains, ("network",))
        self.assertEqual(result.changes_by_domain["network"]["baseline_present"], True)
        self.assertEqual(result.changes_by_domain["network"]["candidate_present"], False)

    def test_identity_and_lineage_are_preserved(self) -> None:
        result = self.service.assess(
            self.baseline,
            self.candidate,
            assessment_id="change-lineage",
            lineage={"stage": "world-model", "source": {"baseline": "model-1"}},
        )
        self.assertEqual(result.assessment_id, "change-lineage")
        self.assertEqual(result.baseline_model_id, "model-1")
        self.assertEqual(result.candidate_model_id, "model-2")
        self.assertEqual(result.lineage["source"]["baseline"], "model-1")

    def test_nested_change_data_is_immutable(self) -> None:
        result = self.service.assess(
            self.baseline,
            self.candidate,
            assessment_id="change-immutable",
        )
        with self.assertRaises(TypeError):
            result.changes_by_domain["network"]["candidate_state"] = {"status": "changed"}
        with self.assertRaises(AttributeError):
            result.assessment_id = "changed"

    def test_source_models_are_not_mutated(self) -> None:
        baseline_before = dict(self.baseline.state_by_domain)
        candidate_before = dict(self.candidate.state_by_domain)
        self.service.assess(
            self.baseline,
            self.candidate,
            assessment_id="change-nonmutation",
        )
        self.assertEqual(dict(self.baseline.state_by_domain), baseline_before)
        self.assertEqual(dict(self.candidate.state_by_domain), candidate_before)

    def test_result_is_descriptive_only(self) -> None:
        result = self.service.assess(
            self.baseline,
            self.candidate,
            assessment_id="change-authority",
        )
        self.assertTrue(result.is_descriptive_only)
        forbidden = {
            "authority_granted",
            "authorization_granted",
            "execution_requested",
            "permission_granted",
            "truth_proven",
            "revision_applied",
        }
        self.assertTrue(forbidden.isdisjoint(vars(result)))

    def test_domain_order_is_deterministic(self) -> None:
        result = self.service.assess(
            self.baseline,
            self.candidate,
            assessment_id="change-order",
        )
        self.assertEqual(result.changed_domains, ("network", "software"))
        self.assertEqual(result.unchanged_domains, ("hardware",))


if __name__ == "__main__":
    unittest.main()
