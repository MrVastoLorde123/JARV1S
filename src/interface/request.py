"""M11.3 interface-to-JARVIS request boundary.

This module converts a normalized interface request into a provider-neutral
JARVIS request envelope. It preserves the interaction identity and content
without interpreting intent, granting authority, authorizing execution, or
mutating policy.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.interface.boundary import InterfaceChannel, InterfaceRequest


@dataclass(frozen=True)
class JARVISRequest:
    """Immutable request envelope handed from an interface into JARVIS."""

    request_id: str
    content: str
    channel: InterfaceChannel
    session_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    source_request_id: str | None = None

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
        if self.source_request_id is not None and (
            not isinstance(self.source_request_id, str) or not self.source_request_id.strip()
        ):
            raise ValueError("source_request_id must be a non-empty string or None")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "request_id", self.request_id.strip())
        object.__setattr__(self, "content", self.content.strip())
        if self.session_id is not None:
            object.__setattr__(self, "session_id", self.session_id.strip())
        if self.source_request_id is not None:
            object.__setattr__(self, "source_request_id", self.source_request_id.strip())
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "content": self.content,
            "channel": self.channel.value,
            "session_id": self.session_id,
            "metadata": dict(self.metadata),
            "source_request_id": self.source_request_id,
            "intent_interpreted": False,
            "truth_guaranteed": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "policy_mutation": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)


class InterfaceRequestBridge:
    """Convert interface transport envelopes into neutral JARVIS requests."""

    def to_jarvis_request(self, request: InterfaceRequest) -> JARVISRequest:
        if not isinstance(request, InterfaceRequest):
            raise TypeError("request must be an InterfaceRequest")
        return JARVISRequest(
            request_id=request.request_id,
            source_request_id=request.request_id,
            content=request.content,
            channel=request.channel,
            session_id=request.session_id,
            metadata=request.metadata,
        )
