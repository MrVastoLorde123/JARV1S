"""M26.3: bounded provider-neutral model suggestion boundary."""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from src.ai.models import AIRequest, AIResponse
from src.ai.provider import AIProvider


class ModelProviderBoundaryError(RuntimeError):
    """Raised when model-provider output cannot cross safely."""


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class ModelSuggestion:
    """Immutable observation produced by a model; never a JARVIS decision."""

    content: Any
    provider: str
    model: str
    finish_reason: str | None
    usage: Any
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        for name in ("provider", "model"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", _freeze(self.metadata))

    @property
    def is_model_output(self) -> bool:
        return True

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def executes_capability(self) -> bool:
        return False

    @property
    def mutates_state(self) -> bool:
        return False

    @property
    def persists_state(self) -> bool:
        return False

    @property
    def establishes_truth(self) -> bool:
        return False

    @property
    def establishes_certainty(self) -> bool:
        return False


class ModelProviderBoundary:
    """Expose an AI provider to JARVIS strictly as a suggestion source."""

    def __init__(self, provider: AIProvider) -> None:
        if not isinstance(provider, AIProvider):
            raise TypeError("provider must implement AIProvider")
        self._provider = provider

    def suggest(
        self,
        task: str,
        context: Any,
        *,
        model: str | None = None,
        generation_options: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> ModelSuggestion:
        """Generate provider output and return it as a bounded suggestion."""
        if not isinstance(task, str) or not task.strip():
            raise ValueError("task must be a non-empty string")
        if generation_options is not None and not isinstance(generation_options, Mapping):
            raise TypeError("generation_options must be a mapping or None")
        if metadata is not None and not isinstance(metadata, Mapping):
            raise TypeError("metadata must be a mapping or None")

        request = AIRequest(
            task=task.strip(),
            context=context,
            model=model,
            generation_options=dict(generation_options or {}),
            metadata=dict(metadata or {}),
        )
        response = self._provider.generate(request)
        if type(response) is not AIResponse:
            raise ModelProviderBoundaryError("provider must return an AIResponse")
        if not isinstance(response.provider, str) or not response.provider.strip():
            raise ModelProviderBoundaryError("provider response has invalid provider identity")
        if not isinstance(response.model, str) or not response.model.strip():
            raise ModelProviderBoundaryError("provider response has invalid model identity")

        return ModelSuggestion(
            content=response.content,
            provider=response.provider,
            model=response.model,
            finish_reason=response.finish_reason,
            usage=response.usage,
            metadata=response.metadata,
        )

    @property
    def provider_name(self) -> str:
        return self._provider.provider_name()

    @property
    def is_ai_provider(self) -> bool:
        return False

    @property
    def authorizes_execution(self) -> bool:
        return False

    @property
    def executes_capability(self) -> bool:
        return False

    @property
    def mutates_state(self) -> bool:
        return False

    @property
    def persists_state(self) -> bool:
        return False

    @property
    def establishes_truth(self) -> bool:
        return False

    @property
    def establishes_certainty(self) -> bool:
        return False


__all__ = ["ModelProviderBoundaryError", "ModelSuggestion", "ModelProviderBoundary"]
