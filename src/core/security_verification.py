"""M81: verify security admission evidence and derive bounded recovery proposals."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from src.core.security_admission import SecurityAdmission, SecurityAdmissionDisposition
from src.core.security_audit import SecurityAuditLedger


class SecurityVerificationDisposition(str, Enum):
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class SecurityRecoveryDisposition(str, Enum):
    NO_ACTION = "NO_ACTION"
    REAUTHENTICATE = "REAUTHENTICATE"
    REVIEW_PERMISSION = "REVIEW_PERMISSION"
    ROTATE_SECRET_REFERENCE = "ROTATE_SECRET_REFERENCE"
    QUARANTINE_CAPABILITY = "QUARANTINE_CAPABILITY"
    INVESTIGATE_AUDIT = "INVESTIGATE_AUDIT"


@dataclass(frozen=True)
class SecurityVerification:
    admission: SecurityAdmission
    disposition: SecurityVerificationDisposition
    audit_chain_valid: bool
    audit_event_present: bool
    reason: str

    @property
    def verified(self) -> bool:
        return self.disposition is SecurityVerificationDisposition.VERIFIED

    def __post_init__(self) -> None:
        if not isinstance(self.admission, SecurityAdmission):
            raise TypeError("admission must be a SecurityAdmission")
        if not isinstance(self.disposition, SecurityVerificationDisposition):
            raise TypeError("disposition must be a SecurityVerificationDisposition")
        if not isinstance(self.audit_chain_valid, bool) or not isinstance(self.audit_event_present, bool):
            raise TypeError("audit verification flags must be bools")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")

    def to_context(self) -> dict[str, Any]:
        return {
            "request_id": self.admission.request.request_id,
            "disposition": self.disposition.value,
            "verified": self.verified,
            "audit_chain_valid": self.audit_chain_valid,
            "audit_event_present": self.audit_event_present,
            "reason": self.reason,
            "authority_granted": False,
            "execution_requested": False,
        }


@dataclass(frozen=True)
class SecurityRecoveryDecision:
    verification: SecurityVerification
    disposition: SecurityRecoveryDisposition
    target_id: str
    reason: str
    applied: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.verification, SecurityVerification):
            raise TypeError("verification must be a SecurityVerification")
        if not isinstance(self.disposition, SecurityRecoveryDisposition):
            raise TypeError("disposition must be a SecurityRecoveryDisposition")
        if not isinstance(self.target_id, str) or not self.target_id.strip():
            raise ValueError("target_id must be a non-empty string")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string")
        if not isinstance(self.applied, bool):
            raise TypeError("applied must be a bool")
        if self.applied:
            raise ValueError("security recovery is a proposal boundary and cannot be applied here")

    def to_context(self) -> dict[str, Any]:
        return {
            "request_id": self.verification.admission.request.request_id,
            "disposition": self.disposition.value,
            "target_id": self.target_id,
            "reason": self.reason,
            "applied": False,
            "authority_granted": False,
        }


def verify_security_admission(admission: SecurityAdmission, audit: SecurityAuditLedger) -> SecurityVerification:
    """Verify that one admission is still supported by its exact audit evidence."""
    if not isinstance(admission, SecurityAdmission):
        raise TypeError("admission must be a SecurityAdmission")
    if not isinstance(audit, SecurityAuditLedger):
        raise TypeError("audit must be a SecurityAuditLedger")
    event = next((item for item in audit.snapshot() if item.event_id == admission.audit_event_id), None)
    chain_valid = audit.verify_chain()
    event_present = event is not None
    reasons = []
    if not chain_valid:
        reasons.append("audit chain verification failed")
    if event is None:
        reasons.append("security admission audit event is missing")
    else:
        if event.resource != admission.request.capability_id:
            reasons.append("audit resource does not match the admitted capability")
        if event.outcome != admission.disposition.value:
            reasons.append("audit outcome does not match the security admission")
    if admission.disposition is not SecurityAdmissionDisposition.ADMITTED:
        reasons.append("security admission was denied")
    disposition = SecurityVerificationDisposition.VERIFIED if not reasons else SecurityVerificationDisposition.FAILED
    reason = "security admission evidence verified" if not reasons else "; ".join(reasons)
    return SecurityVerification(admission, disposition, chain_valid, event_present, reason)


def derive_security_recovery(verification: SecurityVerification) -> SecurityRecoveryDecision:
    """Return a non-applied recovery proposal for one failed security verification."""
    if not isinstance(verification, SecurityVerification):
        raise TypeError("verification must be a SecurityVerification")
    request = verification.admission.request
    if verification.verified:
        return SecurityRecoveryDecision(
            verification,
            SecurityRecoveryDisposition.NO_ACTION,
            request.request_id,
            "security verification succeeded",
        )
    admission = verification.admission
    if not verification.audit_chain_valid or not verification.audit_event_present:
        disposition = SecurityRecoveryDisposition.INVESTIGATE_AUDIT
    elif not admission.trust.trusted or not admission.session.authenticated:
        disposition = SecurityRecoveryDisposition.REAUTHENTICATE
    elif admission.secret is not None and not admission.secret.allowed:
        disposition = SecurityRecoveryDisposition.ROTATE_SECRET_REFERENCE
    elif not admission.isolation.allowed:
        disposition = SecurityRecoveryDisposition.QUARANTINE_CAPABILITY
    elif not admission.permission.allowed:
        disposition = SecurityRecoveryDisposition.REVIEW_PERMISSION
    else:
        disposition = SecurityRecoveryDisposition.INVESTIGATE_AUDIT
    return SecurityRecoveryDecision(
        verification,
        disposition,
        request.capability_id,
        verification.reason,
    )


__all__ = [
    "SecurityVerificationDisposition",
    "SecurityRecoveryDisposition",
    "SecurityVerification",
    "SecurityRecoveryDecision",
    "verify_security_admission",
    "derive_security_recovery",
]
