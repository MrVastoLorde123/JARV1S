"""M19.5 persistence helper for the bounded personalization runtime."""

from __future__ import annotations

from .persistence import PersonalizationRecord, PersonalizationStore
from .profile import PersonalizationProfile


def persist_profile(store: PersonalizationStore, profile: PersonalizationProfile) -> tuple[PersonalizationRecord, ...]:
    """Persist a bounded personalization profile without granting authority."""
    if not isinstance(store, PersonalizationStore):
        raise TypeError("store must be a PersonalizationStore")
    return store.persist_profile(profile)


def reverse_profile_signal(
    store: PersonalizationStore,
    record_id: str,
    reversal_reference: str,
) -> PersonalizationRecord:
    """Reverse one persisted personalization signal explicitly."""
    if not isinstance(store, PersonalizationStore):
        raise TypeError("store must be a PersonalizationStore")
    return store.reverse(record_id, reversal_reference)


__all__ = ["persist_profile", "reverse_profile_signal"]
