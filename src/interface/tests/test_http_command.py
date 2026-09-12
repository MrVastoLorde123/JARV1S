import http.client
import json
import socket
import threading
import unittest

from src.core.jarvis_runtime import JARVISRuntime
from src.interface.http_command import CommandHTTPConfig, create_command_server


class _FakeResponse:
    def __init__(self, content: str) -> None:
        self.content = content

    def to_json(self) -> str:
        return json.dumps(
            {
                "request_id": "command-test",
                "content": self.content,
                "metadata": {"test": True},
                "authority_granted": False,
                "authorization_granted": False,
                "execution_requested": False,
            }
        )


class M28_17CommandHTTPTests(unittest.TestCase):
    def _start_server(self):
        runtime = object.__new__(JARVISRuntime)
        calls = []

        def receive(**kwargs):
            calls.append(kwargs)
            return "result"

        def respond(result):
            self.assertEqual(result, "result")
            return _FakeResponse("JARVIS received the command")

        runtime.receive = receive
        runtime.respond = respond

        probe = socket.socket()
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
        probe.close()

        server = create_command_server(
            runtime,
            config=CommandHTTPConfig(port=port),
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.shutdown)
        self.addCleanup(server.server_close)
        self.addCleanup(thread.join, 2.0)
        return port, calls

    def test_post_command_reaches_canonical_runtime(self):
        port, calls = self._start_server()
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
        connection.request(
            "POST",
            "/api/command",
            body=json.dumps({"content": "hello JARVIS"}),
            headers={
                "Content-Type": "application/json",
                "X-JARVIS-Session-ID": "desktop-test",
                "X-JARVIS-Request-ID": "command-test",
            },
        )
        response = connection.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        connection.close()

        self.assertEqual(response.status, 200)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["request_id"], "command-test")
        self.assertEqual(calls[0]["content"], "hello JARVIS")
        self.assertEqual(calls[0]["session_id"], "desktop-test")
        self.assertEqual(calls[0]["channel"].value, "UI")
        self.assertEqual(payload["content"], "JARVIS received the command")
        self.assertFalse(payload["execution_requested"])

    def test_post_command_rejects_missing_content(self):
        port, calls = self._start_server()
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
        connection.request(
            "POST",
            "/api/command",
            body=json.dumps({}),
            headers={"Content-Type": "application/json"},
        )
        response = connection.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        connection.close()

        self.assertEqual(response.status, 400)
        self.assertEqual(calls, [])
        self.assertIn("content", payload["error"])


if __name__ == "__main__":
    unittest.main()
