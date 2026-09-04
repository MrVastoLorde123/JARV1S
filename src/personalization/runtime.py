"""M19 personalization runtime facade.

Composes preference/behavior resolution with WorkingContext projection.
This facade owns personalization composition only; it does not interpret
intent, mutate policy, authorize actions, or execute capabilities.
"""

from __future__ import annotations

from collections.abc import Iterable

from src.context.working_context import WorkingContext
from src.learning.adaptation import AdaptationRecord

from .behavior_context import BehaviorAdaptationResolver
from .integration import PersonalizationContextIntegrator
from .preference_context import PreferenceContextResolver
from .profile import PersonalizationProfile, build_profile


class PersonalizationRuntime:
    """Build bounded personalization context from established learning state."""

    def __init__(
        self,
        *,
        preference_resolver: PreferenceContextResolver | None = None,
        behavior_resolver: BehaviorAdaptationResolver | None = None,
        integrator: PersonalizationContextIntegrator | None = None,
    ) -> None:
        self.preference_resolver = preference_resolver or PreferenceContextResolver()
        self.behavior_resolver = behavior_resolver or BehaviorAdaptationResolver()
        self.integrator = integrator or PersonalizationContextIntegrator()

    def build_profile(
        self,
        query: str,
        *,
        profile_id: str = "personalization-profile",
        preference_limit: int = 10,
        adaptations: Iterable[AdaptationRecord] = (),
    ) -> PersonalizationProfile:
        preference_profile = self.preference_resolver.resolve(
            query,
            profile_id=profile_id,
            limit=preference_limit,
        )
        behavior_profile = self.behavior_resolver.resolve(
            adaptations,
            profile_id=profile_id,
        )
        signals = preference_profile.signals + behavior_profile.signals
        return build_profile(
            profile_id,
            signals,
            provenance={
                "runtime": "m19.4",
                "query": query.strip(),
                "preference_count": len(preference_profile.signals),
                "behavior_count": len(behavior_profile.signals),
            },
        )

    def apply(
        self,
        working_context: WorkingContext,
        *,
        query: str | None = None,
        profile_id: str = "personalization-profile",
        preference_limit: int = 10,
        adaptations: Iterable[AdaptationRecord] = (),
    ) -> WorkingContext:
        if not isinstance(working_context, WorkingContext):
            raise TypeError("working_context must be a WorkingContext")
        effective_query = working_context.request if query is None else query
        if not isinstance(effective_query, str) or not effective_query.strip():
            raise ValueError("query must be a non-empty string")

        profile = self.build_profile(
            effective_query,
            profile_id=profile_id,
            preference_limit=preference_limit,
            adaptations=adaptations,
        )
        return self.integrator.integrate(working_context, profile)


__all__ = ["PersonalizationRuntime"]
