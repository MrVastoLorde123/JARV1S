"""M11.6 provider-neutral human-in-the-loop interface boundary."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class HumanResponseStatus(str, Enum):
    """Explicit terminal state reported by a human interaction surface."""

    SUBMITTED = "SUBMITTED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


@dataclass(frozen=True)
class DecisionOption:
    """Immutable display/selection option; its meaning belongs to the caller."""

    option_id: str
    label: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("option_id", "label"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "option_id", self.option_id.strip())
        object.__setattr__(self, "label", self.label.strip())
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "option_id": self.option_id,
            "label": self.label,
            "metadata": dict(self.metadata),
            "truth_guaranteed": False,
            "intent_interpreted": False,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
            "policy_mutation": False,
        }


@dataclass(frozen=True)
class HumanDecisionRequest:
    """Immutable prompt asking a human surface to provide an explicit response."""

    decision_id: str
    prompt: str
    options: tuple[DecisionOption, ...]
    session_id: str | None = None
    source_request_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    max_options: int = 16

    def __post_init__(self) -> None:
        if not isinstance(self.decision_id, str) or not self.decision_id.strip():
            raise ValueError("decision_id must be a non-empty string")
        if not isinstance(self.prompt, str) or not self.prompt.strip():
            raise ValueError("prompt must be a non-empty string")
        if not isinstance(self.options, tuple):
            raise TypeError("options must be a tuple")
        if not isinstance(self.max_options, int) or isinstance(self.max_options, bool) or self.max_options <= 0:
            raise ValueError("max_options must be a positive integer")
        if len(self.options) == 0:
            raise ValueError("at least one option is required")
        if len(self.options) > self.max_options:
            raise ValueError("option count exceeds max_options")
        if any(not isinstance(item, DecisionOption) for item in self.options):
            raise TypeError("options must contain DecisionOption values")
        option_ids = [item.option_id for item in self.options]
        if len(set(option_ids)) != len(option_ids):
            raise ValueError("option_id must be unique within a decision")
        for name in ("session_id", "source_request_id"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be a non-empty string or None")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "decision_id", self.decision_id.strip())
        object.__setattr__(self, "prompt", self.prompt.strip())
        if self.session_id is not None:
            object.__setattr__(self, "session_id", self.session_id.strip())
        if self.source_request_id is not None:
            object.__setattr__(self, "source_request_id", self.source_request_id.strip())
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "prompt": self.prompt,
            "options": [item.to_dict() for item in self.options],
            "session_id": self.session_id,
            "source_request_id": self.source_request_id,
            "max_options": self.max_options,
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


@dataclass(frozen=True)
class HumanDecisionResponse:
    """Immutable human response correlated to exactly one decision request."""

    decision_id: str
    response_id: str
    status: HumanResponseStatus
    selected_option_id: str | None = None
    responder_ref: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("decision_id", "response_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.status, HumanResponseStatus):
            try:
                object.__setattr__(self, "status", HumanResponseStatus(self.status))
            except (TypeError, ValueError) as exc:
                raise TypeError("status must be a HumanResponseStatus") from exc
        for name in ("selected_option_id", "responder_ref"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be a non-empty string or None")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        if self.status is HumanResponseStatus.SUBMITTED and self.selected_option_id is None:
            raise ValueError("SUBMITTED response requires selected_option_id")
        if self.status is not HumanResponseStatus.SUBMITTED and self.selected_option_id is not None:
            raise ValueError("non-submitted response cannot select an option")
        object.__setattr__(self, "decision_id", self.decision_id.strip())
        object.__setattr__(self, "response_id", self.response_id.strip())
        if self.selected_option_id is not None:
            object.__setattr__(self, "selected_option_id", self.selected_option_id.strip())
        if self.responder_ref is not None:
            object.__setattr__(self, "responder_ref", self.responder_ref.strip())
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "response_id": self.response_id,
            "status": self.status.value,
            "selected_option_id": self.selected_option_id,
            "responder_ref": self.responder_ref,
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


@dataclass(frozen=True)
class HumanDecisionState:
    """Immutable pending/completed decision state; status is never permission."""

    request: HumanDecisionRequest
    response: HumanDecisionResponse | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.request, HumanDecisionRequest):
            raise TypeError("request must be a HumanDecisionRequest")
        if self.response is not None:
            if not isinstance(self.response, HumanDecisionResponse):
                raise TypeError("response must be a HumanDecisionResponse or None")
            if self.response.decision_id != self.request.decision_id:
                raise ValueError("response must reference the same decision_id")
            if (
                self.response.status is HumanResponseStatus.SUBMITTED
                and self.response.selected_option_id not in {item.option_id for item in self.request.options}
            ):
                raise ValueError("selected_option_id must reference an offered option")

    @property
    def pending(self) -> bool:
        return self.response is None

    @property
    def terminal(self) -> bool:
        return self.response is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "request": self.request.to_dict(),
            "response": self.response.to_dict() if self.response else None,
        }


class HumanDecisionRuntime:
    """Manage bounded human decision exchanges without granting semantic authority."""

    def respond(self, state: HumanDecisionState, response: HumanDecisionResponse) -> HumanDecisionState:
        if not isinstance(state, HumanDecisionState):
            raise TypeError("state must be a HumanDecisionState")
        if not isinstance(response, HumanDecisionResponse):
            raise TypeError("response must be a HumanDecisionResponse")
        if not state.pending:
            raise ValueError("decision already has a terminal response")
        return HumanDecisionState(request=state.request, response=response)

    def cancel(self, state: HumanDecisionState, *, response_id: str, responder_ref: str | None = None) -> HumanDecisionState:
        return self.respond(
            state,
            HumanDecisionResponse(
                decision_id=state.request.decision_id,
                response_id=response_id,
                status=HumanResponseStatus.CANCELLED,
                responder_ref=responder_ref,
            ),
        )

    def expire(self, state: HumanDecisionState, *, response_id: str) -> HumanDecisionState:
        return self.respond(
            state,
            HumanDecisionResponse(
                decision_id=state.request.decision_id,
                response_id=response_id,
                status=HumanResponseStatus.EXPIRED,
            ),
        )


@dataclass(frozen=True)
class HumanDecisionStore:
    """Immutable conflict-aware registry for human decision states."""

    states: tuple[HumanDecisionState, ...] = ()

    def __post_init__(self) -> None:
        ids = [item.request.decision_id for item in self.states]
        if any(not isinstance(item, HumanDecisionState) for item in self.states):
            raise TypeError("states must contain HumanDecisionState values")
        if len(set(ids)) != len(ids):
            raise ValueError("decision_id must be unique within the store")

    def add(self, state: HumanDecisionState) -> "HumanDecisionStore":
        if not isinstance(state, HumanDecisionState):
            raise TypeError("state must be a HumanDecisionState")
        if self.get(state.request.decision_id) is not None:
            raise ValueError(f"decision '{state.request.decision_id}' is already stored")
        return HumanDecisionStore(self.states + (state,))

    def replace(self, state: HumanDecisionState) -> "HumanDecisionStore":
        if not isinstance(state, HumanDecisionState):
            raise TypeError("state must be a HumanDecisionState")
        if self.get(state.request.decision_id) is None:
            raise ValueError(f"decision '{state.request.decision_id}' does not exist")
        return HumanDecisionStore(
            tuple(state if item.request.decision_id == state.request.decision_id else item for item in self.states)
        )

    def get(self, decision_id: str) -> HumanDecisionState | None:
        return next((item for item in self.states if item.request.decision_id == decision_id), None)

    def list(self) -> tuple[HumanDecisionState, ...]:
        return self.states
