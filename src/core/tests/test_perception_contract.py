from __future__ import annotations

import unittest
from datetime import datetime, timezone

from src.core.perception_contract import (
    PerceptionAvailability,
    PerceptionDomain,
    PerceptionObservation,
    PerceptionSnapshot,
)


class M29PerceptionContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.observed_at = datetime(2026, 9, 16, 22, 30, tzinfo=timezone.utc)

    def test_observation_is_immutable_and_provenance_bearing(self) -> None:
        observation = PerceptionObservation(
            observation_id="obs-1",
            source_id="local-filesystem",
            environment_id="desktop",
            domain=PerceptionDomain.FILESYSTEM,
            availability=PerceptionAvailability.READY,
            observed_at=self.observed_at,
            payload={"entries": ["README.md"]},
            provenance={"adapter": "filesystem"},
        )
        self.assertEqual(observation.domain, PerceptionDomain.FILESYSTEM)
        with self.assertRaises(TypeError):
            observation.payload["new"] = "value"  # type: ignore[index]

    def test_snapshot_rejects_mixed_environments_and_duplicate_ids(self) -> None:
        first = PerceptionObservation(
            observation_id="obs-1",
            source_id="proc",
            environment_id="desktop",
            domain=PerceptionDomain.PROCESSES,
            availability=PerceptionAvailability.READY,
            observed_at=self.observed_at,
        )
        duplicate = first
        with self.assertRaises(ValueError):
            PerceptionSnapshot(
                snapshot_id="snap-1",
                environment_id="desktop",
                generated_at=self.observed_at,
                observations=(first, duplicate),
            )

    def test_perception_never_grants_authority(self) -> None:
        snapshot = PerceptionSnapshot(
            snapshot_id="snap-1",
            environment_id="desktop",
            generated_at=self.observed_at,
            observations=(),
        )
        self.assertFalse(snapshot.authority_granted)
        self.assertFalse(snapshot.execution_requested)


if __name__ == "__main__":
    unittest.main()
