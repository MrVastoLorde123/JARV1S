"""Static contract verifier for M59 authorized execution reconciliation bridge."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src" / "agency" / "authorized_execution_reconciliation.py"

required = (
    "class AuthorizedExecutionReconciliation",
    "AuthorizedExecutionRecovery",
    "RecoveryReconciliation",
    "reconcile_recovery",
    "execution_id",
    "work_id",
    "authorization_created",
    "execution_requested",
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
    "derive_recovery_decision(",
)

text = TARGET.read_text(encoding="utf-8")
missing = [marker for marker in required if marker not in text]
forbidden_found = [marker for marker in forbidden if marker in text]
if missing:
    raise SystemExit(f"M59 authorized-execution-reconciliation contract: missing {missing}")
if forbidden_found:
    raise SystemExit(f"M59 authorized-execution-reconciliation contract: forbidden {forbidden_found}")

print("M59 authorized-execution-reconciliation contract: PASS")
