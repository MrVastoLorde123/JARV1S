from abc import ABC, abstractmethod

from src.ai.models import (
    AIRequest,
    AIResponse,
    AICapabilities,
)


class AIProvider(ABC):
    """
    Provider-neutral contract for intelligence providers.

    JARVIS interacts with providers through this interface
    rather than directly depending on a specific AI service.
    """

    @abstractmethod
    def generate(
        self,
        request: AIRequest
    ) -> AIResponse:
        """
        Generate a response for a JARVIS request.
        """

        raise NotImplementedError

    @abstractmethod
    def capabilities(self) -> AICapabilities:
        """
        Return the capabilities supported by this provider.
        """

        raise NotImplementedError

    @abstractmethod
    def provider_name(self) -> str:
        """
        Return the normalized JARVIS provider name.
        """

        raise NotImplementedError