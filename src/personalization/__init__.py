"""M19 bounded personalization contracts."""

from .behavior_context import BehaviorAdaptationResolver
from .integration import PersonalizationContextIntegrator
from .preference_context import PreferenceContextResolver
from .profile import (
    PROFILE_CATEGORIES,
    PersonalizationProfile,
    PersonalizationSignal,
    build_profile,
)
from .runtime import PersonalizationRuntime

__all__ = [
    "PROFILE_CATEGORIES",
    "PersonalizationProfile",
    "PersonalizationSignal",
    "BehaviorAdaptationResolver",
    "PersonalizationContextIntegrator",
    "PreferenceContextResolver",
    "PersonalizationRuntime",
    "build_profile",
]
