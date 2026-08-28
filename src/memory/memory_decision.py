from src.memory.memory_decision_models import (
    MemoryDecision,
    MemoryDecisionContext,
    VALID_DECISIONS,
)

from src.memory.memory_decision_provider import (
    MemoryDecisionProvider,
)


class MemoryDecisionService:
    """
    Orchestrates memory-decision providers.

    The service chooses a provider and validates the returned
    decision.

    It does not persist anything.
    """

    def __init__(
        self,
        default_provider: str | None = None,
    ):
        self._providers = {}

        self._default_provider = (
            default_provider
        )

    def register_provider(
        self,
        provider: MemoryDecisionProvider,
    ):
        """
        Register a memory decision provider.
        """

        if not isinstance(
            provider,
            MemoryDecisionProvider,
        ):
            raise TypeError(
                "Provider must implement "
                "MemoryDecisionProvider."
            )

        name = provider.provider_name()

        if not isinstance(
            name,
            str,
        ) or not name.strip():

            raise ValueError(
                "Provider name must be a "
                "non-empty string."
            )

        name = name.strip()

        self._providers[name] = provider

        if (
            self._default_provider is None
        ):
            self._default_provider = name

    def get_provider(
        self,
        provider_name: str | None = None,
    ):
        """
        Resolve a provider.
        """

        name = (
            provider_name
            or self._default_provider
        )

        if name is None:
            raise ValueError(
                "No default memory decision "
                "provider is configured."
            )

        provider = self._providers.get(
            name
        )

        if provider is None:
            raise ValueError(
                f"Unknown memory decision "
                f"provider: {name}"
            )

        return provider

    def provider_names(
        self,
    ):
        """
        Return registered provider names.
        """

        return tuple(
            sorted(
                self._providers.keys()
            )
        )

    def decide(
        self,
        context: MemoryDecisionContext,
        provider_name: str | None = None,
    ) -> MemoryDecision:
        """
        Ask the selected provider for a decision.
        """

        if not isinstance(
            context,
            MemoryDecisionContext,
        ):
            raise TypeError(
                "context must be a "
                "MemoryDecisionContext."
            )

        provider = self.get_provider(
            provider_name
        )

        decision = provider.decide(
            context
        )

        if not isinstance(
            decision,
            MemoryDecision,
        ):
            raise TypeError(
                "Memory decision provider "
                "must return MemoryDecision."
            )

        if decision.action not in (
            VALID_DECISIONS
        ):
            raise ValueError(
                f"Invalid memory decision "
                f"action: {decision.action}"
            )

        return decision