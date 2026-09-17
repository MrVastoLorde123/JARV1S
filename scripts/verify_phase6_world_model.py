from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORLD_MODEL = ROOT / "src/core/world_model.py"
RUNTIME = ROOT / "src/core/runtime_kernel.py"
TESTS = ROOT / "tests/phase6/test_phase6_world_model.py"
PHASE_DOC = ROOT / "docs/phases/PHASE6_WORLD_MODEL_CONTEXT.md"
ARCH_DOC = ROOT / "docs/architecture/world-model.md"

FORBIDDEN_CALLS = {
    "authorize",
    "execute",
    "run_execution_handoff",
    "select_provider",
    "provider_call",
    "invoke_tool",
}
FORBIDDEN_IMPORTS = {"subprocess", "os.system", "socket"}
REQUIRED_WORLD_SYMBOLS = {
    "ValidityWindow",
    "WorldConflict",
    "WorldEntity",
    "WorldEntityType",
    "WorldModelSystem",
    "WorldObservation",
    "WorldObservationAction",
    "WorldRelation",
    "WorldSnapshot",
}


def _fail(message: str) -> None:
    raise SystemExit(f"Phase 6 contract: FAIL — {message}")


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
    for path in (WORLD_MODEL, RUNTIME, TESTS, PHASE_DOC, ARCH_DOC):
        if not path.exists():
            _fail(f"missing required artifact: {path.relative_to(ROOT)}")

    try:
        world_tree = ast.parse(WORLD_MODEL.read_text(encoding="utf-8"))
        runtime_tree = ast.parse(RUNTIME.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        _fail(f"syntax error: {exc}")

    missing_symbols = REQUIRED_WORLD_SYMBOLS - _class_names(world_tree)
    if missing_symbols:
        _fail(f"missing world-model classes: {sorted(missing_symbols)}")

    world_calls = _call_names(world_tree)
    runtime_calls = _call_names(runtime_tree)
    forbidden_calls = (world_calls | runtime_calls) & FORBIDDEN_CALLS
    if forbidden_calls:
        _fail(f"forbidden authority/execution/provider calls: {sorted(forbidden_calls)}")

    forbidden_imports = (_module_names(world_tree) | _module_names(runtime_tree)) & FORBIDDEN_IMPORTS
    if forbidden_imports:
        _fail(f"forbidden external-execution imports: {sorted(forbidden_imports)}")

    runtime_source = RUNTIME.read_text(encoding="utf-8")
    required_runtime_markers = (
        "world_model: WorldModelSystem | None = None",
        "self._world_model = world_model",
        "def world_model(self) -> WorldModelSystem | None:",
    )
    for marker in required_runtime_markers:
        if marker not in runtime_source:
            _fail(f"runtime integration marker missing: {marker}")

    try:
        import sys

        sys.path.insert(0, str(ROOT))
        from src.core.world_model import WorldModelSystem

        model = WorldModelSystem()
        checks = (
            not model.authorizes_execution,
            not model.executes_capability,
            not model.mutates_external_state,
            not model.persists_state,
            not model.establishes_truth,
            not model.establishes_certainty,
            not model.selects_provider,
        )
        if not all(checks):
            _fail("world-model authority boundary is not explicitly closed")
    except SystemExit:
        raise
    except Exception as exc:
        _fail(f"world-model boundary could not be instantiated: {exc}")

    print("Phase 6 contract: PASS")


if __name__ == "__main__":
    main()
