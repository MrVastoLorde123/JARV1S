import ast
from pathlib import Path
import unittest


class RoleCallerGenerationSurfaceAuditTests(unittest.TestCase):
    """Keep explicit model-role callers from regressing to provider-directed generation."""

    _SOURCE_ROOT = Path(__file__).resolve().parents[2]
    _EXCLUDED_PARTS = {"tests"}
    _EXCLUDED_FILES = {
        Path("src/ai/service.py"),
    }

    def test_production_callers_do_not_directly_generate_from_ai_service(self):
        violations = []
        for path in sorted(self._SOURCE_ROOT.rglob("*.py")):
            relative_path = path.relative_to(self._SOURCE_ROOT.parent.parent)
            if relative_path in self._EXCLUDED_FILES:
                continue
            if any(part in self._EXCLUDED_PARTS for part in path.parts):
                continue

            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError as exc:
                self.fail(f"Could not parse {path}: {exc}")

            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                    continue
                if node.func.attr != "generate":
                    continue
                receiver = node.func.value
                if isinstance(receiver, ast.Attribute) and receiver.attr in {"ai_service", "_ai_service"}:
                    violations.append(f"{path}:{node.lineno} calls {ast.unparse(node.func)}()")

        self.assertEqual(
            violations,
            [],
            "AI-backed production callers must use generate_for_role(); direct AIService.generate() calls "
            "belong only inside the provider-directed AIService boundary itself.\n" + "\n".join(violations),
        )

    def test_production_callers_do_not_probe_for_role_routing_compatibility(self):
        violations = []
        for path in sorted(self._SOURCE_ROOT.rglob("*.py")):
            if path.relative_to(self._SOURCE_ROOT.parent.parent) in self._EXCLUDED_FILES:
                continue
            if any(part in self._EXCLUDED_PARTS for part in path.parts):
                continue

            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                    continue
                if node.func.id != "getattr" or len(node.args) < 2:
                    continue
                if isinstance(node.args[1], ast.Constant) and node.args[1].value == "generate_for_role":
                    violations.append(f"{path}:{node.lineno} probes for generate_for_role with getattr()")

        self.assertEqual(
            violations,
            [],
            "Production callers must depend on the explicit role-routing contract rather than compatibility probing.\n"
            + "\n".join(violations),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
