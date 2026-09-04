"""M14.7 integrated personal world-model boundary.

WorldModelContext is a provider-neutral, immutable composition of the M14
context layers. Integration exposes context; it does not create truth,
intent, policy, authorization, or execution authority.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .cross_domain import CrossDomainContext
from .goal_project import GoalProjectContext
from .relevance import RelevanceResult
from .situational import SituationalContext
from .temporal import TemporalContext
from .world_state import ContextState


class WorldModelValidationError(ValueError):
    """Raised when the integrated world-model boundary is invalid."""


@dataclass(frozen=True)
class WorldModelContext:
    """Immutable integration facade over the M14 context domains."""

    state: ContextState | None = None
    temporal: TemporalContext | None = None
    goal_project: GoalProjectContext | None = None
    situational: SituationalContext | None = None
    cross_domain: CrossDomainContext | None = None
    relevance: RelevanceResult | None = None

    def __post_init__(self) -> None:
        fields = (
            ("state", self.state, ContextState),
            ("temporal", self.temporal, TemporalContext),
            ("goal_project", self.goal_project, GoalProjectContext),
            ("situational", self.situational, SituationalContext),
            ("cross_domain", self.cross_domain, CrossDomainContext),
            ("relevance", self.relevance, RelevanceResult),
        )
        for name, value, expected in fields:
            if value is not None and not isinstance(value, expected):
                raise WorldModelValidationError(
                    f"{name} must be {expected.__name__} or None"
                )

    def with_state(self, state: ContextState | None) -> "WorldModelContext":
        return WorldModelContext(
            state=state,
            temporal=self.temporal,
            goal_project=self.goal_project,
            situational=self.situational,
            cross_domain=self.cross_domain,
            relevance=self.relevance,
        )

    def with_temporal(self, temporal: TemporalContext | None) -> "WorldModelContext":
        return WorldModelContext(
            state=self.state,
            temporal=temporal,
            goal_project=self.goal_project,
            situational=self.situational,
            cross_domain=self.cross_domain,
            relevance=self.relevance,
        )

    def with_goal_project(
        self, goal_project: GoalProjectContext | None
    ) -> "WorldModelContext":
        return WorldModelContext(
            state=self.state,
            temporal=self.temporal,
            goal_project=goal_project,
            situational=self.situational,
            cross_domain=self.cross_domain,
            relevance=self.relevance,
        )

    def with_situational(
        self, situational: SituationalContext | None
    ) -> "WorldModelContext":
        return WorldModelContext(
            state=self.state,
            temporal=self.temporal,
            goal_project=self.goal_project,
            situational=situational,
            cross_domain=self.cross_domain,
            relevance=self.relevance,
        )

    def with_cross_domain(
        self, cross_domain: CrossDomainContext | None
    ) -> "WorldModelContext":
        return WorldModelContext(
            state=self.state,
            temporal=self.temporal,
            goal_project=self.goal_project,
            situational=self.situational,
            cross_domain=cross_domain,
            relevance=self.relevance,
        )

    def with_relevance(self, relevance: RelevanceResult | None) -> "WorldModelContext":
        return WorldModelContext(
            state=self.state,
            temporal=self.temporal,
            goal_project=self.goal_project,
            situational=self.situational,
            cross_domain=self.cross_domain,
            relevance=relevance,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": None if self.state is None else self.state.to_dict(),
            "temporal": None if self.temporal is None else self.temporal.to_dict(),
            "goal_project": None if self.goal_project is None else self.goal_project.to_dict(),
            "situational": None if self.situational is None else self.situational.to_dict(),
            "cross_domain": None if self.cross_domain is None else self.cross_domain.to_dict(),
            "relevance": None if self.relevance is None else self.relevance.to_dict(),
            "truth_guaranteed": False,
            "fact_guaranteed": False,
            "intent_guaranteed": False,
            "authorization_granted": False,
            "policy_authority": False,
            "execution_requested": False,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)
