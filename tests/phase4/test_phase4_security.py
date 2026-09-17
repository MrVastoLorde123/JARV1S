"""Focused Phase 4 security verification suite."""

from __future__ import annotations

import unittest

from src.core.capability_graph import build_capability_graph
from src.core.capability_registry import CapabilityDefinition
from src.core.capability_system import CapabilitySystem
from src.core.runtime_kernel import JarvisRuntime
from src.core.security_admission import SecurityAdmissionDisposition, SecurityRequest
from src.core.security_audit import SecurityAuditLedger
from src.core.security_identity import (
    PrincipalKind,
    SecurityIdentity,
    SecurityIdentityRegistry,
    SecurityLevel,
    SecuritySession,
)
from src.core.security_isolation import CapabilityIsolationBinding, IsolationModel, IsolationProfile, IsolationRequest
from src.core.security_permission import PermissionAction, PermissionGrant, PermissionModel
from src.core.security_secrets import SecretReference, SecretReferenceCatalog, SecretSensitivity
from src.core.security_system import SecuritySystem
from src.core.security_trust import RiskLevel, TrustEvidence, TrustModel, TrustPolicy
from src.core.security_verification import SecurityRecoveryDisposition


class _Orchestration:
    def dispatch(self, request):
        from src.core.interface_backend import InterfaceResponse, InterfaceResponseStatus

        return InterfaceResponse(
            request_id=request.request_id,
            operation=request.operation,
            status=InterfaceResponseStatus.ACCEPTED,
            payload={},
            metadata={"artifact_type": "TEST_STAGE"},
        )


class Phase4SecurityTests(unittest.TestCase):
    def definition(self, capability_id: str) -> CapabilityDefinition:
        return CapabilityDefinition(
            capability_id=capability_id,
            name=capability_id,
            description=f"Capability {capability_id}",
            category="security-test",
            metadata={},
        )

    def capability_system(self) -> CapabilitySystem:
        return CapabilitySystem(
            build_capability_graph((self.definition("network_scan"), self.definition("secret_reader")))
        )

    def identity_registry(self, *, level: SecurityLevel = SecurityLevel.AUTHENTICATED) -> SecurityIdentityRegistry:
        return SecurityIdentityRegistry(
            (
                SecuritySession(
                    "session-1",
                    SecurityIdentity("user-1", "Operator", PrincipalKind.USER),
                    level,
                ),
                SecuritySession(
                    "session-2",
                    SecurityIdentity("user-2", "Other", PrincipalKind.USER),
                    SecurityLevel.AUTHENTICATED,
                ),
            )
        )

    def isolation(self, *, network: bool = False) -> IsolationModel:
        return IsolationModel(
            (
                CapabilityIsolationBinding(
                    "network_scan",
                    IsolationProfile(
                        profile_id="sandbox-scan",
                        network_access=network,
                        allowed_hosts=("scanner.local",),
                    ),
                ),
                CapabilityIsolationBinding(
                    "secret_reader",
                    IsolationProfile(profile_id="sandbox-secret"),
                ),
            )
        )

    def trust(self, *, score: float = 0.95) -> TrustModel:
        return TrustModel(
            (TrustEvidence("trust-1", "user-1", "session-attestation", score, True, "test evidence"),),
            TrustPolicy(minimum_score=0.7, maximum_risk=RiskLevel.MEDIUM),
        )

    def permission_model(self) -> PermissionModel:
        return PermissionModel(
            (
                PermissionGrant("user-1", "network_scan", (PermissionAction.INVOKE,)),
                PermissionGrant("user-1", "secret_reader", (PermissionAction.READ,)),
            )
        )

    def security_system(self, *, network: bool = False, trust_score: float = 0.95) -> SecuritySystem:
        return SecuritySystem(
            identities=self.identity_registry(),
            permissions=self.permission_model(),
            secrets=SecretReferenceCatalog(
                (
                    SecretReference(
                        "secret-1",
                        "user-1",
                        "secret_reader",
                        "credential-store",
                        SecretSensitivity.CRITICAL,
                    ),
                )
            ),
            isolation=self.isolation(network=network),
            trust=self.trust(score=trust_score),
            audit=SecurityAuditLedger(),
            capability_system=self.capability_system(),
        )

    def request(self, *, capability: str = "network_scan", action: PermissionAction = PermissionAction.INVOKE, secret_ref_id: str | None = None, network: bool = False) -> SecurityRequest:
        return SecurityRequest(
            request_id=f"request-{capability}-{action.value.lower()}",
            session_id="session-1",
            capability_id=capability,
            action=action,
            isolation=IsolationRequest(capability, network_required=network, requested_host="scanner.local" if network else None),
            timestamp="2026-09-17T12:00:00Z",
            secret_ref_id=secret_ref_id,
        )

    def test_identity_requires_an_active_authenticated_session(self) -> None:
        session = self.identity_registry().get("session-1")
        session.require_authenticated()
        with self.assertRaises(PermissionError):
            self.identity_registry(level=SecurityLevel.UNAUTHENTICATED).get("session-1").require_authenticated()

    def test_permission_model_is_explicit_and_capability_bound(self) -> None:
        system = self.security_system()
        admitted = system.admit(self.request())
        self.assertTrue(admitted.permission.allowed)
        denied = system.admit(self.request(action=PermissionAction.ADMIN))
        self.assertFalse(denied.permission.allowed)
        self.assertEqual(denied.disposition, SecurityAdmissionDisposition.DENIED)

    def test_secret_boundary_uses_opaque_references_only(self) -> None:
        reference = self.security_system()._secrets.snapshot()[0]
        self.assertFalse(hasattr(reference, "secret_value"))
        self.assertFalse(reference.to_context()["raw_secret_present"])
        denied = self.security_system().admit(self.request(capability="secret_reader", action=PermissionAction.READ, secret_ref_id="secret-1"))
        self.assertTrue(denied.admitted)

    def test_isolation_denies_network_when_profile_forbids_it(self) -> None:
        system = self.security_system(network=False)
        admission = system.admit(self.request(network=True))
        self.assertFalse(admission.isolation.allowed)
        self.assertEqual(admission.disposition, SecurityAdmissionDisposition.DENIED)
        recovery = system.recover(system.verify(admission))
        self.assertEqual(recovery.disposition, SecurityRecoveryDisposition.QUARANTINE_CAPABILITY)

    def test_trust_model_blocks_low_trust(self) -> None:
        system = self.security_system(trust_score=0.2)
        admission = system.admit(self.request())
        self.assertFalse(admission.trust.trusted)
        self.assertEqual(admission.disposition, SecurityAdmissionDisposition.DENIED)
        recovery = system.recover(system.verify(admission))
        self.assertEqual(recovery.disposition, SecurityRecoveryDisposition.REAUTHENTICATE)

    def test_audit_ledger_is_hash_chained_and_detects_tampering(self) -> None:
        system = self.security_system()
        admission = system.admit(self.request())
        self.assertTrue(system.audit.verify_chain())
        event = system.audit.snapshot()[0]
        object.__setattr__(event, "outcome", "TAMPERED")
        self.assertFalse(system.audit.verify_chain())
        verification = system.verify(admission)
        self.assertFalse(verification.verified)
        self.assertEqual(system.recover(verification).disposition, SecurityRecoveryDisposition.INVESTIGATE_AUDIT)

    def test_secret_owner_mismatch_is_denied(self) -> None:
        system = SecuritySystem(
            identities=self.identity_registry(),
            permissions=self.permission_model(),
            secrets=SecretReferenceCatalog(
                (
                    SecretReference(
                        "secret-1",
                        "user-2",
                        "secret_reader",
                        "credential-store",
                        SecretSensitivity.CRITICAL,
                    ),
                )
            ),
            isolation=self.isolation(),
            trust=self.trust(),
            audit=SecurityAuditLedger(),
            capability_system=self.capability_system(),
        )
        admission = system.admit(self.request(capability="secret_reader", action=PermissionAction.READ, secret_ref_id="secret-1"))
        self.assertFalse(admission.secret.allowed)
        self.assertEqual(system.recover(system.verify(admission)).disposition, SecurityRecoveryDisposition.ROTATE_SECRET_REFERENCE)

    def test_security_verification_requires_exact_audit_evidence(self) -> None:
        system = self.security_system()
        admission = system.admit(self.request())
        verification = system.verify(admission)
        self.assertTrue(verification.verified)
        self.assertTrue(verification.audit_event_present)
        self.assertTrue(verification.audit_chain_valid)
        self.assertEqual(system.recover(verification).disposition, SecurityRecoveryDisposition.NO_ACTION)

    def test_unknown_security_capability_links_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            SecuritySystem(
                identities=self.identity_registry(),
                permissions=PermissionModel((PermissionGrant("user-1", "unknown", (PermissionAction.INVOKE,)),)),
                secrets=SecretReferenceCatalog(),
                isolation=IsolationModel(),
                trust=self.trust(),
                audit=SecurityAuditLedger(),
                capability_system=self.capability_system(),
            )

    def test_security_system_exposes_coverage_without_execution_surface(self) -> None:
        system = self.security_system()
        coverage = system.coverage()
        self.assertEqual(coverage.capability_count, 2)
        self.assertEqual(coverage.isolation_covered_count, 2)
        for method in ("authorize", "execute", "invoke", "select_provider", "select_tool"):
            self.assertFalse(hasattr(system, method), method)

    def test_runtime_accepts_injected_security_system(self) -> None:
        security = self.security_system()
        runtime = JarvisRuntime(
            orchestration=_Orchestration(),
            session_id="runtime-session",
            actor_id="runtime-actor",
            security_system=security,
        )
        self.assertIs(runtime.security_system, security)
        self.assertFalse(runtime.authorizes_execution)
        self.assertFalse(runtime.executes_capability)

    def test_recovery_is_never_applied_by_security_layer(self) -> None:
        system = self.security_system(trust_score=0.1)
        decision = system.recover(system.verify(system.admit(self.request())))
        self.assertFalse(decision.applied)
        with self.assertRaises(ValueError):
            type(decision)(decision.verification, decision.disposition, decision.target_id, decision.reason, applied=True)

    def test_end_to_end_verified_security_path_stays_below_authority(self) -> None:
        system = self.security_system()
        admission = system.admit(self.request())
        self.assertEqual(admission.disposition, SecurityAdmissionDisposition.ADMITTED)
        verification = system.verify(admission)
        self.assertTrue(verification.verified)
        self.assertFalse(admission.to_context()["authority_granted"])
        self.assertFalse(verification.to_context()["authority_granted"])
        self.assertFalse(system.summary()["capability_invocation_performed"])


if __name__ == "__main__":
    unittest.main()
