import unittest
from datetime import datetime, timedelta, timezone

from src.core.environment_context_composition import (
    EnvironmentContextCompositionService,
    EnvironmentCurrentContextBundle,
)
from src.core.environment_evidence_current_context import EnvironmentCurrentContext
from src.core.environment_observation_evidence_qualification import EvidenceQualification
from src.core.environment_current_context_freshness import (
    CurrentContextFreshness,
    EnvironmentCurrentContextBundleValidity,
    EnvironmentCurrentContextFreshnessError,
    EnvironmentCurrentContextFreshnessService,
    EnvironmentCurrentContextValidity,
)


class EnvironmentCurrentContextFreshnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 9, 5, 15, 0, tzinfo=timezone.utc)
        self.context = EnvironmentCurrentContext(
            context_id="ctx-1",
            environment_id="env-1",
            domain="hardware",
            subject_kind="observation",
            data={"observed": {"cpu": {"cores": 8}}, "status": "qualified"},
            evidence_status=EvidenceQualification.USABLE,
            observation_ids=("obs-1",),
            adapter_ids=("sensor-a",),
            provenance_id="prov-1",
            qualification_id="qual-1",
        )
        self.service = EnvironmentCurrentContextFreshnessService()

    def test_current_context_is_current(self) -> None:
        result = self.service.assess_context(
            self.context,
            observed_at=self.now - timedelta(seconds=5),
            assessed_at=self.now,
            max_age_seconds=30,
        )
        self.assertIsInstance(result, EnvironmentCurrentContextValidity)
        self.assertEqual(result.freshness, CurrentContextFreshness.CURRENT)
        self.assertTrue(result.usable_as_current)
        self.assertEqual(result.age_seconds, 5.0)

    def test_stale_context_is_not_usable(self) -> None:
        result = self.service.assess_context(
            self.context,
            observed_at=self.now - timedelta(seconds=60),
            assessed_at=self.now,
            max_age_seconds=30,
        )
        self.assertEqual(result.freshness, CurrentContextFreshness.STALE)
        self.assertFalse(result.usable_as_current)

    def test_future_context_is_not_usable(self) -> None:
        result = self.service.assess_context(
            self.context,
            observed_at=self.now + timedelta(seconds=5),
            assessed_at=self.now,
            max_age_seconds=30,
        )
        self.assertEqual(result.freshness, CurrentContextFreshness.FUTURE)
        self.assertFalse(result.usable_as_current)

    def test_naive_observed_timestamp_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.service.assess_context(
                self.context,
                observed_at=datetime(2026, 9, 5, 14, 59, 55),
                assessed_at=self.now,
                max_age_seconds=30,
            )

    def test_naive_assessed_timestamp_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.service.assess_context(
                self.context,
                observed_at=self.now - timedelta(seconds=5),
                assessed_at=datetime(2026, 9, 5, 15, 0),
                max_age_seconds=30,
            )

    def test_negative_age_policy_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.service.assess_context(
                self.context,
                observed_at=self.now,
                assessed_at=self.now,
                max_age_seconds=-1,
            )

    def test_boolean_age_policy_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.service.assess_context(
                self.context,
                observed_at=self.now,
                assessed_at=self.now,
                max_age_seconds=True,
            )

    def test_timestamp_is_normalized_to_utc(self) -> None:
        offset = timezone(timedelta(hours=-3))
        result = self.service.assess_context(
            self.context,
            observed_at=(self.now - timedelta(seconds=5)).astimezone(offset),
            assessed_at=self.now.astimezone(offset),
            max_age_seconds=30,
        )
        self.assertEqual(result.observed_at, self.now - timedelta(seconds=5))
        self.assertEqual(result.assessed_at, self.now)

    def test_context_validity_is_immutable_and_lineage_preserves_mapping(self) -> None:
        result = self.service.assess_context(
            self.context,
            observed_at=self.now - timedelta(seconds=5),
            assessed_at=self.now,
            max_age_seconds=30,
            lineage={"source": {"context_id": "ctx-1"}},
        )
        self.assertEqual(result.lineage["source"]["context_id"], "ctx-1")
        with self.assertRaises(TypeError):
            result.lineage["source"]["context_id"] = "changed"
        with self.assertRaises(AttributeError):
            result.freshness = CurrentContextFreshness.STALE

    def test_assess_bundle_requires_one_timestamp_per_context(self) -> None:
        bundle = EnvironmentCurrentContextBundle(
            bundle_id="bundle-1",
            environment_id="env-1",
            contexts=(self.context,),
            represented_domains=("hardware",),
            missing_domains=(
                "software", "network", "models", "capabilities", "permissions",
                "performance", "costs", "resources", "metadata",
            ),
            data_by_domain={"hardware": self.context.data},
            context_ids=("ctx-1",),
            qualification_ids=("qual-1",),
            provenance_ids=("prov-1",),
        )
        with self.assertRaises(EnvironmentCurrentContextFreshnessError):
            self.service.assess_bundle(
                bundle,
                (),
                assessed_at=self.now,
                max_age_seconds=30,
            )

    def test_bundle_with_all_current_contexts_is_current(self) -> None:
        second = EnvironmentCurrentContext(
            context_id="ctx-2",
            environment_id="env-1",
            domain="software",
            subject_kind="observation",
            data={"observed": {"python": "3.13"}, "status": "qualified"},
            evidence_status=EvidenceQualification.USABLE,
            observation_ids=("obs-2",),
            adapter_ids=("software-a",),
            provenance_id="prov-2",
            qualification_id="qual-2",
        )
        bundle = EnvironmentContextCompositionService().compose(
            (self.context, second),
            bundle_id="bundle-current",
        )
        result = self.service.assess_bundle(
            bundle,
            (self.now - timedelta(seconds=5), self.now - timedelta(seconds=10)),
            assessed_at=self.now,
            max_age_seconds=30,
        )
        self.assertIsInstance(result, EnvironmentCurrentContextBundleValidity)
        self.assertEqual(result.freshness, CurrentContextFreshness.CURRENT)
        self.assertTrue(result.usable_as_current)
        self.assertEqual(result.context_ids, ("ctx-1", "ctx-2"))

    def test_bundle_with_one_stale_context_is_stale(self) -> None:
        second = EnvironmentCurrentContext(
            context_id="ctx-2",
            environment_id="env-1",
            domain="software",
            subject_kind="observation",
            data={"observed": {"python": "3.13"}, "status": "qualified"},
            evidence_status=EvidenceQualification.USABLE,
            observation_ids=("obs-2",),
            adapter_ids=("software-a",),
            provenance_id="prov-2",
            qualification_id="qual-2",
        )
        bundle = EnvironmentContextCompositionService().compose(
            (self.context, second),
            bundle_id="bundle-stale",
        )
        result = self.service.assess_bundle(
            bundle,
            (self.now - timedelta(seconds=5), self.now - timedelta(seconds=60)),
            assessed_at=self.now,
            max_age_seconds=30,
        )
        self.assertEqual(result.freshness, CurrentContextFreshness.STALE)
        self.assertFalse(result.usable_as_current)

    def test_bundle_preserves_order_and_source_lineage(self) -> None:
        second = EnvironmentCurrentContext(
            context_id="ctx-2",
            environment_id="env-1",
            domain="software",
            subject_kind="observation",
            data={"observed": {"python": "3.13"}, "status": "qualified"},
            evidence_status=EvidenceQualification.USABLE,
            observation_ids=("obs-2",),
            adapter_ids=("software-a",),
            provenance_id="prov-2",
            qualification_id="qual-2",
        )
        bundle = EnvironmentContextCompositionService().compose(
            (self.context, second),
            bundle_id="bundle-order",
        )
        result = self.service.assess_bundle(
            bundle,
            (self.now - timedelta(seconds=5), self.now - timedelta(seconds=10)),
            assessed_at=self.now,
            max_age_seconds=30,
            lineage={"source": {"bundle_id": "bundle-order"}},
        )
        self.assertEqual(tuple(item.context_id for item in result.current_context_validities), ("ctx-1", "ctx-2"))
        self.assertEqual(result.lineage["source"]["bundle_id"], "bundle-order")

    def test_result_has_no_authority_fields(self) -> None:
        result = self.service.assess_context(
            self.context,
            observed_at=self.now - timedelta(seconds=5),
            assessed_at=self.now,
            max_age_seconds=30,
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


if __name__ == "__main__":
    unittest.main()
