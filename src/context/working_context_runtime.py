from typing import Any, Iterable, Mapping

from src.context.context_source_integration import ContextSourceIntegration
from src.context.context_source_provider import ContextSourceProvider
from src.context.context_source_selection import ContextSource
from src.context.models import ContextItem, ContextOptions
from src.context.working_context import WorkingContext
from src.core.conversation_models import StateSnapshot
from src.core.execution_progress import ExecutionProgress
from src.core.execution_state import ExecutionState
from src.core.task_models import TaskRequest


class WorkingContextRuntime:
    """Own context construction while remaining outside reasoning and execution."""

    def __init__(
        self,
        source_provider: ContextSourceProvider,
        integration: ContextSourceIntegration | None = None,
    ):
        if not isinstance(source_provider, ContextSourceProvider):
            raise TypeError("source_provider must be a ContextSourceProvider.")
        self.source_provider = source_provider
        self.integration = (
            integration if integration is not None else ContextSourceIntegration()
        )
        if not isinstance(self.integration, ContextSourceIntegration):
            raise TypeError("integration must be a ContextSourceIntegration.")

    def compose(
        self,
        request: str,
        *,
        options: ContextOptions | None = None,
        history_items=None,
        conversation_state: StateSnapshot | None = None,
        task: TaskRequest | None = None,
        execution_state: ExecutionState | None = None,
        execution_progress: ExecutionProgress | None = None,
        observations: Iterable[ContextItem | Mapping[str, Any] | str] | None = None,
        metadata: Mapping[str, Any] | None = None,
        now: float | None = None,
    ) -> WorkingContext:
        """Acquire context inputs and pass them through the established policy pipeline."""
        if not isinstance(request, str):
            raise TypeError("request must be a string.")
        normalized_request = request.strip()
        if not normalized_request:
            raise ValueError("request cannot be empty.")

        sources = tuple(self.source_provider.get_sources(normalized_request))
        if any(not isinstance(source, ContextSource) for source in sources):
            raise TypeError(
                "source_provider.get_sources() must return ContextSource values."
            )

        context_items = self.source_provider.get_context_items(
            normalized_request,
            sources,
        )

        runtime_metadata = {
            "working_context_runtime": "v1",
            "acquired_source_count": len(sources),
        }
        if metadata:
            runtime_metadata.update(dict(metadata))

        return self.integration.compose(
            normalized_request,
            sources,
            context_items,
            now=now,
            options=options,
            history_items=history_items,
            conversation_state=conversation_state,
            task=task,
            execution_state=execution_state,
            execution_progress=execution_progress,
            observations=observations,
            metadata=runtime_metadata,
        )

    __call__ = compose
