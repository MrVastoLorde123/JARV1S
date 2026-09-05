import unittest

from src.core.environment_observation_evidence_qualification import EvidenceQualification
from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_uncertainty import (
    EnvironmentWorldModelUncertainty,
    EnvironmentWorldModelUncertaintyError,
    EnvironmentWorldModelUncertaintyService,
)


class EnvironmentWorldModelUncertaintyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model = EnvironmentWorldModel(
            model_id="model-1",
            environment_id="env-1",
            state_by_domain={"hardware": {"cpu": "x86"}},
            represented_domains=("hardware",),
            missing_domains=("software", "network"),
            context_ids=("ctx-1",),
            qualification_ids=("qual-1",),
            provenance_ids=("prov-1",),
            readiness_id="ready-1",
            source_bundle_id="bundle-1",
        )
        self.service = EnvironmentWorldModelUncertaintyService()

    def test_assessment_builds_bounded_uncertainty(self) -> None:
        result = self.service.assess(
            self.model,
            uncertainty_id="unc-1",
            confidence_by_domain={"hardware": 0.8},
        )
        self.assertIsInstance(result, EnvironmentWorldModelUncertainty)
        self.assertEqual(result.model_id, "model-1")
        self.assertEqual(result.environment_id, "env-1")
        self.assertEqual(result.evidence_status, EvidenceQualification.USABLE)
        self.assertEqual(result.confidence_by_domain["hardware"], 0.8)
        self.assertAlmostEqual(result.uncertainty_by_domain["hardware"], 0.2)
        self.assertTrue(result.is_descriptive_only)
        self.assertTrue(result.usable_for_reasoning)

    def test_confidence_must_cover_exactly_represented_domains(self) -> None:
        with self.assertRaises(EnvironmentWorldModelUncertaintyError):
            self.service.assess(
                self.model,
                uncertainty_id="unc-missing",
                confidence_by_domain={},
            )
        with self.assertRaises(EnvironmentWorldModelUncertaintyError):
            self.service.assess(
                self.model,
                uncertainty_id="unc-extra",
                confidence_by_domain={"hardware": 0.8, "software": 0.4},
            )

    def test_scores_are_bounded(self) -> None:
        with self.assertRaises(ValueError):
            self.service.assess(
                self.model,
                uncertainty_id="unc-bad",
                confidence_by_domain={"hardware": 1.2},
            )
        with self.assertRaises(ValueError):
            EnvironmentWorldModelUncertainty(
                uncertainty_id="unc-bad",
                model_id="model-1",
                environment_id="env-1",
                represented_domains=("hardware",),
                missing_domains=("software",),
                evidence_status=EvidenceQualification.USABLE,
                confidence_by_domain={"hardware": -0.1},
                uncertainty_by_domain={"hardware": 1.1},
            )

    def test_boolean_scores_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.assess(
                self.model,
                uncertainty_id="unc-bool",
                confidence_by_domain={"hardware": True},
            )

    def test_non_numeric_scores_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.assess(
                self.model,
                uncertainty_id="unc-nonnumeric",
                confidence_by_domain={"hardware": "0.8"},
            )

    def test_missing_domains_do_not_receive_confidence(self) -> None:
        result = self.service.assess(
            self.model,
            uncertainty_id="unc-missing-domains",
            confidence_by_domain={"hardware": 0.9},
        )
        self.assertEqual(result.missing_domains, ("software", "network"))
        self.assertNotIn("software", result.confidence_by_domain)
        self.assertNotIn("network", result.confidence_by_domain)

    def test_model_identity_is_preserved(self) -> None:
        result = self.service.assess(
            self.model,
            uncertainty_id="unc-lineage",
            confidence_by_domain={"hardware": 0.6},
            lineage={"model_id": "model-1", "source": {"stage": "world-model"}},
        )
        self.assertEqual(result.model_id, self.model.model_id)
        self.assertEqual(result.lineage["source"]["stage"], "world-model")

    def test_result_and_nested_data_are_immutable(self) -> None:
        result = self.service.assess(
            self.model,
            uncertainty_id="unc-immutable",
            confidence_by_domain={"hardware": 0.7},
            reasons={"hardware": "derived from explicit evidence"},
        )
        with self.assertRaises(TypeError):
            result.confidence_by_domain["hardware"] = 0.1
        with self.assertRaises(TypeError):
            result.reasons["hardware"] = "changed"
        with self.assertRaises(AttributeError):
            result.uncertainty_id = "changed"

    def test_upstream_model_is_not_mutated(self) -> None:
        before = dict(self.model.state_by_domain["hardware"])
        self.service.assess(
            self.model,
            uncertainty_id="unc-upstream",
            confidence_by_domain={"hardware": 0.5},
        )
        self.assertEqual(dict(self.model.state_by_domain["hardware"]), before)

    def test_wrong_model_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.assess(
                object(),
                uncertainty_id="unc-type",
                confidence_by_domain={"hardware": 0.5},
            )

    def test_authority_fields_are_absent(self) -> None:
        result = self.service.assess(
            self.model,
            uncertainty_id="unc-authority",
            confidence_by_domain={"hardware": 0.5},
        )
        forbidden = {
            "authority_granted",
            "authorization_granted",
            "execution_requested",
            "permission_granted",
            "truth_proven",
            "adaptation_truth_proven",
        }
        self.assertTrue(forbidden.isdisjoint(vars(result)))

    def test_reasons_are_preserved(self) -> None:
        result = self.service.assess(
            self.model,
            uncertainty_id="unc-reason",
            confidence_by_domain={"hardware": 0.5},
            reasons={"hardware": "single qualified source"},
        )
        self.assertEqual(result.reasons["hardware"], "single qualified source")


if __name__ == "__main__":
    unittest.main()
