import json
import unittest

from src.context.cross_domain import CrossDomainContext, DomainReference
from src.context.goal_project import GoalProjectContext
from src.context.relevance import ContextRelevance, ContextRelevanceRanking
from src.context.situational import SituationalContext
from src.context.temporal import TemporalContext
from src.context.world_model import WorldModelContext, WorldModelValidationError
from src.context.world_state import ContextState


class WorldModelContextTests(unittest.TestCase):
    def test_empty_world_model_is_valid(self):
        model = WorldModelContext()
        self.assertIsNone(model.state)
        self.assertIsNone(model.temporal)
        self.assertIsNone(model.goal_project)
        self.assertIsNone(model.situational)
        self.assertIsNone(model.cross_domain)
        self.assertIsNone(model.relevance)

    def test_accepts_all_context_domains(self):
        state = ContextState("state-1", {"active": True}, observed_at="2026-09-03T22:00:00+00:00")
        temporal = TemporalContext((state,))
        goal_project = GoalProjectContext()
        situational = SituationalContext(state)
        ref = DomainReference("project", "p1")
        cross_domain = CrossDomainContext(references=(ref,))
        relevance = ContextRelevanceRanking((ContextRelevance(ref, 0.9),))
        model = WorldModelContext(state, temporal, goal_project, situational, cross_domain, relevance)
        self.assertIs(model.state, state)
        self.assertIs(model.temporal, temporal)
        self.assertIs(model.goal_project, goal_project)
        self.assertIs(model.situational, situational)
        self.assertIs(model.cross_domain, cross_domain)
        self.assertIs(model.relevance, relevance)

    def test_rejects_invalid_domain_type(self):
        with self.assertRaises(WorldModelValidationError):
            WorldModelContext(state="not-context")

    def test_rejects_invalid_temporal_type(self):
        with self.assertRaises(WorldModelValidationError):
            WorldModelContext(temporal="not-temporal")

    def test_rejects_invalid_goal_project_type(self):
        with self.assertRaises(WorldModelValidationError):
            WorldModelContext(goal_project="not-goals")

    def test_rejects_invalid_situational_type(self):
        with self.assertRaises(WorldModelValidationError):
            WorldModelContext(situational="not-situation")

    def test_rejects_invalid_cross_domain_type(self):
        with self.assertRaises(WorldModelValidationError):
            WorldModelContext(cross_domain="not-cross-domain")

    def test_rejects_invalid_relevance_type(self):
        with self.assertRaises(WorldModelValidationError):
            WorldModelContext(relevance="not-ranking")

    def test_with_state_is_functional(self):
        original = WorldModelContext()
        state = ContextState("state-1", {"mode": "work"})
        updated = original.with_state(state)
        self.assertIsNone(original.state)
        self.assertIs(updated.state, state)

    def test_with_temporal_is_functional(self):
        original = WorldModelContext()
        temporal = TemporalContext()
        updated = original.with_temporal(temporal)
        self.assertIsNone(original.temporal)
        self.assertIs(updated.temporal, temporal)

    def test_with_goal_project_is_functional(self):
        original = WorldModelContext()
        value = GoalProjectContext()
        updated = original.with_goal_project(value)
        self.assertIsNone(original.goal_project)
        self.assertIs(updated.goal_project, value)

    def test_with_situational_is_functional(self):
        original = WorldModelContext()
        state = ContextState("state-1", {"online": True})
        value = SituationalContext(state)
        updated = original.with_situational(value)
        self.assertIsNone(original.situational)
        self.assertIs(updated.situational, value)

    def test_with_cross_domain_is_functional(self):
        original = WorldModelContext()
        value = CrossDomainContext(references=(DomainReference("project", "p1"),))
        updated = original.with_cross_domain(value)
        self.assertIsNone(original.cross_domain)
        self.assertIs(updated.cross_domain, value)

    def test_with_relevance_is_functional(self):
        original = WorldModelContext()
        ref = DomainReference("project", "p1")
        value = ContextRelevanceRanking((ContextRelevance(ref, 0.9),))
        updated = original.with_relevance(value)
        self.assertIsNone(original.relevance)
        self.assertIs(updated.relevance, value)

    def test_replacements_preserve_other_domains(self):
        state = ContextState("state-1", {"active": True})
        goal_project = GoalProjectContext()
        cross_domain = CrossDomainContext(references=(DomainReference("project", "p1"),))
        original = WorldModelContext(state=state, goal_project=goal_project, cross_domain=cross_domain)
        replacement = ContextState("state-2", {"active": False})
        updated = original.with_state(replacement)
        self.assertIs(updated.state, replacement)
        self.assertIs(updated.goal_project, goal_project)
        self.assertIs(updated.cross_domain, cross_domain)

    def test_to_dict_marks_non_authority(self):
        model = WorldModelContext()
        data = model.to_dict()
        self.assertFalse(data["truth_guaranteed"])
        self.assertFalse(data["fact_guaranteed"])
        self.assertFalse(data["intent_guaranteed"])
        self.assertFalse(data["authorization_granted"])
        self.assertFalse(data["policy_authority"])
        self.assertFalse(data["execution_requested"])

    def test_to_json_is_serializable(self):
        model = WorldModelContext()
        data = json.loads(model.to_json())
        self.assertIsInstance(data, dict)


if __name__ == "__main__":
    unittest.main()
