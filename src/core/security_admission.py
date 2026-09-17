"""M80: provider-neutral security admission before any downstream execution."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from src.core.security_audit import SecurityAuditLedger
from src.core.security_identity import SecurityIdentityRegistry, SecuritySession
from src.core.security_isolation import IsolationEvaluation, IsolationModel, IsolationRequest
from src.core.security_permission import PermissionAction, PermissionEvaluation, PermissionModel, PermissionRequest
from src.core.security_secrets import SecretAccessEvaluation, SecretAccessRequest, SecretReferenceCatalog
from src.core.security_trust import TrustAssessment, TrustModel


class SecurityAdmissionDisposition(str, Enum):
    ADMITTED = "ADMITTED"
    DENIED = "DENIED"


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True)
class SecurityRequest:
    request_id: str
    session_id: str
    capability_id: str
    action: PermissionAction
    isolation: IsolationRequest
    timestamp: str
    secret_ref_id: str | None = None

    def __post_init__(self) -> None:
        for name in ("request_id", "session_id", "capability_id", "timestamp"):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        if not isinstance(self.action, PermissionAction):
            raise TypeError("action must be a PermissionAction")
        if not isinstance(self.isolation, IsolationRequest):
            raise TypeError("isolation must be an IsolationRequest")
        if self.isolation.capability_id != self.capability_id:
            raise ValueError("isolation capability must match security request capability")
        if self.secret_ref_id is not None:
            object.__setattr__(self, "secret_ref_id", _text(self.secret_ref_id, "secret_ref_id"))


@dataclass(frozen=True)
class SecurityAdmission:
    request: SecurityRequest
    session: SecuritySession
    permission: PermissionEvaluation
    secret: SecretAccessEvaluation | None
    isolation: IsolationEvaluation
    trust: TrustAssessment
    disposition: SecurityAdmissionDisposition
    reason: str
    audit_event_id: str

    @property
    def admitted(self) -> bool:
        return self.disposition is SecurityAdmissionDisposition.ADMITTED

    def to_context(self) -> dict[str, Any]:
        return {
            "request_id": self.request.request_id,
            "session_id": self.request.session_id,
            "principal_id": self.session.identity.principal_id,
            "capability_id": self.request.capability_id,
            "action": self.request.action.value,
            "disposition": self.disposition.value,
            "reason": self.reason,
            "audit_event_id": self.audit_event_id,
            "permission_allowed": self.permission.allowed,
            "secret_allowed": None if self.secret is None else self.secret.allowed,
            "isolation_allowed": self.isolation.allowed,
            "trust": self.trust.trusted,
            "security_ready": self.admitted,
            "authority_granted": False,
            "execution_requested": False,
        }


class SecurityAdmissionService:
    """Evaluate all Phase 4 security controls without invoking a capability."""

    def __init__(
        self,
        identities: SecurityIdentityRegistry,
        permissions: PermissionModel,
        secrets: SecretReferenceCatalog,
        isolation: IsolationModel,
        trust: TrustModel,
        audit: SecurityAuditLedger,
    ) -> None:
        for name, value in (
            ("identities", identities),
            ("permissions", permissions),
            ("secrets", secrets),
            ("isolation", isolation),
            ("trust", trust),
            ("audit", audit),
        ):
            if value is None:
                raise TypeError(f"{name} is required")
        self._identities = identities
        self._permissions = permissions
        self._secrets = secrets
        self._isolation = isolation
        self._trust = trust
        self._audit = audit

    def admit(self, request: SecurityRequest) -> SecurityAdmission:
        if not isinstance(request, SecurityRequest):
            raise TypeError("request must be a SecurityRequest")
        session = self._identities.get(request.session_id)
        try:
            session.require_authenticated()
        except PermissionError as exc:
            permission = PermissionEvaluation(
                PermissionRequest(session.identity.principal_id, request.capability_id, request.action),
                False,
                str(exc),
            )
            isolation = IsolationEvaluation(request.isolation, None, False, str(exc))
            trust = self._trust.assess(session.identity.principal_id)
            return self._record(request, session, permission, None, isolation, trust, SecurityAdmissionDisposition.DENIED, str(exc))

        permission = self._permissions.evaluate(
            PermissionRequest(session.identity.principal_id, request.capability_id, request.action)
        )
        secret = None
        if request.secret_ref_id is not None:
            secret = self._secrets.evaluate(
                SecretAccessRequest(
                    principal_id=session.identity.principal_id,
                    capability_id=request.capability_id,
                    secret_ref_id=request.secret_ref_id,
                    purpose=f"security request {request.request_id}",
                )
            )
        isolation = self._isolation.evaluate(request.isolation)
        trust = self._trust.assess(session.identity.principal_id)

        failures = []
        if not permission.allowed:
            failures.append(permission.reason)
        if secret is not None and not secret.allowed:
            failures.append(secret.reason)
        if not isolation.allowed:
            failures.append(isolation.reason)
        if not trust.trusted:
            failures.append(trust.reason)
        disposition = SecurityAdmissionDisposition.ADMITTED if not failures else SecurityAdmissionDisposition.DENIED
        reason = "security controls satisfied" if not failures else "; ".join(failures)
        return self._record(request, session, permission, secret, isolation, trust, disposition, reason)

    def _record(
        self,
        request: SecurityRequest,
        session: SecuritySession,
        permission: PermissionEvaluation,
        secret: SecretAccessEvaluation | None,
        isolation: IsolationEvaluation,
        trust: TrustAssessment,
        disposition: SecurityAdmissionDisposition,
        reason: str,
    ) -> SecurityAdmission:
        event = self._audit.build_and_append(
            event_id=f"audit-{request.request_id}",
            timestamp=request.timestamp,
            principal_id=session.identity.principal_id,
            action=f"SECURITY_ADMISSION:{request.action.value}",
            resource=request.capability_id,
            outcome=disposition.value,
            details={
                "request_id": request.request_id,
                "permission_allowed": permission.allowed,
                "secret_allowed": None if secret is None else secret.allowed,
                "isolation_allowed": isolation.allowed,
                "trust": trust.trusted,
                "reason": reason,
            },
        )
        return SecurityAdmission(
            request=request,
            session=session,
            permission=permission,
            secret=secret,
            isolation=isolation,
            trust=trust,
            disposition=disposition,
            reason=reason,
            audit_event_id=event.event_id,
        )


__all__ = ["SecurityAdmissionDisposition", "SecurityRequest", "SecurityAdmission", "SecurityAdmissionService"]
