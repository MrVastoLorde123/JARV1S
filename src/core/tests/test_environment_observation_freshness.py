import unittest
from datetime import datetime, timedelta, timezone

from src.core.environment_observation import EnvironmentObservation
from src.core.environment_observation_freshness import (
    EnvironmentObservationFreshnessService,
    ObservationFreshness,
)


UTC = timezone.utc


def observation(observation_id="obs-1"):
    return EnvironmentObservation(
        observation_id=observation_id,
        adapter_id="reader",
        environment_id="env-1",
        domain="hardware",
        payload={"cpu": {"cores": 8}},
    )


class EnvironmentObservationFreshnessTests(unittest.TestCase):
    def setUp(self):
        self.service = EnvironmentObservationFreshnessService()
        self.assessed_at = datetime(2026, 9, 5, 12, 0, tzinfo=UTC)

    def test_current_observation_is_usable(self):
        result = self.service.assess(
            observation(),
            observed_at=self.assessed_at - timedelta(seconds=10),
            assessed_at=self.assessed_at,
            max_age_seconds=30,
        )
        self.assertIs(result.freshness, ObservationFreshness.CURRENT)
        self.assertTrue(result.usable_as_current)
        self.assertEqual(result.age_seconds, 10)

    def test_boundary_age_is_current(self):
        result = self.service.assess(
            observation(),
            observed_at=self.assessed_at - timedelta(seconds=30),
            assessed_at=self.assessed_at,
            max_age_seconds=30,
        )
        self.assertIs(result.freshness, ObservationFreshness.CURRENT)

    def test_stale_observation_is_not_usable_as_current(self):
        result = self.service.assess(
            observation(),
            observed_at=self.assessed_at - timedelta(seconds=31),
            assessed_at=self.assessed_at,
            max_age_seconds=30,
        )
        self.assertIs(result.freshness, ObservationFreshness.STALE)
        self.assertFalse(result.usable_as_current)

    def test_future_observation_is_not_usable(self):
        result = self.service.assess(
            observation(),
            observed_at=self.assessed_at + timedelta(seconds=1),
            assessed_at=self.assessed_at,
            max_age_seconds=30,
        )
        self.assertIs(result.freshness, ObservationFreshness.FUTURE)
        self.assertFalse(result.usable_as_current)
        self.assertEqual(result.age_seconds, -1)

    def test_zero_max_age_only_accepts_same_timestamp(self):
        result = self.service.assess(
            observation(),
            observed_at=self.assessed_at,
            assessed_at=self.assessed_at,
            max_age_seconds=0,
        )
        self.assertIs(result.freshness, ObservationFreshness.CURRENT)

    def test_negative_max_age_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.assess(
                observation(),
                observed_at=self.assessed_at,
                assessed_at=self.assessed_at,
                max_age_seconds=-1,
            )

    def test_naive_observed_at_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.assess(
                observation(),
                observed_at=datetime(2026, 9, 5, 12, 0),
                assessed_at=self.assessed_at,
                max_age_seconds=30,
            )

    def test_naive_assessed_at_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.assess(
                observation(),
                observed_at=self.assessed_at,
                assessed_at=datetime(2026, 9, 5, 12, 0),
                max_age_seconds=30,
            )

    def test_timezone_offsets_are_normalized(self):
        observed_at = datetime(2026, 9, 5, 14, 0, tzinfo=timezone(timedelta(hours=2)))
        result = self.service.assess(
            observation(),
            observed_at=observed_at,
            assessed_at=self.assessed_at,
            max_age_seconds=1,
        )
        self.assertIs(result.freshness, ObservationFreshness.CURRENT)
        self.assertEqual(result.observed_at.tzinfo, UTC)

    def test_source_identity_and_environment_are_preserved(self):
        result = self.service.assess(
            observation("obs-source"),
            observed_at=self.assessed_at,
            assessed_at=self.assessed_at,
            max_age_seconds=30,
        )
        self.assertEqual(result.observation_id, "obs-source")
        self.assertEqual(result.environment_id, "env-1")
        self.assertEqual(result.domain, "hardware")

    def test_assessment_does_not_mutate_observation(self):
        source = observation()
        before = source.payload
        self.service.assess(
            source,
            observed_at=self.assessed_at - timedelta(seconds=100),
            assessed_at=self.assessed_at,
            max_age_seconds=30,
        )
        self.assertIs(source.payload, before)
        self.assertEqual(source.payload["cpu"]["cores"], 8)

    def test_assessment_result_is_immutable(self):
        result = self.service.assess(
            observation(),
            observed_at=self.assessed_at,
            assessed_at=self.assessed_at,
            max_age_seconds=30,
        )
        with self.assertRaises((AttributeError, TypeError)):
            result.freshness = ObservationFreshness.STALE

    def test_assess_many_is_deterministic_and_rejects_duplicate_ids(self):
        first = observation("one")
        second = observation("two")
        results = self.service.assess_many(
            [
                (first, self.assessed_at - timedelta(seconds=5)),
                (second, self.assessed_at - timedelta(seconds=50)),
            ],
            assessed_at=self.assessed_at,
            max_age_seconds=30,
        )
        self.assertEqual(
            tuple(item.freshness for item in results),
            (ObservationFreshness.CURRENT, ObservationFreshness.STALE),
        )

        with self.assertRaises(ValueError):
            self.service.assess_many(
                [(first, self.assessed_at), (first, self.assessed_at)],
                assessed_at=self.assessed_at,
                max_age_seconds=30,
            )

    def test_wrong_observation_type_is_rejected(self):
        with self.assertRaises(TypeError):
            self.service.assess(
                object(),
                observed_at=self.assessed_at,
                assessed_at=self.assessed_at,
                max_age_seconds=30,
            )


if __name__ == "__main__":
    unittest.main()
