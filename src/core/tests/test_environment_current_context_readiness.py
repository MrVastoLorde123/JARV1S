import unittest
from datetime import datetime, timezone

from src.core.environment_context_composition import EnvironmentCurrentContextBundle
from src.core.environment_current_context_freshness import (
    CurrentContextFreshness,
    EnvironmentCurrentContextBundleValidity,
    EnvironmentCurrentContextValidity,
)
from src.core.environment_current_context_readiness import (
    CurrentContextReadiness,
    EnvironmentCurrentContextReadiness,
    EnvironmentCurrentContextReadinessError,
    EnvironmentCurrentContextReadinessService,
)
from src.core.environment_evidence_current_context import EnvironmentCurrentContext
from src.core.environment_observation import ENVIRONMENT_DOMAINS
from src.core.environment_observation_evidence_qualification import EvidenceQualification


class EnvironmentCurrentContextReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 9, 5, 15, 0, tzinfo=timezone.utc)
        self.context = EnvironmentCurrentContext(
            context_id="ctx-1",
            environment_id="env-1",
            domain="hardware",
            subject_kind="observation",
            data={"observed": {"cpu": "x86"}, "status": "qualified"},
            evidence_status=EvidenceQualification.USABLE,
            observation_ids=("obs-1",),
            adapter_ids=("adapter-1",),
            provenance_id="prov-1",
            qualification_id="qual-1",
        )
        represented = ("hardware",)
        missing = tuple(domain for domain in ENVIRONMENT_DOMAINS if domain not in represented)
        self.bundle = EnvironmentCurrentContextBundle(
            bundle_id="bundle-1",
            environment_id="env-1",
            contexts=(self.context,),
            represented_domains=represented,
            missing_domains=missing,
            data_by_domain={"hardware": self.context.data},
            context_ids=("ctx-1",),
            qualification_ids=("qual-1",),
            provenance_ids=("prov-1",),
        )
        self.service = EnvironmentCurrentContextReadinessService()

    def _validity(self, freshness: CurrentContextFreshness) -> EnvironmentCurrentContextBundleValidity:
        per_context = EnvironmentCurrentContextValidity(
            context_id="ctx-1",
            environment_id="env-1",
            domain="hardware",
            observed_at=self.now,
            assessed_at=self.now,
            max_age_seconds=30,
            freshness=freshness,
        )
        return EnvironmentCurrentContextBundleValidity(
            bundle_id="bundle-1",
            environment_id="env-1",
            context_ids=("ctx-1",),
            observed_at=(self.now,),
            assessed_at=self.now,
            max_age_seconds=30,
            freshness=freshness,
            current_context_validities=(per_context,),
        )

    def test_current_bundle_is_ready(self):
        result = self.service.qualify(self.bundle, self._validity(CurrentContextFreshness.CURRENT), readiness_id="r-ready")
        self.assertIsInstance(result, EnvironmentCurrentContextReadiness)
        self.assertEqual(result.readiness, CurrentContextReadiness.READY)
        self.assertTrue(result.usable_for_world_model)
        self.assertEqual(result.context_ids, ("ctx-1",))

    def test_stale_bundle_is_not_ready(self):
        result = self.service.qualify(self.bundle, self._validity(CurrentContextFreshness.STALE), readiness_id="r-stale")
        self.assertEqual(result.readiness, CurrentContextReadiness.STALE)
        self.assertFalse(result.usable_for_world_model)

    def test_future_bundle_is_not_ready(self):
        result = self.service.qualify(self.bundle, self._validity(CurrentContextFreshness.FUTURE), readiness_id="r-future")
        self.assertEqual(result.readiness, CurrentContextReadiness.FUTURE)
        self.assertFalse(result.usable_for_world_model)

    def test_invalid_bundle_is_not_ready(self):
        result = self.service.qualify(self.bundle, self._validity(CurrentContextFreshness.INVALID), readiness_id="r-invalid")
        self.assertEqual(result.readiness, CurrentContextReadiness.INVALID)
        self.assertFalse(result.usable_for_world_model)

    def test_mismatched_bundle_identity_is_rejected(self):
        validity = self._validity(CurrentContextFreshness.CURRENT)
        mismatched = EnvironmentCurrentContextBundleValidity(
            bundle_id="other",
            environment_id=validity.environment_id,
            context_ids=validity.context_ids,
            observed_at=validity.observed_at,
            assessed_at=validity.assessed_at,
            max_age_seconds=validity.max_age_seconds,
            freshness=validity.freshness,
            current_context_validities=validity.current_context_validities,
        )
        with self.assertRaises(EnvironmentCurrentContextReadinessError):
            self.service.qualify(self.bundle, mismatched, readiness_id="r-bad-id")

    def test_mismatched_context_identity_is_rejected(self):
        validity = EnvironmentCurrentContextBundleValidity(
            bundle_id="bundle-1",
            environment_id="env-1",
            context_ids=("ctx-other",),
            observed_at=(self.now,),
            assessed_at=self.now,
            max_age_seconds=30,
            freshness=CurrentContextFreshness.CURRENT,
            current_context_validities=(EnvironmentCurrentContextValidity(
                context_id="ctx-other",
                environment_id="env-1",
                domain="hardware",
                observed_at=self.now,
                assessed_at=self.now,
                max_age_seconds=30,
                freshness=CurrentContextFreshness.CURRENT,
            ),),
        )
        with self.assertRaises(EnvironmentCurrentContextReadinessError):
            self.service.qualify(self.bundle, validity, readiness_id="r-bad-context")

    def test_result_preserves_lineage_and_is_immutable(self):
        result = self.service.qualify(
            self.bundle,
            self._validity(CurrentContextFreshness.CURRENT),
            readiness_id="r-lineage",
            lineage={"source": {"stage": "context-freshness"}},
        )
        self.assertEqual(result.lineage["source"]["stage"], "context-freshness")
        with self.assertRaises(TypeError):
            result.lineage["source"]["stage"] = "changed"
        with self.assertRaises(AttributeError):
            result.readiness = CurrentContextReadiness.STALE

    def test_result_has_no_authority_fields(self):
        result = self.service.qualify(self.bundle, self._validity(CurrentContextFreshness.CURRENT), readiness_id="r-authority")
        forbidden = {
            "authority_granted", "authorization_granted", "execution_requested",
            "permission_granted", "truth_proven", "adaptation_truth_proven",
        }
        self.assertTrue(forbidden.isdisjoint(vars(result)))

    def test_wrong_types_are_rejected(self):
        with self.assertRaises(TypeError):
            self.service.qualify(object(), object(), readiness_id="r-types")


if __name__ == "__main__":
    unittest.main()
