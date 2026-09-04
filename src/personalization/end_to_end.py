"""M19.6 end-to-end personalization integration boundary.

Personalization is injected through the existing WorkingContextRuntime seam.
It remains descriptive context only and cannot alter routing, policy,
confirmation, authorization, or execution semantics.
"""

from __future__ import annotations

from collections.abc import Iterable

from src.context.working_context import WorkingContext
from src.context.working_context_runtime import WorkingContextRuntime
from src.learning.adaptation import AdaptationRecord

from .integration import PersonalizationContextIntegrator
from .persistence import PersonalizationStore
from .profile import PersonalizationProfile, build_profile
from .runtime import PersonalizationRuntime


class PersonalizedWorkingContextRuntime(WorkingContextRuntime):
    """Decorate the established context runtime with bounded personalization."""

    def __init__(
        self,
        base_runtime: WorkingContextRuntime,
        *,
        personalization_runtime: PersonalizationRuntime | None = None,
        persistence_store: PersonalizationStore | None = None,
        profile_id: str = "personalization-profile",
        preference_limit: int = 10,
    ) -> None:
        if not isinstance(base_runtime, WorkingContextRuntime):
            raise TypeError("base_runtime must be a WorkingContextRuntime")
        super().__init__(base_runtime.source_provider, integration=base_runtime.integration)
        self.base_runtime = base_runtime
        self.personalization_runtime = personalization_runtime or PersonalizationRuntime()
        self.persistence_store = persistence_store
        self.profile_id = profile_id
        self.preference_limit = preference_limit

    def _merged_profile(
        self,
        query: str,
        *,
        adaptations: Iterable[AdaptationRecord] = (),
    ) -> PersonalizationProfile:
        dynamic = self.personalization_runtime.build_profile(
            query,
            profile_id=self.profile_id,
            preference_limit=self.preference_limit,
            adaptations=adaptations,
        )
        if self.persistence_store is None:
            return dynamic

        persisted = self.persistence_store.active_profile(self.profile_id)
        signals_by_id = {signal.signal_id: signal for signal in persisted.signals}
        signals_by_id.update({signal.signal_id: signal for signal in dynamic.signals})
        return build_profile(
            self.profile_id,
            tuple(signals_by_id.values()),
            provenance={
                "runtime": "m19.6",
                "persisted_signal_count": len(persisted.signals),
                "dynamic_signal_count": len(dynamic.signals),
            },
        )

    def compose(self, request: str, **kwargs) -> WorkingContext:
        adaptations = kwargs.pop("personalization_adaptations", ())
        working_context = self.base_runtime.compose(request, **kwargs)
        profile = self._merged_profile(request, adaptations=adaptations)
        integrated = PersonalizationContextIntegrator().integrate(working_context, profile)
        return integrated


__all__ = ["PersonalizedWorkingContextRuntime"]
