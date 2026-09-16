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

    @classmethod
    def _parse_tree(cls, path: Path):
        """Parse repository Python sources while tolerating legacy UTF-8 BOMs."""
        try:
            source = path.read_text(encoding="utf-8-sig")
            return ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            raise AssertionError(f"Could not parse {path}: {exc}") from exc

    @staticmethod
    def _is_ai_service_receiver(node):
        return isinstance(node, ast.Attribute) and node.attr in {"ai_service", "_ai_service"}

    @classmethod
    def _ai_service_aliases(cls, tree):
        """Return aliases created directly or transitively from an AIService receiver."""
        aliases = set()
        changed = True
        while changed:
            changed = False
            for node in ast.walk(tree):
                if not isinstance(node, ast.Assign):
                    continue
                if len(node.targets) != 1:
                    continue
                target = node.targets[0]
                if not isinstance(target, ast.Name):
                    continue
                value = node.value
                is_alias = cls._is_ai_service_receiver(value)
                if isinstance(value, ast.Name) and value.id in aliases:
                    is_alias = True
                if is_alias and target.id not in aliases:
                    aliases.add(target.id)
                    changed = True
        return aliases

    @classmethod
    def _is_ai_service_source(cls, node, aliases):
        return cls._is_ai_service_receiver(node) or (
            isinstance(node, ast.Name) and node.id in aliases
        )

    def test_production_callers_do_not_directly_generate_from_ai_service(self):
        violations = []
        for path in sorted(self._SOURCE_ROOT.rglob("*.py")):
            relative_path = path.relative_to(self._SOURCE_ROOT.parent.parent)
            if relative_path in self._EXCLUDED_FILES:
                continue
            if any(part in self._EXCLUDED_PARTS for part in path.parts):
                continue

            tree = self._parse_tree(path)
            aliases = self._ai_service_aliases(tree)

            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                    continue
                if node.func.attr != "generate":
                    continue
                if self._is_ai_service_source(node.func.value, aliases):
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

            tree = self._parse_tree(path)
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

    def test_production_callers_do_not_dynamically_generate_from_ai_service(self):
        violations = []
        for path in sorted(self._SOURCE_ROOT.rglob("*.py")):
            relative_path = path.relative_to(self._SOURCE_ROOT.parent.parent)
            if relative_path in self._EXCLUDED_FILES:
                continue
            if any(part in self._EXCLUDED_PARTS for part in path.parts):
                continue

            tree = self._parse_tree(path)
            aliases = self._ai_service_aliases(tree)
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                    continue
                if node.func.id != "getattr" or len(node.args) < 2:
                    continue
                receiver = node.args[0]
                attribute = node.args[1]
                if not self._is_ai_service_source(receiver, aliases):
                    continue
                if isinstance(attribute, ast.Constant) and attribute.value == "generate":
                    violations.append(f"{path}:{node.lineno} dynamically probes for generate with getattr()")

        self.assertEqual(
            violations,
            [],
            "Production callers must not bypass role routing by dynamically resolving AIService.generate().\n"
            + "\n".join(violations),
        )

    def test_production_alias_audit_detects_transitive_ai_service_aliases(self):
        source = ast.parse(
            """
service = self.ai_service
provider = service
provider.generate(request)
"""
        )
        aliases = self._ai_service_aliases(source)
        self.assertEqual(aliases, {"service", "provider"})
        call = next(
            node for node in ast.walk(source)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        )
        self.assertTrue(self._is_ai_service_source(call.func.value, aliases))


if __name__ == "__main__":
    unittest.main(verbosity=2)
