from dataclasses import replace
from typing import Iterable, Mapping, Any

from src.context.context_source_resolution import ContextSourceResolver
from src.context.context_source_selection import ContextSource, ContextSourceSelector
from src.context.models import ContextItem, ContextOptions
from src.context.working_context import WorkingContext
from src.context.working_context_composer import WorkingContextComposer
from src.core.conversation_models import StateSnapshot
from src.core.execution_progress import ExecutionProgress
from src.core.execution_state import ExecutionState
from src.core.task_models import TaskRequest


class ContextSourceIntegration:
    """Enforce selection before persistent items enter working context."""

    def __init__(self, selector=None, resolver=None, composer=None):
        self.selector = selector or ContextSourceSelector()
        self.resolver = resolver or ContextSourceResolver()
        self.composer = composer or WorkingContextComposer()

    def compose(
        self,
        request: str,
        sources: Iterable[ContextSource],
        context_items: Mapping[str, ContextItem] | Iterable[ContextItem],
        *,
        now: float | None = None,
        options: ContextOptions | None = None,
        history_items=None,
        conversation_state: StateSnapshot | None = None,
        task: TaskRequest | None = None,
        execution_state: ExecutionState | None = None,
        execution_progress: ExecutionProgress | None = None,
        observations=None,
        metadata: Mapping[str, Any] | None = None,
    ) -> WorkingContext:
        selection = self.selector.select(request, sources, now=now)
        resolution = self.resolver.resolve(selection, context_items)

        base_options = options or ContextOptions()
        safe_options = replace(
            base_options,
            include_memories=False,
            include_evidence=False,
            include_history=False,
        )

        integration_metadata = {
            "source_selection_count": len(selection.selected),
            "source_resolution_missing_count": len(resolution.missing_source_ids),
        }
        if metadata:
            integration_metadata.update(dict(metadata))

        return self.composer.compose(
            request,
            options=safe_options,
            history_items=history_items,
            conversation_state=conversation_state,
            task=task,
            execution_state=execution_state,
            execution_progress=execution_progress,
            observations=observations,
            source_selection=resolution.selection,
            resolved_persistent_items=resolution.items,
            metadata=integration_metadata,
        )
