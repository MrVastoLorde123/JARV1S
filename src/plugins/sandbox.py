"""M22.5 bounded plugin isolation and sandbox contracts.

This module defines immutable containment metadata and deterministic sandbox
admission results. It does not authorize, launch, or execute capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class PluginIsolationError(ValueError):
    """Raised when a sandbox contract is invalid."""


class IsolationMode(str, Enum):
    """Bounded isolation modes supported by the contract."""

    PROCESS = "PROCESS"


class SandboxAdmissionStatus(str, Enum):
    """Deterministic result of sandbox-contract admission checks."""

    ADMISSIBLE = "ADMISSIBLE"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class SandboxProfile:
    """Immutable declarative containment profile for a capability."""

    profile_id: str
    isolation_mode: IsolationMode = IsolationMode.PROCESS
    network_disabled: bool = True
    filesystem_read_only: bool = True
    writable_paths: tuple[str, ...] = ()
    environment_allowlist: tuple[str, ...] = ()
    timeout_seconds: int = 30
    memory_limit_mb: int = 256
    cpu_limit_percent: int = 100

    def __post_init__(self) -> None:
        if not isinstance(self.profile_id, str) or not self.profile_id.strip():
            raise PluginIsolationError("profile_id must be a non-empty string")
        if not isinstance(self.isolation_mode, IsolationMode):
            raise PluginIsolationError("isolation_mode must be an IsolationMode")
        for name, value in (
            ("network_disabled", self.network_disabled),
            ("filesystem_read_only", self.filesystem_read_only),
        ):
            if not isinstance(value, bool):
                raise PluginIsolationError(f"{name} must be a bool")
        for name, values in (
            ("writable_paths", self.writable_paths),
            ("environment_allowlist", self.environment_allowlist),
        ):
            if not isinstance(values, tuple) or not all(
                isinstance(item, str) and item.strip() for item in values
            ):
                raise PluginIsolationError(f"{name} must contain non-empty strings")
        for name, value, minimum in (
            ("timeout_seconds", self.timeout_seconds, 1),
            ("memory_limit_mb", self.memory_limit_mb, 1),
            ("cpu_limit_percent", self.cpu_limit_percent, 1),
        ):
            if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
                raise PluginIsolationError(
                    f"{name} must be an integer >= {minimum}"
                )
        if self.filesystem_read_only and self.writable_paths:
            raise PluginIsolationError(
                "writable_paths must be empty when filesystem_read_only is true"
            )
        if self.cpu_limit_percent > 100:
            raise PluginIsolationError("cpu_limit_percent must be <= 100")

    @property
    def identity(self) -> str:
        return self.profile_id.strip()

    def to_context(self) -> dict[str, object]:
        return {
            "sandbox_profile_id": self.identity,
            "isolation_mode": self.isolation_mode.value,
            "network_disabled": self.network_disabled,
            "filesystem_read_only": self.filesystem_read_only,
            "writable_paths": self.writable_paths,
            "environment_allowlist": self.environment_allowlist,
            "timeout_seconds": self.timeout_seconds,
            "memory_limit_mb": self.memory_limit_mb,
            "cpu_limit_percent": self.cpu_limit_percent,
            "sandbox_bound": True,
            "authority_granted": False,
            "permission_granted": False,
            "authorization_granted": False,
            "execution_started": False,
            "containment_active": False,
        }


@dataclass(frozen=True)
class SandboxAdmissionResult:
    """Immutable result of sandbox-contract validation."""

    capability_id: str
    profile_id: str
    status: SandboxAdmissionStatus
    reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.capability_id, str) or not self.capability_id.strip():
            raise PluginIsolationError("capability_id must be a non-empty string")
        if not isinstance(self.profile_id, str) or not self.profile_id.strip():
            raise PluginIsolationError("profile_id must be a non-empty string")
        if not isinstance(self.status, SandboxAdmissionStatus):
            raise PluginIsolationError(
                "status must be a SandboxAdmissionStatus"
            )
        if not isinstance(self.reasons, tuple) or not all(
            isinstance(item, str) and item.strip() for item in self.reasons
        ):
            raise PluginIsolationError("reasons must contain non-empty strings")
        if self.status is SandboxAdmissionStatus.ADMISSIBLE and self.reasons:
            raise PluginIsolationError(
                "an admissible result cannot contain rejection reasons"
            )
        if self.status is SandboxAdmissionStatus.REJECTED and not self.reasons:
            raise PluginIsolationError(
                "a rejected result requires at least one reason"
            )

    @property
    def admissible(self) -> bool:
        return self.status is SandboxAdmissionStatus.ADMISSIBLE

    def to_context(self) -> dict[str, object]:
        return {
            "capability_id": self.capability_id.strip(),
            "sandbox_profile_id": self.profile_id.strip(),
            "admission_status": self.status.value,
            "admission_evaluated": True,
            "admissible": self.admissible,
            "reasons": self.reasons,
            "authority_granted": False,
            "permission_granted": False,
            "authorization_granted": False,
            "execution_started": False,
        }


class SandboxAdmissionEvaluator:
    """Evaluate sandbox metadata without authorizing or executing a capability."""

    def evaluate(
        self,
        capability_id: str,
        profile: SandboxProfile,
        *,
        supported_modes: tuple[IsolationMode, ...] = (IsolationMode.PROCESS,),
    ) -> SandboxAdmissionResult:
        if not isinstance(capability_id, str) or not capability_id.strip():
            raise PluginIsolationError("capability_id must be a non-empty string")
        if not isinstance(profile, SandboxProfile):
            raise TypeError("profile must be a SandboxProfile")
        if not isinstance(supported_modes, tuple) or not all(
            isinstance(item, IsolationMode) for item in supported_modes
        ):
            raise PluginIsolationError(
                "supported_modes must be a tuple of IsolationMode values"
            )
        reasons: list[str] = []
        if profile.isolation_mode not in supported_modes:
            reasons.append(
                f"isolation mode {profile.isolation_mode.value} is unsupported"
            )
        if profile.timeout_seconds <= 0:
            reasons.append("timeout_seconds must be positive")
        if profile.memory_limit_mb <= 0:
            reasons.append("memory_limit_mb must be positive")
        status = (
            SandboxAdmissionStatus.ADMISSIBLE
            if not reasons
            else SandboxAdmissionStatus.REJECTED
        )
        return SandboxAdmissionResult(
            capability_id=capability_id.strip(),
            profile_id=profile.identity,
            status=status,
            reasons=tuple(reasons),
        )


class SandboxProfileRegistry:
    """Explicit, conflict-aware registry of sandbox profiles."""

    def __init__(self) -> None:
        self._profiles: dict[str, SandboxProfile] = {}

    def register(self, profile: SandboxProfile) -> SandboxProfile:
        if not isinstance(profile, SandboxProfile):
            raise TypeError("profile must be a SandboxProfile")
        key = profile.identity
        if key in self._profiles:
            raise PluginIsolationError(f"sandbox profile already exists: {key}")
        self._profiles[key] = profile
        return profile

    def get(self, profile_id: str) -> SandboxProfile | None:
        if not isinstance(profile_id, str) or not profile_id.strip():
            raise PluginIsolationError("profile_id must be a non-empty string")
        return self._profiles.get(profile_id.strip())

    def list_profiles(self) -> tuple[SandboxProfile, ...]:
        return tuple(self._profiles[key] for key in sorted(self._profiles))

    def __len__(self) -> int:
        return len(self._profiles)
