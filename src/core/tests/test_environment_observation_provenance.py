import unittest
from datetime import datetime, timezone
from types import MappingProxyType

from src.core.environment_observation import EnvironmentObservation
from src.core.environment_observation_aggregation import EnvironmentObservationAggregate
from src.core.environment_observation_provenance import EnvironmentObservationProvenance, EnvironmentObservationProvenanceService


UTC = timezone.utc
OBSERVED = datetime(2026, 9, 5, 12, 0, tzinfo=UTC)
RECORDED = datetime(2026, 9, 5, 12, 1, tzinfo=UTC)


def observation(observation_id="obs-1", adapter_id="reader", payload=None):
    return EnvironmentObservation(
        observation_id=observation_id,
        adapter_id=adapter_id,
        environment_id="env-1",
        domain="hardware",
        payload=payload or {"cpu": {"cores": 8}},
    )


class EnvironmentObservationProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.service = EnvironmentObservationProvenanceService()

    def test_from_observation_preserves_source_identity(self):
        result = self.service.from_observation(
            observation("obs-source", "hardware-reader"),
            observed_at=OBSERVED,
            recorded_at=RECORDED,
            provenance_id="prov-1",
        )
        self.assertIsInstance(result, EnvironmentObservationProvenance)
        self.assertEqual(result.observation_ids, ("obs-source",))
        self.assertEqual(result.adapter_ids, ("hardware-reader",))
        self.assertEqual(result.environment_id, "env-1")
        self.assertEqual(result.domain, "hardware")

    def test_from_observation_supports_assessment_and_lineage(self):
        result = self.service.from_observation(
            observation(),
            observed_at=OBSERVED,
            recorded_at=RECORDED,
            provenance_id="prov-1",
            assessment_id="assessment-1",
            lineage={"parent": {"source": "sensor"}},
        )
        self.assertEqual(result.assessment_id, "assessment-1")
        self.assertEqual(result.lineage["parent"]["source"], "sensor")

    def test_from_observation_requires_aware_timestamps(self):
        with self.assertRaises(ValueError):
            self.service.from_observation(
                observation(),
                observed_at=datetime(2026, 9, 5, 12, 0),
                recorded_at=RECORDED,
                provenance_id="prov-1",
            )
        with self.assertRaises(ValueError):
            self.service.from_observation(
                observation(),
                observed_at=OBSERVED,
                recorded_at=datetime(2026, 9, 5, 12, 1),
                provenance_id="prov-1",
            )

    def test_timestamps_are_normalized_to_utc(self):
        offset = timezone.utc
        result = self.service.from_observation(
            observation(),
            observed_at=OBSERVED,
            recorded_at=RECORDED,
            provenance_id="prov-1",
        )
        self.assertEqual(result.observed_at[0].tzinfo, offset)
        self.assertEqual(result.recorded_at.tzinfo, offset)

    def test_lineage_is_immutable(self):
        lineage = {"source": {"kind": "sensor"}}
        result = self.service.from_observation(
            observation(),
            observed_at=OBSERVED,
            recorded_at=RECORDED,
            provenance_id="prov-1",
            lineage=lineage,
        )
        self.assertEqual(result.lineage["source"]["kind"], "sensor")
        lineage["source"]["kind"] = "changed"
        self.assertEqual(result.lineage["source"]["kind"], "sensor")

    def test_result_is_immutable(self):
        result = self.service.from_observation(
            observation(), observed_at=OBSERVED, recorded_at=RECORDED, provenance_id="prov-1"
        )
        with self.assertRaises((AttributeError, TypeError)):
            result.provenance_id = "changed"

    def test_from_aggregate_preserves_all_sources(self):
        aggregate = EnvironmentObservationAggregate(
            environment_id="env-1",
            domain="hardware",
            payload={"cpu": {"cores": 8}},
            observation_ids=("obs-1", "obs-2"),
            adapter_ids=("reader-a", "reader-b"),
            observed_at=(OBSERVED, OBSERVED),
        )
        result = self.service.from_aggregate(
            aggregate,
            recorded_at=RECORDED,
            provenance_id="prov-aggregate",
            assessment_id="assessment-2",
        )
        self.assertEqual(result.observation_ids, ("obs-1", "obs-2"))
        self.assertEqual(result.adapter_ids, ("reader-a", "reader-b"))
        self.assertEqual(result.assessment_id, "assessment-2")

    def test_wrong_observation_type_is_rejected(self):
        with self.assertRaises(TypeError):
            self.service.from_observation(
                object(), observed_at=OBSERVED, recorded_at=RECORDED, provenance_id="prov-1"
            )

    def test_wrong_aggregate_type_is_rejected(self):
        with self.assertRaises(TypeError):
            self.service.from_aggregate(
                object(), recorded_at=RECORDED, provenance_id="prov-1"
            )

    def test_duplicate_source_ids_are_rejected(self):
        with self.assertRaises(ValueError):
            EnvironmentObservationProvenance(
                provenance_id="prov-1",
                observation_ids=("obs-1", "obs-1"),
                adapter_ids=("a", "b"),
                environment_id="env-1",
                domain="hardware",
                observed_at=(OBSERVED, OBSERVED),
                recorded_at=RECORDED,
            )

    def test_misaligned_source_metadata_is_rejected(self):
        with self.assertRaises(ValueError):
            EnvironmentObservationProvenance(
                provenance_id="prov-1",
                observation_ids=("obs-1", "obs-2"),
                adapter_ids=("a",),
                environment_id="env-1",
                domain="hardware",
                observed_at=(OBSERVED, OBSERVED),
                recorded_at=RECORDED,
            )

    def test_provenance_has_no_authority_fields(self):
        result = self.service.from_observation(
            observation(), observed_at=OBSERVED, recorded_at=RECORDED, provenance_id="prov-1"
        )
        self.assertFalse(hasattr(result, "authorization_granted"))
        self.assertFalse(hasattr(result, "authority_granted"))


if __name__ == "__main__":
    unittest.main()
