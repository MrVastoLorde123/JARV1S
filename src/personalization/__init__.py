"""M19 bounded personalization contracts."""

from .preference_context import PreferenceContextResolver
from .profile import (
    PROFILE_CATEGORIES,
    PersonalizationProfile,
    PersonalizationSignal,
    build_profile,
)

__all__ = [
    "PROFILE_CATEGORIES",
    "PersonalizationProfile",
    "PersonalizationSignal",
    "PreferenceContextResolver",
    "build_profile",
]
