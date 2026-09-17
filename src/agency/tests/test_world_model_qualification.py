from unittest import TestCase

from src.agency.agent_entity import AgentEntity, AgentLandscape, AgentStatus
from src.agency.world_model import WorldModelFact, WorldModelSnapshot
from src.agency.world_model_qualification import (
    WorldFactFreshness,
    WorldFactQualification,
    WorldModelQualification,
    assess_world_model,
)


class M43WorldModelQualificationTests(TestCase):
    def _fact(self, fact_id="fact-1", value="EXECUTING", observed_at="2026-09-17T00:00:00+00:00"):
        return WorldModelFact(
            fact_id,
            "agent-1",
            "agent.status",
            value,
            ("obs-1",),
            metadata={"observed_at": observed_at},
        )

    def _snapshot(self, facts):
        return WorldModelSnapshot(
            "wm-1",
            "2026-09-17T00:00:00+00:00",
            "WORLD",
            tuple(facts),
            source_observation_ids=("obs-1", "obs-2"),
        )

    def test_current_fact_is_usable_without_establishing_truth(self):
        result = assess_world_model(
            self._snapshot((self._fact(),)),
            assessed_at="2026-09-17T00:05:00+00:00",
            max_age_seconds=600,
        )
        self.assertIsInstance(result, WorldModelQualification)
        assessment = result.assessments[0]
        self.assertEqual(WorldFactFreshness.CURRENT, assessment.freshness)
        self.assertEqual(WorldFactQualification.USABLE, assessment.qualification)
        self.assertFalse(result.to_context()["truth_established"])
        self.assertFalse(result.to_context()["authority_granted"])

    def test_stale_fact_is_not_usable(self):
        result = assess_world_model(
            self._snapshot((self._fact(observed_at="2026-09-16T23:00:00+00:00"),)),
            assessed_at="2026-09-17T00:05:00+00:00",
            max_age_seconds=600,
        )
        assessment = result.assessments[0]
        self.assertEqual(WorldFactFreshness.STALE, assessment.freshness)
        self.assertEqual(WorldFactQualification.STALE, assessment.qualification)

    def test_conflicting_peer_values_are_preserved_not_resolved(self):
        result = assess_world_model(
            self._snapshot((self._fact("fact-1", "EXECUTING"), self._fact("fact-2", "RETURNING"))),
            assessed_at="2026-09-17T00:05:00+00:00",
            max_age_seconds=600,
        )
        self.assertEqual(WorldFactQualification.CONFLICTING, result.assessments[0].qualification)
        self.assertEqual(("fact-2",), result.assessments[0].conflicting_fact_ids)
        self.assertEqual(("fact-1",), result.assessments[1].conflicting_fact_ids)

    def test_invalid_and_future_timestamps_fail_closed(self):
        invalid = assess_world_model(
            self._snapshot((self._fact(observed_at="not-a-time"),)),
            assessed_at="2026-09-17T00:05:00+00:00",
            max_age_seconds=600,
        )
        self.assertEqual(WorldFactFreshness.INVALID, invalid.assessments[0].freshness)
        self.assertEqual(WorldFactQualification.INVALID, invalid.assessments[0].qualification)

        future = assess_world_model(
            self._snapshot((self._fact(observed_at="2026-09-17T01:00:00+00:00"),)),
            assessed_at="2026-09-17T00:05:00+00:00",
            max_age_seconds=600,
        )
        self.assertEqual(WorldFactFreshness.FUTURE, future.assessments[0].freshness)
        self.assertEqual(WorldFactQualification.INVALID, future.assessments[0].qualification)

    def test_contract_rejects_wrong_input_type(self):
        with self.assertRaises(TypeError):
            assess_world_model("not snapshot", assessed_at="2026-09-17T00:05:00+00:00", max_age_seconds=60)
