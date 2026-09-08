import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType

from src.core.interface_backend import (
    InterfaceBackendError,
    InterfaceOperation,
    InterfaceRequest,
    InterfaceResponse,
    InterfaceResponseStatus,
    SelfImprovementInterfaceBackend,
)


class _Port:
    def __init__(self, response=None):
        self.requests = []
        self.response = response

    def dispatch(self, request):
        self.requests.append(request)
        return self.response or InterfaceResponse(
            request_id=request.request_id,
            operation=request.operation,
            status=InterfaceResponseStatus.ACCEPTED,
            payload={"ok": True, "nested": [{"x": 1}]},
            metadata={"source": "test"},
        )


class M25_1InterfaceBackendTests(unittest.TestCase):
    def _request(self, **kwargs):
        values = {
            "request_id": "interface-request-251",
            "session_id": "session-251",
            "actor_id": "user-251",
            "operation": InterfaceOperation.STATUS,
            "payload": {"query": {"component": "self-improvement"}},
            "metadata": {"client": "test"},
        }
        values.update(kwargs)
        return InterfaceRequest(**values)

    def test_request_is_typed_and_immutable(self):
        request = self._request(payload={"steps": ["one", {"x": 1}]})
        self.assertIsInstance(request.payload, MappingProxyType)
        self.assertIsInstance(request.payload["steps"], tuple)
        self.assertIsInstance(request.payload["steps"][1], MappingProxyType)
        with self.assertRaises(TypeError):
            request.payload["x"] = 1
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            request.request_id = "changed"

    def test_required_request_metadata_is_enforced(self):
        for field in ("request_id", "session_id", "actor_id"):
            values = {
                "request_id": "request-251",
                "session_id": "session-251",
                "actor_id": "actor-251",
                "operation": InterfaceOperation.STATUS,
                "payload": {},
                "metadata": {},
            }
            values[field] = " "
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    InterfaceRequest(**values)

    def test_operation_must_be_typed(self):
        with self.assertRaises(TypeError):
            self._request(operation="STATUS")
        self.assertEqual({item.value for item in InterfaceOperation}, {
            "PROPOSE", "EVALUATE", "DECIDE", "APPLY", "VERIFY", "ROLLBACK", "STATUS"
        })

    def test_payload_and_metadata_must_be_mappings(self):
        with self.assertRaises(TypeError):
            self._request(payload=[1])
        with self.assertRaises(TypeError):
            self._request(metadata=[1])

    def test_response_is_typed_and_immutable(self):
        response = InterfaceResponse(
            request_id="request-251",
            operation=InterfaceOperation.STATUS,
            status=InterfaceResponseStatus.ACCEPTED,
            payload={"result": ["ok", {"depth": 1}]},
            metadata={"trace": {"step": 1}},
        )
        self.assertIsInstance(response.payload, MappingProxyType)
        self.assertIsInstance(response.payload["result"], tuple)
        self.assertIsInstance(response.payload["result"][1], MappingProxyType)
        with self.assertRaises(TypeError):
            response.payload["x"] = 1
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            response.status = InterfaceResponseStatus.FAILED

    def test_response_status_must_be_typed(self):
        with self.assertRaises(TypeError):
            InterfaceResponse(
                request_id="r",
                operation=InterfaceOperation.STATUS,
                status="ACCEPTED",
                payload={},
                metadata={},
            )
        self.assertEqual({item.value for item in InterfaceResponseStatus}, {"ACCEPTED", "REJECTED", "FAILED"})

    def test_backend_requires_injected_orchestration_port(self):
        with self.assertRaises(TypeError):
            SelfImprovementInterfaceBackend(None)
        with self.assertRaises(TypeError):
            SelfImprovementInterfaceBackend(object())

    def test_backend_routes_request_to_injected_port(self):
        port = _Port()
        backend = SelfImprovementInterfaceBackend(port)
        request = self._request()
        response = backend.handle(request)
        self.assertEqual(port.requests, [request])
        self.assertEqual(response.request_id, request.request_id)
        self.assertIs(response.operation, request.operation)
        self.assertEqual(response.status, InterfaceResponseStatus.ACCEPTED)

    def test_exact_request_type_is_required(self):
        port = _Port()
        with self.assertRaises(TypeError):
            SelfImprovementInterfaceBackend(port).handle(object())

    def test_port_must_return_exact_response_type(self):
        port = _Port(response=object())
        with self.assertRaises(TypeError):
            SelfImprovementInterfaceBackend(port).handle(self._request())

    def test_response_request_identity_must_match(self):
        port = _Port(response=InterfaceResponse(
            request_id="other",
            operation=InterfaceOperation.STATUS,
            status=InterfaceResponseStatus.ACCEPTED,
            payload={},
            metadata={},
        ))
        with self.assertRaises(InterfaceBackendError):
            SelfImprovementInterfaceBackend(port).handle(self._request())

    def test_response_operation_identity_must_match(self):
        port = _Port(response=InterfaceResponse(
            request_id="interface-request-251",
            operation=InterfaceOperation.VERIFY,
            status=InterfaceResponseStatus.ACCEPTED,
            payload={},
            metadata={},
        ))
        with self.assertRaises(InterfaceBackendError):
            SelfImprovementInterfaceBackend(port).handle(self._request())

    def test_backend_authority_walls_are_closed(self):
        backend = SelfImprovementInterfaceBackend(_Port())
        for name in (
            "authorizes_execution", "executes_capability", "mutates_state",
            "persists_state", "establishes_truth", "establishes_certainty", "is_ai_provider"
        ):
            self.assertFalse(getattr(backend, name))

    def test_response_payload_is_recursively_frozen_by_contract(self):
        port = _Port()
        response = SelfImprovementInterfaceBackend(port).handle(self._request())
        self.assertIsInstance(response.payload["nested"], tuple)
        self.assertIsInstance(response.payload["nested"][0], MappingProxyType)
        with self.assertRaises(TypeError):
            response.payload["nested"][0]["y"] = 2


if __name__ == "__main__":
    unittest.main()
