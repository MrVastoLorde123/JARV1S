from dataclasses import replace
from typing import Callable, Iterable, Mapping, Any

from src.context.context_builder import build_context
from src.context.context_source_selection import ContextSourceSelection
from src.context.models import ContextItem, ContextOptions, ContextPackage, OBSERVATION
from src.context.working_context import WorkingContext
from src.core.conversation_models import StateSnapshot
from src.core.execution_progress import ExecutionProgress
from src.core.execution_state import ExecutionState
from src.core.task_models import TaskRequest


class WorkingContextComposer:
    """Compose existing context sources into one provider-neutral working context."""

    def __init__(self, context_builder: Callable[..., ContextPackage] = build_context):
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
        source_selection: ContextSourceSelection | None = None,
        resolved_persistent_items: Iterable[ContextItem] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> WorkingContext:
        if not isinstance(request, str):
            raise TypeError("request must be a string.")
        request = request.strip()
        if not request:
            raise ValueError("request cannot be empty.")
        if source_selection is not None and not isinstance(source_selection, ContextSourceSelection):
            raise TypeError("source_selection must be a ContextSourceSelection or None.")

        context_package = self.context_builder(
            request,
            options=options,
            history_items=history_items,
            state_snapshot=conversation_state,
        )

        if resolved_persistent_items is not None:
            persistent_items = tuple(resolved_persistent_items)
            for item in persistent_items:
                if not isinstance(item, ContextItem):
                    raise TypeError("resolved_persistent_items must contain ContextItem values.")
                if item.source_type not in {"MEMORY", "EVIDENCE", "HISTORY"}:
                    raise ValueError("resolved_persistent_items must contain persistent context items.")
                if item.provenance.get("source_id") is None:
                    raise ValueError("resolved persistent items must provide provenance.source_id.")

            if source_selection is None:
                raise ValueError("resolved_persistent_items require an explicit source_selection.")

            package_items = persistent_items + tuple(
                item
                for item in context_package.items
                if item.source_type not in {"MEMORY", "EVIDENCE", "HISTORY"}
            )
            context_metadata = dict(context_package.metadata)
            context_metadata["resolved_persistent_item_count"] = len(persistent_items)
            context_package = replace(
                context_package,
                items=package_items,
                metadata=context_metadata,
            )

        normalized_observations = tuple(
            self._normalize_observation(item) for item in (observations or ())
        )

        context_metadata = {
            "composer_version": "1.2",
            "has_conversation_state": conversation_state is not None,
            "has_task": task is not None,
            "has_execution_state": execution_state is not None,
            "has_execution_progress": execution_progress is not None,
            "observation_count": len(normalized_observations),
            "has_source_selection": source_selection is not None,
            "has_resolved_persistent_items": resolved_persistent_items is not None,
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
            source_selection=source_selection,
            metadata=context_metadata,
        )

    @staticmethod
    def _normalize_observation(item: ContextItem | Mapping[str, Any] | str) -> ContextItem:
        if isinstance(item, ContextItem):
            return item
        if isinstance(item, str):
            content = item.strip()
            if not content:
                raise ValueError("observation content cannot be empty.")
            return ContextItem(source_type=OBSERVATION, content=content)
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
        raise TypeError("observations must contain ContextItem, mapping, or string values.")
