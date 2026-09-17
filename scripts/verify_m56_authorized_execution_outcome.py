"""Static contract verifier for M56 authorized execution outcome bridge."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src" / "agency" / "authorized_execution_outcome.py"

required = (
    "class AuthorizedExecutionOutcome",
    "AuthorizedExecutionRuntimeAdmission",
    "AgencyExecutionOutcome",
    "VerificationInput",
    "classify_agency_outcome",
    "build_verification_input",
    "verification_performed",
    "recovery_derived",
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
    raise SystemExit(f"M56 authorized-execution-outcome contract: missing {missing}")
if forbidden_found:
    raise SystemExit(f"M56 authorized-execution-outcome contract: forbidden {forbidden_found}")

print("M56 authorized-execution-outcome contract: PASS")
