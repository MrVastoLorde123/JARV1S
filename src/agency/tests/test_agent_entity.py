import unittest

from src.agency.agent_entity import AgentEntity, AgentLandscape, AgentStatus


class AgentEntityTests(unittest.TestCase):
    def agent(self, **overrides):
        values = {
            "agent_id": "agent-07",
            "display_name": "Researcher-07",
            "archetype": "researcher",
            "assignment_id": "assignment-1",
            "status": AgentStatus.ASSIGNED,
            "landscape": AgentLandscape.AGENTS,
            "capability_ids": ("search", "summarize"),
            "created_at": "10:00:00",
            "updated_at": "10:00:00",
        }
        values.update(overrides)
        return AgentEntity(**values)

    def test_agent_is_a_runtime_instance_not_authority(self):
        serialized = self.agent().to_context()
        self.assertEqual(serialized["agent_id"], "agent-07")
        self.assertEqual(serialized["display_name"], "Researcher-07")
        self.assertFalse(serialized["authority_granted"])
        self.assertFalse(serialized["permissions_granted"])

    def test_agent_can_move_between_landscapes(self):
        moving = self.agent().move_to(AgentLandscape.MODELS, "10:01:00")
        self.assertEqual(moving.status, AgentStatus.TRAVELLING)
        self.assertEqual(moving.landscape, AgentLandscape.AGENTS)
        self.assertEqual(moving.destination, AgentLandscape.MODELS)

    def test_arrival_changes_current_landscape_and_enters_execution(self):
        arrived = self.agent().move_to(AgentLandscape.MODELS, "10:01:00").arrive(
            AgentLandscape.MODELS, "10:02:00"
        )
        self.assertEqual(arrived.status, AgentStatus.EXECUTING)
        self.assertEqual(arrived.landscape, AgentLandscape.MODELS)
        self.assertIsNone(arrived.destination)

    def test_entity_is_immutable(self):
        agent = self.agent()
        with self.assertRaises(Exception):
            agent.display_name = "mutated"

    def test_invalid_identity_is_rejected(self):
        with self.assertRaises(ValueError):
            self.agent(agent_id="")

    def test_duplicate_capabilities_are_rejected(self):
        with self.assertRaises(ValueError):
            self.agent(capability_ids=("search", "search"))

    def test_invalid_status_type_is_rejected(self):
        with self.assertRaises(TypeError):
            self.agent(status="EXECUTING")


if __name__ == "__main__":
    unittest.main()
