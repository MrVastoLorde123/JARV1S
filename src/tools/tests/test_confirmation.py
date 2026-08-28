from __future__ import annotations

import unittest

from src.tools.confirmation import (
    AutoApproveConfirmationProvider,
    AutoDenyConfirmationProvider,
    ConfirmationResponse,
)
from src.tools.errors import ToolLayerError
from src.tools.models import ToolRequest
from src.tools.tests.support import make_definition


class TestConfirmationResponse(unittest.TestCase):
    def test_valid_response(self) -> None:
        response = ConfirmationResponse(approved=True)
        self.assertIsNone(response.reason)

    def test_rejects_non_bool_approved(self) -> None:
        with self.assertRaises(ToolLayerError):
            ConfirmationResponse(approved="yes")  # type: ignore[arg-type]

    def test_rejects_non_string_reason(self) -> None:
        with self.assertRaises(ToolLayerError):
            ConfirmationResponse(approved=True, reason=123)  # type: ignore[arg-type]


class TestAutoDenyConfirmationProvider(unittest.TestCase):
    def test_always_denies(self) -> None:
        provider = AutoDenyConfirmationProvider()
        definition = make_definition(name="delete_everything")
        request = ToolRequest(tool_name="delete_everything")

        response = provider.confirm(definition, request)

        self.assertFalse(response.approved)
        self.assertIsNotNone(response.reason)


class TestAutoApproveConfirmationProvider(unittest.TestCase):
    def test_always_approves(self) -> None:
        provider = AutoApproveConfirmationProvider()
        definition = make_definition(name="delete_everything")
        request = ToolRequest(tool_name="delete_everything")

        response = provider.confirm(definition, request)

        self.assertTrue(response.approved)


if __name__ == "__main__":
    unittest.main()
