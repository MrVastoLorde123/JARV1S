from unittest import TestCase

from src.agency.agent_entity import AgentEntity, AgentLandscape, AgentStatus
from src.agency.current_context import CurrentContext, build_current_context
from src.agency.world_model import WorldModelFact, WorldModelSnapshot
from src.agency.world_model_qualification import assess_world_model, WorldFactQualification


class M44CurrentContextTests(TestCase):
    def _snapshot(self):
        facts = (
            WorldModelFact(
                "fact-1", "agent-1", "agent.status", "EXECUTING", ("obs-1",),
                metadata={"observed_at": "2026-09-17T00:00:00+00:00"},
            ),
            WorldModelFact(
                "fact-2", "agent-1", "agent.model_id", "model-1", ("obs-1",),
                metadata={"observed_at": "2026-09-17T00:00:00+00:00"},
            ),
        )
        return WorldModelSnapshot(
            "wm-1", "2026-09-17T00:00:00+00:00", "WORLD", facts,
            source_observation_ids=("obs-1",),
        )

    def _qualification(self):
        snapshot = self._snapshot()
        return snapshot, assess_world_model(
            snapshot,
            assessed_at="2026-09-17T00:05:00+00:00",
            max_age_seconds=600,
        )

    def test_only_usable_facts_are_admitted(self):
        snapshot, qualification = self._qualification()
        context = build_current_context(snapshot, qualification, context_id="ctx-1")
        self.assertIsInstance(context, CurrentContext)
        self.assertEqual(2, context.fact_count)
        self.assertEqual((), context.excluded_fact_ids)
        self.assertFalse(context.to_context()["truth_established"])
        self.assertFalse(context.to_context()["intent_established"])
        self.assertFalse(context.to_context()["execution_requested"])

    def test_non_usable_facts_are_excluded_not_resolved(self):
        snapshot = WorldModelSnapshot(
            "wm-2", "2026-09-17T00:00:00+00:00", "WORLD",
            (
                WorldModelFact("fact-1", "agent-1", "agent.status", "EXECUTING", ("obs-1",), metadata={"observed_at": "2026-09-16T20:00:00+00:00"}),
                WorldModelFact("fact-2", "agent-1", "agent.status", "RETURNING", ("obs-2",), metadata={"observed_at": "2026-09-17T00:00:00+00:00"}),
            ),
            source_observation_ids=("obs-1", "obs-2"),
        )
        qualification = assess_world_model(snapshot, assessed_at="2026-09-17T00:05:00+00:00", max_age_seconds=600)
        context = build_current_context(snapshot, qualification, context_id="ctx-2")
        self.assertEqual(0, context.fact_count)
        self.assertEqual(("fact-1", "fact-2"), context.excluded_fact_ids)
        self.assertTrue(all(a.qualification is WorldFactQualification.CONFLICTING or a.qualification is WorldFactQualification.STALE for a in qualification.assessments))

    def test_snapshot_and_qualification_identity_must_match(self):
        snapshot, qualification = self._qualification()
        other = WorldModelSnapshot("wm-other", snapshot.generated_at, snapshot.scope, snapshot.facts, snapshot.source_observation_ids)
        with self.assertRaises(ValueError):
            build_current_context(other, qualification, context_id="ctx-3")

    def test_qualification_must_cover_exact_snapshot_facts(self):
        snapshot, qualification = self._qualification()
        truncated = type(qualification)(
            qualification.model_id,
            qualification.assessed_at,
            qualification.assessments[:1],
            qualification.snapshot_source_observation_ids,
        )
        with self.assertRaises(ValueError):
            build_current_context(snapshot, truncated, context_id="ctx-4")
