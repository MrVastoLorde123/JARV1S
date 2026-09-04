"""M19 bounded personalization contracts."""

from .behavior_context import BehaviorAdaptationResolver
from .end_to_end import PersonalizedWorkingContextRuntime
from .integration import PersonalizationContextIntegrator
from .persistence import (
    PersonalizationPersistenceConflictError,
    PersonalizationRecord,
    PersonalizationState,
    PersonalizationStore,
)
from .preference_context import PreferenceContextResolver
from .profile import (
    PROFILE_CATEGORIES,
    PersonalizationProfile,
    PersonalizationSignal,
    build_profile,
)
from .runtime import PersonalizationRuntime
from .runtime_m195 import persist_profile, reverse_profile_signal

__all__ = [
    "PROFILE_CATEGORIES",
    "PersonalizationProfile",
    "PersonalizationSignal",
    "BehaviorAdaptationResolver",
    "PersonalizationContextIntegrator",
    "PreferenceContextResolver",
    "PersonalizationRuntime",
    "PersonalizedWorkingContextRuntime",
    "PersonalizationPersistenceConflictError",
    "PersonalizationRecord",
    "PersonalizationState",
    "PersonalizationStore",
    "persist_profile",
    "reverse_profile_signal",
    "build_profile",
]
