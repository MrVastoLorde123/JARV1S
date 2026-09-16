"""Core-test compatibility fixtures for the strict model-routing contract.

Core tests predate mandatory role routing and commonly construct ``AIService``
with a provider but without a model profile.  Keep that adaptation in the
core-test boundary rather than weakening production routing semantics.
"""

from src.ai.model_routing import ModelProfile, ModelRole
from src.ai.service import AIService


_original_register_provider = AIService.register_provider


def _register_provider_with_test_general_model(self, provider):
    _original_register_provider(self, provider)
    model_id = f"core-test:{provider.provider_name()}"
    try:
        self.register_model(
            ModelProfile(
                model_id=model_id,
                roles=frozenset({ModelRole.GENERAL}),
                priority=0,
            )
        )
    except Exception:
        # Services explicitly backed by a routing runtime/catalog retain their
        # own configuration and must not be mutated by the core-test fixture.
        raise


if not getattr(AIService.register_provider, "_core_test_routing_adapter", False):
    _register_provider_with_test_general_model._core_test_routing_adapter = True
    AIService.register_provider = _register_provider_with_test_general_model
