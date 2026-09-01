"""Provider-neutral natural-language intent classification for JARVIS."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from src.ai.models import AIRequest
from src.ai.service import AIService


class IntentKind(str, Enum):
    """High-level intent categories produced by the interpretation layer."""

    CONVERSATION = "conversation"
    QUESTION = "question"
    TASK = "task"
    TOOL = "tool"


@dataclass(frozen=True)
class RequestIntent:
    """Untrusted but structurally validated interpretation of user input."""

    kind: IntentKind
    content: str
    reasoning: str = ""
    confidence: float | None = None
    metadata: dict[str, Any] | None = None


@runtime_checkable
class RequestIntentClassifier(Protocol):
    """Classify ordinary natural language without executing anything."""

    def classify(self, text: str) -> RequestIntent:
        ...


class AIRequestIntentClassifier:
    """Use an AI provider to classify natural language into a small intent vocabulary.

    The model returns data only. No routing side effect or tool execution is
    performed by this class.
    """

    _KINDS = {kind.value: kind for kind in IntentKind}

    def __init__(self, ai_service: AIService, *, provider_name: str | None = None) -> None:
        if not isinstance(ai_service, AIService):
            raise TypeError("ai_service must be an AIService")
        self._ai_service = ai_service
        self._provider_name = provider_name

    def classify(self, text: str) -> RequestIntent:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        if not text.strip():
            raise ValueError("text cannot be empty")

        response = self._ai_service.generate(
            AIRequest(
                task=(
                    "Classify the user's request. Return ONLY a JSON object with "
                    "kind, content, reasoning, and optional confidence. "
                    "kind must be exactly one of: conversation, question, task, tool. "
                    "Use tool when the user is asking JARVIS to operate a capability; "
                    "use task for a broader action that may later require planning; "
                    "use question for information-seeking requests; use conversation "
                    "for ordinary dialogue. Do not execute anything.\n\n"
                    f"User input: {text}"
                ),
                context=None,
                generation_options={"temperature": 0},
                metadata={"purpose": "request_intent_classification"},
            ),
            provider_name=self._provider_name,
        )

        try:
            parsed = json.loads(str(response.content))
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError("AI returned invalid JSON intent classification") from exc

        if not isinstance(parsed, dict):
            raise ValueError("AI intent classification must be a JSON object")

        kind_value = parsed.get("kind")
        if not isinstance(kind_value, str) or kind_value.strip().lower() not in self._KINDS:
            raise ValueError("AI returned an unsupported intent kind")

        content = parsed.get("content", text)
        if not isinstance(content, str) or not content.strip():
            raise ValueError("AI intent content must be a non-empty string")

        confidence = parsed.get("confidence")
        if confidence is not None:
            if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
                raise ValueError("intent confidence must be numeric")
            if not 0.0 <= float(confidence) <= 1.0:
                raise ValueError("intent confidence must be between 0 and 1")

        reasoning = parsed.get("reasoning", "")
        if not isinstance(reasoning, str):
            raise ValueError("intent reasoning must be a string")

        return RequestIntent(
            kind=self._KINDS[kind_value.strip().lower()],
            content=content.strip(),
            reasoning=reasoning,
            confidence=float(confidence) if confidence is not None else None,
            metadata={"source": "ai"},
        )
