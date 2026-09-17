"""M82: composition root for JARVIS security controls."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from src.core.capability_system import CapabilitySystem
from src.core.security_admission import SecurityAdmission, SecurityAdmissionService, SecurityRequest
from src.core.security_audit import SecurityAuditLedger
from src.core.security_identity import SecurityIdentityRegistry
from src.core.security_isolation import CapabilityIsolationBinding, IsolationModel
from src.core.security_permission import PermissionGrant, PermissionModel
from src.core.security_secrets import SecretReferenceCatalog
from src.core.security_trust import TrustModel
from src.core.security_verification import SecurityRecoveryDecision, SecurityVerification, derive_security_recovery, verify_security_admission


@dataclass(frozen=True)
class SecurityCoverage:
    capability_count: int
    permission_covered_count: int
    isolation_covered_count: int
    secret_reference_count: int
    audit_event_count: int

    def to_context(self) -> dict[str, Any]:
        return {
            "capability_count": self.capability_count,
            "permission_covered_count": self.permission_covered_count,
            "isolation_covered_count": self.isolation_covered_count,
            "secret_reference_count": self.secret_reference_count,
            "audit_event_count": self.audit_event_count,
            "authority_granted": False,
        }


class SecuritySystem:
    """Provider-neutral security control plane; never invokes capabilities."""

    def __init__(
        self,
        *,
        identities: SecurityIdentityRegistry,
        permissions: PermissionModel,
        secrets: SecretReferenceCatalog,
        isolation: IsolationModel,
        trust: TrustModel,
        audit: SecurityAuditLedger,
        capability_system: CapabilitySystem | None = None,
    ) -> None:
        self._identities = identities
        self._permissions = permissions
        self._secrets = secrets
        self._isolation = isolation
        self._trust = trust
        self._audit = audit
        self._capability_system = capability_system
        self._validate_capability_links()
        self._admission = SecurityAdmissionService(
            identities,
            permissions,
            secrets,
            isolation,
            trust,
            audit,
        )

    def _validate_capability_links(self) -> None:
        if self._capability_system is None:
            return
        known = set(self._capability_system.capability_ids)
        unknown_permissions = [grant.capability_id for grant in self._permissions.snapshot() if grant.capability_id not in known]
        unknown_secrets = [reference.capability_id for reference in self._secrets.snapshot() if reference.capability_id not in known]
        unknown_isolation = [binding.capability_id for binding in self._isolation.snapshot() if binding.capability_id not in known]
        unknown = unknown_permissions + unknown_secrets + unknown_isolation
        if unknown:
            raise ValueError(f"security controls reference unknown capabilities: {tuple(dict.fromkeys(unknown))}")

    @property
    def capability_system(self) -> CapabilitySystem | None:
        return self._capability_system

    @property
    def audit(self) -> SecurityAuditLedger:
        return self._audit

    def admit(self, request: SecurityRequest) -> SecurityAdmission:
        return self._admission.admit(request)

    def verify(self, admission: SecurityAdmission) -> SecurityVerification:
        return verify_security_admission(admission, self._audit)

    def recover(self, verification: SecurityVerification) -> SecurityRecoveryDecision:
        return derive_security_recovery(verification)

    def coverage(self) -> SecurityCoverage:
        capabilities = 0 if self._capability_system is None else len(self._capability_system.capability_ids)
        permission_capabilities = {grant.capability_id for grant in self._permissions.snapshot()}
        isolation_capabilities = {binding.capability_id for binding in self._isolation.snapshot()}
        return SecurityCoverage(
            capability_count=capabilities,
            permission_covered_count=len(permission_capabilities),
            isolation_covered_count=len(isolation_capabilities),
            secret_reference_count=len(self._secrets.snapshot()),
            audit_event_count=len(self._audit.snapshot()),
        )

    def summary(self) -> Mapping[str, Any]:
        coverage = self.coverage()
        return {
            "coverage": coverage.to_context(),
            "trust_evidence_count": len(self._trust.snapshot()),
            "identity_session_count": len(self._identities.snapshot()),
            "audit_chain_valid": self._audit.verify_chain(),
            "authority_granted": False,
            "execution_requested": False,
            "capability_invocation_performed": False,
        }

    def to_context(self) -> dict[str, Any]:
        return {
            "summary": dict(self.summary()),
            "coverage": self.coverage().to_context(),
            "identities": tuple(item.to_context() for item in self._identities.snapshot()),
            "permissions": tuple(item for item in (grant for grant in self._permissions.snapshot())),
            "secrets": tuple(item.to_context() for item in self._secrets.snapshot()),
            "isolation": tuple(
                {
                    "capability_id": binding.capability_id,
                    "profile_id": binding.profile.profile_id,
                }
                for binding in self._isolation.snapshot()
            ),
            "trust": tuple(item.to_context() for item in self._trust.snapshot()),
            "audit_event_ids": tuple(item.event_id for item in self._audit.snapshot()),
            "authority_granted": False,
            "execution_requested": False,
        }


__all__ = ["SecurityCoverage", "SecuritySystem"]
