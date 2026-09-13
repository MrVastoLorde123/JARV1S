from __future__ import annotations

import unittest

from src.agents.need_evaluator import AgentNeedPolicy
from src.agents.permanent_agent import PermanentAgentDefinition, PermanentAgentRegistry


class PermanentAgentRegistryTests(unittest.TestCase):
    def _definition(self, agent_id: str = "coding-agent") -> PermanentAgentDefinition:
        return PermanentAgentDefinition(
            agent_id=agent_id,
            name="Coding Agent",
            role="software engineering",
            need_policy=AgentNeedPolicy(
                allowed_capabilities=frozenset({"read_repo", "write_repo", "run_tests"}),
            ),
            operating_rules=("Prefer the smallest correct change.",),
            verification_rules=("Run focused tests.",),
        )

    def test_definition_keeps_identity_policy_and_model_optional(self) -> None:
        definition = self._definition()
        self.assertEqual(definition.agent_id, "coding-agent")
        self.assertEqual(definition.role, "software engineering")
        self.assertIsNone(definition.model_id)
        self.assertEqual(definition.operating_rules, ("Prefer the smallest correct change.",))

    def test_registry_rejects_duplicate_identity(self) -> None:
        registry = PermanentAgentRegistry((self._definition(),))
        with self.assertRaises(ValueError):
            registry.register(self._definition())

    def test_registry_provides_authority_evaluator_for_each_agent(self) -> None:
        registry = PermanentAgentRegistry((self._definition(),))
        evaluators = registry.evaluators()
        self.assertIn("coding-agent", evaluators)
        self.assertEqual(
            evaluators["coding-agent"].policy.allowed_capabilities,
            frozenset({"read_repo", "write_repo", "run_tests"}),
        )

    def test_unknown_agent_requires_explicit_lookup_failure(self) -> None:
        registry = PermanentAgentRegistry((self._definition(),))
        self.assertIsNone(registry.get("missing-agent"))
        with self.assertRaises(LookupError):
            registry.require("missing-agent")


if __name__ == "__main__":
    unittest.main(verbosity=2)
