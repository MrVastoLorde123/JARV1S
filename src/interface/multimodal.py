"""M11.5 provider-neutral multi-modal interface boundary."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from src.interface.boundary import InterfaceChannel
from src.interface.request import JARVISRequest


class InterfaceModality(str, Enum):
    """Transport modality; it carries no semantic or authority meaning."""

    TEXT = "TEXT"
    AUDIO = "AUDIO"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    FILE = "FILE"
    STRUCTURED = "STRUCTURED"


@dataclass(frozen=True)
class ModalityDescriptor:
    """Immutable description of one interface payload without embedding media bytes."""

    modality: InterfaceModality
    media_type: str
    payload_ref: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.modality, InterfaceModality):
            try:
                object.__setattr__(self, "modality", InterfaceModality(self.modality))
            except (TypeError, ValueError) as exc:
                raise TypeError("modality must be an InterfaceModality") from exc
        for name in ("media_type", "payload_ref"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "media_type", self.media_type.strip())
        object.__setattr__(self, "payload_ref", self.payload_ref.strip())
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "modality": self.modality.value,
            "media_type": self.media_type,
            "payload_ref": self.payload_ref,
            "metadata": dict(self.metadata),
            "truth_guaranteed": False,
            "intent_interpreted": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "policy_mutation": False,
        }


@dataclass(frozen=True)
class MultiModalRequest:
    """Immutable multi-modal transport envelope that projects to one JARVIS request."""

    request_id: str
    content: str
    channel: InterfaceChannel
    modalities: tuple[ModalityDescriptor, ...] = ()
    session_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    max_modalities: int = 16

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
        if not isinstance(self.modalities, tuple):
            raise TypeError("modalities must be a tuple")
        if not isinstance(self.max_modalities, int) or isinstance(self.max_modalities, bool) or self.max_modalities <= 0:
            raise ValueError("max_modalities must be a positive integer")
        if len(self.modalities) > self.max_modalities:
            raise ValueError("modality count exceeds max_modalities")
        if any(not isinstance(item, ModalityDescriptor) for item in self.modalities):
            raise TypeError("modalities must contain ModalityDescriptor values")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "request_id", self.request_id.strip())
        object.__setattr__(self, "content", self.content.strip())
        if self.session_id is not None:
            object.__setattr__(self, "session_id", self.session_id.strip())
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_jarvis_request(self) -> JARVISRequest:
        """Project modalities into the existing provider-neutral request contract."""
        modality_payload = tuple(item.to_dict() for item in self.modalities)
        combined_metadata = {
            **dict(self.metadata),
            "modalities": modality_payload,
        }
        return JARVISRequest(
            request_id=self.request_id,
            source_request_id=self.request_id,
            content=self.content,
            channel=self.channel,
            session_id=self.session_id,
            metadata=combined_metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "content": self.content,
            "channel": self.channel.value,
            "session_id": self.session_id,
            "modalities": [item.to_dict() for item in self.modalities],
            "max_modalities": self.max_modalities,
            "metadata": dict(self.metadata),
            "truth_guaranteed": False,
            "intent_interpreted": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "policy_mutation": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)


class MultiModalRuntime:
    """Build bounded multi-modal envelopes without interpreting their contents."""

    def create(
        self,
        *,
        request_id: str,
        content: str,
        channel: InterfaceChannel,
        modalities: tuple[ModalityDescriptor, ...] = (),
        session_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        max_modalities: int = 16,
    ) -> MultiModalRequest:
        return MultiModalRequest(
            request_id=request_id,
            content=content,
            channel=channel,
            modalities=modalities,
            session_id=session_id,
            metadata=metadata or {},
            max_modalities=max_modalities,
        )

    def add_modality(
        self,
        request: MultiModalRequest,
        descriptor: ModalityDescriptor,
    ) -> MultiModalRequest:
        if not isinstance(request, MultiModalRequest):
            raise TypeError("request must be a MultiModalRequest")
        if not isinstance(descriptor, ModalityDescriptor):
            raise TypeError("descriptor must be a ModalityDescriptor")
        if len(request.modalities) >= request.max_modalities:
            raise ValueError("request modality bound has been reached")
        return MultiModalRequest(
            request_id=request.request_id,
            content=request.content,
            channel=request.channel,
            modalities=request.modalities + (descriptor,),
            session_id=request.session_id,
            metadata=request.metadata,
            max_modalities=request.max_modalities,
        )
