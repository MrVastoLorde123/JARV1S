from typing import Iterable, Mapping, Any

from src.context.models import ContextItem, ContextOptions
from src.context.working_context import WorkingContext
from src.context.working_context_composer import WorkingContextComposer
from src.core.task_models import TaskRequest


class JARVISWorkingContextRuntime:
    """Runtime boundary that composes working context from an existing JARVIS instance."""

    def __init__(
        self,
        jarvis,
        composer: WorkingContextComposer | None = None,
    ):
        if jarvis is None:
            raise TypeError("jarvis must not be None.")
        self.jarvis = jarvis
        self.composer = composer if composer is not None else WorkingContextComposer()
        if not isinstance(self.composer, WorkingContextComposer):
            raise TypeError("composer must be a WorkingContextComposer.")

    def compose(
        self,
        request: str,
        *,
        task: TaskRequest | None = None,
        execution_state=None,
        execution_progress=None,
        observations: Iterable[ContextItem | Mapping[str, Any] | str] | None = None,
        history_items=None,
        metadata: Mapping[str, Any] | None = None,
    ) -> WorkingContext:
        """Compose context using the current state owned by JARVIS."""
        context_options = getattr(self.jarvis, "context_options", ContextOptions())
        conversation = getattr(self.jarvis, "conversation", None)
        if conversation is None:
            raise AttributeError("jarvis must expose a conversation state.")

        return self.composer.compose(
            request,
            options=context_options,
            history_items=history_items,
            conversation_state=conversation.snapshot(),
            task=task,
            execution_state=execution_state,
            execution_progress=execution_progress,
            observations=observations,
            metadata=metadata,
        )
