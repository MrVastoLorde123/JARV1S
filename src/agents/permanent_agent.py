"""Permanent-agent definitions and registry contracts for JARVIS."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.agents.communication import AgentCommunicationGuide, DEFAULT_AGENT_COMMUNICATION_GUIDE
from src.agents.need_evaluator import AgentNeedEvaluator, AgentNeedPolicy


@dataclass(frozen=True)
class PermanentAgentDefinition:
    """Durable identity and operating contract for one permanent agent."""

    agent_id: str
    name: str
    role: str
    need_policy: AgentNeedPolicy
    communication_guide: AgentCommunicationGuide = DEFAULT_AGENT_COMMUNICATION_GUIDE
    operating_rules: tuple[str, ...] = ()
    verification_rules: tuple[str, ...] = ()
    model_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field_name in ("agent_id", "name", "role"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
            if len(value) > 256:
                raise ValueError(f"{field_name} exceeds 256 characters")
            object.__setattr__(self, field_name, value.strip())
        if not isinstance(self.need_policy, AgentNeedPolicy):
            raise TypeError("need_policy must be an AgentNeedPolicy")
        if not isinstance(self.communication_guide, AgentCommunicationGuide):
            raise TypeError("communication_guide must be an AgentCommunicationGuide")
        for field_name in ("operating_rules", "verification_rules"):
            values = tuple(getattr(self, field_name))
            if any(not isinstance(value, str) or not value.strip() for value in values):
                raise ValueError(f"{field_name} must contain non-empty strings")
            object.__setattr__(self, field_name, tuple(value.strip() for value in values))
        if self.model_id is not None:
            if not isinstance(self.model_id, str) or not self.model_id.strip():
                raise ValueError("model_id must be a non-empty string or None")
            object.__setattr__(self, "model_id", self.model_id.strip())
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def evaluator(self) -> AgentNeedEvaluator:
        """Build the authority evaluator JARVIS uses for this agent."""
        return AgentNeedEvaluator(self.need_policy)


class PermanentAgentRegistry:
    """JARVIS-owned registry of permanent agent definitions."""

    def __init__(self, definitions: tuple[PermanentAgentDefinition, ...] = ()) -> None:
        self._definitions: dict[str, PermanentAgentDefinition] = {}
        for definition in definitions:
            self.register(definition)

    def register(self, definition: PermanentAgentDefinition) -> None:
        if not isinstance(definition, PermanentAgentDefinition):
            raise TypeError("definition must be a PermanentAgentDefinition")
        if definition.agent_id in self._definitions:
            raise ValueError(f"permanent agent already registered: {definition.agent_id}")
        self._definitions[definition.agent_id] = definition

    def get(self, agent_id: str) -> PermanentAgentDefinition | None:
        if not isinstance(agent_id, str) or not agent_id.strip():
            raise ValueError("agent_id must be a non-empty string")
        return self._definitions.get(agent_id.strip())

    def require(self, agent_id: str) -> PermanentAgentDefinition:
        definition = self.get(agent_id)
        if definition is None:
            raise LookupError(f"permanent agent not found: {agent_id}")
        return definition

    def all(self) -> tuple[PermanentAgentDefinition, ...]:
        return tuple(self._definitions.values())

    def evaluators(self) -> Mapping[str, AgentNeedEvaluator]:
        return MappingProxyType({agent_id: definition.evaluator() for agent_id, definition in self._definitions.items()})


__all__ = ["PermanentAgentDefinition", "PermanentAgentRegistry"]
