class AIError(Exception):
    """
    Base exception for all JARVIS AI-provider failures.
    """


class AuthenticationError(AIError):
    """
    Provider credentials are missing or invalid.
    """


class RateLimitError(AIError):
    """
    The provider rejected the request because a rate
    or quota limit was reached.
    """


class ProviderUnavailableError(AIError):
    """
    The provider or its service is currently unavailable.
    """


class InvalidRequestError(AIError):
    """
    JARVIS sent a request the provider cannot accept.
    """


class CapabilityError(AIError):
    """
    The requested provider capability is unavailable.
    """


class TimeoutError(AIError):
    """
    The provider did not respond within the allowed time.
    """


class GenerationError(AIError):
    """
    Generation failed for a provider-specific reason
    that does not fit another category.
    """