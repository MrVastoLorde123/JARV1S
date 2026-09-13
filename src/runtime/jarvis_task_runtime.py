"""High-level V1 JARVIS task runtime wired to the configured AI service."""

from __future__ import annotations

from src.ai.service import AIService
from src.runtime.autonomous_ai_reasoning_provider import AutonomousAIReasoningProvider
from src.runtime.autonomous_task_runtime import SQLiteAutonomousTaskRuntime
from src.runtime.autonomous_task_progress import AutonomousTaskProgressEvaluator
from src.tools.registry import ToolRegistry


class JARVISTaskRuntime(SQLiteAutonomousTaskRuntime):
    """Durable autonomous task runtime using JARVIS's AI service as reasoning capability."""

    def __init__(
        self,
        ai_service: AIService,
        *,
        provider_name: str | None = None,
        connection_factory=None,
        registry: ToolRegistry | None = None,
        progress_evaluator: AutonomousTaskProgressEvaluator | None = None,
    ) -> None:
        if not isinstance(ai_service, AIService):
            raise TypeError("ai_service must be an AIService")
        provider = AutonomousAIReasoningProvider(ai_service, provider_name=provider_name)
        kwargs = {"registry": registry, "progress_evaluator": progress_evaluator}
        if connection_factory is not None:
            kwargs["connection_factory"] = connection_factory
        super().__init__(provider.reason, **kwargs)


__all__ = ["JARVISTaskRuntime"]
