from dataclasses import dataclass
from typing import Any

from src.ai.models import AIResponse
from src.context.models import ContextPackage


@dataclass(frozen=True)
class JARVISResponse:
    """
    Structured response returned by the JARVIS Core.

    The user-facing answer is stored in `content`.

    Conversation responses preserve the original AI response and
    context used to produce it. Command and execution responses
    may not have either and therefore store None.
    """

    content: str

    ai_response: AIResponse | None

    context: ContextPackage | None

    metadata: dict[str, Any]
