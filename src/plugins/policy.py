"""M22.4 bounded capability permission and policy-binding contracts.

This module describes which permissions a policy binds to a capability/version.
Bindings are declarative metadata. They do not authorize, execute, or invoke work.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .lifecycle import SemanticVersion


class CapabilityPolicyError(ValueError):
    """Raised when a capability permission/policy contract is invalid."""


class PermissionEffect(str, Enum):
    """Declarative effect of a permission-policy binding."""

    ALLOW = "ALLOW"
    DENY = "DENY"


@dataclass(frozen=True)
class CapabilityPermissionBinding:
    """Immutable declaration binding one permission to one capability identity."""

    capability_id: str
    permission: str
    effect: PermissionEffect
    version: str | None = None
    policy_id: str = "unspecified"
    rationale: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.capability_id, str) or not self.capability_id.strip():
            raise CapabilityPolicyError("capability_id must be a non-empty string")
        if not isinstance(self.permission, str) or not self.permission.strip():
            raise CapabilityPolicyError("permission must be a non-empty string")
        if not isinstance(self.effect, PermissionEffect):
            raise CapabilityPolicyError("effect must be a PermissionEffect")
        object.__setattr__(self, "permission", self.permission.strip().lower())
        if not isinstance(self.policy_id, str) or not self.policy_id.strip():
            raise CapabilityPolicyError("policy_id must be a non-empty string")
        if self.version is not None:
            parsed = SemanticVersion.parse(self.version)
            object.__setattr__(self, "version", str(parsed))
        if self.rationale is not None and (
            not isinstance(self.rationale, str) or not self.rationale.strip()
        ):
            raise CapabilityPolicyError(
                "rationale must be None or a non-empty string"
            )

    @property
    def identity(self) -> tuple[str, str, str | None, str]:
        return (
            self.capability_id.strip().lower(),
            self.permission,
            self.version,
            self.policy_id.strip(),
        )

    def to_context(self) -> dict[str, object]:
        return {
            "capability_id": self.capability_id,
            "permission": self.permission,
            "effect": self.effect.value,
            "version": self.version,
            "policy_id": self.policy_id,
            "rationale": self.rationale,
            "permission_bound": True,
            "authority_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
        }


class CapabilityPolicyBindingRegistry:
    """Explicit, conflict-aware registry of declarative permission bindings."""

    def __init__(self) -> None:
        self._bindings: dict[tuple[str, str, str | None, str], CapabilityPermissionBinding] = {}

    def register(self, binding: CapabilityPermissionBinding) -> CapabilityPermissionBinding:
        if not isinstance(binding, CapabilityPermissionBinding):
            raise TypeError("binding must be a CapabilityPermissionBinding")
        key = binding.identity
        if key in self._bindings:
            raise CapabilityPolicyError(
                "permission policy binding already exists for "
                f"{binding.capability_id}@{binding.version or '*'} "
                f"permission '{binding.permission}' under policy '{binding.policy_id}'"
            )
        self._bindings[key] = binding
        return binding

    def get(
        self,
        capability_id: str,
        permission: str,
        *,
        version: str | None = None,
        policy_id: str = "unspecified",
    ) -> CapabilityPermissionBinding | None:
        if not isinstance(permission, str) or not permission.strip():
            raise CapabilityPolicyError("permission must be a non-empty string")
        normalized_version = None if version is None else str(SemanticVersion.parse(version))
        return self._bindings.get(
            (
                capability_id.strip().lower(),
                permission.strip().lower(),
                normalized_version,
                policy_id.strip(),
            )
        )

    def list_for_capability(
        self,
        capability_id: str,
        *,
        version: str | None = None,
        policy_id: str | None = None,
    ) -> tuple[CapabilityPermissionBinding, ...]:
        normalized_capability = capability_id.strip().lower()
        normalized_version = None if version is None else str(SemanticVersion.parse(version))
        normalized_policy = None if policy_id is None else policy_id.strip()
        bindings = [
            binding
            for binding in self._bindings.values()
            if binding.capability_id.strip().lower() == normalized_capability
            and (normalized_version is None or binding.version == normalized_version)
            and (normalized_policy is None or binding.policy_id.strip() == normalized_policy)
        ]
        return tuple(
            sorted(
                bindings,
                key=lambda item: (
                    item.policy_id.strip(),
                    item.permission,
                    item.version or "",
                    item.effect.value,
                ),
            )
        )

    def __len__(self) -> int:
        return len(self._bindings)
