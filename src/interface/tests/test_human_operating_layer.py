import unittest

from src.interface.boundary import InterfaceBoundary, InterfaceChannel, InterfaceResponse
from src.interface.human_operating_layer import HumanOperatingLayer, HumanTurn


class FakeRuntime:
    """Minimal shape used to verify the layer delegates rather than interprets."""

    def __init__(self):
        self.received = []

    def process(self, request):
        self.received.append(request)
        return request

    def respond(self, result):
        return InterfaceResponse(request_id=result.request_id, content=f"echo: {result.content}")


class HumanOperatingLayerTests(unittest.TestCase):
    def setUp(self):
        self.runtime = FakeRuntime()
        self.operator = HumanOperatingLayer.__new__(HumanOperatingLayer)
        self.operator.runtime = self.runtime
        self.operator.boundary = InterfaceBoundary()
        self.operator.channel = InterfaceChannel.TEXT
        self.operator._session_id = "test-session"
        self.operator._request_id_factory = iter(["request-1", "request-2"]).__next__

    def test_plain_text_becomes_runtime_request(self):
        result = self.operator.handle("hello jarvis")
        self.assertIsInstance(result, HumanTurn)
        self.assertEqual(result.response, "echo: hello jarvis")
        self.assertEqual(result.session_id, "test-session")
        self.assertEqual(len(self.runtime.received), 1)
        request = self.runtime.received[0]
        self.assertEqual(request.content, "hello jarvis")
        self.assertEqual(request.session_id, "test-session")
        self.assertFalse(request.to_dict()["authority_granted"])

    def test_commands_do_not_reach_runtime(self):
        self.assertEqual(self.operator.handle(":session"), "Active session: test-session")
        self.assertEqual(self.operator.handle(":help").splitlines()[0], "Commands:")
        self.assertEqual(self.operator.handle(":unknown"), "Unknown command: :unknown. Use :help.")
        self.assertEqual(len(self.runtime.received), 0)

    def test_new_session_changes_session_identity_only(self):
        old = self.operator.session_id
        result = self.operator.handle(":new")
        self.assertTrue(result.startswith("Started new session: local-"))
        self.assertNotEqual(old, self.operator.session_id)
        self.assertEqual(len(self.runtime.received), 0)

    def test_quit_is_local_control(self):
        self.assertEqual(self.operator.handle(":quit"), "__QUIT__")
        self.assertEqual(len(self.runtime.received), 0)

    def test_empty_input_is_not_sent(self):
        self.assertEqual(self.operator.handle("   "), "Please enter a request.")
        self.assertEqual(len(self.runtime.received), 0)

    def test_run_keeps_accepting_normal_requests_until_quit(self):
        inputs = iter(["first", ":session", "second", ":quit"])
        outputs = []
        self.operator.run(input_fn=lambda prompt: next(inputs), output_fn=outputs.append)
        self.assertEqual(len(self.runtime.received), 2)
        self.assertEqual(self.runtime.received[0].session_id, "test-session")
        self.assertEqual(self.runtime.received[1].session_id, "test-session")
        self.assertTrue(any("echo: first" in output for output in outputs))
        self.assertTrue(any("echo: second" in output for output in outputs))
        self.assertTrue(any("Active session: test-session" in output for output in outputs))
        self.assertTrue(outputs[-1].endswith("session ended."))


if __name__ == "__main__":
    unittest.main(verbosity=2)
