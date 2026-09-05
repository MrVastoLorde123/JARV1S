import unittest
from datetime import datetime, timedelta, timezone
from types import MappingProxyType

from src.core.environment_observation import EnvironmentObservation
from src.core.environment_observation_aggregation import (
    EnvironmentObservationAggregationError,
    EnvironmentObservationAggregationService,
)
from src.core.environment_observation_freshness import EnvironmentObservationValidity, ObservationFreshness

UTC = timezone.utc


class EnvironmentObservationAggregationTests(unittest.TestCase):
    def setUp(self):
        self.assessed_at = datetime(2026, 9, 5, 12, 0, tzinfo=UTC)
        self.service = EnvironmentObservationAggregationService()
        self.first = EnvironmentObservation(
            observation_id="obs-1",
            adapter_id="reader-a",
            environment_id="env-1",
            domain="hardware",
            payload={"cpu": {"cores": 8}, "gpu": "rtx"},
        )
        self.second = EnvironmentObservation(
            observation_id="obs-2",
            adapter_id="reader-b",
            environment_id="env-1",
            domain="hardware",
            payload={"gpu": "rtx", "cpu": {"cores": 8}},
        )

    def validity(self, observation, seconds=5, freshness=ObservationFreshness.CURRENT):
        return EnvironmentObservationValidity(
            observation_id=observation.observation_id,
            environment_id=observation.environment_id,
            domain=observation.domain,
            observed_at=self.assessed_at - timedelta(seconds=seconds),
            assessed_at=self.assessed_at,
            max_age_seconds=30,
            freshness=freshness,
        )

    def test_aggregate_accepts_current_consistent_observations(self):
        result = self.service.aggregate(
            [self.first, self.second],
            [self.validity(self.first), self.validity(self.second, 10)],
        )
        self.assertEqual(result.environment_id, "env-1")
        self.assertEqual(result.domain, "hardware")
        self.assertEqual(result.payload["cpu"]["cores"], 8)
        self.assertEqual(result.observation_ids, ("obs-1", "obs-2"))
        self.assertEqual(result.adapter_ids, ("reader-a", "reader-b"))

    def test_aggregate_payload_is_recursively_immutable(self):
        result = self.service.aggregate(
            [self.first, self.second],
            [self.validity(self.first), self.validity(self.second)],
        )
        self.assertIsInstance(result.payload, MappingProxyType)
        self.assertIsInstance(result.payload["cpu"], MappingProxyType)
        with self.assertRaises(TypeError):
            result.payload["cpu"]["cores"] = 16

    def test_conflicting_observations_are_rejected(self):
        conflict = EnvironmentObservation(
            observation_id="obs-3",
            adapter_id="reader-c",
            environment_id="env-1",
            domain="hardware",
            payload={"cpu": {"cores": 16}, "gpu": "rtx"},
        )
        with self.assertRaisesRegex(EnvironmentObservationAggregationError, "conflicting"):
            self.service.aggregate(
                [self.first, conflict],
                [self.validity(self.first), self.validity(conflict)],
            )

    def test_stale_observation_is_rejected(self):
        with self.assertRaisesRegex(EnvironmentObservationAggregationError, "CURRENT"):
            self.service.aggregate(
                [self.first, self.second],
                [self.validity(self.first), self.validity(self.second, freshness=ObservationFreshness.STALE)],
            )

    def test_future_observation_is_rejected(self):
        with self.assertRaisesRegex(EnvironmentObservationAggregationError, "CURRENT"):
            self.service.aggregate(
                [self.first, self.second],
                [self.validity(self.first), self.validity(self.second, freshness=ObservationFreshness.FUTURE)],
            )

    def test_at_least_two_observations_are_required(self):
        with self.assertRaises(EnvironmentObservationAggregationError):
            self.service.aggregate([self.first], [self.validity(self.first)])

    def test_lengths_must_match(self):
        with self.assertRaises(EnvironmentObservationAggregationError):
            self.service.aggregate([self.first, self.second], [self.validity(self.first)])

    def test_duplicate_observation_ids_are_rejected(self):
        duplicate = EnvironmentObservation(
            observation_id="obs-1",
            adapter_id="reader-b",
            environment_id="env-1",
            domain="hardware",
            payload={"cpu": {"cores": 8}, "gpu": "rtx"},
        )
        with self.assertRaises(EnvironmentObservationAggregationError):
            self.service.aggregate(
                [self.first, duplicate],
                [self.validity(self.first), self.validity(duplicate)],
            )

    def test_scope_must_match(self):
        other = EnvironmentObservation(
            observation_id="obs-4",
            adapter_id="reader-d",
            environment_id="env-2",
            domain="hardware",
            payload={"cpu": {"cores": 8}, "gpu": "rtx"},
        )
        with self.assertRaises(EnvironmentObservationAggregationError):
            self.service.aggregate(
                [self.first, other],
                [self.validity(self.first), self.validity(other)],
            )

    def test_validity_identity_must_match(self):
        other_id = EnvironmentObservationValidity(
            observation_id="obs-x",
            environment_id="env-1",
            domain="hardware",
            observed_at=self.assessed_at,
            assessed_at=self.assessed_at,
            max_age_seconds=30,
            freshness=ObservationFreshness.CURRENT,
        )
        with self.assertRaises(EnvironmentObservationAggregationError):
            self.service.aggregate([self.first, self.second], [self.validity(self.first), other_id])

    def test_invalid_observation_type_is_rejected(self):
        with self.assertRaises(TypeError):
            self.service.aggregate(
                [self.first, object()],
                [self.validity(self.first), self.validity(self.second)],
            )

    def test_invalid_validity_type_is_rejected(self):
        with self.assertRaises(TypeError):
            self.service.aggregate([self.first, self.second], [self.validity(self.first), object()])

    def test_aggregation_does_not_mutate_sources(self):
        first_payload = self.first.payload
        second_payload = self.second.payload
        self.service.aggregate(
            [self.first, self.second],
            [self.validity(self.first), self.validity(self.second)],
        )
        self.assertIs(self.first.payload, first_payload)
        self.assertIs(self.second.payload, second_payload)


if __name__ == "__main__":
    unittest.main()
