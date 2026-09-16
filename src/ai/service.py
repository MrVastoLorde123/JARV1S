from dataclasses import fields, replace

from src.ai.errors import (
    CapabilityError,
    InvalidRequestError,
)
from src.ai.model_catalog import ModelCatalog
from src.ai.model_routing import (
    ModelProfile,
    ModelRole,
    ModelRouter,
    RoutingRequest,
)
from src.ai.model_routing_runtime import ModelRoutingRuntime
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

    def __init__(self, default_provider=None, model_router=None, model_catalog=None, model_routing_runtime=None):
        if model_routing_runtime is not None and (model_router is not None or model_catalog is not None):
            raise TypeError("provide model_routing_runtime or model_router/model_catalog, not both")
        self._providers = {}
        self._default_provider = default_provider
        self._model_router = model_router or ModelRouter()
        self._model_catalog = None
        self._model_routing_runtime = None
        self._model_routing_configured = (
            model_router is not None
            or model_catalog is not None
            or model_routing_runtime is not None
        )
        if model_catalog is not None:
            self.set_model_catalog(model_catalog)
        if model_routing_runtime is not None:
            self.set_model_routing_runtime(model_routing_runtime)

    def register_provider(self, provider: AIProvider):
        """Register an AI provider under its normalized provider name."""
        if not isinstance(provider, AIProvider):
            raise TypeError("provider must be an AIProvider")
        name = provider.provider_name()
        if not isinstance(name, str) or not name.strip():
            raise InvalidRequestError("Provider name cannot be empty.")
        if name in self._providers and self._providers[name] is not provider:
            raise InvalidRequestError(f"Provider '{name}' is already registered.")
        self._providers[name] = provider

    def set_default_provider(self, provider_name):
        """Select the default provider."""
        if provider_name not in self._providers:
            raise InvalidRequestError(f"Unknown provider: {provider_name}")
        self._default_provider = provider_name

    def get_provider(self, provider_name=None):
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

    def register_model(self, profile: ModelProfile) -> None:
        """Register an observed model profile for deterministic routing."""
        if self._model_routing_runtime is not None:
            raise InvalidRequestError("register_model() is unavailable with model routing runtime")
        self._model_routing_configured = True
        self._model_router.register(profile)

    def set_model_router(self, model_router: ModelRouter) -> None:
        """Replace the model router without changing provider semantics."""
        if not isinstance(model_router, ModelRouter):
            raise TypeError("model_router must be a ModelRouter")
        self._model_router = model_router
        self._model_catalog = None
        self._model_routing_runtime = None
        self._model_routing_configured = True

    def set_model_catalog(self, model_catalog: ModelCatalog) -> None:
        """Bind a runtime observation catalog as the routing availability source."""
        if not isinstance(model_catalog, ModelCatalog):
            raise TypeError("model_catalog must be a ModelCatalog")
        if self._model_routing_runtime is not None:
            raise InvalidRequestError("model catalog cannot replace model routing runtime")
        self._model_catalog = model_catalog
        self._model_router = model_catalog.router()
        self._model_routing_configured = True

    def set_model_routing_runtime(self, model_routing_runtime: ModelRoutingRuntime) -> None:
        """Bind observation, role policy, and routing as one runtime boundary."""
        if not isinstance(model_routing_runtime, ModelRoutingRuntime):
            raise TypeError("model_routing_runtime must be a ModelRoutingRuntime")
        self._model_routing_runtime = model_routing_runtime
        self._model_catalog = model_routing_runtime.catalog
        self._model_router = ModelRouter()
        self._model_routing_configured = True

    def list_models(self):
        """Return registered model profiles or current runtime/catalog profiles."""
        if self._model_routing_runtime is not None:
            return self._model_routing_runtime.list_models()
        if self._model_catalog is not None:
            return self._model_catalog.profiles()
        return self._model_router.list_profiles()

    def observed_model_ids(self) -> tuple[str, ...]:
        """Return the latest provider-observed model identifiers."""
        if self._model_routing_runtime is not None:
            return self._model_routing_runtime.observed_model_ids()
        if self._model_catalog is not None:
            return self._model_catalog.observed_model_ids()
        return ()

    def observe_models(self, model_ids) -> None:
        """Refresh model availability from an explicit provider observation."""
        if self._model_routing_runtime is not None:
            self._model_routing_runtime.observe_models(model_ids)
            return
        if self._model_catalog is None:
            raise InvalidRequestError("No model catalog has been configured.")
        self._model_catalog.observe_ids(model_ids)
        self._model_router = self._model_catalog.router()

    def observe_openai_models(self, payload) -> tuple[str, ...]:
        """Refresh model availability from an OpenAI-compatible /v1/models payload."""
        if self._model_routing_runtime is not None:
            return self._model_routing_runtime.observe_openai_models(payload)
        if self._model_catalog is None:
            raise InvalidRequestError("No model catalog has been configured.")
        observed = self._model_catalog.observe_openai_models(payload)
        self._model_router = self._model_catalog.router()
        return observed

    def observe_provider_models(self, provider_name=None) -> tuple[str, ...]:
        """Observe a provider's model inventory without executing a generation request."""
        provider = self.get_provider(provider_name)
        list_models = getattr(provider, "list_models", None)
        if not callable(list_models):
            raise InvalidRequestError(
                f"Provider '{provider.provider_name()}' does not expose model observation."
            )
        try:
            observed = tuple(list_models())
        except TypeError as exc:
            raise InvalidRequestError(
                f"Provider '{provider.provider_name()}' returned a non-iterable model inventory."
            ) from exc
        if any(not isinstance(model_id, str) or not model_id.strip() for model_id in observed):
            raise InvalidRequestError(
                f"Provider '{provider.provider_name()}' returned an invalid model inventory."
            )
        self.observe_models(observed)
        return observed

    def route_model(self, role: ModelRole, preferred_model=None):
        """Select a cognitive model without granting any runtime authority."""
        if self._model_routing_runtime is not None:
            return self._model_routing_runtime.route(role, preferred_model=preferred_model)
        return self._model_router.route(
            RoutingRequest(role=role, preferred_model=preferred_model)
        )

    def get_capabilities(self, provider_name=None) -> AICapabilities:
        provider = self.get_provider(provider_name)
        capabilities = provider.capabilities()
        if not isinstance(capabilities, AICapabilities):
            raise InvalidRequestError("Provider capabilities() must return AICapabilities.")
        return capabilities

    def _check_capabilities(self, provider, required_capabilities):
        """Verify that a provider supports required request capabilities."""
        if not required_capabilities:
            return
        capabilities = self.get_capabilities(provider.provider_name())
        declared_capabilities = {item.name for item in fields(AICapabilities)}
        for capability in required_capabilities:
            if not isinstance(capability, str) or not capability.strip():
                raise InvalidRequestError("required_capabilities must contain non-empty strings.")
            if capability not in declared_capabilities:
                raise InvalidRequestError(f"Unknown provider capability '{capability}'.")
            if not isinstance(getattr(capabilities, capability), bool):
                raise InvalidRequestError(f"Provider capability '{capability}' is not boolean.")
            if not getattr(capabilities, capability):
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
        if not isinstance(request.task, str) or not request.task.strip():
            raise InvalidRequestError("AIRequest task cannot be empty.")
        provider = self.get_provider(provider_name)
        self._check_capabilities(provider, required_capabilities)
        response = provider.generate(request)
        if not isinstance(response, AIResponse):
            raise InvalidRequestError("AI provider generate() must return AIResponse.")
        if response.provider != provider.provider_name():
            raise InvalidRequestError(
                f"AI provider response names '{response.provider}', expected '{provider.provider_name()}'."
            )
        if not isinstance(response.model, str) or not response.model.strip():
            raise InvalidRequestError("AI provider response model cannot be empty.")
        return response

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

        explicit_model = preferred_model or request.model
        decision = self.route_model(
            role=role,
            preferred_model=explicit_model,
        )
        routed_request = replace(request, model=decision.model_id)
        return self.generate(
            routed_request,
            provider_name=provider_name,
            required_capabilities=required_capabilities,
        )
