"""M77: deterministic isolation profiles for capability execution boundaries."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Sequence


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True)
class IsolationProfile:
    profile_id: str
    network_access: bool = False
    filesystem_read: bool = False
    filesystem_write: bool = False
    subprocess_allowed: bool = False
    allowed_paths: tuple[str, ...] = ()
    allowed_hosts: tuple[str, ...] = ()
    environment_allowlist: tuple[str, ...] = ()
    max_duration_seconds: int = 30
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "profile_id", _text(self.profile_id, "profile_id"))
        for name in ("network_access", "filesystem_read", "filesystem_write", "subprocess_allowed"):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a bool")
        if not isinstance(self.max_duration_seconds, int) or isinstance(self.max_duration_seconds, bool) or self.max_duration_seconds <= 0:
            raise ValueError("max_duration_seconds must be a positive integer")
        for name in ("allowed_paths", "allowed_hosts", "environment_allowlist"):
            values = getattr(self, name)
            if not isinstance(values, tuple) or any(not isinstance(item, str) or not item.strip() for item in values):
                raise TypeError(f"{name} must be a tuple of non-empty strings")
            if len(set(values)) != len(values):
                raise ValueError(f"{name} must not contain duplicates")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class IsolationRequest:
    capability_id: str
    network_required: bool = False
    requested_host: str | None = None
    filesystem_read_required: bool = False
    filesystem_write_required: bool = False
    requested_path: str | None = None
    subprocess_required: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "capability_id", _text(self.capability_id, "capability_id"))
        for name in ("network_required", "filesystem_read_required", "filesystem_write_required", "subprocess_required"):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a bool")
        for name in ("requested_host", "requested_path"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be a non-empty string or None")


@dataclass(frozen=True)
class IsolationEvaluation:
    request: IsolationRequest
    profile: IsolationProfile | None
    allowed: bool
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.request, IsolationRequest):
            raise TypeError("request must be an IsolationRequest")
        if self.profile is not None and not isinstance(self.profile, IsolationProfile):
            raise TypeError("profile must be an IsolationProfile or None")
        if not isinstance(self.allowed, bool):
            raise TypeError("allowed must be a bool")
        object.__setattr__(self, "reason", _text(self.reason, "reason"))


@dataclass(frozen=True)
class CapabilityIsolationBinding:
    capability_id: str
    profile: IsolationProfile

    def __post_init__(self) -> None:
        object.__setattr__(self, "capability_id", _text(self.capability_id, "capability_id"))
        if not isinstance(self.profile, IsolationProfile):
            raise TypeError("profile must be an IsolationProfile")


class IsolationModel:
    def __init__(self, bindings: Sequence[CapabilityIsolationBinding] = ()) -> None:
        values = tuple(bindings)
        if any(not isinstance(item, CapabilityIsolationBinding) for item in values):
            raise TypeError("bindings must contain CapabilityIsolationBinding values")
        ids = [item.capability_id for item in values]
        if len(ids) != len(set(ids)):
            raise ValueError("capability isolation bindings must be unique")
        self._bindings = MappingProxyType({item.capability_id: item for item in values})

    def evaluate(self, request: IsolationRequest) -> IsolationEvaluation:
        if not isinstance(request, IsolationRequest):
            raise TypeError("request must be an IsolationRequest")
        binding = self._bindings.get(request.capability_id)
        if binding is None:
            return IsolationEvaluation(request, None, False, "no isolation profile is bound to the capability")
        profile = binding.profile
        checks = (
            (request.network_required, profile.network_access, "network access is denied by the isolation profile"),
            (request.filesystem_read_required, profile.filesystem_read, "filesystem read is denied by the isolation profile"),
            (request.filesystem_write_required, profile.filesystem_write, "filesystem write is denied by the isolation profile"),
            (request.subprocess_required, profile.subprocess_allowed, "subprocess execution is denied by the isolation profile"),
        )
        for requested, allowed, reason in checks:
            if requested and not allowed:
                return IsolationEvaluation(request, profile, False, reason)
        if request.requested_host is not None and request.requested_host not in profile.allowed_hosts:
            return IsolationEvaluation(request, profile, False, "requested host is outside the isolation allowlist")
        if request.requested_path is not None and request.requested_path not in profile.allowed_paths:
            return IsolationEvaluation(request, profile, False, "requested path is outside the isolation allowlist")
        return IsolationEvaluation(request, profile, True, "request is inside the capability isolation profile")

    def snapshot(self) -> tuple[CapabilityIsolationBinding, ...]:
        return tuple(self._bindings.values())


__all__ = ["IsolationProfile", "IsolationRequest", "IsolationEvaluation", "CapabilityIsolationBinding", "IsolationModel"]
