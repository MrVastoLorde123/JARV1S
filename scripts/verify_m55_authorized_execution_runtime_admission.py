"""Repository-local M55 authorized execution runtime admission verification."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

required = {
    "src/agency/authorized_execution_runtime_admission.py": [
        "AuthorizedExecutionRuntimeAdmission",
        "create_authorized_execution_runtime_admission",
        "execution_result.handoff",
        "execution_performed",
    ],
    "src/agency/tests/test_authorized_execution_runtime_admission.py": [
        "test_runtime_result_can_bind_to_exact_admission",
        "test_mismatched_execution_result_is_rejected",
        "test_non_bridge_result_is_rejected",
    ],
}

for relative, markers in required.items():
    text = (ROOT / relative).read_text(encoding="utf-8")
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"M55 authorized-execution-runtime-admission contract: FAIL {relative}: {missing}")

text = (ROOT / "src/agency/authorized_execution_runtime_admission.py").read_text(encoding="utf-8")
for forbidden in (
    "authorize(",
    "select_provider",
    "select_tool",
    "provider_call",
    "subprocess",
    "run_execution_handoff(",
):
    if forbidden in text:
        raise SystemExit(
            "M55 authorized-execution-runtime-admission contract: FAIL forbidden execution/authority surface: "
            + forbidden
        )

print("M55 authorized-execution-runtime-admission contract: PASS")
