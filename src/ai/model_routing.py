"""Deterministic model-role routing contract for JARVIS.

The router selects a cognitive component; it never grants authority,
permissions, tools, or execution rights. Availability is an observation,
not an authorization decision.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class ModelRole(str, Enum):
    GENERAL = "GENERAL"
    CODING = "CODING"
    DIAGNOSTIC = "DIAGNOSTIC"
    VERIFICATION = "VERIFICATION"
    LIGHTWEIGHT = "LIGHTWEIGHT"


@dataclass(frozen=True)
class ModelProfile:
    model_id: str
    roles: frozenset[ModelRole]
    priority: int = 0
    available: bool = True
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.model_id.strip():
            raise ValueError("model_id cannot be empty")
        if not self.roles:
            raise ValueError("roles cannot be empty")
        if self.priority < 0:
            raise ValueError("priority cannot be negative")


@dataclass(frozen=True)
class RoutingRequest:
    role: ModelRole
    preferred_model: str | None = None
    require_available: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.role, ModelRole):
            raise TypeError("role must be a ModelRole")


@dataclass(frozen=True)
class RoutingDecision:
    role: ModelRole
    model_id: str
    reason: str
    candidates_considered: tuple[str, ...] = field(default_factory=tuple)


class ModelRouter:
    """Select a registered model by role without owning execution authority."""

    def __init__(self, profiles: Iterable[ModelProfile] = ()) -> None:
        self._profiles: dict[str, ModelProfile] = {}
        for profile in profiles:
            self.register(profile)

    def register(self, profile: ModelProfile) -> None:
        if not isinstance(profile, ModelProfile):
            raise TypeError("profile must be a ModelProfile")
        if profile.model_id in self._profiles:
            raise ValueError(f"duplicate model_id: {profile.model_id}")
        self._profiles[profile.model_id] = profile

    def profile(self, model_id: str) -> ModelProfile:
        try:
            return self._profiles[model_id]
        except KeyError as exc:
            raise KeyError(f"unknown model: {model_id}") from exc

    def list_profiles(self) -> tuple[ModelProfile, ...]:
        return tuple(self._profiles.values())

    def route(self, request: RoutingRequest) -> RoutingDecision:
        if not isinstance(request, RoutingRequest):
            raise TypeError("request must be a RoutingRequest")

        if request.preferred_model is not None:
            preferred = self.profile(request.preferred_model)
            if request.role not in preferred.roles:
                raise ValueError(
                    f"model '{preferred.model_id}' does not serve role {request.role.value}"
                )
            if request.require_available and not preferred.available:
                raise ValueError(f"preferred model '{preferred.model_id}' is unavailable")
            return RoutingDecision(
                role=request.role,
                model_id=preferred.model_id,
                reason="explicit model preference",
                candidates_considered=(preferred.model_id,),
            )

        candidates = [
            profile
            for profile in self._profiles.values()
            if request.role in profile.roles and (profile.available or not request.require_available)
        ]
        if not candidates:
            raise LookupError(f"no model available for role {request.role.value}")

        candidates.sort(key=lambda profile: (-profile.priority, profile.model_id))
        chosen = candidates[0]
        return RoutingDecision(
            role=request.role,
            model_id=chosen.model_id,
            reason="highest-priority available model for role",
            candidates_considered=tuple(profile.model_id for profile in candidates),
        )
