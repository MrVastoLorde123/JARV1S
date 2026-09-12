import http.client
import json
import socket
import threading
import unittest

from src.interface.http_capabilities import CapabilityHTTPConfig, create_capability_server
from src.tools.models import RiskLevel, ToolDefinition


class _FakeCapabilitySource:
    def list_definitions(self):
        return (
            ToolDefinition(
                name="run_test",
                description="Run constrained verification",
                version="1.0.0",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                risk_level=RiskLevel.MEDIUM,
                requires_confirmation=False,
                metadata={"category": "verification"},
            ),
        )


class M28_18CapabilityHTTPTests(unittest.TestCase):
    def test_catalog_is_read_only_and_reflects_backend_definition(self):
        probe = socket.socket()
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
        probe.close()

        server = create_capability_server(
            _FakeCapabilitySource(),
            config=CapabilityHTTPConfig(port=port),
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.shutdown)
        self.addCleanup(server.server_close)
        self.addCleanup(thread.join, 2.0)

        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
        connection.request("GET", "/api/capabilities")
        response = connection.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        connection.close()

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["schema"], "m28.capabilities.v1")
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["authority_granted"])
        self.assertFalse(payload["execution_requested"])
        self.assertEqual(payload["capabilities"][0]["name"], "run_test")
        self.assertEqual(payload["capabilities"][0]["risk_level"], "medium")


if __name__ == "__main__":
    unittest.main()
