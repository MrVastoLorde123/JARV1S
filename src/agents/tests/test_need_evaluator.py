from __future__ import annotations

import unittest

from src.agents.communication import (
    AgentCommunication,
    AgentDirectiveKind,
    AgentNeed,
)
from src.agents.need_evaluator import AgentNeedEvaluator, AgentNeedPolicy


class AgentNeedEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evaluator = AgentNeedEvaluator(
            AgentNeedPolicy(
                allowed_capabilities=frozenset({"read_repo", "write_repo", "run_tests"}),
                max_scope_keys=2,
            )
        )

    def test_allowlisted_need_with_reason_is_granted(self) -> None:
        message = AgentCommunication.capability_request(
            agent_id="coding-agent",
            task_id="task-1",
            summary="Need repository access for the assigned fix.",
            needs=(
                AgentNeed(
                    "write_repo",
                    "The task requires updating the two files identified in the approved plan.",
                    scope={"paths": ["src/a.py", "src/b.py"]},
                ),
            ),
        )
        directive = self.evaluator.evaluate(message)
        self.assertEqual(directive.kind, AgentDirectiveKind.GRANT)
        self.assertEqual(directive.granted_needs, ("write_repo",))
        self.assertEqual(directive.denied_needs, ())

    def test_unknown_need_is_denied_even_when_agent_claims_it_is_necessary(self) -> None:
        message = AgentCommunication.capability_request(
            agent_id="coding-agent",
            task_id="task-2",
            summary="Need an elevated capability immediately.",
            needs=(
                AgentNeed(
                    "disable_security",
                    "This will make the task easier and I consider it necessary.",
                    scope={"reason": "speed"},
                ),
            ),
        )
        directive = self.evaluator.evaluate(message)
        self.assertEqual(directive.kind, AgentDirectiveKind.DENY)
        self.assertEqual(directive.denied_needs, ("disable_security",))

    def test_overbroad_scope_is_denied(self) -> None:
        message = AgentCommunication.tool_request(
            agent_id="coding-agent",
            task_id="task-3",
            summary="Run tests for the changed code.",
            tool_name="run_tests",
            reason="Verify the targeted behavior before completion.",
            scope={"repository": "JARV1S", "branch": "feature/x", "paths": [], "extra": "not-needed"},
        )
        directive = self.evaluator.evaluate(message)
        self.assertEqual(directive.kind, AgentDirectiveKind.DENY)
        self.assertEqual(directive.denied_needs, ("run_tests",))

    def test_mixed_request_is_partially_granted(self) -> None:
        message = AgentCommunication.capability_request(
            agent_id="coding-agent",
            task_id="task-4",
            summary="Request the minimum capabilities needed to complete the task.",
            needs=(
                AgentNeed("read_repo", "Inspect the existing implementation."),
                AgentNeed("modify_branch_protection", "Would simplify the workflow."),
            ),
        )
        directive = self.evaluator.evaluate(message)
        self.assertEqual(directive.kind, AgentDirectiveKind.PARTIAL_GRANT)
        self.assertEqual(directive.granted_needs, ("read_repo",))
        self.assertEqual(directive.denied_needs, ("modify_branch_protection",))

    def test_non_authority_message_does_not_trigger_grant(self) -> None:
        message = AgentCommunication.status(
            agent_id="coding-agent",
            task_id="task-5",
            summary="I have completed inspection of the repository.",
        )
        directive = self.evaluator.evaluate(message)
        self.assertEqual(directive.kind, AgentDirectiveKind.CONTINUE)
        self.assertEqual(directive.granted_needs, ())
        self.assertEqual(directive.denied_needs, ())


if __name__ == "__main__":
    unittest.main(verbosity=2)
