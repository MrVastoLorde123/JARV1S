from typing import Any, Mapping

from src.ai.models import AIRequest
from src.context.working_context import WorkingContext


class WorkingContextConsumptionBoundary:
    """Translate an already-composed WorkingContext into a provider-neutral AIRequest."""

    def consume(
        self,
        working_context: WorkingContext,
        *,
        model: str | None = None,
        generation_options: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> AIRequest:
        """Create the downstream reasoning request without retrieving, selecting, or executing anything."""
        if not isinstance(working_context, WorkingContext):
            raise TypeError("working_context must be a WorkingContext.")

        request_metadata = {
            "working_context_consumed": True,
        }
        if metadata:
            request_metadata.update(dict(metadata))

        return AIRequest(
            task=working_context.request,
            context=working_context.to_context(),
            model=model,
            generation_options=dict(generation_options or {}),
            metadata=request_metadata,
        )

    __call__ = consume
