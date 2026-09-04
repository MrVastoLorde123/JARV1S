"""M19.4 personalization integration.

Projects a bounded PersonalizationProfile into the existing WorkingContext as
provider-neutral descriptive context. It does not mutate memory, policy,
authority, authorization, or execution state.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Mapping

from src.context.models import ContextItem, PRIVATE
from src.context.working_context import WorkingContext

from .profile import PersonalizationProfile


class PersonalizationContextIntegrator:
    """Add bounded personalization signals to an existing working context."""

    def integrate(
        self,
        working_context: WorkingContext,
        profile: PersonalizationProfile,
    ) -> WorkingContext:
        if not isinstance(working_context, WorkingContext):
            raise TypeError("working_context must be a WorkingContext")
        if not isinstance(profile, PersonalizationProfile):
            raise TypeError("profile must be a PersonalizationProfile")

        personalization_items = tuple(
            ContextItem(
                source_type="PERSONALIZATION",
                content=(
                    f"{signal.category.lower().replace('_', ' ')} preference/profile signal: "
                    f"{signal.key} = {signal.value}"
                ),
                relevance_score=max(0.0, min(1.0, float(signal.confidence))),
                confidence=signal.confidence,
                importance=signal.importance,
                privacy_level=PRIVATE,
                provenance={
                    "source_id": f"personalization:{signal.signal_id}",
                    "profile_id": profile.profile_id,
                    "signal_id": signal.signal_id,
                    "signal_category": signal.category,
                    "signal_source_ids": signal.source_ids,
                },
            )
            for signal in profile.signals
        )

        existing_items = tuple(working_context.context_package.items)
        package_metadata = dict(working_context.context_package.metadata)
        package_metadata.update(
            {
                "personalization_profile_id": profile.profile_id,
                "personalization_signal_count": len(personalization_items),
            }
        )

        updated_package = replace(
            working_context.context_package,
            items=existing_items + personalization_items,
            metadata=package_metadata,
        )

        runtime_metadata = dict(working_context.metadata)
        runtime_metadata.update(
            {
                "personalization_integrated": True,
                "personalization_profile_id": profile.profile_id,
                "personalization_signal_count": len(personalization_items),
                "personalization_authority_granted": False,
                "personalization_authorization_granted": False,
                "personalization_policy_mutation": False,
                "personalization_execution_requested": False,
            }
        )

        return replace(
            working_context,
            context_package=updated_package,
            metadata=runtime_metadata,
        )


__all__ = ["PersonalizationContextIntegrator"]
