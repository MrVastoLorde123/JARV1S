from __future__ import annotations

import unittest

from src.tools.errors import InvalidRequestError, InvalidResultError, UnknownToolError
from src.tools.models import ToolRequest
from src.tools.registry import ToolRegistry
from src.tools.service import ToolService
from src.tools.tests.support import (
    EchoHandler,
    MalformedResultHandler,
    RaisingHandler,
    WrongToolNameHandler,
)


class ServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = ToolRegistry()
        self.service = ToolService(self.registry)


class TestSuccessfulExecution(ServiceTestCase):
    def test_successful_invocation_returns_success_result(self) -> None:
        self.registry.register(EchoHandler(name="echo"))
        request = ToolRequest(tool_name="echo", arguments={"text": "hi"})

        result = self.service.invoke(request)

        self.assertTrue(result.success)
        self.assertEqual(result.tool_name, "echo")
        self.assertEqual(result.content, {"text": "hi"})
        self.assertIsNone(result.error)

    def test_invocation_id_is_propagated(self) -> None:
        self.registry.register(EchoHandler(name="echo"))
        request = ToolRequest(tool_name="echo", invocation_id="req-1")

        result = self.service.invoke(request)

        self.assertEqual(result.invocation_id, "req-1")

    def test_tool_name_lookup_is_case_insensitive(self) -> None:
        self.registry.register(EchoHandler(name="Echo"))
        request = ToolRequest(tool_name="echo")

        result = self.service.invoke(request)

        self.assertTrue(result.success)


class TestInvalidRequests(ServiceTestCase):
    def test_non_tool_request_object_raises(self) -> None:
        with self.assertRaises(InvalidRequestError):
            self.service.invoke({"tool_name": "echo"})  # type: ignore[arg-type]

    def test_none_raises(self) -> None:
        with self.assertRaises(InvalidRequestError):
            self.service.invoke(None)  # type: ignore[arg-type]


class TestUnknownTool(ServiceTestCase):
    def test_unknown_tool_raises(self) -> None:
        request = ToolRequest(tool_name="does-not-exist")
        with self.assertRaises(UnknownToolError):
            self.service.invoke(request)


class TestHandlerExecutionFailure(ServiceTestCase):
    def test_handler_exception_becomes_failed_result(self) -> None:
        self.registry.register(RaisingHandler(name="boom"))
        request = ToolRequest(tool_name="boom")

        result = self.service.invoke(request)

        self.assertFalse(result.success)
        self.assertEqual(result.tool_name, "boom")
        self.assertIsNotNone(result.error)
        self.assertEqual(result.error.code, "tool_execution_error")
        self.assertIn("simulated tool failure", result.error.message)

    def test_handler_exception_does_not_propagate(self) -> None:
        self.registry.register(RaisingHandler(name="boom"))
        request = ToolRequest(tool_name="boom")

        # Should not raise.
        self.service.invoke(request)


class TestMalformedHandlerResults(ServiceTestCase):
    def test_non_tool_result_return_raises(self) -> None:
        self.registry.register(MalformedResultHandler(name="malformed"))
        request = ToolRequest(tool_name="malformed")

        with self.assertRaises(InvalidResultError):
            self.service.invoke(request)

    def test_result_for_wrong_tool_raises(self) -> None:
        self.registry.register(WrongToolNameHandler(name="impersonator"))
        request = ToolRequest(tool_name="impersonator")

        with self.assertRaises(InvalidResultError):
            self.service.invoke(request)


class TestProviderIsolation(unittest.TestCase):
    """The service must not require any external service to function."""

    def test_service_only_depends_on_registry(self) -> None:
        # Constructing a ToolService should require nothing but a
        # ToolRegistry -- no database handle, no network client, no
        # AI/model client.
        registry = ToolRegistry()
        service = ToolService(registry)
        registry.register(EchoHandler(name="echo"))

        result = service.invoke(ToolRequest(tool_name="echo", arguments={"a": 1}))
        self.assertTrue(result.success)

    def test_multiple_services_share_no_hidden_state(self) -> None:
        registry_a = ToolRegistry()
        registry_a.register(EchoHandler(name="echo"))
        registry_b = ToolRegistry()

        service_a = ToolService(registry_a)
        service_b = ToolService(registry_b)

        self.assertTrue(service_a.invoke(ToolRequest(tool_name="echo")).success)
        with self.assertRaises(UnknownToolError):
            service_b.invoke(ToolRequest(tool_name="echo"))


if __name__ == "__main__":
    unittest.main()
