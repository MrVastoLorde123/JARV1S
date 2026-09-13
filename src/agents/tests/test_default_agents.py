from __future__ import annotations

import unittest

from src.agents.default_agents import DEFAULT_CODING_AGENT


class DefaultAgentProfileTests(unittest.TestCase):
    def test_default_coding_agent_is_ready_for_policy_evaluation(self) -> None:
        self.assertEqual(DEFAULT_CODING_AGENT.agent_id, "coding-agent")
        self.assertEqual(DEFAULT_CODING_AGENT.role, "software engineering")
        self.assertIsNone(DEFAULT_CODING_AGENT.model_id)
        self.assertIn("read_repo", DEFAULT_CODING_AGENT.need_policy.allowed_capabilities)
        self.assertIn("write_repo", DEFAULT_CODING_AGENT.need_policy.allowed_capabilities)
        self.assertIn("run_tests", DEFAULT_CODING_AGENT.need_policy.allowed_capabilities)
        self.assertTrue(DEFAULT_CODING_AGENT.operating_rules)
        self.assertTrue(DEFAULT_CODING_AGENT.verification_rules)


if __name__ == "__main__":
    unittest.main(verbosity=2)
