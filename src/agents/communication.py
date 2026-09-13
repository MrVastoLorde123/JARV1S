"""Structured communication contract between agents and JARVIS.

Agents are capable of reasoning, but they are not the authority. This module
provides the language an agent uses to communicate with JARVIS about state,
questions, blockers, capability needs, tool needs, escalation, and completion.

The protocol deliberately does not grant permission. An agent can describe
what it needs and why; JARVIS decides whether anything is granted.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping
from uuid import uuid4


_MAX_TEXT_LENGTH = 4096
_MAX_ITEMS = 32


class AgentMessageKind(str, Enum):
    """The communication intent an agent is sending to JARVIS."""

    STATUS = "STATUS"
    QUESTION = "QUESTION"
    CAPABILITY_REQUEST = "CAPABILITY_REQUEST"
    TOOL_REQUEST = "TOOL_REQUEST"
    BLOCKER = "BLOCKER"
    ESCALATION = "ESCALATION"
    COMPLETION = "COMPLETION"


class AgentUrgency(str, Enum):
    """How urgently JARVIS should evaluate an agent message."""

    INFORMATIONAL = "INFORMATIONAL"
    NORMAL = "NORMAL"
    BLOCKING = "BLOCKING"
    CRITICAL = "CRITICAL"


class AgentNeedStatus(str, Enum):
    """Current disposition known by the agent for a requested need."""

    REQUESTED = "REQUESTED"
    GRANTED = "GRANTED"
    DENIED = "DENIED"
    PARTIALLY_GRANTED = "PARTIALLY_GRANTED"
    NOT_NEEDED = "NOT_NEEDED"


class AgentDirectiveKind(str, Enum):
    """Deterministic classes of instruction JARVIS can return to an agent."""

    CONTINUE = "CONTINUE"
    WAIT = "WAIT"
    ANSWER = "ANSWER"
    GRANT = "GRANT"
    DENY = "DENY"
    PARTIAL_GRANT = "PARTIAL_GRANT"
    ESCALATE = "ESCALATE"
    STOP = "STOP"


def _text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    if len(value) > _MAX_TEXT_LENGTH:
        raise ValueError(f"{field_name} exceeds {_MAX_TEXT_LENGTH} characters")
    return value.strip()


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


def _freeze_mapping(value: Mapping[str, Any] | None, field_name: str) -> Mapping[str, Any]:
    if value is None:
        return MappingProxyType({})
    if not isinstance(value, Mapping):
        raise TypeError(f"{field_name} must be a mapping or None")
    frozen = _freeze(value)
    if not isinstance(frozen, Mapping):
        raise TypeError(f"{field_name} must freeze to a mapping")
    return frozen


def _items(values: tuple[str, ...] | list[str], field_name: str) -> tuple[str, ...]:
    if len(values) > _MAX_ITEMS:
        raise ValueError(f"{field_name} exceeds {_MAX_ITEMS} items")
    result = tuple(values)
    if any(not isinstance(item, str) or not item.strip() for item in result):
        raise ValueError(f"{field_name} must contain only non-empty strings")
    return tuple(item.strip() for item in result)


@dataclass(frozen=True)
class AgentNeed:
    """One capability/resource need an agent is communicating to JARVIS."""

    name: str
    reason: str
    status: AgentNeedStatus = AgentNeedStatus.REQUESTED
    scope: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _text(self.name, "name"))
        object.__setattr__(self, "reason", _text(self.reason, "reason"))
        if not isinstance(self.status, AgentNeedStatus):
            raise TypeError("status must be an AgentNeedStatus")
        object.__setattr__(self, "scope", _freeze_mapping(self.scope, "scope"))

    @property
    def pending(self) -> bool:
        return self.status is AgentNeedStatus.REQUESTED


@dataclass(frozen=True)
class AgentCommunication:
    """Immutable message an agent sends to JARVIS."""

    agent_id: str
    task_id: str
    kind: AgentMessageKind
    summary: str
    urgency: AgentUrgency = AgentUrgency.NORMAL
    question: str | None = None
    needs: tuple[AgentNeed, ...] = ()
    evidence: Mapping[str, Any] = field(default_factory=dict)
    requested_action: str | None = None
    blocking: bool = False
    message_id: str = field(default_factory=lambda: f"agent-msg-{uuid4().hex[:16]}")

    def __post_init__(self) -> None:
        object.__setattr__(self, "agent_id", _text(self.agent_id, "agent_id"))
        object.__setattr__(self, "task_id", _text(self.task_id, "task_id"))
        if not isinstance(self.kind, AgentMessageKind):
            raise TypeError("kind must be an AgentMessageKind")
        object.__setattr__(self, "summary", _text(self.summary, "summary"))
        if not isinstance(self.urgency, AgentUrgency):
            raise TypeError("urgency must be an AgentUrgency")
        if self.question is not None:
            object.__setattr__(self, "question", _text(self.question, "question"))
        if len(self.needs) > _MAX_ITEMS:
            raise ValueError(f"needs exceeds {_MAX_ITEMS} items")
        if any(not isinstance(need, AgentNeed) for need in self.needs):
            raise TypeError("needs must contain AgentNeed values")
        object.__setattr__(self, "evidence", _freeze_mapping(self.evidence, "evidence"))
        if self.requested_action is not None:
            object.__setattr__(self, "requested_action", _text(self.requested_action, "requested_action"))
        if not isinstance(self.blocking, bool):
            raise TypeError("blocking must be a bool")
        object.__setattr__(self, "message_id", _text(self.message_id, "message_id"))

        if self.kind is AgentMessageKind.QUESTION and self.question is None:
            raise ValueError("QUESTION messages require question")
        if self.kind is AgentMessageKind.CAPABILITY_REQUEST and not self.needs:
            raise ValueError("CAPABILITY_REQUEST messages require at least one need")
        if self.kind is AgentMessageKind.TOOL_REQUEST and not self.needs:
            raise ValueError("TOOL_REQUEST messages require at least one need")
        if self.kind in {AgentMessageKind.BLOCKER, AgentMessageKind.ESCALATION} and not self.blocking:
            raise ValueError(f"{self.kind.value} messages must set blocking=True")

    @property
    def pending_needs(self) -> tuple[AgentNeed, ...]:
        return tuple(need for need in self.needs if need.pending)

    @classmethod
    def status(
        cls,
        *,
        agent_id: str,
        task_id: str,
        summary: str,
        evidence: Mapping[str, Any] | None = None,
    ) -> "AgentCommunication":
        return cls(
            agent_id=agent_id,
            task_id=task_id,
            kind=AgentMessageKind.STATUS,
            summary=summary,
            urgency=AgentUrgency.INFORMATIONAL,
            evidence=evidence or {},
        )

    @classmethod
    def question_message(
        cls,
        *,
        agent_id: str,
        task_id: str,
        summary: str,
        question: str,
        blocking: bool = True,
    ) -> "AgentCommunication":
        return cls(
            agent_id=agent_id,
            task_id=task_id,
            kind=AgentMessageKind.QUESTION,
            summary=summary,
            question=question,
            blocking=blocking,
        )

    @classmethod
    def capability_request(
        cls,
        *,
        agent_id: str,
        task_id: str,
        summary: str,
        needs: tuple[AgentNeed, ...],
        requested_action: str | None = None,
        blocking: bool = True,
    ) -> "AgentCommunication":
        return cls(
            agent_id=agent_id,
            task_id=task_id,
            kind=AgentMessageKind.CAPABILITY_REQUEST,
            summary=summary,
            needs=needs,
            requested_action=requested_action,
            blocking=blocking,
        )

    @classmethod
    def tool_request(
        cls,
        *,
        agent_id: str,
        task_id: str,
        summary: str,
        tool_name: str,
        reason: str,
        scope: Mapping[str, Any] | None = None,
        blocking: bool = True,
    ) -> "AgentCommunication":
        return cls(
            agent_id=agent_id,
            task_id=task_id,
            kind=AgentMessageKind.TOOL_REQUEST,
            summary=summary,
            needs=(AgentNeed(tool_name, reason, scope=scope or {}),),
            requested_action=f"Invoke tool: {tool_name}",
            blocking=blocking,
        )

    @classmethod
    def blocker(
        cls,
        *,
        agent_id: str,
        task_id: str,
        summary: str,
        evidence: Mapping[str, Any] | None = None,
    ) -> "AgentCommunication":
        return cls(
            agent_id=agent_id,
            task_id=task_id,
            kind=AgentMessageKind.BLOCKER,
            summary=summary,
            urgency=AgentUrgency.BLOCKING,
            evidence=evidence or {},
            blocking=True,
        )

    @classmethod
    def escalation(
        cls,
        *,
        agent_id: str,
        task_id: str,
        summary: str,
        evidence: Mapping[str, Any] | None = None,
        critical: bool = False,
    ) -> "AgentCommunication":
        return cls(
            agent_id=agent_id,
            task_id=task_id,
            kind=AgentMessageKind.ESCALATION,
            urgency=AgentUrgency.CRITICAL if critical else AgentUrgency.BLOCKING,
            summary=summary,
            evidence=evidence or {},
            blocking=True,
        )

    @classmethod
    def completion(
        cls,
        *,
        agent_id: str,
        task_id: str,
        summary: str,
        evidence: Mapping[str, Any] | None = None,
    ) -> "AgentCommunication":
        return cls(
            agent_id=agent_id,
            task_id=task_id,
            kind=AgentMessageKind.COMPLETION,
            summary=summary,
            urgency=AgentUrgency.INFORMATIONAL,
            evidence=evidence or {},
        )


@dataclass(frozen=True)
class AgentDirective:
    """Non-ambiguous instruction JARVIS returns to an agent."""

    kind: AgentDirectiveKind
    summary: str
    granted_needs: tuple[str, ...] = ()
    denied_needs: tuple[str, ...] = ()
    answer: str | None = None
    reason: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.kind, AgentDirectiveKind):
            raise TypeError("kind must be an AgentDirectiveKind")
        object.__setattr__(self, "summary", _text(self.summary, "summary"))
        object.__setattr__(self, "granted_needs", _items(self.granted_needs, "granted_needs"))
        object.__setattr__(self, "denied_needs", _items(self.denied_needs, "denied_needs"))
        if self.answer is not None:
            object.__setattr__(self, "answer", _text(self.answer, "answer"))
        if not isinstance(self.reason, str):
            raise TypeError("reason must be a string")
        if self.kind is AgentDirectiveKind.ANSWER and self.answer is None:
            raise ValueError("ANSWER directives require answer")
        if self.kind in {AgentDirectiveKind.GRANT, AgentDirectiveKind.PARTIAL_GRANT} and not self.granted_needs:
            raise ValueError(f"{self.kind.value} directives require granted_needs")
        if self.kind is AgentDirectiveKind.DENY and not self.denied_needs:
            raise ValueError("DENY directives require denied_needs")


@dataclass(frozen=True)
class AgentCommunicationGuide:
    """The permanent operating rules every JARVIS agent receives."""

    protocol_version: str = "1"
    required_behaviors: tuple[str, ...] = (
        "Report meaningful state changes to JARVIS.",
        "Ask JARVIS explicit questions when required information is missing.",
        "Request capabilities or tools through structured need requests.",
        "Explain why a requested capability is necessary and keep its scope minimal.",
        "Report blockers instead of silently improvising around authority boundaries.",
        "Escalate uncertainty when available evidence is insufficient for a safe decision.",
        "Report verification evidence honestly and distinguish observations from conclusions.",
        "Treat grants as scoped permissions, never as general authority.",
        "Do not pressure, manipulate, impersonate, or misrepresent facts to obtain access.",
        "Stop or wait when JARVIS denies, limits, or defers a request.",
    )

    def __post_init__(self) -> None:
        if not isinstance(self.protocol_version, str) or not self.protocol_version.strip():
            raise ValueError("protocol_version must be a non-empty string")
        object.__setattr__(self, "protocol_version", self.protocol_version.strip())
        object.__setattr__(self, "required_behaviors", _items(self.required_behaviors, "required_behaviors"))


DEFAULT_AGENT_COMMUNICATION_GUIDE = AgentCommunicationGuide()


__all__ = [
    "AgentCommunication",
    "AgentCommunicationGuide",
    "AgentDirective",
    "AgentDirectiveKind",
    "AgentMessageKind",
    "AgentNeed",
    "AgentNeedStatus",
    "AgentUrgency",
    "DEFAULT_AGENT_COMMUNICATION_GUIDE",
]
