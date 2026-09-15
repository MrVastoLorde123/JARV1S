from dataclasses import replace

from src.ai.errors import (
    CapabilityError,
    InvalidRequestError,
)
from src.ai.model_routing import (
    ModelProfile,
    ModelRole,
    ModelRouter,
    RoutingRequest,
)
from src.ai.models import (
    AIRequest,
    AIResponse,
    AICapabilities,
)
from src.ai.provider import AIProvider


class AIService:
    """
    JARVIS-level orchestration layer for AI providers and model routing.

    Model routing selects a cognitive component; it does not grant authority,
    permissions, tools, execution rights, or verification truth.
    """

    def __init__(self, default_provider=None, model_router=None):
        self._providers = {}
        self._default_provider = default_provider
        self._model_router = model_router or ModelRouter()

    def register_provider(
        self,
        provider: AIProvider
    ):
        """Register an AI provider under its normalized provider name."""
        name = provider.provider_name()
        if not name:
            raise InvalidRequestError("Provider name cannot be empty.")
        self._providers[name] = provider

    def set_default_provider(
        self,
        provider_name
    ):
        """Select the default provider."""
        if provider_name not in self._providers:
            raise InvalidRequestError(
                f"Unknown provider: {provider_name}"
            )
        self._default_provider = provider_name

    def get_provider(
        self,
        provider_name=None
    ):
        """Retrieve a registered provider, using the default when omitted."""
        name = provider_name or self._default_provider
        if not name:
            raise InvalidRequestError("No AI provider has been selected.")
        provider = self._providers.get(name)
        if provider is None:
            raise InvalidRequestError(f"Unknown provider: {name}")
        return provider

    def list_providers(self):
        """Return the names of all registered providers."""
        return tuple(self._providers.keys())

    def register_model(
        self,
        profile: ModelProfile,
    ) -> None:
        """Register an observed model profile for deterministic routing."""
        self._model_router.register(profile)

    def set_model_router(
        self,
        model_router: ModelRouter,
    ) -> None:
        """Replace the model router without changing provider semantics."""
        if not isinstance(model_router, ModelRouter):
            raise TypeError("model_router must be a ModelRouter")
        self._model_router = model_router

    def list_models(self):
        """Return the currently registered model profiles."""
        return self._model_router.list_profiles()

    def route_model(
        self,
        role: ModelRole,
        preferred_model: str | None = None,
    ):
        """Select a cognitive model without granting any runtime authority."""
        return self._model_router.route(
            RoutingRequest(
                role=role,
                preferred_model=preferred_model,
            )
        )

    def get_capabilities(
        self,
        provider_name=None
    ) -> AICapabilities:
        provider = self.get_provider(provider_name)
        return provider.capabilities()

    def _check_capabilities(
        self,
        provider,
        required_capabilities
    ):
        """Verify that a provider supports required request capabilities."""
        if not required_capabilities:
            return
        capabilities = provider.capabilities()
        for capability in required_capabilities:
            supported = getattr(capabilities, capability, False)
            if not supported:
                raise CapabilityError(
                    f"Provider '{provider.provider_name()}' "
                    f"does not support capability '{capability}'."
                )

    def generate(
        self,
        request: AIRequest,
        provider_name=None,
        required_capabilities=None,
    ) -> AIResponse:
        """Execute an AI request through the selected provider."""
        if not isinstance(request, AIRequest):
            raise InvalidRequestError("generate() requires an AIRequest.")
        if not request.task.strip():
            raise InvalidRequestError("AIRequest task cannot be empty.")

        provider = self.get_provider(provider_name)
        self._check_capabilities(provider, required_capabilities)
        return provider.generate(request)

    def generate_for_role(
        self,
        request: AIRequest,
        role: ModelRole,
        provider_name=None,
        preferred_model=None,
        required_capabilities=None,
    ) -> AIResponse:
        """
        Route a request to a model role, then execute through the provider.

        Routing remains a cognitive selection only. Authority, permissions,
        tools, verification, and execution policy remain outside the router.
        """
        if not isinstance(request, AIRequest):
            raise InvalidRequestError("generate_for_role() requires an AIRequest.")
        decision = self.route_model(
            role=role,
            preferred_model=preferred_model or request.model,
        )
        routed_request = replace(request, model=decision.model_id)
        return self.generate(
            routed_request,
            provider_name=provider_name,
            required_capabilities=required_capabilities,
        )
