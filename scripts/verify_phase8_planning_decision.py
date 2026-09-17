from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLANNING = ROOT / "src/core/planning_decision.py"
RUNTIME = ROOT / "src/core/runtime_kernel.py"
TESTS = ROOT / "tests/phase8/test_phase8_planning_decision.py"
PHASE_DOC = ROOT / "docs/phases/PHASE8_GOALS_PLANNING_DECISION_SUPPORT.md"
ARCH_DOC = ROOT / "docs/architecture/goals-planning-decision.md"

FORBIDDEN_CALLS = {
    "authorize",
    "execute",
    "run_execution_handoff",
    "select_provider",
    "provider_call",
    "invoke_tool",
}
FORBIDDEN_IMPORTS = {"subprocess", "os.system", "socket"}
REQUIRED_SYMBOLS = {
    "CandidatePlan",
    "Goal",
    "GoalStatus",
    "PlanEvaluation",
    "PlanFeasibility",
    "PlanRanking",
    "PlannedStep",
    "PlanningContext",
    "PlanningDecisionSystem",
    "PlanningResult",
}


def _fail(message: str) -> None:
    raise SystemExit(f"Phase 8 contract: FAIL — {message}")


def _call_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                names.add(node.func.attr)
    return names


def _module_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def _class_names(tree: ast.AST) -> set[str]:
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}


def main() -> None:
    for path in (PLANNING, RUNTIME, TESTS, PHASE_DOC, ARCH_DOC):
        if not path.exists():
            _fail(f"missing required artifact: {path.relative_to(ROOT)}")

    try:
        planning_tree = ast.parse(PLANNING.read_text(encoding="utf-8"))
        runtime_tree = ast.parse(RUNTIME.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        _fail(f"syntax error: {exc}")

    missing = REQUIRED_SYMBOLS - _class_names(planning_tree)
    if missing:
        _fail(f"missing planning classes: {sorted(missing)}")

    forbidden_calls = (_call_names(planning_tree) | _call_names(runtime_tree)) & FORBIDDEN_CALLS
    if forbidden_calls:
        _fail(f"forbidden authority/execution/provider calls: {sorted(forbidden_calls)}")

    forbidden_imports = (_module_names(planning_tree) | _module_names(runtime_tree)) & FORBIDDEN_IMPORTS
    if forbidden_imports:
        _fail(f"forbidden external-execution imports: {sorted(forbidden_imports)}")

    runtime_source = RUNTIME.read_text(encoding="utf-8")
    for marker in (
        "planning_system: PlanningDecisionSystem | None = None",
        "self._planning_system = planning_system",
        "def planning_system(self) -> PlanningDecisionSystem | None:",
    ):
        if marker not in runtime_source:
            _fail(f"runtime integration marker missing: {marker}")

    try:
        import sys

        sys.path.insert(0, str(ROOT))
        from src.core.planning_decision import PlanningDecisionSystem

        system = PlanningDecisionSystem()
        checks = (
            not system.authorizes_execution,
            not system.executes_capability,
            not system.mutates_external_state,
            not system.persists_state,
            not system.establishes_truth,
            not system.establishes_certainty,
        )
        if not all(checks):
            _fail("planning authority boundary is not explicitly closed")
    except SystemExit:
        raise
    except Exception as exc:
        _fail(f"planning boundary could not be instantiated: {exc}")

    print("Phase 8 contract: PASS")


if __name__ == "__main__":
    main()
