"""M19.3 behavior-adaptation resolution.

Converts already-accepted bounded adaptations into descriptive behavior
signals. This layer never accepts, rejects, reverses, or authorizes an
adaptation; it only resolves existing state for personalization use.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from src.learning.adaptation import AdaptationRecord, AdaptationState, AdaptationKind

from .profile import PersonalizationProfile, PersonalizationSignal, build_profile


class BehaviorAdaptationResolver:
    """Resolve accepted BEHAVIOR adaptations into an immutable profile."""

    def resolve(
        self,
        adaptations: Iterable[AdaptationRecord],
        *,
        profile_id: str = "personalization-profile",
    ) -> PersonalizationProfile:
        values = tuple(adaptations)
        if any(not isinstance(item, AdaptationRecord) for item in values):
            raise TypeError("adaptations must contain AdaptationRecord values")

        signals: list[PersonalizationSignal] = []
        for record in values:
            if record.state != AdaptationState.ACCEPTED:
                continue
            if record.proposal.kind != AdaptationKind.BEHAVIOR:
                continue

            source_ids = [f"adaptation:{record.record_id}"]
            source_ids.extend(
                f"evaluation:{evaluation_id}"
                for evaluation_id in record.proposal.supporting_evaluation_ids
            )

            signals.append(
                PersonalizationSignal(
                    signal_id=f"behavior:{record.record_id}",
                    category="BEHAVIOR",
                    key=record.proposal.target,
                    value=str(record.proposal.proposed_value),
                    confidence=record.proposal.confidence or 0.0,
                    importance=0.0,
                    source_ids=tuple(source_ids),
                    explicit_user_preference=record.proposal.explicit_user_preference,
                    metadata={
                        "adaptation_record_id": record.record_id,
                        "acceptance_reference": record.acceptance_reference,
                        "current_value": record.proposal.current_value,
                        "proposed_value": record.proposal.proposed_value,
                        "reversible": record.proposal.reversible,
                    },
                )
            )

        return build_profile(
            profile_id,
            tuple(signals),
            provenance={
                "resolver": "m19.3",
                "adaptation_count": len(values),
                "accepted_behavior_count": len(signals),
            },
        )


__all__ = ["BehaviorAdaptationResolver"]
