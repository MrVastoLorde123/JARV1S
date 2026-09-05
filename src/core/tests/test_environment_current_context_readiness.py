import unittest

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


class EnvironmentCurrentContextReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle = EnvironmentCurrentContextBundle(
            bundle_id="bundle-1",
            environment_id="env-1",
            contexts=(),
            represented_domains=(),
            missing_domains=(),
            data_by_domain={},
            context_ids=(),
            qualification_ids=(),
            provenance_ids=(),
        )

    def _bundle_validity(self, freshness, per_context):
        return EnvironmentCurrentContextBundleValidity(
            bundle_id="bundle-1",
            environment_id="env-1",
            context_ids=("ctx-1",),
            observed_at=(),
            assessed_at=per_context[0].assessed_at,
            max_age_seconds=30,
            freshness=freshness,
            current_context_validities=tuple(per_context),
        )

    def test_requires_exact_bundle_and_validity_types(self):
        service = EnvironmentCurrentContextReadinessService()
        with self.assertRaises(TypeError):
            service.qualify(object(), object(), readiness_id="r1")

    def test_mismatched_bundle_identity_is_rejected(self):
        validity = EnvironmentCurrentContextBundleValidity(
            bundle_id="other",
            environment_id="env-1",
            context_ids=(),
            observed_at=(),
            assessed_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            max_age_seconds=30,
            freshness=CurrentContextFreshness.CURRENT,
            current_context_validities=(),
        )
        with self.assertRaises(EnvironmentCurrentContextReadinessError):
            EnvironmentCurrentContextReadinessService().qualify(self.bundle, validity, readiness_id="r1")

    def test_mismatched_context_identity_is_rejected(self):
        from datetime import datetime, timezone
        validity = EnvironmentCurrentContextBundleValidity(
            bundle_id="bundle-1",
            environment_id="env-1",
            context_ids=("ctx-other",),
            observed_at=(datetime(2026, 9, 5, tzinfo=timezone.utc),),
            assessed_at=datetime(2026, 9, 5, tzinfo=timezone.utc),
            max_age_seconds=30,
            freshness=CurrentContextFreshness.CURRENT,
            current_context_validities=(
                EnvironmentCurrentContextValidity(
                    context_id="ctx-other",
                    environment_id="env-1",
                    domain="hardware",
                    observed_at=datetime(2026, 9, 5, tzinfo=timezone.utc),
                    assessed_at=datetime(2026, 9, 5, tzinfo=timezone.utc),
                    max_age_seconds=30,
                    freshness=CurrentContextFreshness.CURRENT,
                ),
            ),
        )
        with self.assertRaises(EnvironmentCurrentContextReadinessError):
            EnvironmentCurrentContextReadinessService().qualify(self.bundle, validity, readiness_id="r1")

    def test_current_bundle_is_ready(self):
        from datetime import datetime, timezone
        dt = datetime(2026, 9, 5, tzinfo=timezone.utc)
        # Use a minimal valid bundle-like fixture assembled through real contexts.
        from src.core.environment_evidence_current_context import EnvironmentCurrentContext
        from src.core.environment_observation_evidence_qualification import EvidenceQualification
        context = EnvironmentCurrentContext(
            context_id="ctx-1", environment_id="env-1", domain="hardware", subject_kind="observation",
            data={"observed": {"cpu": "x86"}, "status": "qualified"},
            evidence_status=EvidenceQualification.USABLE, observation_ids=("obs-1",),
            adapter_ids=("adapter-1",), provenance_id="prov-1", qualification_id="qual-1",
        )
        bundle = EnvironmentCurrentContextBundle(
            bundle_id="bundle-1", environment_id="env-1", contexts=(context,),
            represented_domains=("hardware",), missing_domains=("software","network","models","capabilities","permissions","performance","costs","resources","metadata"),
            data_by_domain={"hardware": context.data}, context_ids=("ctx-1",), qualification_ids=("qual-1",), provenance_ids=("prov-1",),
        )
        validity = EnvironmentCurrentContextBundleValidity(
            bundle_id="bundle-1", environment_id="env-1", context_ids=("ctx-1",), observed_at=(dt,), assessed_at=dt,
            max_age_seconds=30, freshness=CurrentContextFreshness.CURRENT,
            current_context_validities=(EnvironmentCurrentContextValidity(
                context_id="ctx-1", environment_id="env-1", domain="hardware", observed_at=dt, assessed_at=dt,
                max_age_seconds=30, freshness=CurrentContextFreshness.CURRENT),),
        )
        result = EnvironmentCurrentContextReadinessService().qualify(bundle, validity, readiness_id="r-ready")
        self.assertIsInstance(result, EnvironmentCurrentContextReadiness)
        self.assertEqual(result.readiness, CurrentContextReadiness.READY)
        self.assertTrue(result.usable_for_world_model)

    def test_stale_bundle_is_not_ready(self):
        from datetime import datetime, timezone
        dt = datetime(2026, 9, 5, tzinfo=timezone.utc)
        from src.core.environment_evidence_current_context import EnvironmentCurrentContext
        from src.core.environment_observation_evidence_qualification import EvidenceQualification
        context = EnvironmentCurrentContext(
            context_id="ctx-1", environment_id="env-1", domain="hardware", subject_kind="observation",
            data={"observed": {"cpu": "x86"}, "status": "qualified"}, evidence_status=EvidenceQualification.USABLE,
            observation_ids=("obs-1",), adapter_ids=("adapter-1",), provenance_id="prov-1", qualification_id="qual-1")
        bundle = EnvironmentCurrentContextBundle(
            bundle_id="bundle-1", environment_id="env-1", contexts=(context,), represented_domains=("hardware",),
            missing_domains=("software","network","models","capabilities","permissions","performance","costs","resources","metadata"),
            data_by_domain={"hardware": context.data}, context_ids=("ctx-1",), qualification_ids=("qual-1",), provenance_ids=("prov-1",))
        stale = EnvironmentCurrentContextValidity(
            context_id="ctx-1", environment_id="env-1", domain="hardware", observed_at=dt, assessed_at=dt,
            max_age_seconds=30, freshness=CurrentContextFreshness.STALE)
        validity = EnvironmentCurrentContextBundleValidity(
            bundle_id="bundle-1", environment_id="env-1", context_ids=("ctx-1",), observed_at=(dt,), assessed_at=dt,
            max_age_seconds=30, freshness=CurrentContextFreshness.STALE, current_context_validities=(stale,))
        result = EnvironmentCurrentContextReadinessService().qualify(bundle, validity, readiness_id="r-stale")
        self.assertEqual(result.readiness, CurrentContextReadiness.STALE)
        self.assertFalse(result.usable_for_world_model)

    def test_future_bundle_is_not_ready(self):
        from datetime import datetime, timezone
        dt = datetime(2026, 9, 5, tzinfo=timezone.utc)
        from src.core.environment_evidence_current_context import EnvironmentCurrentContext
        from src.core.environment_observation_evidence_qualification import EvidenceQualification
        context = EnvironmentCurrentContext(
            context_id="ctx-1", environment_id="env-1", domain="hardware", subject_kind="observation",
            data={"observed": {"cpu": "x86"}, "status": "qualified"}, evidence_status=EvidenceQualification.USABLE,
            observation_ids=("obs-1",), adapter_ids=("adapter-1",), provenance_id="prov-1", qualification_id="qual-1")
        bundle = EnvironmentCurrentContextBundle(
            bundle_id="bundle-1", environment_id="env-1", contexts=(context,), represented_domains=("hardware",),
            missing_domains=("software","network","models","capabilities","permissions","performance","costs","resources","metadata"),
            data_by_domain={"hardware": context.data}, context_ids=("ctx-1",), qualification_ids=("qual-1",), provenance_ids=("prov-1",))
        future = EnvironmentCurrentContextValidity(
            context_id="ctx-1", environment_id="env-1", domain="hardware", observed_at=dt, assessed_at=dt,
            max_age_seconds=30, freshness=CurrentContextFreshness.FUTURE)
        validity = EnvironmentCurrentContextBundleValidity(
            bundle_id="bundle-1", environment_id="env-1", context_ids=("ctx-1",), observed_at=(dt,), assessed_at=dt,
            max_age_seconds=30, freshness=CurrentContextFreshness.FUTURE, current_context_validities=(future,))
        result = EnvironmentCurrentContextReadinessService().qualify(bundle, validity, readiness_id="r-future")
        self.assertEqual(result.readiness, CurrentContextReadiness.FUTURE)
        self.assertFalse(result.usable_for_world_model)

    def test_invalid_bundle_is_not_ready(self):
        from datetime import datetime, timezone
        dt = datetime(2026, 9, 5, tzinfo=timezone.utc)
        from src.core.environment_evidence_current_context import EnvironmentCurrentContext
        from src.core.environment_observation_evidence_qualification import EvidenceQualification
        context = EnvironmentCurrentContext(
            context_id="ctx-1", environment_id="env-1", domain="hardware", subject_kind="observation",
            data={"observed": {"cpu": "x86"}, "status": "qualified"}, evidence_status=EvidenceQualification.USABLE,
            observation_ids=("obs-1",), adapter_ids=("adapter-1",), provenance_id="prov-1", qualification_id="qual-1")
        bundle = EnvironmentCurrentContextBundle(
            bundle_id="bundle-1", environment_id="env-1", contexts=(context,), represented_domains=("hardware",),
            missing_domains=("software","network","models","capabilities","permissions","performance","costs","resources","metadata"),
            data_by_domain={"hardware": context.data}, context_ids=("ctx-1",), qualification_ids=("qual-1",), provenance_ids=("prov-1",))
        invalid = EnvironmentCurrentContextValidity(
            context_id="ctx-1", environment_id="env-1", domain="hardware", observed_at=dt, assessed_at=dt,
            max_age_seconds=30, freshness=CurrentContextFreshness.INVALID)
        validity = EnvironmentCurrentContextBundleValidity(
            bundle_id="bundle-1", environment_id="env-1", context_ids=("ctx-1",), observed_at=(dt,), assessed_at=dt,
            max_age_seconds=30, freshness=CurrentContextFreshness.INVALID, current_context_validities=(invalid,))
        result = EnvironmentCurrentContextReadinessService().qualify(bundle, validity, readiness_id="r-invalid")
        self.assertEqual(result.readiness, CurrentContextReadiness.INVALID)
        self.assertFalse(result.usable_for_world_model)

    def test_lineage_and_result_are_immutable(self):
        from datetime import datetime, timezone
        dt = datetime(2026, 9, 5, tzinfo=timezone.utc)
        from src.core.environment_evidence_current_context import EnvironmentCurrentContext
        from src.core.environment_observation_evidence_qualification import EvidenceQualification
        context = EnvironmentCurrentContext(
            context_id="ctx-1", environment_id="env-1", domain="hardware", subject_kind="observation",
            data={"observed": {}, "status": "qualified"}, evidence_status=EvidenceQualification.USABLE,
            observation_ids=("obs-1",), adapter_ids=("adapter-1",), provenance_id="prov-1", qualification_id="qual-1")
        bundle = EnvironmentCurrentContextBundle(
            bundle_id="bundle-1", environment_id="env-1", contexts=(context,), represented_domains=("hardware",),
            missing_domains=("software","network","models","capabilities","permissions","performance","costs","resources","metadata"),
            data_by_domain={"hardware": context.data}, context_ids=("ctx-1",), qualification_ids=("qual-1",), provenance_ids=("prov-1",))
        validity = EnvironmentCurrentContextBundleValidity(
            bundle_id="bundle-1", environment_id="env-1", context_ids=("ctx-1",), observed_at=(dt,), assessed_at=dt,
            max_age_seconds=30, freshness=CurrentContextFreshness.CURRENT,
            current_context_validities=(EnvironmentCurrentContextValidity(
                context_id="ctx-1", environment_id="env-1", domain="hardware", observed_at=dt, assessed_at=dt,
                max_age_seconds=30, freshness=CurrentContextFreshness.CURRENT),),
        )
        result = EnvironmentCurrentContextReadinessService().qualify(bundle, validity, readiness_id="r-immutable", lineage={"source": {"kind": "context-freshness"}})
        self.assertEqual(result.lineage["source"]["kind"], "context-freshness")
        with self.assertRaises(TypeError):
            result.lineage["source"]["kind"] = "changed"
        with self.assertRaises(AttributeError):
            result.readiness = CurrentContextReadiness.STALE

    def test_result_has_no_authority_fields(self):
        from datetime import datetime, timezone
        dt = datetime(2026, 9, 5, tzinfo=timezone.utc)
        from src.core.environment_evidence_current_context import EnvironmentCurrentContext
        from src.core.environment_observation_evidence_qualification import EvidenceQualification
        context = EnvironmentCurrentContext(
            context_id="ctx-1", environment_id="env-1", domain="hardware", subject_kind="observation",
            data={"observed": {}, "status": "qualified"}, evidence_status=EvidenceQualification.USABLE,
            observation_ids=("obs-1",), adapter_ids=("adapter-1",), provenance_id="prov-1", qualification_id="qual-1")
        bundle = EnvironmentCurrentContextBundle(
            bundle_id="bundle-1", environment_id="env-1", contexts=(context,), represented_domains=("hardware",),
            missing_domains=("software","network","models","capabilities","permissions","performance","costs","resources","metadata"),
            data_by_domain={"hardware": context.data}, context_ids=("ctx-1",), qualification_ids=("qual-1",), provenance_ids=("prov-1",))
        validity = EnvironmentCurrentContextBundleValidity(
            bundle_id="bundle-1", environment_id="env-1", context_ids=("ctx-1",), observed_at=(dt,), assessed_at=dt,
            max_age_seconds=30, freshness=CurrentContextFreshness.CURRENT,
            current_context_validities=(EnvironmentCurrentContextValidity(
                context_id="ctx-1", environment_id="env-1", domain="hardware", observed_at=dt, assessed_at=dt,
                max_age_seconds=30, freshness=CurrentContextFreshness.CURRENT),),
        )
        result = EnvironmentCurrentContextReadinessService().qualify(bundle, validity, readiness_id="r-authority")
        forbidden = {"authority_granted", "authorization_granted", "execution_requested", "permission_granted", "truth_proven", "adaptation_truth_proven"}
        self.assertTrue(forbidden.isdisjoint(vars(result)))
