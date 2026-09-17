from unittest import TestCase

from src.agency.agent_entity import AgentEntity, AgentLandscape, AgentStatus
from src.agency.world_model import WorldModelFact, WorldModelSnapshot, build_world_model_snapshot
from src.agency.world_projection import WorldObservation, WorldObservationProjector


class M42WorldModelTests(TestCase):
    def _observation(self):
        agent = AgentEntity(
            agent_id="agent-1",
            display_name="Worker One",
            archetype="technical-worker",
            assignment_id="assign-1",
            status=AgentStatus.EXECUTING,
            landscape=AgentLandscape.WORK,
            model_id="model-1",
            created_at="2026-09-17T00:00:00+00:00",
            updated_at="2026-09-17T00:01:00+00:00",
        )
        return WorldObservationProjector().project(
            (agent,),
            "2026-09-17T00:02:00+00:00",
            current_landscape=AgentLandscape.WORK,
        )

    def test_snapshot_preserves_observation_lineage(self):
        snapshot = build_world_model_snapshot(self._observation(), model_id="wm-1")
        self.assertIsInstance(snapshot, WorldModelSnapshot)
        self.assertEqual(4, snapshot.fact_count)
        self.assertTrue(snapshot.source_observation_ids)
        self.assertTrue(all(fact.source_observation_ids for fact in snapshot.facts))
        self.assertFalse(snapshot.to_context()["truth_established"])
        self.assertFalse(snapshot.to_context()["authority_granted"])

    def test_subject_query_is_deterministic(self):
        snapshot = build_world_model_snapshot(self._observation(), model_id="wm-2")
        facts = snapshot.facts_for_subject("agent-1")
        self.assertEqual(("agent.status", "agent.landscape", "agent.model_id", "agent.active"), tuple(f.domain for f in facts))
        self.assertEqual((), snapshot.facts_for_subject("unknown"))

    def test_fact_contract_rejects_invalid_lineage(self):
        with self.assertRaises(ValueError):
            WorldModelFact("fact-1", "agent-1", "agent.status", "EXECUTING", ())

    def test_snapshot_rejects_duplicate_fact_identity(self):
        fact = WorldModelFact("same", "agent-1", "agent.status", "EXECUTING", ("obs-1",))
        with self.assertRaises(ValueError):
            WorldModelSnapshot("wm-3", "2026-09-17T00:00:00+00:00", "WORLD", (fact, fact))

    def test_input_type_is_required(self):
        with self.assertRaises(TypeError):
            build_world_model_snapshot("not observation", model_id="wm-4")
