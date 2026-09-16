from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "src" / "agency" / "work_state.py"
TESTS = ROOT / "src" / "agency" / "tests" / "test_work_state.py"
DECISION = ROOT / "docs" / "decisions" / "M31.1-work-state-agency.md"
MILESTONE = ROOT / "docs" / "milestones" / "M31_WORK_STATE_AGENCY.md"


def require(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"missing M31 artifact: {path}")
    return path.read_text(encoding="utf-8")


contract = require(CONTRACT)
tests = require(TESTS)
decision = require(DECISION)
milestone = require(MILESTONE)

required_contract_markers = (
    "class WorkState",
    "class WorkStage",
    "class WorkStatus",
    "class WorkRole",
    "class WorkBlocker",
    "def infer_work_role",
    "assigned_agent_ids",
    "required_capabilities",
    "evidence_cursor",
    "authority",
)
required_tests = (
    "test_work_state_is_immutable_and_bounded",
    "test_blockers_are_first_class_work_state",
    "test_dynamic_role_inference_uses_work_state_signals",
    "test_role_is_not_authority",
)
for marker in required_contract_markers:
    if marker not in contract:
        raise SystemExit(f"missing M31 contract marker: {marker}")
for marker in required_tests:
    if marker not in tests:
        raise SystemExit(f"missing M31 focused test: {marker}")
if "dynamic" not in decision.lower() or "authority" not in decision.lower():
    raise SystemExit("M31 decision must document dynamic role and authority separation")
if "Work State" not in milestone or "M31.5" not in milestone:
    raise SystemExit("M31 milestone record is incomplete")

print("M31 work state / agency contract: PASS")
