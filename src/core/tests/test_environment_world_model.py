import unittest
from datetime import datetime, timezone

from src.core.environment_context_composition import EnvironmentContextCompositionService
from src.core.environment_current_context_freshness import (
    CurrentContextFreshness,
    EnvironmentCurrentContextBundleValidity,
    EnvironmentCurrentContextValidity,
)
from src.core.environment_current_context_readiness import EnvironmentCurrentContextReadinessService
from src.core.environment_evidence_current_context import EnvironmentCurrentContext
from src.core.environment_observation_evidence_qualification import EvidenceQualification
from src.core.environment_world_model import EnvironmentWorldModel, EnvironmentWorldModelError, EnvironmentWorldModelService


class EnvironmentWorldModelTests(unittest.TestCase):
    def setUp(self) -> None:
        now = datetime(2026, 9, 5, 15, 0, tzinfo=timezone.utc)
        context = EnvironmentCurrentContext(
            context_id="ctx-1",
            environment_id="env-1",
            domain="hardware",
            subject_kind="observation",
            data={"observed": {"cpu": {"arch": "x86", "cores": 8}}, "status": "qualified"},
            evidence_status=EvidenceQualification.USABLE,
            observation_ids=("obs-1",),
            adapter_ids=("adapter-1",),
            provenance_id="prov-1",
            qualification_id="qual-1",
        )
        self.bundle = EnvironmentContextCompositionService().compose(
            (context,),
            bundle_id="bundle-1",
        )
        validity = EnvironmentCurrentContextBundleValidity(
            bundle_id="bundle-1",
            environment_id="env-1",
            context_ids=("ctx-1",),
            observed_at=(now,),
            assessed_at=now,
            max_age_seconds=30,
            freshness=CurrentContextFreshness.CURRENT,
            current_context_validities=(
                EnvironmentCurrentContextValidity(
                    context_id="ctx-1",
                    environment_id="env-1",
                    domain="hardware",
                    observed_at=now,
                    assessed_at=now,
                    max_age_seconds=30,
                    freshness=CurrentContextFreshness.CURRENT,
                ),
            ),
        )
        self.validity = validity
        self.readiness = EnvironmentCurrentContextReadinessService().qualify(
            self.bundle,
            validity,
            readiness_id="ready-1",
        )
        self.service = EnvironmentWorldModelService()

    def test_ready_bundle_builds_world_model(self) -> None:
        result = self.service.build(
            self.bundle,
            self.validity,
            readiness_id=self.readiness.readiness_id,
            model_id="wm-1",
        )
        self.assertIsInstance(result, EnvironmentWorldModel)
        self.assertEqual(result.environment_id, "env-1")
        self.assertEqual(result.state_by_domain["hardware"]["observed"]["cpu"]["cores"], 8)
        self.assertTrue(result.is_descriptive_only)

    def test_source_identity_and_lineage_are_preserved(self) -> None:
        result = self.service.build(
            self.bundle,
            self.validity,
            readiness_id="ready-1",
            model_id="wm-2",
            lineage={"source": {"bundle": "bundle-1"}},
        )
        self.assertEqual(result.source_bundle_id, "bundle-1")
        self.assertEqual(result.context_ids, ("ctx-1",))
        self.assertEqual(result.qualification_ids, ("qual-1",))
        self.assertEqual(result.provenance_ids, ("prov-1",))
        self.assertEqual(result.lineage["source"]["bundle"], "bundle-1")

    def test_missing_domains_remain_missing(self) -> None:
        result = self.service.build(self.bundle, self.validity, readiness_id="ready-1", model_id="wm-3")
        self.assertEqual(result.represented_domains, ("hardware",))
        self.assertIn("network", result.missing_domains)
        self.assertNotIn("network", result.state_by_domain)

    def test_stale_validity_is_rejected(self) -> None:
        stale = EnvironmentCurrentContextBundleValidity(
            bundle_id="bundle-1",
            environment_id="env-1",
            context_ids=("ctx-1",),
            observed_at=self.validity.observed_at,
            assessed_at=self.validity.assessed_at,
            max_age_seconds=30,
            freshness=CurrentContextFreshness.STALE,
            current_context_validities=(
                EnvironmentCurrentContextValidity(
                    context_id="ctx-1", environment_id="env-1", domain="hardware",
                    observed_at=self.validity.observed_at[0], assessed_at=self.validity.assessed_at,
                    max_age_seconds=30, freshness=CurrentContextFreshness.STALE,
                ),
            ),
        )
        with self.assertRaises(EnvironmentWorldModelError):
            self.service.build(self.bundle, stale, readiness_id="ready-1", model_id="wm-stale")

    def test_context_identity_mismatch_is_rejected(self) -> None:
        bad = EnvironmentCurrentContextBundleValidity(
            bundle_id="bundle-1", environment_id="env-1", context_ids=("ctx-other",),
            observed_at=self.validity.observed_at, assessed_at=self.validity.assessed_at,
            max_age_seconds=30, freshness=CurrentContextFreshness.CURRENT,
            current_context_validities=(
                EnvironmentCurrentContextValidity(
                    context_id="ctx-other", environment_id="env-1", domain="hardware",
                    observed_at=self.validity.observed_at[0], assessed_at=self.validity.assessed_at,
                    max_age_seconds=30, freshness=CurrentContextFreshness.CURRENT,
                ),
            ),
        )
        with self.assertRaises(EnvironmentWorldModelError):
            self.service.build(self.bundle, bad, readiness_id="ready-1", model_id="wm-bad")

    def test_bundle_environment_mismatch_is_rejected(self) -> None:
        bad = EnvironmentCurrentContextBundleValidity(
            bundle_id="bundle-1", environment_id="env-other", context_ids=("ctx-1",),
            observed_at=self.validity.observed_at, assessed_at=self.validity.assessed_at,
            max_age_seconds=30, freshness=CurrentContextFreshness.CURRENT,
            current_context_validities=self.validity.current_context_validities,
        )
        with self.assertRaises(EnvironmentWorldModelError):
            self.service.build(self.bundle, bad, readiness_id="ready-1", model_id="wm-bad-env")

    def test_model_is_immutable(self) -> None:
        result = self.service.build(self.bundle, self.validity, readiness_id="ready-1", model_id="wm-immutable")
        with self.assertRaises(TypeError):
            result.state_by_domain["hardware"]["observed"]["cpu"]["cores"] = 16
        with self.assertRaises(AttributeError):
            result.model_id = "changed"

    def test_lineage_is_immutable(self) -> None:
        result = self.service.build(
            self.bundle, self.validity, readiness_id="ready-1", model_id="wm-lineage",
            lineage={"source": {"kind": "ready-context"}},
        )
        with self.assertRaises(TypeError):
            result.lineage["source"]["kind"] = "changed"

    def test_model_has_no_authority_fields(self) -> None:
        result = self.service.build(self.bundle, self.validity, readiness_id="ready-1", model_id="wm-authority")
        forbidden = {
            "authority_granted", "authorization_granted", "execution_requested",
            "permission_granted", "truth_proven", "adaptation_truth_proven",
        }
        self.assertTrue(forbidden.isdisjoint(vars(result)))

    def test_input_bundle_is_not_mutated(self) -> None:
        before = self.bundle.data_by_domain["hardware"]["observed"]["cpu"]["cores"]
        _ = self.service.build(self.bundle, self.validity, readiness_id="ready-1", model_id="wm-no-mutation")
        after = self.bundle.data_by_domain["hardware"]["observed"]["cpu"]["cores"]
        self.assertEqual(before, 8)
        self.assertEqual(after, 8)


if __name__ == "__main__":
    unittest.main()
