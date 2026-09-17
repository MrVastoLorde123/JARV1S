"""Static contract verifier for M58 authorized execution recovery bridge."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src" / "agency" / "authorized_execution_recovery.py"

required = (
    "class AuthorizedExecutionRecovery",
    "AuthorizedExecutionVerification",
    "RecoveryDecision",
    "derive_recovery_decision",
    "execution_requested",
    "authorization_created",
)
forbidden = (
    "authorize(",
    "run_execution_handoff(",
    "verify(",
    "execute(",
    "select_provider",
    "select_tool",
    "provider_call",
    "subprocess",
)

text = TARGET.read_text(encoding="utf-8")
missing = [marker for marker in required if marker not in text]
forbidden_found = [marker for marker in forbidden if marker in text]
if missing:
    raise SystemExit(f"M58 authorized-execution-recovery contract: missing {missing}")
if forbidden_found:
    raise SystemExit(f"M58 authorized-execution-recovery contract: forbidden {forbidden_found}")

print("M58 authorized-execution-recovery contract: PASS")
