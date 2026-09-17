from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "src/core/proactive_initiative.py"
RUNTIME = ROOT / "src/core/runtime_kernel.py"
TESTS = ROOT / "tests/phase9/test_phase9_proactive_initiative.py"
PHASE_DOC = ROOT / "docs/phases/PHASE9_PROACTIVE_INITIATIVE_INTEGRATION.md"
ARCH_DOC = ROOT / "docs/architecture/proactive-initiative-integration.md"

FORBIDDEN_CALLS = {
    "authorize",
    "execute",
    "run_execution_handoff",
    "select_provider",
    "provider_call",
    "invoke_tool",
    "send_notification",
    "enqueue",
    "schedule",
}
FORBIDDEN_IMPORTS = {"subprocess", "os.system", "socket"}
REQUIRED_SYMBOLS = {
    "ProactiveInitiativeContext",
    "ProactiveInitiativeResult",
    "ProactiveInitiativeSystem",
    "ProactiveInitiativeValidationError",
}


def _fail(message: str) -> None:
    raise SystemExit(f"Phase 9 contract: FAIL — {message}")


def _calls(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                names.add(node.func.attr)
    return names


def _imports(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def main() -> None:
    for path in (BRIDGE, RUNTIME, TESTS, PHASE_DOC, ARCH_DOC):
        if not path.exists():
            _fail(f"missing required artifact: {path.relative_to(ROOT)}")

    try:
        bridge_tree = ast.parse(BRIDGE.read_text(encoding="utf-8"))
        runtime_tree = ast.parse(RUNTIME.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        _fail(f"syntax error: {exc}")

    class_names = {
        node.name
        for node in ast.walk(bridge_tree)
        if isinstance(node, ast.ClassDef)
    }
    missing = REQUIRED_SYMBOLS - class_names
    if missing:
        _fail(f"missing bridge symbols: {sorted(missing)}")

    forbidden_calls = (_calls(bridge_tree) | _calls(runtime_tree)) & FORBIDDEN_CALLS
    if forbidden_calls:
        _fail(f"forbidden authority/execution/runtime calls: {sorted(forbidden_calls)}")

    forbidden_imports = (_imports(bridge_tree) | _imports(runtime_tree)) & FORBIDDEN_IMPORTS
    if forbidden_imports:
        _fail(f"forbidden external-execution imports: {sorted(forbidden_imports)}")

    runtime_source = RUNTIME.read_text(encoding="utf-8")
    markers = (
        "proactive_initiative: ProactiveInitiativeSystem | None = None",
        "self._proactive_initiative = proactive_initiative",
        "def proactive_initiative(self) -> ProactiveInitiativeSystem | None:",
    )
    for marker in markers:
        if marker not in runtime_source:
            _fail(f"runtime integration marker missing: {marker}")

    try:
        import sys

        sys.path.insert(0, str(ROOT))
        from src.core.proactive_initiative import ProactiveInitiativeSystem

        system = ProactiveInitiativeSystem()
        checks = (
            not system.authorizes_execution,
            not system.executes_capability,
            not system.mutates_state,
            not system.persists_state,
            not system.establishes_truth,
            not system.establishes_certainty,
            not system.selects_provider,
        )
        if not all(checks):
            _fail("proactive initiative authority boundary is not explicitly closed")
    except SystemExit:
        raise
    except Exception as exc:
        _fail(f"proactive initiative boundary could not be instantiated: {exc}")

    print("Phase 9 contract: PASS")


if __name__ == "__main__":
    main()
