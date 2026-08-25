from src.ai.errors import (
    CapabilityError,
    InvalidRequestError,
)
from src.ai.models import (
    AIRequest,
    AIResponse,
    AICapabilities,
)
from src.ai.provider import AIProvider


class AIService:
    """
    JARVIS-level orchestration layer for AI providers.

    The service knows which providers are available and
    decides which provider should execute a request.

    It does not implement provider-specific communication.
    """

    def __init__(self, default_provider=None):
        self._providers = {}
        self._default_provider = default_provider

    def register_provider(
        self,
        provider: AIProvider
    ):
        """
        Register an AI provider.

        The provider's normalized name is used as its identifier.
        """

        name = provider.provider_name()

        if not name:
            raise InvalidRequestError(
                "Provider name cannot be empty."
            )

        self._providers[name] = provider

    def set_default_provider(
        self,
        provider_name
    ):
        """
        Select the default provider.
        """

        if provider_name not in self._providers:
            raise InvalidRequestError(
                f"Unknown provider: {provider_name}"
            )

        self._default_provider = provider_name

    def get_provider(
        self,
        provider_name=None
    ):
        """
        Retrieve a registered provider.

        If provider_name is omitted, the default provider
        is used.
        """

        name = (
            provider_name
            or self._default_provider
        )

        if not name:
            raise InvalidRequestError(
                "No AI provider has been selected."
            )

        provider = self._providers.get(name)

        if provider is None:
            raise InvalidRequestError(
                f"Unknown provider: {name}"
            )

        return provider

    def list_providers(self):
        """
        Return the names of all registered providers.
        """

        return tuple(
            self._providers.keys()
        )

    def get_capabilities(
        self,
        provider_name=None
    ) -> AICapabilities:

        provider = self.get_provider(
            provider_name
        )

        return provider.capabilities()

    def _check_capabilities(
        self,
        provider,
        required_capabilities
    ):
        """
        Verify that a provider supports the
        capabilities required by a request.
        """

        if not required_capabilities:
            return

        capabilities = provider.capabilities()

        for capability in required_capabilities:

            supported = getattr(
                capabilities,
                capability,
                False
            )

            if not supported:
                raise CapabilityError(
                    f"Provider '{provider.provider_name()}' "
                    f"does not support capability "
                    f"'{capability}'."
                )

    def generate(
        self,
        request: AIRequest,
        provider_name=None,
        required_capabilities=None,
    ) -> AIResponse:
        """
        Execute an AI request through the selected provider.
        """

        if not isinstance(request, AIRequest):
            raise InvalidRequestError(
                "generate() requires an AIRequest."
            )

        if not request.task.strip():
            raise InvalidRequestError(
                "AIRequest task cannot be empty."
            )

        provider = self.get_provider(
            provider_name
        )

        self._check_capabilities(
            provider,
            required_capabilities
        )

        return provider.generate(
            request
        )