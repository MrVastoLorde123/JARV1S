"""M19.1 bounded personal profile.

The profile describes stable user preferences and working patterns without
becoming an intent, policy, permission, or authorization source.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Iterable, Mapping


PROFILE_CATEGORIES = frozenset({"PREFERENCE", "BEHAVIOR", "WORKING_STYLE"})


@dataclass(frozen=True)
class PersonalizationSignal:
    """One evidence-backed descriptive personalization signal."""

    signal_id: str
    category: str
    key: str
    value: str
    confidence: float = 0.0
    importance: float = 0.0
    source_ids: tuple[str, ...] = ()
    explicit_user_preference: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("signal_id", "key", "value", "category"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")

        normalized_category = self.category.strip().upper()
        object.__setattr__(self, "category", normalized_category)
        if normalized_category not in PROFILE_CATEGORIES:
            raise ValueError(f"unsupported personalization category: {self.category}")

        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise TypeError("confidence must be numeric")
        if isinstance(self.importance, bool) or not isinstance(self.importance, (int, float)):
            raise TypeError("importance must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not 0.0 <= float(self.importance) <= 1.0:
            raise ValueError("importance must be between 0.0 and 1.0")
        if not isinstance(self.source_ids, tuple):
            raise TypeError("source_ids must be a tuple")
        if not self.source_ids:
            raise ValueError("source_ids must contain at least one provenance identity")
        if len(set(self.source_ids)) != len(self.source_ids):
            raise ValueError("source_ids must be unique")
        if not all(isinstance(item, str) and item.strip() for item in self.source_ids):
            raise ValueError("source_ids must contain non-empty strings")
        if not isinstance(self.explicit_user_preference, bool):
            raise TypeError("explicit_user_preference must be a bool")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "signal_id", self.signal_id.strip())
        object.__setattr__(self, "key", self.key.strip())
        object.__setattr__(self, "value", self.value.strip())
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "category": self.category,
            "key": self.key,
            "value": self.value,
            "confidence": self.confidence,
            "importance": self.importance,
            "source_ids": self.source_ids,
            "explicit_user_preference": self.explicit_user_preference,
            "metadata": dict(self.metadata),
            "truth_guaranteed": False,
            "authority_granted": False,
            "authorization_granted": False,
            "policy_mutation": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class PersonalizationProfile:
    """Immutable bounded profile used only to improve assistance quality."""

    profile_id: str
    signals: tuple[PersonalizationSignal, ...] = ()
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.profile_id, str) or not self.profile_id.strip():
            raise ValueError("profile_id must be a non-empty string")
        if not isinstance(self.signals, tuple):
            raise TypeError("signals must be a tuple")
        seen: set[str] = set()
        for signal in self.signals:
            if not isinstance(signal, PersonalizationSignal):
                raise TypeError("signals must contain PersonalizationSignal values")
            if signal.signal_id in seen:
                raise ValueError("signal identities must be unique")
            seen.add(signal.signal_id)
        if not isinstance(self.provenance, Mapping):
            raise TypeError("provenance must be a mapping")
        object.__setattr__(self, "profile_id", self.profile_id.strip())
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))

    @property
    def preferences(self) -> tuple[PersonalizationSignal, ...]:
        return tuple(signal for signal in self.signals if signal.category == "PREFERENCE")

    @property
    def behaviors(self) -> tuple[PersonalizationSignal, ...]:
        return tuple(signal for signal in self.signals if signal.category == "BEHAVIOR")

    @property
    def working_style(self) -> tuple[PersonalizationSignal, ...]:
        return tuple(signal for signal in self.signals if signal.category == "WORKING_STYLE")

    def for_key(self, key: str) -> tuple[PersonalizationSignal, ...]:
        normalized = key.strip()
        return tuple(signal for signal in self.signals if signal.key == normalized)

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "signals": [signal.to_dict() for signal in self.signals],
            "provenance": dict(self.provenance),
            "truth_guaranteed": False,
            "authority_granted": False,
            "authorization_granted": False,
            "policy_mutation": False,
            "execution_requested": False,
        }


def build_profile(
    profile_id: str,
    signals: Iterable[PersonalizationSignal],
    *,
    provenance: Mapping[str, Any] | None = None,
) -> PersonalizationProfile:
    """Build a deterministic immutable profile from already-established signals."""
    normalized = tuple(signals)
    return PersonalizationProfile(
        profile_id=profile_id,
        signals=normalized,
        provenance={"source": "m19.1", **dict(provenance or {})},
    )


__all__ = [
    "PROFILE_CATEGORIES",
    "PersonalizationSignal",
    "PersonalizationProfile",
    "build_profile",
]
