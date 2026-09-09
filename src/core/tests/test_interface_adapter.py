import unittest
from types import MappingProxyType

from src.core.interface_adapter import InterfaceAdapter, InterfaceAdapterError
from src.core.interface_backend import (
    InterfaceOperation,
    InterfaceRequest,
    InterfaceResponse,
    InterfaceResponseStatus,
)


class _Backend:
    def __init__(self, response=None):
        self.request = None
        self.response = response

    def handle(self, request):
        self.request = request
        return self.response or InterfaceResponse(
            request_id=request.request_id,
            operation=request.operation,
            status=InterfaceResponseStatus.ACCEPTED,
            payload={"result": {"nested": [1, 2]}},
            metadata={"stage": "candidate"},
        )


class M25_5InterfaceAdapterTests(unittest.TestCase):
    def _envelope(self, operation="PROPOSE"):
        return {
            "request_id": "request-255",
            "session_id": "session-255",
            "actor_id": "actor-255",
            "operation": operation,
            "payload": {"value": 1},
            "metadata": {"channel": "test"},
        }

    def test_adapter_requires_backend(self):
        with self.assertRaises(TypeError):
            InterfaceAdapter(None)
        with self.assertRaises(TypeError):
            InterfaceAdapter(object())

    def test_to_request_translates_external_operation_string(self):
        backend = _Backend()
        adapter = InterfaceAdapter(backend)
        request = adapter.to_request(self._envelope())
        self.assertIsInstance(request, InterfaceRequest)
        self.assertIs(request.operation, InterfaceOperation.PROPOSE)
        self.assertEqual(request.request_id, "request-255")

    def test_to_request_rejects_missing_required_fields(self):
        adapter = InterfaceAdapter(_Backend())
        envelope = self._envelope()
        del envelope["actor_id"]
        with self.assertRaises(InterfaceAdapterError):
            adapter.to_request(envelope)

    def test_to_request_rejects_unknown_operation(self):
        adapter = InterfaceAdapter(_Backend())
        with self.assertRaises(InterfaceAdapterError):
            adapter.to_request(self._envelope("NOT_REAL"))

    def test_to_request_rejects_non_mapping(self):
        adapter = InterfaceAdapter(_Backend())
        with self.assertRaises(TypeError):
            adapter.to_request(object())

    def test_canonical_operation_is_accepted(self):
        adapter = InterfaceAdapter(_Backend())
        envelope = self._envelope(InterfaceOperation.EVALUATE)
        request = adapter.to_request(envelope)
        self.assertIs(request.operation, InterfaceOperation.EVALUATE)

    def test_handle_delegates_canonical_request(self):
        backend = _Backend()
        adapter = InterfaceAdapter(backend)
        response = adapter.handle(self._envelope())
        self.assertEqual(backend.request.request_id, "request-255")
        self.assertIs(backend.request.operation, InterfaceOperation.PROPOSE)
        self.assertEqual(response["status"], "ACCEPTED")

    def test_from_response_serializes_enums_to_external_values(self):
        adapter = InterfaceAdapter(_Backend())
        request = InterfaceRequest(
            "request-255",
            "session-255",
            "actor-255",
            InterfaceOperation.APPLY,
            {},
            {},
        )
        response = InterfaceResponse(
            request_id=request.request_id,
            operation=request.operation,
            status=InterfaceResponseStatus.REJECTED,
            payload={"reason": "bounded"},
            metadata={"stage": "application"},
        )
        external = adapter.from_response(response)
        self.assertIsInstance(external, MappingProxyType)
        self.assertEqual(external["operation"], "APPLY")
        self.assertEqual(external["status"], "REJECTED")

    def test_from_response_is_recursive_and_immutable(self):
        adapter = InterfaceAdapter(_Backend())
        response = InterfaceResponse(
            request_id="request-255",
            operation=InterfaceOperation.PROPOSE,
            status=InterfaceResponseStatus.ACCEPTED,
            payload={"nested": [{"x": 1}]},
            metadata={"nested": {"flag": True}},
        )
        external = adapter.from_response(response)
        self.assertIsInstance(external["payload"], MappingProxyType)
        self.assertIsInstance(external["payload"]["nested"], tuple)
        self.assertIsInstance(external["metadata"], MappingProxyType)
        with self.assertRaises(TypeError):
            external["status"] = "FAILED"
        with self.assertRaises(TypeError):
            external["payload"]["nested"][0]["x"] = 2

    def test_adapter_does_not_mutate_caller_envelope(self):
        backend = _Backend()
        adapter = InterfaceAdapter(backend)
        envelope = self._envelope()
        original = dict(envelope)
        adapter.handle(envelope)
        self.assertEqual(envelope, original)

    def test_response_identity_and_operation_are_backend_owned(self):
        response = InterfaceResponse(
            request_id="request-255",
            operation=InterfaceOperation.VERIFY,
            status=InterfaceResponseStatus.FAILED,
            payload={},
            metadata={},
        )
        adapter = InterfaceAdapter(_Backend(response))
        external = adapter.handle(self._envelope("VERIFY"))
        self.assertEqual(external["request_id"], "request-255")
        self.assertEqual(external["operation"], "VERIFY")
        self.assertEqual(external["status"], "FAILED")

    def test_adapter_boundary_has_no_authority_or_execution_powers(self):
        adapter = InterfaceAdapter(_Backend())
        self.assertFalse(adapter.authorizes_execution)
        self.assertFalse(adapter.executes_capability)
        self.assertFalse(adapter.mutates_state)
        self.assertFalse(adapter.persists_state)
        self.assertFalse(adapter.establishes_truth)
        self.assertFalse(adapter.establishes_certainty)
        self.assertFalse(adapter.is_ai_provider)

    def test_payload_and_metadata_must_remain_backend_contract_types(self):
        adapter = InterfaceAdapter(_Backend())
        envelope = self._envelope()
        envelope["payload"] = []
        with self.assertRaises(TypeError):
            adapter.to_request(envelope)
        envelope = self._envelope()
        envelope["metadata"] = []
        with self.assertRaises(TypeError):
            adapter.to_request(envelope)

    def test_response_must_be_exact_canonical_type(self):
        class BadBackend:
            def handle(self, request):
                return {"status": "ACCEPTED"}
        adapter = InterfaceAdapter(BadBackend())
        with self.assertRaises(TypeError):
            adapter.handle(self._envelope())
