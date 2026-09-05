"""M22.3 bounded capability lifecycle and versioning contracts.

This module records immutable capability-version identities and explicit lifecycle
transitions. It does not grant trust, permission, authorization, or execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from functools import total_ordering
import re


class CapabilityLifecycleError(ValueError):
    """Raised when a capability lifecycle/versioning contract is invalid."""


class LifecycleStatus(str, Enum):
    """Bounded lifecycle states for a capability version."""

    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    RETIRED = "RETIRED"


@total_ordering
@dataclass(frozen=True)
class SemanticVersion:
    """Semantic Version 2.0 precedence value with optional build metadata."""

    major: int
    minor: int
    patch: int
    prerelease: tuple[str, ...] = ()
    build: tuple[str, ...] = ()

    _PATTERN = re.compile(
        r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
        r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
        r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
    )

    @classmethod
    def parse(cls, value: str) -> "SemanticVersion":
        if not isinstance(value, str) or not value.strip():
            raise CapabilityLifecycleError("version must be a non-empty string")
        match = cls._PATTERN.fullmatch(value.strip())
        if match is None:
            raise CapabilityLifecycleError(
                "version must use Semantic Versioning MAJOR.MINOR.PATCH"
            )
        prerelease = tuple((match.group(4) or "").split(".")) if match.group(4) else ()
        for identifier in prerelease:
            if identifier.isdigit() and len(identifier) > 1 and identifier.startswith("0"):
                raise CapabilityLifecycleError(
                    "numeric prerelease identifiers must not contain leading zeroes"
                )
        build = tuple((match.group(5) or "").split(".")) if match.group(5) else ()
        return cls(
            major=int(match.group(1)),
            minor=int(match.group(2)),
            patch=int(match.group(3)),
            prerelease=prerelease,
            build=build,
        )

    def __post_init__(self) -> None:
        for name in ("major", "minor", "patch"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise CapabilityLifecycleError(f"{name} must be a non-negative integer")
        for name, identifiers in (("prerelease", self.prerelease), ("build", self.build)):
            if not isinstance(identifiers, tuple) or not all(
                isinstance(item, str) and item for item in identifiers
            ):
                raise CapabilityLifecycleError(f"{name} must be a tuple of non-empty strings")

    def __str__(self) -> str:
        core = f"{self.major}.{self.minor}.{self.patch}"
        prerelease = f"-{'.'.join(self.prerelease)}" if self.prerelease else ""
        build = f"+{'.'.join(self.build)}" if self.build else ""
        return f"{core}{prerelease}{build}"

    def _precedence_key(self) -> tuple[object, ...]:
        prerelease_key: tuple[tuple[int, object], ...] = tuple(
            (0, int(item)) if item.isdigit() else (1, item)
            for item in self.prerelease
        )
        return (self.major, self.minor, self.patch, prerelease_key)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        if (self.major, self.minor, self.patch) != (
            other.major,
            other.minor,
            other.patch,
        ):
            return (self.major, self.minor, self.patch) < (
                other.major,
                other.minor,
                other.patch,
            )
        if not self.prerelease and not other.prerelease:
            return False
        if not self.prerelease:
            return False
        if not other.prerelease:
            return True
        for left, right in zip(self.prerelease, other.prerelease):
            if left == right:
                continue
            left_numeric = left.isdigit()
            right_numeric = right.isdigit()
            if left_numeric and right_numeric:
                return int(left) < int(right)
            if left_numeric != right_numeric:
                return left_numeric
            return left < right
        return len(self.prerelease) < len(other.prerelease)


@dataclass(frozen=True)
class CapabilityVersion:
    """Immutable identity and lifecycle metadata for one capability version."""

    capability_id: str
    version: str
    lifecycle: LifecycleStatus = LifecycleStatus.ACTIVE
    supersedes: str | None = None
    release_notes: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.capability_id, str) or not self.capability_id.strip():
            raise CapabilityLifecycleError("capability_id must be a non-empty string")
        if not isinstance(self.lifecycle, LifecycleStatus):
            raise CapabilityLifecycleError("lifecycle must be a LifecycleStatus")
        parsed = SemanticVersion.parse(self.version)
        object.__setattr__(self, "version", str(parsed))
        if self.supersedes is not None:
            previous = SemanticVersion.parse(self.supersedes)
            object.__setattr__(self, "supersedes", str(previous))
            if not previous < parsed:
                raise CapabilityLifecycleError("supersedes must identify an older version")
        if self.release_notes is not None and (
            not isinstance(self.release_notes, str) or not self.release_notes.strip()
        ):
            raise CapabilityLifecycleError(
                "release_notes must be None or a non-empty string"
            )

    @property
    def semantic_version(self) -> SemanticVersion:
        return SemanticVersion.parse(self.version)

    def transition(self, target: LifecycleStatus) -> "CapabilityVersion":
        """Return a new lifecycle record using only forward lifecycle transitions."""
        if not isinstance(target, LifecycleStatus):
            raise CapabilityLifecycleError("target must be a LifecycleStatus")
        if target is self.lifecycle:
            return self
        allowed = {
            LifecycleStatus.ACTIVE: {LifecycleStatus.DEPRECATED, LifecycleStatus.RETIRED},
            LifecycleStatus.DEPRECATED: {LifecycleStatus.RETIRED},
            LifecycleStatus.RETIRED: set(),
        }
        if target not in allowed[self.lifecycle]:
            raise CapabilityLifecycleError(
                f"invalid lifecycle transition: {self.lifecycle.value} -> {target.value}"
            )
        return CapabilityVersion(
            capability_id=self.capability_id,
            version=self.version,
            lifecycle=target,
            supersedes=self.supersedes,
            release_notes=self.release_notes,
        )

    def to_context(self) -> dict[str, object]:
        return {
            "capability_id": self.capability_id,
            "version": self.version,
            "lifecycle": self.lifecycle.value,
            "supersedes": self.supersedes,
            "release_notes": self.release_notes,
            "authority_granted": False,
            "permission_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
        }


class CapabilityLifecycleRegistry:
    """Explicit, deterministic lifecycle/version history for capabilities."""

    def __init__(self) -> None:
        self._versions: dict[tuple[str, str], CapabilityVersion] = {}

    @staticmethod
    def _capability_key(capability_id: str) -> str:
        if not isinstance(capability_id, str) or not capability_id.strip():
            raise CapabilityLifecycleError("capability_id must be a non-empty string")
        return capability_id.strip().lower()

    def register(self, version: CapabilityVersion) -> CapabilityVersion:
        if not isinstance(version, CapabilityVersion):
            raise TypeError("version must be a CapabilityVersion")
        key = (self._capability_key(version.capability_id), version.version)
        if key in self._versions:
            raise CapabilityLifecycleError(
                f"capability version '{version.capability_id}@{version.version}' is already registered"
            )
        self._versions[key] = version
        return version

    def get(self, capability_id: str, version: str) -> CapabilityVersion | None:
        parsed = SemanticVersion.parse(version)
        return self._versions.get((self._capability_key(capability_id), str(parsed)))

    def transition(
        self,
        capability_id: str,
        version: str,
        target: LifecycleStatus,
    ) -> CapabilityVersion:
        current = self.get(capability_id, version)
        if current is None:
            raise CapabilityLifecycleError(
                f"capability version '{capability_id}@{version}' is not registered"
            )
        updated = current.transition(target)
        if updated is current:
            return current
        key = (self._capability_key(current.capability_id), current.version)
        self._versions[key] = updated
        return updated

    def list_versions(
        self,
        capability_id: str,
        *,
        include_retired: bool = True,
    ) -> tuple[CapabilityVersion, ...]:
        key = self._capability_key(capability_id)
        versions = [
            item
            for (item_key, _), item in self._versions.items()
            if item_key == key and (include_retired or item.lifecycle is not LifecycleStatus.RETIRED)
        ]
        return tuple(
            sorted(
                versions,
                key=lambda item: (item.semantic_version._precedence_key(), item.version),
                reverse=True,
            )
        )

    def latest(
        self,
        capability_id: str,
        *,
        include_retired: bool = False,
    ) -> CapabilityVersion | None:
        versions = self.list_versions(capability_id, include_retired=include_retired)
        return versions[0] if versions else None

    def __len__(self) -> int:
        return len(self._versions)
