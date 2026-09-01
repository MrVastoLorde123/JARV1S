"""Natural-language request routing built on top of the deterministic command router."""

from __future__ import annotations

from src.core.request_intent import IntentKind, RequestIntent, RequestIntentClassifier
from src.core.request_router import RequestRouter
from src.core.task_models import RequestType, RouteDecision, TaskRequest, TaskType


class IntelligentRequestRouter:
    """Route ordinary language after preserving explicit command semantics."""

    def __init__(
        self,
        classifier: RequestIntentClassifier,
        *,
        base_router: RequestRouter | None = None,
    ) -> None:
        if not isinstance(classifier, RequestIntentClassifier):
            raise TypeError("classifier must implement RequestIntentClassifier")
        self._classifier = classifier
        self._base_router = base_router or RequestRouter()

    def route(self, text: str) -> RouteDecision:
        """Return a structured route without executing the destination."""
        if not isinstance(text, str):
            raise TypeError("Request input must be a string.")
        if not text.strip():
            raise ValueError("Request input cannot be empty.")

        explicit = self._base_router.route(text)
        if explicit.request_type == RequestType.COMMAND:
            return explicit

        intent = self._classifier.classify(text.strip())
        return self._from_intent(text, intent)

    @staticmethod
    def _from_intent(original_input: str, intent: RequestIntent) -> RouteDecision:
        metadata = {
            "intent_kind": intent.kind.value,
            "intent_reasoning": intent.reasoning,
        }
        if intent.confidence is not None:
            metadata["intent_confidence"] = intent.confidence

        if intent.kind in (IntentKind.TASK, IntentKind.TOOL):
            task_type = (
                TaskType.TOOL
                if intent.kind == IntentKind.TOOL
                else TaskType.ACTION
            )
            task = TaskRequest(
                content=intent.content,
                task_type=task_type,
                metadata=dict(intent.metadata or {}),
            )
            return RouteDecision(
                request_type=RequestType.TASK,
                original_input=original_input,
                task=task,
                reason="Natural-language intent was classified as executable work.",
                metadata=metadata,
            )

        return RouteDecision(
            request_type=RequestType.CONVERSATION,
            original_input=original_input,
            reason="Natural-language intent remains on the conversational path.",
            metadata=metadata,
        )
