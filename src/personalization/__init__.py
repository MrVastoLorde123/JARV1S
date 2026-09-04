"""M19 bounded personalization contracts."""

from .behavior_context import BehaviorAdaptationResolver
from .preference_context import PreferenceContextResolver
from .profile import (
    PROFILE_CATEGORIES,
    PersonalizationProfile,
    PersonalizationSignal,
    build_profile,
)

__all__ = [
    "BehaviorAdaptationResolver",
    "PROFILE_CATEGORIES",
    "PersonalizationProfile",
    "PersonalizationSignal",
    "PreferenceContextResolver",
    "build_profile",
]
