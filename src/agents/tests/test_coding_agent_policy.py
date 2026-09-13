from __future__ import annotations

import unittest

from src.agents.coding_agent_policy import (
    CodingAgentPolicy,
    CodingWorkKind,
    DEFAULT_CODING_AGENT_POLICY,
)


class CodingAgentPolicyTests(unittest.TestCase):
    def test_default_policy_has_operating_and_verification_rules(self) -> None:
        policy = DEFAULT_CODING_AGENT_POLICY
        self.assertIsInstance(policy, CodingAgentPolicy)
        self.assertTrue(policy.required_rules)
        self.assertTrue(policy.verification_rules)
        self.assertTrue(any("JARVIS communication" in rule for rule in policy.required_rules))
        self.assertTrue(any("focused tests" in rule for rule in policy.verification_rules))
        self.assertTrue(any("browser" in rule.lower() for rule in policy.verification_rules))

    def test_work_kind_adds_specialized_verification(self) -> None:
        ui_rules = DEFAULT_CODING_AGENT_POLICY.rules_for(CodingWorkKind.UI)
        security_rules = DEFAULT_CODING_AGENT_POLICY.rules_for(CodingWorkKind.SECURITY)
        database_rules = DEFAULT_CODING_AGENT_POLICY.rules_for(CodingWorkKind.DATABASE)

        self.assertTrue(any("browser-level" in rule for rule in ui_rules))
        self.assertTrue(any("security boundary" in rule for rule in security_rules))
        self.assertTrue(any("fresh initialization or restart" in rule for rule in database_rules))

    def test_unknown_work_kind_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            DEFAULT_CODING_AGENT_POLICY.rules_for("ui")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main(verbosity=2)
