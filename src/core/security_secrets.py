"""M76: reference secrets without exposing or storing raw secret material."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Sequence


class SecretSensitivity(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    SENSITIVE = "SENSITIVE"
    CRITICAL = "CRITICAL"


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True)
class SecretReference:
    secret_ref_id: str
    owner_principal_id: str
    capability_id: str
    scope: str
    sensitivity: SecretSensitivity
    version: int = 1
    exportable: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("secret_ref_id", "owner_principal_id", "capability_id", "scope"):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        if not isinstance(self.sensitivity, SecretSensitivity):
            raise TypeError("sensitivity must be a SecretSensitivity")
        if not isinstance(self.version, int) or isinstance(self.version, bool) or self.version <= 0:
            raise ValueError("version must be a positive integer")
        if not isinstance(self.exportable, bool):
            raise TypeError("exportable must be a bool")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_context(self) -> dict[str, Any]:
        return {
            "secret_ref_id": self.secret_ref_id,
            "owner_principal_id": self.owner_principal_id,
            "capability_id": self.capability_id,
            "scope": self.scope,
            "sensitivity": self.sensitivity.value,
            "version": self.version,
            "exportable": self.exportable,
            "raw_secret_present": False,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class SecretAccessRequest:
    principal_id: str
    capability_id: str
    secret_ref_id: str
    purpose: str

    def __post_init__(self) -> None:
        for name in ("principal_id", "capability_id", "secret_ref_id", "purpose"):
            object.__setattr__(self, name, _text(getattr(self, name), name))


@dataclass(frozen=True)
class SecretAccessEvaluation:
    request: SecretAccessRequest
    allowed: bool
    reason: str
    reference: SecretReference | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.request, SecretAccessRequest):
            raise TypeError("request must be a SecretAccessRequest")
        if not isinstance(self.allowed, bool):
            raise TypeError("allowed must be a bool")
        object.__setattr__(self, "reason", _text(self.reason, "reason"))
        if self.reference is not None and not isinstance(self.reference, SecretReference):
            raise TypeError("reference must be a SecretReference or None")


class SecretReferenceCatalog:
    """Security catalog for opaque references; never stores secret values."""

    def __init__(self, references: Sequence[SecretReference] = ()) -> None:
        values = tuple(references)
        if any(not isinstance(item, SecretReference) for item in values):
            raise TypeError("references must contain SecretReference values")
        ids = [item.secret_ref_id for item in values]
        if len(ids) != len(set(ids)):
            raise ValueError("secret reference IDs must be unique")
        self._references = MappingProxyType({item.secret_ref_id: item for item in values})

    def get(self, secret_ref_id: str) -> SecretReference:
        normalized = _text(secret_ref_id, "secret_ref_id")
        try:
            return self._references[normalized]
        except KeyError as exc:
            raise KeyError(normalized) from exc

    def evaluate(self, request: SecretAccessRequest) -> SecretAccessEvaluation:
        if not isinstance(request, SecretAccessRequest):
            raise TypeError("request must be a SecretAccessRequest")
        reference = self._references.get(request.secret_ref_id)
        if reference is None:
            return SecretAccessEvaluation(request, False, "unknown secret reference")
        if reference.owner_principal_id != request.principal_id:
            return SecretAccessEvaluation(request, False, "principal does not own the secret reference", reference)
        if reference.capability_id != request.capability_id:
            return SecretAccessEvaluation(request, False, "capability is outside the secret reference scope", reference)
        return SecretAccessEvaluation(request, True, "opaque secret reference is permitted", reference)

    def snapshot(self) -> tuple[SecretReference, ...]:
        return tuple(self._references.values())


__all__ = ["SecretSensitivity", "SecretReference", "SecretAccessRequest", "SecretAccessEvaluation", "SecretReferenceCatalog"]
