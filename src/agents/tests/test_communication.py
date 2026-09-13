from __future__ import annotations

import unittest

from src.agents.communication import (
    AgentCommunication,
    AgentCommunicationGuide,
    AgentDirective,
    AgentDirectiveKind,
    AgentMessageKind,
    AgentNeed,
    AgentNeedStatus,
    AgentUrgency,
    DEFAULT_AGENT_COMMUNICATION_GUIDE,
)


class AgentCommunicationTests(unittest.TestCase):
    def test_capability_request_requires_explicit_need_and_reason(self) -> None:
        message = AgentCommunication.capability_request(
            agent_id="coding-agent",
            task_id="task-1",
            summary="Need repository write access for the approved edit.",
            needs=(AgentNeed("repository.write", "The assigned task requires changing two source files."),),
        )

        self.assertEqual(message.kind, AgentMessageKind.CAPABILITY_REQUEST)
        self.assertEqual(message.urgency, AgentUrgency.NORMAL)
        self.assertTrue(message.blocking)
        self.assertEqual(message.pending_needs[0].name, "repository.write")
        self.assertEqual(message.pending_needs[0].reason, "The assigned task requires changing two source files.")

    def test_tool_request_is_scoped_to_one_declared_need(self) -> None:
        message = AgentCommunication.tool_request(
            agent_id="coding-agent",
            task_id="task-2",
            summary="Run the required focused verification.",
            tool_name="run_test",
            reason="The coding-agent verification policy requires focused tests after this change.",
            scope={"runner": "python_unittest", "target": "src.agents.tests.test_communication"},
        )

        self.assertEqual(message.kind, AgentMessageKind.TOOL_REQUEST)
        self.assertEqual(len(message.needs), 1)
        self.assertEqual(message.needs[0].name, "run_test")
        self.assertEqual(message.needs[0].scope["runner"], "python_unittest")

    def test_question_and_blocker_require_the_right_communication_shape(self) -> None:
        question = AgentCommunication.question_message(
            agent_id="research-agent",
            task_id="task-3",
            summary="The requested source is ambiguous.",
            question="Which repository should be treated as authoritative?",
        )
        self.assertEqual(question.question, "Which repository should be treated as authoritative?")
        self.assertTrue(question.blocking)

        blocker = AgentCommunication.blocker(
            agent_id="coding-agent",
            task_id="task-4",
            summary="Write access was denied by the authority layer.",
            evidence={"tool": "write_file", "code": "policy_denied"},
        )
        self.assertEqual(blocker.urgency, AgentUrgency.BLOCKING)
        self.assertTrue(blocker.blocking)

    def test_agent_cannot_turn_a_denial_into_authority(self) -> None:
        need = AgentNeed("browser.execute", "UI verification requires browser interaction.", AgentNeedStatus.REQUESTED)
        request = AgentCommunication.capability_request(
            agent_id="ui-agent",
            task_id="task-5",
            summary="Request browser verification capability.",
            needs=(need,),
        )
        self.assertEqual(request.pending_needs, (need,))

        denial = AgentDirective(
            kind=AgentDirectiveKind.DENY,
            summary="Browser access is not available for this task.",
            denied_needs=("browser.execute",),
            reason="The task scope does not authorize browser execution.",
        )
        self.assertEqual(denial.kind, AgentDirectiveKind.DENY)
        self.assertEqual(denial.denied_needs, ("browser.execute",))

        with self.assertRaises(ValueError):
            AgentNeed(
                "browser.execute",
                "UI verification requires browser interaction.",
                AgentNeedStatus.GRANTED,
            )

        self.assertEqual(request.pending_needs, (need,))
        self.assertEqual(need.status, AgentNeedStatus.REQUESTED)

    def test_directives_require_explicit_shape(self) -> None:
        grant = AgentDirective(
            kind=AgentDirectiveKind.GRANT,
            summary="Grant the scoped verification tool.",
            granted_needs=("run_test",),
        )
        self.assertEqual(grant.granted_needs, ("run_test",))

        with self.assertRaises(ValueError):
            AgentDirective(kind=AgentDirectiveKind.ANSWER, summary="Missing answer")

        with self.assertRaises(ValueError):
            AgentDirective(kind=AgentDirectiveKind.DENY, summary="Missing denial list")

    def test_communication_guide_contains_non_manipulation_and_scope_rules(self) -> None:
        guide = DEFAULT_AGENT_COMMUNICATION_GUIDE
        self.assertIsInstance(guide, AgentCommunicationGuide)
        self.assertEqual(guide.protocol_version, "1")
        self.assertTrue(any("scope" in rule.lower() for rule in guide.required_behaviors))
        self.assertTrue(any("manipulate" in rule.lower() for rule in guide.required_behaviors))
        self.assertTrue(any("denies" in rule.lower() or "denied" in rule.lower() for rule in guide.required_behaviors))


if __name__ == "__main__":
    unittest.main(verbosity=2)
