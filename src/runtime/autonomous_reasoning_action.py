"""Provider-neutral structured action contract for autonomous reasoning."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class AutonomousReasoningActionValidationError(ValueError):
    """Raised when an autonomous reasoning action is malformed."""


class AutonomousReasoningDisposition(str, Enum):
    CONTINUE = "continue"
    TOOL_REQUEST = "tool_request"
    WAIT_AUTHORIZATION = "wait_authorization"
    WAIT_INPUT = "wait_input"
    WAIT_TOOL = "wait_tool"
    COMPLETE = "complete"
    FAIL = "fail"


@dataclass(frozen=True)
class AutonomousReasoningAction:
    """One explicit next disposition emitted by a reasoning provider."""

    action_id: str
    disposition: AutonomousReasoningDisposition
    rationale: str
    tool_name: str | None = None
    arguments: Mapping[str, Any] = field(default_factory=dict)
    result: Any = None
    wait_reason: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.action_id, str) or not self.action_id.strip():
            raise AutonomousReasoningActionValidationError("action_id must be a non-empty string")
        if not isinstance(self.disposition, AutonomousReasoningDisposition):
            raise AutonomousReasoningActionValidationError(
                "disposition must be an AutonomousReasoningDisposition"
            )
        if not isinstance(self.rationale, str) or not self.rationale.strip():
            raise AutonomousReasoningActionValidationError("rationale must be a non-empty string")
        if not isinstance(self.arguments, Mapping):
            raise AutonomousReasoningActionValidationError("arguments must be a mapping")
        if not isinstance(self.metadata, Mapping):
            raise AutonomousReasoningActionValidationError("metadata must be a mapping")

        if self.disposition is AutonomousReasoningDisposition.TOOL_REQUEST:
            if not isinstance(self.tool_name, str) or not self.tool_name.strip():
                raise AutonomousReasoningActionValidationError(
                    "tool_name is required for TOOL_REQUEST"
                )
        elif self.tool_name is not None:
            raise AutonomousReasoningActionValidationError(
                "tool_name is only valid for TOOL_REQUEST"
            )

        waiting = {
            AutonomousReasoningDisposition.WAIT_AUTHORIZATION,
            AutonomousReasoningDisposition.WAIT_INPUT,
            AutonomousReasoningDisposition.WAIT_TOOL,
        }
        if self.disposition in waiting:
            if not isinstance(self.wait_reason, str) or not self.wait_reason.strip():
                raise AutonomousReasoningActionValidationError(
                    "wait_reason is required for a waiting disposition"
                )
        elif self.wait_reason is not None:
            raise AutonomousReasoningActionValidationError(
                "wait_reason is only valid for a waiting disposition"
            )

        if self.disposition is AutonomousReasoningDisposition.COMPLETE and self.result is None:
            raise AutonomousReasoningActionValidationError(
                "result is required for COMPLETE"
            )
        if self.disposition is not AutonomousReasoningDisposition.COMPLETE and self.result is not None:
            raise AutonomousReasoningActionValidationError(
                "result is only valid for COMPLETE"
            )

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "AutonomousReasoningAction":
        if not isinstance(payload, Mapping):
            raise AutonomousReasoningActionValidationError("reasoning action payload must be a mapping")
        try:
            disposition = AutonomousReasoningDisposition(payload["disposition"])
        except (KeyError, TypeError, ValueError) as exc:
            raise AutonomousReasoningActionValidationError(
                "payload must contain a supported disposition"
            ) from exc

        return cls(
            action_id=payload.get("action_id", "generated-action"),
            disposition=disposition,
            rationale=payload.get("rationale", "No rationale supplied."),
            tool_name=payload.get("tool_name"),
            arguments=payload.get("arguments", {}),
            result=payload.get("result"),
            wait_reason=payload.get("wait_reason"),
            metadata=payload.get("metadata", {}),
        )

    @classmethod
    def from_json(cls, payload: str) -> "AutonomousReasoningAction":
        if not isinstance(payload, str) or not payload.strip():
            raise AutonomousReasoningActionValidationError("reasoning action JSON must be non-empty")
        try:
            decoded = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise AutonomousReasoningActionValidationError(
                "reasoning action JSON is invalid"
            ) from exc
        return cls.from_mapping(decoded)

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "disposition": self.disposition.value,
            "rationale": self.rationale,
            "tool_name": self.tool_name,
            "arguments": dict(self.arguments),
            "result": self.result,
            "wait_reason": self.wait_reason,
            "metadata": dict(self.metadata),
            "tool_request_is_authorization": False,
            "model_output_is_truth": False,
            "authority_granted": False,
            "execution_requested": self.disposition is AutonomousReasoningDisposition.TOOL_REQUEST,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
