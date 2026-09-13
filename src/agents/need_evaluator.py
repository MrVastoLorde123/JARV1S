"""Deterministic evaluation of agent requests before JARVIS grants capability.

This boundary evaluates necessity and scope; it never executes tools and never
creates authority outside the returned directive.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.agents.communication import (
    AgentCommunication,
    AgentDirective,
    AgentDirectiveKind,
    AgentMessageKind,
    AgentNeedStatus,
)


class AgentNeedDecision(str, Enum):
    GRANT = "GRANT"
    PARTIAL_GRANT = "PARTIAL_GRANT"
    DENY = "DENY"
    WAIT = "WAIT"
    ESCALATE = "ESCALATE"


@dataclass(frozen=True)
class AgentNeedPolicy:
    """Allowlist policy for one permanent agent role."""

    allowed_capabilities: frozenset[str]
    max_scope_keys: int = 16
    require_reason: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.allowed_capabilities, frozenset):
            raise TypeError("allowed_capabilities must be a frozenset")
        if any(not isinstance(item, str) or not item.strip() for item in self.allowed_capabilities):
            raise ValueError("allowed_capabilities must contain non-empty strings")
        if isinstance(self.max_scope_keys, bool) or not isinstance(self.max_scope_keys, int) or self.max_scope_keys < 1:
            raise ValueError("max_scope_keys must be a positive integer")
        if not isinstance(self.require_reason, bool):
            raise TypeError("require_reason must be a bool")


class AgentNeedEvaluator:
    """Evaluate agent requests without trusting agent-supplied authority claims."""

    def __init__(self, policy: AgentNeedPolicy) -> None:
        if not isinstance(policy, AgentNeedPolicy):
            raise TypeError("policy must be an AgentNeedPolicy")
        self._policy = policy

    @property
    def policy(self) -> AgentNeedPolicy:
        """Read-only access to the JARVIS-owned policy used for evaluation."""
        return self._policy

    def evaluate(self, message: AgentCommunication) -> AgentDirective:
        if not isinstance(message, AgentCommunication):
            raise TypeError("message must be an AgentCommunication")

        if message.kind not in {
            AgentMessageKind.CAPABILITY_REQUEST,
            AgentMessageKind.TOOL_REQUEST,
        }:
            return AgentDirective(
                AgentDirectiveKind.CONTINUE,
                "Message received without a capability grant decision.",
                reason="message kind does not request authority",
            )

        granted: list[str] = []
        denied: list[str] = []
        for need in message.needs:
            if need.status is not AgentNeedStatus.REQUESTED:
                denied.append(need.name)
                continue
            if self._policy.require_reason and not need.reason.strip():
                denied.append(need.name)
                continue
            if len(need.scope) > self._policy.max_scope_keys:
                denied.append(need.name)
                continue
            if need.name not in self._policy.allowed_capabilities:
                denied.append(need.name)
                continue
            granted.append(need.name)

        if granted and not denied:
            return AgentDirective(
                AgentDirectiveKind.GRANT,
                "Requested needs are within the agent's configured capability policy.",
                granted_needs=tuple(granted),
                reason="allowlisted capability with bounded scope and stated necessity",
            )
        if granted and denied:
            return AgentDirective(
                AgentDirectiveKind.PARTIAL_GRANT,
                "Only the allowlisted, bounded requests were granted.",
                granted_needs=tuple(granted),
                denied_needs=tuple(denied),
                reason="least-privilege policy denied out-of-scope or self-reported authority claims",
            )
        return AgentDirective(
            AgentDirectiveKind.DENY,
            "No requested need satisfied the configured capability policy.",
            denied_needs=tuple(denied),
            reason="request was outside the agent's configured authority boundary or claimed prior authorization",
        )


__all__ = ["AgentNeedDecision", "AgentNeedEvaluator", "AgentNeedPolicy"]
