"""Static contract verifier for Phase 4 Security."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    ROOT / "src" / "core" / "security_identity.py": (
        "SecurityIdentity",
        "SecuritySession",
        "SecurityIdentityRegistry",
    ),
    ROOT / "src" / "core" / "security_permission.py": (
        "PermissionGrant",
        "PermissionEvaluation",
        "PermissionModel",
    ),
    ROOT / "src" / "core" / "security_secrets.py": (
        "SecretReference",
        "SecretAccessEvaluation",
        "SecretReferenceCatalog",
        "raw_secret_present",
    ),
    ROOT / "src" / "core" / "security_isolation.py": (
        "IsolationProfile",
        "IsolationEvaluation",
        "IsolationModel",
    ),
    ROOT / "src" / "core" / "security_trust.py": (
        "TrustEvidence",
        "TrustAssessment",
        "TrustModel",
    ),
    ROOT / "src" / "core" / "security_audit.py": (
        "SecurityAuditEvent",
        "SecurityAuditLedger",
        "verify_chain",
    ),
    ROOT / "src" / "core" / "security_admission.py": (
        "SecurityRequest",
        "SecurityAdmission",
        "SecurityAdmissionService",
    ),
    ROOT / "src" / "core" / "security_verification.py": (
        "SecurityVerification",
        "SecurityRecoveryDecision",
        "derive_security_recovery",
    ),
    ROOT / "src" / "core" / "security_system.py": (
        "SecuritySystem",
        "SecurityCoverage",
        "capability_system",
    ),
    ROOT / "src" / "core" / "runtime_kernel.py": (
        "SecuritySystem",
        "security_system:",
        "def security_system",
    ),
}

FORBIDDEN = (
    "authorize(",
    "run_execution_handoff(",
    "execute(",
    "invoke(",
    "select_provider",
    "select_tool",
    "provider_call",
    "subprocess.call",
    "subprocess.run",
    "open(",
    "write_text(",
    "unlink(",
)

for target, required_markers in TARGETS.items():
    if not target.exists():
        raise SystemExit(f"Phase 4 contract: missing {target}")
    text = target.read_text(encoding="utf-8")
    missing = [marker for marker in required_markers if marker not in text]
    if missing:
        raise SystemExit(f"Phase 4 contract: {target.name} missing markers {missing}")
    forbidden = [item for item in FORBIDDEN if item in text]
    if forbidden:
        raise SystemExit(f"Phase 4 contract: {target.name} contains forbidden surfaces {forbidden}")

secret_text = (ROOT / "src" / "core" / "security_secrets.py").read_text(encoding="utf-8")
for marker in ("raw_secret_present", "secret_ref_id"):
    if marker not in secret_text:
        raise SystemExit(f"Phase 4 contract: secret boundary marker missing {marker}")
if re.search(r"(?m)^\s*(?:secret_value|raw_secret)\s*:", secret_text):
    raise SystemExit("Phase 4 contract: raw secret field detected")

runtime_text = (ROOT / "src" / "core" / "runtime_kernel.py").read_text(encoding="utf-8")
for marker in (
    "def authorizes_execution(self) -> bool:",
    "def executes_capability(self) -> bool:",
    "return False",
):
    if marker not in runtime_text:
        raise SystemExit(f"Phase 4 contract: runtime authority marker missing {marker}")

print("Phase 4 contract: PASS")
