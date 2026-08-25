from dataclasses import dataclass
from typing import Any

from src.ai.models import AIResponse
from src.context.models import ContextPackage


@dataclass(frozen=True)
class JARVISResponse:
    """
    Structured response returned by the JARVIS Core.

    The user-facing answer is stored in `content`.

    The original AI response and the context used to
    produce it are preserved for provenance and debugging.
    """

    content: str
    ai_response: AIResponse
    context: ContextPackage

    metadata: dict[str, Any]