import unittest

from src.core.capability_catalog import CapabilityCatalog
from src.tools.bootstrap import build_workspace_tool_stack
from src.tools.models import ToolDefinition


class CapabilityCatalogTests(unittest.TestCase):
    def test_lists_deterministic_tool_definitions(self):
        stack = build_workspace_tool_stack(".")
        catalog = CapabilityCatalog(stack.gate)

        definitions = catalog.list()

        self.assertTrue(definitions)
        self.assertTrue(all(isinstance(item, ToolDefinition) for item in definitions))
        self.assertEqual(
            [item.name for item in definitions],
            sorted(item.name for item in definitions),
        )

    def test_find_is_case_and_whitespace_insensitive(self):
        stack = build_workspace_tool_stack(".")
        catalog = CapabilityCatalog(stack.gate)

        definition = catalog.find("  READ_FILE ")

        self.assertIsNotNone(definition)
        self.assertEqual("read_file", definition.name)

    def test_missing_capability_returns_none(self):
        stack = build_workspace_tool_stack(".")
        catalog = CapabilityCatalog(stack.gate)

        self.assertIsNone(catalog.find("does_not_exist"))

    def test_catalog_is_read_only(self):
        stack = build_workspace_tool_stack(".")
        catalog = CapabilityCatalog(stack.gate)
        before = tuple(item.name for item in catalog.list())

        catalog.list()

        after = tuple(item.name for item in catalog.list())
        self.assertEqual(before, after)
        self.assertEqual(len(stack.registry), len(before))


if __name__ == "__main__":
    unittest.main()
