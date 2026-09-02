from typing import Callable, Iterable, Mapping, Any

from src.context.context_builder import build_context
from src.context.models import ContextItem, ContextOptions, ContextPackage, OBSERVATION
from src.context.working_context import WorkingContext
from src.core.conversation_models import StateSnapshot
from src.core.execution_progress import ExecutionProgress
from src.core.execution_state import ExecutionState
from src.core.task_models import TaskRequest


class WorkingContextComposer:
    """Compose existing context sources into one provider-neutral working context."""

    def __init__(
        self,
        context_builder: Callable[..., ContextPackage] = build_context,
    ):
        if not callable(context_builder):
            raise TypeError("context_builder must be callable.")
        self.context_builder = context_builder

    def compose(
        self,
        request: str,
        *,
        options: ContextOptions | None = None,
        history_items: Iterable[Mapping[str, Any] | ContextItem] | None = None,
        conversation_state: StateSnapshot | None = None,
        task: TaskRequest | None = None,
        execution_state: ExecutionState | None = None,
        execution_progress: ExecutionProgress | None = None,
        observations: Iterable[ContextItem | Mapping[str, Any] | str] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> WorkingContext:
        if not isinstance(request, str):
            raise TypeError("request must be a string.")
        request = request.strip()
        if not request:
            raise ValueError("request cannot be empty.")

        context_package = self.context_builder(
            request,
            options=options,
            history_items=history_items,
            state_snapshot=conversation_state,
        )

        normalized_observations = tuple(
            self._normalize_observation(item)
            for item in (observations or ())
        )

        context_metadata = {
            "composer_version": "1.0",
            "has_conversation_state": conversation_state is not None,
            "has_task": task is not None,
            "has_execution_state": execution_state is not None,
            "has_execution_progress": execution_progress is not None,
            "observation_count": len(normalized_observations),
        }
        if metadata:
            context_metadata.update(dict(metadata))

        return WorkingContext(
            request=request,
            context_package=context_package,
            conversation_state=conversation_state,
            task=task,
            execution_state=execution_state,
            execution_progress=execution_progress,
            observations=normalized_observations,
            metadata=context_metadata,
        )

    @staticmethod
    def _normalize_observation(
        item: ContextItem | Mapping[str, Any] | str,
    ) -> ContextItem:
        if isinstance(item, ContextItem):
            return item

        if isinstance(item, str):
            content = item.strip()
            if not content:
                raise ValueError("observation content cannot be empty.")
            return ContextItem(
                source_type=OBSERVATION,
                content=content,
            )

        if isinstance(item, Mapping):
            content = str(item.get("content", "")).strip()
            if not content:
                raise ValueError("observation content cannot be empty.")
            return ContextItem(
                source_type=str(item.get("source_type", OBSERVATION)),
                content=content,
                relevance_score=float(item.get("relevance_score", 0.0)),
                confidence=item.get("confidence"),
                importance=item.get("importance"),
                privacy_level=str(item.get("privacy_level", "PRIVATE")),
                provenance=dict(item.get("provenance", {})),
            )

        raise TypeError(
            "observations must contain ContextItem, mapping, or string values."
        )
