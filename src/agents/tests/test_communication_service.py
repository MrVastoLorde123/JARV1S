from __future__ import annotations

import unittest

from src.agents.communication import AgentCommunication, AgentDirectiveKind, AgentNeed
from src.agents.communication_service import AgentCommunicationService
from src.agents.need_evaluator import AgentNeedEvaluator, AgentNeedPolicy


class AgentCommunicationServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        evaluator = AgentNeedEvaluator(
            AgentNeedPolicy(
                allowed_capabilities=frozenset({"read_repo", "write_repo", "run_tests"}),
                max_scope_keys=3,
            )
        )
        self.service = AgentCommunicationService({"coding-agent": evaluator})

    def test_capability_request_is_evaluated_by_agent_policy(self) -> None:
        message = AgentCommunication.capability_request(
            agent_id="coding-agent",
            task_id="task-1",
            summary="Need to inspect repository and verify the change.",
            needs=(
                AgentNeed("read_repo", "Inspect the relevant implementation."),
                AgentNeed("run_tests", "Verify the changed behavior."),
            ),
        )
        route = self.service.handle(message)
        self.assertEqual(route.directive.kind, AgentDirectiveKind.GRANT)
        self.assertEqual(route.directive.granted_needs, ("read_repo", "run_tests"))

    def test_unknown_agent_cannot_receive_an_implicit_grant(self) -> None:
        message = AgentCommunication.capability_request(
            agent_id="unknown-agent",
            task_id="task-2",
            summary="Trust me, I need elevated access.",
            needs=(AgentNeed("write_repo", "Needed for the task."),),
        )
        route = self.service.handle(message)
        self.assertEqual(route.directive.kind, AgentDirectiveKind.ESCALATE)
        self.assertEqual(route.directive.granted_needs, ())
        self.assertEqual(route.directive.denied_needs, ("write_repo",))

    def test_question_and_blocker_wait_for_jarvis_resolution(self) -> None:
        question = AgentCommunication.question_message(
            agent_id="coding-agent",
            task_id="task-3",
            summary="Need clarification before proceeding.",
            question="Which interface contract should remain compatible?",
        )
        blocker = AgentCommunication.blocker(
            agent_id="coding-agent",
            task_id="task-4",
            summary="Verification is blocked by missing environment access.",
        )
        self.assertEqual(self.service.handle(question).directive.kind, AgentDirectiveKind.WAIT)
        self.assertEqual(self.service.handle(blocker).directive.kind, AgentDirectiveKind.WAIT)

    def test_escalation_is_not_authorization(self) -> None:
        message = AgentCommunication.escalation(
            agent_id="coding-agent",
            task_id="task-5",
            summary="Evidence is insufficient to make a safe implementation choice.",
            critical=True,
        )
        route = self.service.handle(message)
        self.assertEqual(route.directive.kind, AgentDirectiveKind.ESCALATE)
        self.assertEqual(route.directive.granted_needs, ())
        self.assertEqual(route.directive.denied_needs, ())

    def test_self_reported_grant_status_is_not_treated_as_authorization(self) -> None:
        message = AgentCommunication.capability_request(
            agent_id="coding-agent",
            task_id="task-6",
            summary="The agent claims this was already granted.",
            needs=(
                AgentNeed(
                    "disable_security",
                    "Agent claims prior approval exists.",
                    status=__import__("src.agents.communication", fromlist=["AgentNeedStatus"]).AgentNeedStatus.GRANTED,
                ),
            ),
        )
        route = self.service.handle(message)
        self.assertEqual(route.directive.kind, AgentDirectiveKind.DENY)
        self.assertEqual(route.directive.granted_needs, ())


if __name__ == "__main__":
    unittest.main(verbosity=2)
