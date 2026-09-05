import unittest
from datetime import datetime, timedelta, timezone

from src.core.environment_observation import EnvironmentObservation
from src.core.environment_observation_aggregation import EnvironmentObservationAggregate
from src.core.environment_observation_consistency import EnvironmentObservationConsistencyService
from src.core.environment_observation_evidence_qualification import (
    EnvironmentObservationEvidenceQualificationService,
)
from src.core.environment_observation_freshness import EnvironmentObservationFreshnessService
from src.core.environment_observation_provenance import EnvironmentObservationProvenanceService
from src.core.environment_evidence_current_context import (
    EnvironmentCurrentContext,
    EnvironmentEvidenceCurrentContextError,
    EnvironmentEvidenceCurrentContextService,
)


class EnvironmentEvidenceCurrentContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 9, 5, 15, 0, tzinfo=timezone.utc)
        self.observation = EnvironmentObservation(
            observation_id="obs-1",
            adapter_id="sensor-a",
            environment_id="env-1",
            domain="hardware",
            payload={"cpu": {"arch": "x86", "cores": 8}},
        )
        self.validity = EnvironmentObservationFreshnessService().assess(
            self.observation,
            observed_at=self.now - timedelta(seconds=5),
            assessed_at=self.now,
            max_age_seconds=30,
        )
        self.provenance = EnvironmentObservationProvenanceService().from_observation(
            self.observation,
            observed_at=self.now - timedelta(seconds=5),
            recorded_at=self.now,
            provenance_id="prov-1",
        )
        self.qualification = EnvironmentObservationEvidenceQualificationService().qualify_observation(
            self.observation,
            self.validity,
            self.provenance,
            qualification_id="qual-1",
            qualified_at=self.now,
        )
        self.service = EnvironmentEvidenceCurrentContextService()

    def test_usable_observation_becomes_current_context(self) -> None:
        result = self.service.from_observation(
            self.observation,
            self.qualification,
            context_id="ctx-1",
        )
        self.assertIsInstance(result, EnvironmentCurrentContext)
        self.assertTrue(result.usable_for_reasoning)
        self.assertEqual(result.environment_id, "env-1")
        self.assertEqual(result.domain, "hardware")
        self.assertEqual(result.observation_ids, ("obs-1",))
        self.assertEqual(result.provenance_id, "prov-1")
        self.assertEqual(result.data["observed"]["cpu"]["cores"], 8)

    def test_non_usable_qualification_is_rejected(self) -> None:
        stale = EnvironmentObservationFreshnessService().assess(
            self.observation,
            observed_at=self.now - timedelta(seconds=60),
            assessed_at=self.now,
            max_age_seconds=30,
        )
        stale_provenance = EnvironmentObservationProvenanceService().from_observation(
            self.observation,
            observed_at=stale.observed_at,
            recorded_at=self.now,
            provenance_id="prov-stale",
        )
        qualification = EnvironmentObservationEvidenceQualificationService().qualify_observation(
            self.observation,
            stale,
            stale_provenance,
            qualification_id="qual-stale",
            qualified_at=self.now,
        )
        with self.assertRaises(EnvironmentEvidenceCurrentContextError):
            self.service.from_observation(self.observation, qualification, context_id="ctx-stale")

    def test_subject_kind_mismatch_is_rejected(self) -> None:
        second = EnvironmentObservation(
            observation_id="obs-2",
            adapter_id="sensor-b",
            environment_id="env-1",
            domain="hardware",
            payload={"cpu": {"arch": "x86", "cores": 8}},
        )
        second_validity = EnvironmentObservationFreshnessService().assess(
            second,
            observed_at=self.now - timedelta(seconds=5),
            assessed_at=self.now,
            max_age_seconds=30,
        )
        consistency = EnvironmentObservationConsistencyService().compare(self.observation, second)
        aggregate = EnvironmentObservationAggregate(
            environment_id="env-1",
            domain="hardware",
            payload=self.observation.payload,
            observation_ids=("obs-1", "obs-2"),
            adapter_ids=("sensor-a", "sensor-b"),
            observed_at=(self.validity.observed_at, second_validity.observed_at),
        )
        provenance = EnvironmentObservationProvenanceService().from_aggregate(
            aggregate,
            recorded_at=self.now,
            provenance_id="prov-aggregate",
        )
        aggregate_qualification = EnvironmentObservationEvidenceQualificationService().qualify_aggregate(
            aggregate,
            (self.validity, second_validity),
            (consistency,),
            provenance,
            qualification_id="qual-aggregate",
            qualified_at=self.now,
        )
        with self.assertRaises(EnvironmentEvidenceCurrentContextError):
            self.service.from_observation(self.observation, aggregate_qualification, context_id="ctx-bad-kind")

    def test_aggregate_context_preserves_all_lineage(self) -> None:
        second = EnvironmentObservation(
            observation_id="obs-2",
            adapter_id="sensor-b",
            environment_id="env-1",
            domain="hardware",
            payload={"cpu": {"arch": "x86", "cores": 8}},
        )
        second_validity = EnvironmentObservationFreshnessService().assess(
            second,
            observed_at=self.now - timedelta(seconds=7),
            assessed_at=self.now,
            max_age_seconds=30,
        )
        consistency = EnvironmentObservationConsistencyService().compare(self.observation, second)
        aggregate = EnvironmentObservationAggregate(
            environment_id="env-1",
            domain="hardware",
            payload=self.observation.payload,
            observation_ids=("obs-1", "obs-2"),
            adapter_ids=("sensor-a", "sensor-b"),
            observed_at=(self.validity.observed_at, second_validity.observed_at),
        )
        provenance = EnvironmentObservationProvenanceService().from_aggregate(
            aggregate,
            recorded_at=self.now,
            provenance_id="prov-aggregate",
        )
        qualification = EnvironmentObservationEvidenceQualificationService().qualify_aggregate(
            aggregate,
            (self.validity, second_validity),
            (consistency,),
            provenance,
            qualification_id="qual-aggregate",
            qualified_at=self.now,
            lineage={"source": {"stage": "aggregation"}},
        )
        result = self.service.from_aggregate(
            aggregate,
            qualification,
            context_id="ctx-aggregate",
        )
        self.assertEqual(result.observation_ids, ("obs-1", "obs-2"))
        self.assertEqual(result.adapter_ids, ("sensor-a", "sensor-b"))
        self.assertEqual(result.provenance_id, "prov-aggregate")
        self.assertEqual(result.qualification_id, "qual-aggregate")
        self.assertEqual(result.lineage["qualification_id"], "qual-aggregate")

    def test_qualification_scope_mismatch_is_rejected(self) -> None:
        other = EnvironmentObservation(
            observation_id="obs-other",
            adapter_id="sensor-other",
            environment_id="env-other",
            domain="hardware",
            payload={"cpu": {"arch": "x86", "cores": 8}},
        )
        other_validity = EnvironmentObservationFreshnessService().assess(
            other,
            observed_at=self.now - timedelta(seconds=5),
            assessed_at=self.now,
            max_age_seconds=30,
        )
        other_provenance = EnvironmentObservationProvenanceService().from_observation(
            other,
            observed_at=other_validity.observed_at,
            recorded_at=self.now,
            provenance_id="prov-other",
        )
        other_qualification = EnvironmentObservationEvidenceQualificationService().qualify_observation(
            other,
            other_validity,
            other_provenance,
            qualification_id="qual-other",
            qualified_at=self.now,
        )
        with self.assertRaises(EnvironmentEvidenceCurrentContextError):
            self.service.from_observation(self.observation, other_qualification, context_id="ctx-bad-scope")

    def test_context_data_and_lineage_are_immutable(self) -> None:
        result = self.service.from_observation(
            self.observation,
            self.qualification,
            context_id="ctx-immutable",
            lineage={"source": {"kind": "qualified-evidence"}},
        )
        with self.assertRaises(TypeError):
            result.data["observed"]["cpu"]["cores"] = 99
        with self.assertRaises(TypeError):
            result.lineage["source"]["kind"] = "changed"
        with self.assertRaises(AttributeError):
            result.data = {}

    def test_result_has_no_authority_fields(self) -> None:
        result = self.service.from_observation(self.observation, self.qualification, context_id="ctx-authority")
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
