"""M19.5 bounded personalization persistence and reversal boundary.

Persisted personalization is descriptive state only. Reversal removes a
signal from the active personalization projection without mutating the
underlying memory, evidence, learning adaptation, policy, authorization, or
execution systems.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from .profile import PersonalizationProfile, PersonalizationSignal, build_profile


class PersonalizationState(str, Enum):
    ACTIVE = "ACTIVE"
    REVERSED = "REVERSED"


@dataclass(frozen=True)
class PersonalizationRecord:
    """Immutable persisted personalization state for one signal."""

    record_id: str
    signal: PersonalizationSignal
    state: PersonalizationState = PersonalizationState.ACTIVE
    reversal_reference: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.record_id, str) or not self.record_id.strip():
            raise ValueError("record_id must be a non-empty string")
        if not isinstance(self.signal, PersonalizationSignal):
            raise TypeError("signal must be a PersonalizationSignal")
        if not isinstance(self.state, PersonalizationState):
            try:
                object.__setattr__(self, "state", PersonalizationState(self.state))
            except (TypeError, ValueError) as exc:
                raise TypeError("state must be a PersonalizationState") from exc
        if self.state == PersonalizationState.REVERSED:
            if not isinstance(self.reversal_reference, str) or not self.reversal_reference.strip():
                raise ValueError("reversed personalization requires a reversal reference")

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "signal": self.signal.to_dict(),
            "state": self.state.value,
            "reversal_reference": self.reversal_reference,
            "authority_granted": False,
            "authorization_granted": False,
            "policy_mutation": False,
            "execution_requested": False,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PersonalizationRecord":
        if not isinstance(data, dict):
            raise TypeError("record data must be a mapping")
        signal_data = data.get("signal")
        if not isinstance(signal_data, dict):
            raise ValueError("record signal must be a mapping")
        signal = PersonalizationSignal(
            signal_id=signal_data["signal_id"],
            category=signal_data["category"],
            key=signal_data["key"],
            value=signal_data["value"],
            confidence=signal_data.get("confidence", 0.0),
            importance=signal_data.get("importance", 0.0),
            source_ids=tuple(signal_data.get("source_ids", ())),
            explicit_user_preference=signal_data.get("explicit_user_preference", False),
            metadata=signal_data.get("metadata", {}),
        )
        return cls(
            record_id=data["record_id"],
            signal=signal,
            state=PersonalizationState(data.get("state", PersonalizationState.ACTIVE)),
            reversal_reference=data.get("reversal_reference"),
        )


class PersonalizationPersistenceConflictError(ValueError):
    """Raised when persisted personalization identity conflicts with state."""


class PersonalizationStore:
    """Small durable JSON store for bounded personalization records."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._records: dict[str, PersonalizationRecord] = self._read()

    def persist_profile(self, profile: PersonalizationProfile) -> tuple[PersonalizationRecord, ...]:
        if not isinstance(profile, PersonalizationProfile):
            raise TypeError("profile must be a PersonalizationProfile")

        persisted: list[PersonalizationRecord] = []
        changed = False
        for signal in profile.signals:
            record_id = f"personalization:{signal.signal_id}"
            existing = self._records.get(record_id)
            if existing is not None:
                if existing.signal != signal:
                    raise PersonalizationPersistenceConflictError(
                        f"personalization record '{record_id}' conflicts with stored state"
                    )
                persisted.append(existing)
                continue

            record = PersonalizationRecord(record_id=record_id, signal=signal)
            self._records[record_id] = record
            persisted.append(record)
            changed = True

        if changed:
            self._write()
        return tuple(persisted)

    def reverse(self, record_id: str, reversal_reference: str) -> PersonalizationRecord:
        record = self.get(record_id)
        if record is None:
            raise KeyError(f"unknown personalization record '{record_id}'")
        if record.state != PersonalizationState.ACTIVE:
            raise ValueError("only active personalization can be reversed")
        if not isinstance(reversal_reference, str) or not reversal_reference.strip():
            raise ValueError("reversal_reference must be a non-empty string")

        reversed_record = PersonalizationRecord(
            record_id=record.record_id,
            signal=record.signal,
            state=PersonalizationState.REVERSED,
            reversal_reference=reversal_reference.strip(),
        )
        self._records[record.record_id] = reversed_record
        self._write()
        return reversed_record

    def get(self, record_id: str) -> PersonalizationRecord | None:
        return self._records.get(record_id)

    def records(self) -> tuple[PersonalizationRecord, ...]:
        return tuple(self._records.values())

    def active_records(self) -> tuple[PersonalizationRecord, ...]:
        return tuple(
            record
            for record in self._records.values()
            if record.state == PersonalizationState.ACTIVE
        )

    def active_profile(
        self,
        profile_id: str = "persisted-personalization",
    ) -> PersonalizationProfile:
        signals = tuple(record.signal for record in self.active_records())
        return build_profile(
            profile_id,
            signals,
            provenance={
                "runtime": "m19.5",
                "source": "personalization_store",
                "active_record_count": len(signals),
            },
        )

    def _read(self) -> dict[str, PersonalizationRecord]:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, json.JSONDecodeError):
            return {}

        if not isinstance(payload, dict):
            return {}
        raw_records = payload.get("records", [])
        if not isinstance(raw_records, list):
            raise ValueError("personalization store records must be a list")

        records: dict[str, PersonalizationRecord] = {}
        for raw_record in raw_records:
            record = PersonalizationRecord.from_dict(raw_record)
            if record.record_id in records:
                raise PersonalizationPersistenceConflictError(
                    f"duplicate personalization record '{record.record_id}'"
                )
            records[record.record_id] = record
        return records

    def _write(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_name(f"{self.path.name}.tmp")
        payload = json.dumps(
            {"records": [record.to_dict() for record in self._records.values()]},
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        temporary_path.write_text(payload + "\n", encoding="utf-8")
        temporary_path.replace(self.path)


__all__ = [
    "PersonalizationPersistenceConflictError",
    "PersonalizationRecord",
    "PersonalizationState",
    "PersonalizationStore",
]
