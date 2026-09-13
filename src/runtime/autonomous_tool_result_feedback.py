from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.tools.models import ToolResult

_MAX_OBSERVATION_LENGTH = 16384


@dataclass(frozen=True)
class AutonomousToolResultFeedback:
    """Bounded observation data derived from one executed tool result."""

    tool_name: str
    invocation_id: str | None
    success: bool
    observation: str
    context_delta: dict[str, Any]


class AutonomousToolResultFeedbackAdapter:
    """Convert tool outcomes into deterministic reasoning observations."""

    def __init__(self) -> None:
        pass

    def adapt(self, result: ToolResult) -> AutonomousToolResultFeedback:
        if not isinstance(result, ToolResult):
            raise TypeError("result must be a ToolResult")

        if result.success:
            observation = f"Tool '{result.tool_name}' completed successfully."
            payload = result.content
            context_delta = {
                "tool_result": {
                    "tool_name": result.tool_name,
                    "invocation_id": result.invocation_id,
                    "success": True,
                    "content": payload,
                    "metadata": dict(result.metadata),
                }
            }
            if payload is not None:
                observation = f"{observation} Returned content: {payload!r}"
        else:
            assert result.error is not None
            observation = (
                f"Tool '{result.tool_name}' failed: "
                f"{result.error.code}: {result.error.message}"
            )
            context_delta = {
                "tool_result": {
                    "tool_name": result.tool_name,
                    "invocation_id": result.invocation_id,
                    "success": False,
                    "error": {
                        "code": result.error.code,
                        "message": result.error.message,
                        "details": dict(result.error.details),
                    },
                    "metadata": dict(result.metadata),
                }
            }

        if len(observation) > _MAX_OBSERVATION_LENGTH:
            observation = observation[:_MAX_OBSERVATION_LENGTH]

        return AutonomousToolResultFeedback(
            tool_name=result.tool_name,
            invocation_id=result.invocation_id,
            success=result.success,
            observation=observation,
            context_delta=context_delta,
        )


__all__ = [
    "AutonomousToolResultFeedback",
    "AutonomousToolResultFeedbackAdapter",
]
