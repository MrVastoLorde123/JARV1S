from __future__ import annotations

import ast
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REASONING = ROOT / "src/core/reasoning.py"
RUNTIME = ROOT / "src/core/runtime_kernel.py"
TESTS = ROOT / "tests/phase7/test_phase7_reasoning.py"
PHASE_DOC = ROOT / "docs/phases/PHASE7_REASONING_UNCERTAINTY_PREDICTION.md"
ARCH_DOC = ROOT / "docs/architecture/reasoning-uncertainty.md"
DECISION_DOC = ROOT / "docs/decisions/PHASE7_REASONING_BOUNDARY.md"

REQUIRED_SYMBOLS = {
    "BeliefRevision",
    "EvidencePolarity",
    "EvidenceSignal",
    "Hypothesis",
    "Prediction",
    "ReasoningContext",
    "ReasoningEvaluation",
    "ReasoningResult",
    "ReasoningStepKind",
    "ReasoningSystem",
    "ReasoningTraceStep",
    "RevisionStatus",
}
FORBIDDEN_CALLS = {
    "authorize",
    "execute",
    "run_execution_handoff",
    "select_provider",
    "provider_call",
    "invoke_tool",
}
FORBIDDEN_IMPORTS = {"subprocess", "socket", "os.system"}


def _fail(message: str) -> None:
    raise SystemExit(f"Phase 7 contract: FAIL — {message}")


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
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
    }


def main() -> None:
    for path in (REASONING, RUNTIME, TESTS, PHASE_DOC, ARCH_DOC, DECISION_DOC):
        if not path.exists():
            _fail(f"missing required artifact: {path.relative_to(ROOT)}")

    try:
        reasoning_tree = ast.parse(REASONING.read_text(encoding="utf-8"))
        runtime_tree = ast.parse(RUNTIME.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        _fail(f"syntax error: {exc}")

    missing_symbols = REQUIRED_SYMBOLS - _class_names(reasoning_tree)
    if missing_symbols:
        _fail(f"missing reasoning classes: {sorted(missing_symbols)}")

    forbidden_calls = (_call_names(reasoning_tree) | _call_names(runtime_tree)) & FORBIDDEN_CALLS
    if forbidden_calls:
        _fail(f"forbidden authority/execution/provider calls: {sorted(forbidden_calls)}")

    forbidden_imports = (_module_names(reasoning_tree) | _module_names(runtime_tree)) & FORBIDDEN_IMPORTS
    if forbidden_imports:
        _fail(f"forbidden external-execution imports: {sorted(forbidden_imports)}")

    runtime_source = RUNTIME.read_text(encoding="utf-8")
    required_runtime_markers = (
        "reasoning_system: ReasoningSystem | None = None",
        "self._reasoning_system = reasoning_system",
        "def reasoning_system(self) -> ReasoningSystem | None:",
    )
    for marker in required_runtime_markers:
        if marker not in runtime_source:
            _fail(f"runtime integration marker missing: {marker}")

    sys.path.insert(0, str(ROOT))
    try:
        from src.core.reasoning import ReasoningSystem

        system = ReasoningSystem()
        checks = (
            not system.authorizes_execution,
            not system.executes_capability,
            not system.mutates_external_state,
            not system.persists_state,
            not system.establishes_truth,
            not system.establishes_certainty,
            not system.selects_provider,
        )
        if not all(checks):
            _fail("reasoning authority boundary is not explicitly closed")
    except SystemExit:
        raise
    except Exception as exc:
        _fail(f"reasoning boundary could not be instantiated: {exc}")

    print("Phase 7 contract: PASS")


if __name__ == "__main__":
    main()
