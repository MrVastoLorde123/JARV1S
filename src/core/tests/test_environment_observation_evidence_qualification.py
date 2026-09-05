import unittest
from datetime import datetime, timedelta, timezone

from src.core.environment_observation import EnvironmentObservation
from src.core.environment_observation_aggregation import EnvironmentObservationAggregate
from src.core.environment_observation_consistency import (
    EnvironmentObservationConsistencyService,
    ObservationConsistency,
)
from src.core.environment_observation_evidence_qualification import (
    EvidenceQualification,
    EnvironmentObservationEvidenceQualification,
    EnvironmentObservationEvidenceQualificationError,
    EnvironmentObservationEvidenceQualificationService,
)
from src.core.environment_observation_freshness import (
    EnvironmentObservationFreshnessService,
    ObservationFreshness,
)
from src.core.environment_observation_provenance import EnvironmentObservationProvenanceService


class EnvironmentObservationEvidenceQualificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 9, 5, 15, 0, tzinfo=timezone.utc)
        self.observation = EnvironmentObservation(
            observation_id="obs-1",
            adapter_id="sensor-a",
            environment_id="env-1",
            domain="hardware",
            payload={"cpu": "x86"},
        )
        self.second_observation = EnvironmentObservation(
            observation_id="obs-2",
            adapter_id="sensor-b",
            environment_id="env-1",
            domain="hardware",
            payload={"cpu": "x86"},
        )
        self.freshness = EnvironmentObservationFreshnessService()
        self.provenance = EnvironmentObservationProvenanceService()
        self.service = EnvironmentObservationEvidenceQualificationService()
        self.validity = self.freshness.assess(
            self.observation,
            observed_at=self.now - timedelta(seconds=5),
            assessed_at=self.now,
            max_age_seconds=30,
        )
        self.provenance_record = self.provenance.from_observation(
            self.observation,
            observed_at=self.now - timedelta(seconds=5),
            recorded_at=self.now,
            provenance_id="prov-1",
        )

    def test_current_observation_is_usable(self) -> None:
        result = self.service.qualify_observation(
            self.observation,
            self.validity,
            self.provenance_record,
            qualification_id="qual-1",
            qualified_at=self.now,
        )
        self.assertEqual(result.qualification, EvidenceQualification.USABLE)
        self.assertTrue(result.usable_for_downstream_reasoning)
        self.assertEqual(result.observation_ids, ("obs-1",))
        self.assertEqual(result.adapter_ids, ("sensor-a",))
        self.assertEqual(result.validity, (ObservationFreshness.CURRENT,))
        self.assertEqual(result.consistency, ())

    def test_stale_observation_is_unusable(self) -> None:
        stale = self.freshness.assess(
            self.observation,
            observed_at=self.now - timedelta(seconds=60),
            assessed_at=self.now,
            max_age_seconds=30,
        )
        provenance = self.provenance.from_observation(
            self.observation,
            observed_at=self.now - timedelta(seconds=60),
            recorded_at=self.now,
            provenance_id="prov-stale",
        )
        result = self.service.qualify_observation(
            self.observation,
            stale,
            provenance,
            qualification_id="qual-stale",
            qualified_at=self.now,
        )
        self.assertEqual(result.qualification, EvidenceQualification.UNUSABLE)
        self.assertFalse(result.usable_for_downstream_reasoning)
        self.assertEqual(result.validity, (ObservationFreshness.STALE,))

    def test_observation_identity_mismatch_is_rejected(self) -> None:
        other_validity = self.freshness.assess(
            self.second_observation,
            observed_at=self.now - timedelta(seconds=5),
            assessed_at=self.now,
            max_age_seconds=30,
        )
        with self.assertRaises(EnvironmentObservationEvidenceQualificationError):
            self.service.qualify_observation(
                self.observation,
                other_validity,
                self.provenance_record,
                qualification_id="qual-bad",
                qualified_at=self.now,
            )

    def test_provenance_scope_mismatch_is_rejected(self) -> None:
        wrong = self.provenance.from_observation(
            EnvironmentObservation(
                observation_id="obs-other",
                adapter_id="sensor-other",
                environment_id="env-other",
                domain="hardware",
                payload={},
            ),
            observed_at=self.now - timedelta(seconds=5),
            recorded_at=self.now,
            provenance_id="prov-other",
        )
        with self.assertRaises(EnvironmentObservationEvidenceQualificationError):
            self.service.qualify_observation(
                self.observation,
                self.validity,
                wrong,
                qualification_id="qual-bad-provenance",
                qualified_at=self.now,
            )

    def test_aggregate_with_all_gates_pass_is_usable(self) -> None:
        second_validity = self.freshness.assess(
            self.second_observation,
            observed_at=self.now - timedelta(seconds=7),
            assessed_at=self.now,
            max_age_seconds=30,
        )
        aggregate = EnvironmentObservationAggregate(
            environment_id="env-1",
            domain="hardware",
            payload={"cpu": "x86"},
            observation_ids=("obs-1", "obs-2"),
            adapter_ids=("sensor-a", "sensor-b"),
            observed_at=(self.validity.observed_at, second_validity.observed_at),
        )
        consistency = EnvironmentObservationConsistencyService().compare(
            self.observation,
            self.second_observation,
        )
        provenance = self.provenance.from_aggregate(
            aggregate,
            recorded_at=self.now,
            provenance_id="prov-aggregate",
        )
        result = self.service.qualify_aggregate(
            aggregate,
            (self.validity, second_validity),
            (consistency,),
            provenance,
            qualification_id="qual-aggregate",
            qualified_at=self.now,
        )
        self.assertEqual(result.qualification, EvidenceQualification.USABLE)
        self.assertTrue(result.usable_for_downstream_reasoning)
        self.assertEqual(result.observation_ids, aggregate.observation_ids)
        self.assertEqual(result.adapter_ids, aggregate.adapter_ids)
        self.assertEqual(result.consistency, (ObservationConsistency.CONSISTENT,))

    def test_aggregate_with_missing_consistency_is_insufficient(self) -> None:
        second_validity = self.freshness.assess(
            self.second_observation,
            observed_at=self.now - timedelta(seconds=7),
            assessed_at=self.now,
            max_age_seconds=30,
        )
        aggregate = EnvironmentObservationAggregate(
            environment_id="env-1",
            domain="hardware",
            payload={"cpu": "x86"},
            observation_ids=("obs-1", "obs-2"),
            adapter_ids=("sensor-a", "sensor-b"),
            observed_at=(self.validity.observed_at, second_validity.observed_at),
        )
        provenance = self.provenance.from_aggregate(
            aggregate,
            recorded_at=self.now,
            provenance_id="prov-incomplete",
        )
        result = self.service.qualify_aggregate(
            aggregate,
            (self.validity, second_validity),
            (),
            provenance,
            qualification_id="qual-incomplete",
            qualified_at=self.now,
        )
        self.assertEqual(result.qualification, EvidenceQualification.INSUFFICIENT)
        self.assertFalse(result.usable_for_downstream_reasoning)

    def test_aggregate_with_conflict_is_conflicting(self) -> None:
        conflicting = EnvironmentObservation(
            observation_id="obs-2",
            adapter_id="sensor-b",
            environment_id="env-1",
            domain="hardware",
            payload={"cpu": "arm"},
        )
        second_validity = self.freshness.assess(
            conflicting,
            observed_at=self.now - timedelta(seconds=7),
            assessed_at=self.now,
            max_age_seconds=30,
        )
        aggregate = EnvironmentObservationAggregate(
            environment_id="env-1",
            domain="hardware",
            payload={"cpu": "x86"},
            observation_ids=("obs-1", "obs-2"),
            adapter_ids=("sensor-a", "sensor-b"),
            observed_at=(self.validity.observed_at, second_validity.observed_at),
        )
        consistency = EnvironmentObservationConsistencyService().compare(
            self.observation,
            conflicting,
        )
        provenance = self.provenance.from_aggregate(
            aggregate,
            recorded_at=self.now,
            provenance_id="prov-conflict",
        )
        result = self.service.qualify_aggregate(
            aggregate,
            (self.validity, second_validity),
            (consistency,),
            provenance,
            qualification_id="qual-conflict",
            qualified_at=self.now,
        )
        self.assertEqual(result.qualification, EvidenceQualification.CONFLICTING)
        self.assertEqual(result.consistency, (ObservationConsistency.CONFLICTING,))

    def test_aggregate_with_stale_source_is_unusable(self) -> None:
        stale = self.freshness.assess(
            self.second_observation,
            observed_at=self.now - timedelta(seconds=60),
            assessed_at=self.now,
            max_age_seconds=30,
        )
        aggregate = EnvironmentObservationAggregate(
            environment_id="env-1",
            domain="hardware",
            payload={"cpu": "x86"},
            observation_ids=("obs-1", "obs-2"),
            adapter_ids=("sensor-a", "sensor-b"),
            observed_at=(self.validity.observed_at, stale.observed_at),
        )
        consistency = EnvironmentObservationConsistencyService().compare(
            self.observation,
            self.second_observation,
        )
        provenance = self.provenance.from_aggregate(
            aggregate,
            recorded_at=self.now,
            provenance_id="prov-stale-aggregate",
        )
        result = self.service.qualify_aggregate(
            aggregate,
            (self.validity, stale),
            (consistency,),
            provenance,
            qualification_id="qual-stale-aggregate",
            qualified_at=self.now,
        )
        self.assertEqual(result.qualification, EvidenceQualification.UNUSABLE)

    def test_aggregate_consistency_pair_outside_sources_is_rejected(self) -> None:
        outside = EnvironmentObservationConsistencyService().compare(
            self.observation,
            EnvironmentObservation(
                observation_id="obs-3",
                adapter_id="sensor-c",
                environment_id="env-1",
                domain="hardware",
                payload={"cpu": "x86"},
            ),
        )
        second_validity = self.freshness.assess(
            self.second_observation,
            observed_at=self.now - timedelta(seconds=7),
            assessed_at=self.now,
            max_age_seconds=30,
        )
        aggregate = EnvironmentObservationAggregate(
            environment_id="env-1",
            domain="hardware",
            payload={"cpu": "x86"},
            observation_ids=("obs-1", "obs-2"),
            adapter_ids=("sensor-a", "sensor-b"),
            observed_at=(self.validity.observed_at, second_validity.observed_at),
        )
        provenance = self.provenance.from_aggregate(
            aggregate,
            recorded_at=self.now,
            provenance_id="prov-invalid-pair",
        )
        with self.assertRaises(EnvironmentObservationEvidenceQualificationError):
            self.service.qualify_aggregate(
                aggregate,
                (self.validity, second_validity),
                (outside,),
                provenance,
                qualification_id="qual-invalid-pair",
                qualified_at=self.now,
            )

    def test_qualification_is_immutable_and_lineage_preserves_mapping(self) -> None:
        result = self.service.qualify_observation(
            self.observation,
            self.validity,
            self.provenance_record,
            qualification_id="qual-immutable",
            qualified_at=self.now,
            lineage={"source": {"kind": "sensor"}},
        )
        self.assertIsInstance(result, EnvironmentObservationEvidenceQualification)
        self.assertEqual(result.lineage["source"]["kind"], "sensor")
        with self.assertRaises(TypeError):
            result.lineage["source"]["kind"] = "changed"
        with self.assertRaises(AttributeError):
            result.qualification = EvidenceQualification.CONFLICTING

    def test_qualified_timestamp_is_normalized_to_utc(self) -> None:
        offset = timezone(timedelta(hours=-3))
        local_time = self.now.astimezone(offset)
        result = self.service.qualify_observation(
            self.observation,
            self.validity,
            self.provenance_record,
            qualification_id="qual-time",
            qualified_at=local_time,
        )
        self.assertEqual(result.qualified_at, self.now)

    def test_result_has_no_authority_fields(self) -> None:
        result = self.service.qualify_observation(
            self.observation,
            self.validity,
            self.provenance_record,
            qualification_id="qual-authority",
            qualified_at=self.now,
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
