from __future__ import annotations

import unittest

from src.tools.errors import DuplicateToolError, InvalidHandlerError, UnknownToolError
from src.tools.registry import ToolRegistry, normalize_name
from src.tools.tests.support import BadDefinitionHandler, EchoHandler, NotAHandler


class TestNormalizeName(unittest.TestCase):
    def test_normalizes(self) -> None:
        cases = [
            ("Echo", "echo"),
            ("  echo  ", "echo"),
            ("ECHO", "echo"),
            ("echo", "echo"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(normalize_name(raw), expected)


class TestRegister(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = ToolRegistry()

    def test_register_returns_definition(self) -> None:
        handler = EchoHandler()
        definition = self.registry.register(handler)
        self.assertEqual(definition.name, "echo")
        self.assertTrue(self.registry.has("echo"))

    def test_register_is_case_and_whitespace_insensitive(self) -> None:
        self.registry.register(EchoHandler(name="Read File"))
        self.assertTrue(self.registry.has("read file"))
        self.assertTrue(self.registry.has("READ FILE"))
        self.assertTrue(self.registry.has("  read file  "))
        self.assertIs(self.registry.get("Read File"), self.registry.get("read file"))

    def test_duplicate_registration_rejected_by_default(self) -> None:
        self.registry.register(EchoHandler(name="echo"))
        with self.assertRaises(DuplicateToolError):
            self.registry.register(EchoHandler(name="echo"))

    def test_duplicate_registration_allowed_with_replace(self) -> None:
        first = EchoHandler(name="echo")
        second = EchoHandler(name="echo")
        self.registry.register(first)
        self.registry.register(second, replace=True)
        self.assertIs(self.registry.get("echo"), second)

    def test_invalid_handler_missing_execute_rejected(self) -> None:
        with self.assertRaises(InvalidHandlerError):
            self.registry.register(NotAHandler())  # type: ignore[arg-type]

    def test_invalid_handler_bad_definition_type_rejected(self) -> None:
        with self.assertRaises(InvalidHandlerError):
            self.registry.register(BadDefinitionHandler())  # type: ignore[arg-type]

    def test_rejects_plain_objects(self) -> None:
        with self.assertRaises(InvalidHandlerError):
            self.registry.register(object())  # type: ignore[arg-type]


class TestGetAndHas(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = ToolRegistry()

    def test_get_unknown_tool_raises(self) -> None:
        with self.assertRaises(UnknownToolError):
            self.registry.get("does-not-exist")

    def test_has_returns_false_for_unknown(self) -> None:
        self.assertFalse(self.registry.has("does-not-exist"))

    def test_contains_operator(self) -> None:
        self.registry.register(EchoHandler(name="echo"))
        self.assertIn("echo", self.registry)
        self.assertIn("ECHO", self.registry)
        self.assertNotIn("missing", self.registry)


class TestUnregister(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = ToolRegistry()

    def test_unregister_removes_handler(self) -> None:
        self.registry.register(EchoHandler(name="echo"))
        self.registry.unregister("echo")
        self.assertFalse(self.registry.has("echo"))

    def test_unregister_unknown_raises(self) -> None:
        with self.assertRaises(UnknownToolError):
            self.registry.unregister("does-not-exist")


class TestListDefinitions(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = ToolRegistry()

    def test_deterministic_enumeration(self) -> None:
        self.registry.register(EchoHandler(name="zebra"))
        self.registry.register(EchoHandler(name="apple"))
        self.registry.register(EchoHandler(name="mango"))

        names = [d.name for d in self.registry.list_definitions()]
        self.assertEqual(names, ["apple", "mango", "zebra"])

    def test_enumeration_stable_across_calls(self) -> None:
        self.registry.register(EchoHandler(name="b"))
        self.registry.register(EchoHandler(name="a"))
        first = [d.name for d in self.registry.list_definitions()]
        second = [d.name for d in self.registry.list_definitions()]
        self.assertEqual(first, second)

    def test_empty_registry_returns_empty_list(self) -> None:
        self.assertEqual(self.registry.list_definitions(), [])

    def test_len(self) -> None:
        self.assertEqual(len(self.registry), 0)
        self.registry.register(EchoHandler(name="echo"))
        self.assertEqual(len(self.registry), 1)


if __name__ == "__main__":
    unittest.main()
