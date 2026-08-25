from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AIRequest:
    """
    Provider-neutral request sent from JARVIS to an AI provider.
    """

    task: str
    context: Any

    model: str | None = None

    generation_options: dict[str, Any] = field(
        default_factory=dict
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class AIUsage:
    """
    Optional usage information returned by an AI provider.

    Providers that do not expose usage information can
    leave these values as None.
    """

    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(frozen=True)
class AIResponse:
    """
    Provider-neutral response returned to JARVIS.
    """

    content: Any

    provider: str
    model: str

    finish_reason: str | None = None

    usage: AIUsage | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class AICapabilities:
    """
    Describes capabilities offered by an AI provider.
    """

    text_generation: bool = False
    streaming: bool = False
    structured_output: bool = False
    tool_calling: bool = False
    vision: bool = False
    embeddings: bool = False