"""M28.13 bridge from the world model to the canonical M11 interface boundary.

The bridge is intentionally transport-neutral.  It packages an immutable
WorldObservation as ordinary M11 interface output without creating a second
API, event bus, authority surface, or state store.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from src.agency.world_projection import WorldObservation

from .boundary import InterfaceBoundary, InterfaceResponse


@dataclass(frozen=True)
class WorldObservationFrame:
    """Provider-neutral serialized world state ready for an M11 response."""

    request_id: str
    observation: WorldObservation
    session_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.request_id, str) or not self.request_id.strip():
            raise ValueError("request_id must be a non-empty string")
        if not isinstance(self.observation, WorldObservation):
            raise TypeError("observation must be a WorldObservation")
        if self.session_id is not None and (
            not isinstance(self.session_id, str) or not self.session_id.strip()
        ):
            raise ValueError("session_id must be a non-empty string or None")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")

        object.__setattr__(self, "request_id", self.request_id.strip())
        if self.session_id is not None:
            object.__setattr__(self, "session_id", self.session_id.strip())
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "m28.13.world_observation",
            "request_id": self.request_id,
            "session_id": self.session_id,
            "world": self.observation.to_context(),
            "metadata": dict(self.metadata),
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "policy_mutation": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)


class WorldObservationInterfaceAdapter:
    """Adapt backend WorldObservation into the existing M11 output envelope."""

    OBSERVATION_TYPE = "WORLD_OBSERVATION"
    SCHEMA = "m28.13.world_observation"

    def __init__(self, boundary: InterfaceBoundary | None = None) -> None:
        self._boundary = boundary or InterfaceBoundary()

    def frame(
        self,
        observation: WorldObservation,
        *,
        request_id: str,
        session_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> WorldObservationFrame:
        return WorldObservationFrame(
            request_id=request_id,
            observation=observation,
            session_id=session_id,
            metadata=metadata or {},
        )

    def response(self, frame: WorldObservationFrame) -> InterfaceResponse:
        if not isinstance(frame, WorldObservationFrame):
            raise TypeError("frame must be a WorldObservationFrame")

        metadata = {
            "interface_payload": self.OBSERVATION_TYPE,
            "schema": self.SCHEMA,
            "session_id": frame.session_id,
            "read_only": True,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            **dict(frame.metadata),
        }
        return self._boundary.response(
            request_id=frame.request_id,
            content=frame.to_json(),
            metadata=metadata,
        )

    def snapshot(
        self,
        observation: WorldObservation,
        *,
        request_id: str,
        session_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> InterfaceResponse:
        """Create one read-only M11 response from the current world observation."""
        return self.response(
            self.frame(
                observation,
                request_id=request_id,
                session_id=session_id,
                metadata=metadata,
            )
        )
