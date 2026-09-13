"""JARVIS-side routing for structured permanent-agent communication."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from src.agents.communication import (
    AgentCommunication,
    AgentDirective,
    AgentDirectiveKind,
    AgentMessageKind,
)
from src.agents.need_evaluator import AgentNeedEvaluator


@dataclass(frozen=True)
class AgentCommunicationRoute:
    """The deterministic disposition of one agent message."""

    agent_id: str
    task_id: str
    directive: AgentDirective


class AgentCommunicationService:
    """Receive agent messages and apply JARVIS-owned communication policy."""

    def __init__(self, evaluators: Mapping[str, AgentNeedEvaluator]) -> None:
        if not isinstance(evaluators, Mapping) or not evaluators:
            raise ValueError("evaluators must be a non-empty mapping")
        if any(not isinstance(agent_id, str) or not agent_id.strip() for agent_id in evaluators):
            raise ValueError("evaluator keys must be non-empty agent IDs")
        if any(not isinstance(evaluator, AgentNeedEvaluator) for evaluator in evaluators.values()):
            raise TypeError("evaluators must contain AgentNeedEvaluator values")
        self._evaluators = dict(evaluators)

    def handle(self, message: AgentCommunication) -> AgentCommunicationRoute:
        if not isinstance(message, AgentCommunication):
            raise TypeError("message must be an AgentCommunication")

        if message.kind in {AgentMessageKind.CAPABILITY_REQUEST, AgentMessageKind.TOOL_REQUEST}:
            evaluator = self._evaluators.get(message.agent_id)
            if evaluator is None:
                directive = AgentDirective(
                    AgentDirectiveKind.ESCALATE,
                    "No configured authority policy exists for this agent.",
                    denied_needs=tuple(need.name for need in message.pending_needs),
                    reason="unknown agent identity or missing permanent-agent policy",
                )
            else:
                directive = evaluator.evaluate(message)
        elif message.kind in {AgentMessageKind.QUESTION, AgentMessageKind.BLOCKER}:
            directive = AgentDirective(
                AgentDirectiveKind.WAIT,
                "JARVIS must supply information or resolve the reported blocker before the agent continues.",
                reason="agent reported a blocking dependency",
            )
        elif message.kind is AgentMessageKind.ESCALATION:
            directive = AgentDirective(
                AgentDirectiveKind.ESCALATE,
                "Escalation accepted for JARVIS-level review.",
                reason="agent explicitly escalated an unresolved issue",
            )
        else:
            directive = AgentDirective(
                AgentDirectiveKind.CONTINUE,
                "Communication received.",
                reason="message contains state or completion information without an authority request",
            )

        return AgentCommunicationRoute(
            agent_id=message.agent_id,
            task_id=message.task_id,
            directive=directive,
        )


__all__ = ["AgentCommunicationRoute", "AgentCommunicationService"]
