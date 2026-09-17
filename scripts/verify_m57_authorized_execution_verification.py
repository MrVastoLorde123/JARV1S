"""Static contract verifier for M57 authorized execution verification bridge."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src" / "agency" / "authorized_execution_verification.py"

required = (
    "class AuthorizedExecutionVerification",
    "AuthorizedExecutionOutcome",
    "VerificationDecision",
    "VerificationDisposition",
    "verification_performed",
    "recovery_derived",
)
forbidden = (
    "verify(",
    "authorize(",
    "run_execution_handoff(",
    "execute(",
    "select_provider",
    "select_tool",
    "provider_call",
    "subprocess",
    "derive_recovery_decision(",
)

text = TARGET.read_text(encoding="utf-8")
missing = [marker for marker in required if marker not in text]
forbidden_found = [marker for marker in forbidden if marker in text]
if missing:
    raise SystemExit(f"M57 authorized-execution-verification contract: missing {missing}")
if forbidden_found:
    raise SystemExit(f"M57 authorized-execution-verification contract: forbidden {forbidden_found}")

print("M57 authorized-execution-verification contract: PASS")
