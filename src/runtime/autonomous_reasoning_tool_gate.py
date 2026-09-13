from __future__ import annotations

from dataclasses import dataclass

from src.runtime.autonomous_reasoning_action import AutonomousReasoningAction, AutonomousReasoningDisposition
from src.tools.models import ToolRequest, ToolResult
from src.tools.registry import ToolRegistry
from src.tools.service import ToolService

@dataclass(frozen=True)
class AutonomousReasoningToolGateResult:
    tool_request: ToolRequest
    executed: bool
    authorization_required: bool
    tool_result: ToolResult | None = None
    reason: str | None = None

class AutonomousReasoningToolGate:
    def __init__(self, registry: ToolRegistry, tool_service: ToolService) -> None:
        if not isinstance(registry, ToolRegistry): raise TypeError("registry must be a ToolRegistry")
        if not isinstance(tool_service, ToolService): raise TypeError("tool_service must be a ToolService")
        self._registry = registry
        self._tool_service = tool_service

    def evaluate(self, action: AutonomousReasoningAction, *, confirmed: bool = False) -> AutonomousReasoningToolGateResult:
        if not isinstance(action, AutonomousReasoningAction): raise TypeError("action must be an AutonomousReasoningAction")
        if action.disposition is not AutonomousReasoningDisposition.TOOL_REQUEST: raise ValueError("action disposition must be TOOL_REQUEST")
        if not isinstance(confirmed, bool): raise TypeError("confirmed must be a bool")
        tool_name = action.tool_name
        assert tool_name is not None
        request = ToolRequest(tool_name=tool_name, arguments=action.arguments, metadata={"source":"autonomous_reasoning","reasoning_action_id":action.action_id}, invocation_id=action.action_id)
        definition = self._registry.get(tool_name).definition()
        if definition.requires_confirmation and not confirmed:
            return AutonomousReasoningToolGateResult(request, False, True, reason=f"tool '{definition.name}' requires confirmation")
        result = self._tool_service.invoke(request)
        return AutonomousReasoningToolGateResult(request, True, False, result)
