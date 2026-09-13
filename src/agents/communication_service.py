"""JARVIS-side routing for structured permanent-agent communication."""

from __future__ import annotations

from dataclasses import dataclass

from src.agents.communication import (
    AgentCommunication,
    AgentDirective,
    AgentDirectiveKind,
    AgentMessageKind,
)
from src.agents.permanent_agent import PermanentAgentRegistry


@dataclass(frozen=True)
class AgentCommunicationRoute:
    """The deterministic disposition of one agent message."""

    agent_id: str
    task_id: str
    directive: AgentDirective


class AgentCommunicationService:
    """Receive agent messages and apply JARVIS-owned communication policy."""

    def __init__(self, registry: PermanentAgentRegistry) -> None:
        if not isinstance(registry, PermanentAgentRegistry):
            raise TypeError("registry must be a PermanentAgentRegistry")
        self._registry = registry

    def handle(self, message: AgentCommunication) -> AgentCommunicationRoute:
        if not isinstance(message, AgentCommunication):
            raise TypeError("message must be an AgentCommunication")

        if message.kind in {AgentMessageKind.CAPABILITY_REQUEST, AgentMessageKind.TOOL_REQUEST}:
            definition = self._registry.get(message.agent_id)
            if definition is None:
                directive = AgentDirective(
                    AgentDirectiveKind.ESCALATE,
                    "No configured authority policy exists for this agent.",
                    denied_needs=tuple(need.name for need in message.pending_needs),
                    reason="unknown agent identity or missing permanent-agent policy",
                )
            else:
                directive = definition.evaluator().evaluate(message)
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
