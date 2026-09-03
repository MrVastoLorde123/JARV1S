"""M11.1 provider-neutral human/interface interaction boundary."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class InterfaceChannel(str, Enum):
    """Origin surface for an interaction; it carries no authority semantics."""

    TEXT = "TEXT"
    VOICE = "VOICE"
    UI = "UI"
    API = "API"
    OTHER = "OTHER"


@dataclass(frozen=True)
class InterfaceRequest:
    """Immutable transport envelope at the boundary between an interface and JARVIS."""

    request_id: str
    channel: InterfaceChannel
    content: str
    session_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("request_id", "content"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.channel, InterfaceChannel):
            try:
                object.__setattr__(self, "channel", InterfaceChannel(self.channel))
            except (TypeError, ValueError) as exc:
                raise TypeError("channel must be an InterfaceChannel") from exc
        if self.session_id is not None and (
            not isinstance(self.session_id, str) or not self.session_id.strip()
        ):
            raise ValueError("session_id must be a non-empty string or None")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "request_id", self.request_id.strip())
        object.__setattr__(self, "content", self.content.strip())
        if self.session_id is not None:
            object.__setattr__(self, "session_id", self.session_id.strip())
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "channel": self.channel.value,
            "content": self.content,
            "session_id": self.session_id,
            "metadata": dict(self.metadata),
            "intent_interpreted": False,
            "truth_guaranteed": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "policy_mutation": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)


@dataclass(frozen=True)
class InterfaceResponse:
    """Immutable output envelope returned toward an interface surface."""

    request_id: str
    content: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("request_id", "content"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "request_id", self.request_id.strip())
        object.__setattr__(self, "content", self.content.strip())
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "content": self.content,
            "metadata": dict(self.metadata),
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)


class InterfaceBoundary:
    """Package and validate interface traffic without interpreting or authorizing it."""

    def request(
        self,
        *,
        request_id: str,
        channel: InterfaceChannel,
        content: str,
        session_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> InterfaceRequest:
        return InterfaceRequest(
            request_id=request_id,
            channel=channel,
            content=content,
            session_id=session_id,
            metadata=metadata or {},
        )

    def response(
        self,
        *,
        request_id: str,
        content: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> InterfaceResponse:
        return InterfaceResponse(
            request_id=request_id,
            content=content,
            metadata=metadata or {},
        )
