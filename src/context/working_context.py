from dataclasses import dataclass, field
from typing import Any

from src.context.context_source_selection import ContextSourceSelection
from src.context.models import ContextItem, ContextPackage
from src.core.conversation_models import StateSnapshot
from src.core.execution_progress import ExecutionProgress
from src.core.execution_state import ExecutionState
from src.core.task_models import TaskRequest


@dataclass(frozen=True)
class WorkingContext:
    """Provider-neutral context describing JARVIS's current working situation."""

    request: str
    context_package: ContextPackage

    conversation_state: StateSnapshot | None = None
    task: TaskRequest | None = None
    execution_state: ExecutionState | None = None
    execution_progress: ExecutionProgress | None = None
    observations: tuple[ContextItem, ...] = ()
    source_selection: ContextSourceSelection | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.request, str) or not self.request.strip():
            raise ValueError("request must be a non-empty string.")
        if not isinstance(self.context_package, ContextPackage):
            raise TypeError("context_package must be a ContextPackage.")
        if self.conversation_state is not None and not isinstance(self.conversation_state, StateSnapshot):
            raise TypeError("conversation_state must be a StateSnapshot or None.")
        if self.task is not None and not isinstance(self.task, TaskRequest):
            raise TypeError("task must be a TaskRequest or None.")
        if self.execution_state is not None and not isinstance(self.execution_state, ExecutionState):
            raise TypeError("execution_state must be an ExecutionState or None.")
        if self.execution_progress is not None and not isinstance(self.execution_progress, ExecutionProgress):
            raise TypeError("execution_progress must be an ExecutionProgress or None.")
        if self.source_selection is not None and not isinstance(self.source_selection, ContextSourceSelection):
            raise TypeError("source_selection must be a ContextSourceSelection or None.")
        if not isinstance(self.observations, tuple):
            raise TypeError("observations must be a tuple.")
        for item in self.observations:
            if not isinstance(item, ContextItem):
                raise TypeError("observations must contain ContextItem values.")

        if self.execution_state is not None and self.execution_progress is not None:
            if self.execution_state.goal != self.execution_progress.goal:
                raise ValueError("execution_state and execution_progress must belong to the same goal.")

        if self.source_selection is not None:
            selected_ids = set(self.source_selection.selected_source_ids)
            persistent_types = {"MEMORY", "EVIDENCE", "HISTORY"}
            for item in self.context_package.items:
                if item.source_type not in persistent_types:
                    continue
                source_id = item.provenance.get("source_id")
                if source_id is None:
                    raise ValueError("persistent context items require provenance.source_id when source_selection is present.")
                if str(source_id) not in selected_ids:
                    raise ValueError("context package contains a persistent source excluded by source_selection.")

    def to_context(self) -> dict[str, Any]:
        """Return a provider-neutral representation for downstream reasoning."""
        return {
            "request": self.request,
            "context": {
                "request": self.context_package.request,
                "items": tuple(
                    {
                        "source_type": item.source_type,
                        "content": item.content,
                        "relevance_score": item.relevance_score,
                        "confidence": item.confidence,
                        "importance": item.importance,
                        "privacy_level": item.privacy_level,
                        "provenance": dict(item.provenance),
                    }
                    for item in self.context_package.items
                ),
                "instructions": self.context_package.instructions,
                "metadata": dict(self.context_package.metadata),
            },
            "conversation_state": (
                None
                if self.conversation_state is None
                else {
                    "conversation_id": self.conversation_state.conversation_id,
                    "active_topic": self.conversation_state.active_topic,
                    "active_task": self.conversation_state.active_task,
                    "turn_count": len(self.conversation_state.turns),
                }
            ),
            "task": (
                None
                if self.task is None
                else {
                    "content": self.task.content,
                    "task_type": self.task.task_type.value,
                    "metadata": dict(self.task.metadata),
                }
            ),
            "execution_state": None if self.execution_state is None else self.execution_state.to_context(),
            "execution_progress": None if self.execution_progress is None else self.execution_progress.to_context(),
            "observations": tuple(
                {
                    "source_type": item.source_type,
                    "content": item.content,
                    "relevance_score": item.relevance_score,
                    "confidence": item.confidence,
                    "importance": item.importance,
                    "privacy_level": item.privacy_level,
                    "provenance": dict(item.provenance),
                }
                for item in self.observations
            ),
            "source_selection": (
                None
                if self.source_selection is None
                else {
                    "selected_source_ids": self.source_selection.selected_source_ids,
                    "excluded_source_ids": self.source_selection.excluded_source_ids,
                    "refresh_required": self.source_selection.refresh_required,
                }
            ),
            "metadata": dict(self.metadata),
        }
