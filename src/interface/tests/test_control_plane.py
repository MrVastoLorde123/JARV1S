import json
import threading
import unittest
from urllib.request import Request, urlopen

from src.core.interface_backend import InterfaceOperation, InterfaceResponseStatus
from src.core.runtime_activity_stream import RuntimeActivityStream
from src.interface.control_host import local_model_projection
from src.interface.control_plane import ControlPlaneActivityRecorder, ControlPlaneSnapshotBuilder
from src.interface.http_control_plane import ControlPlaneHTTPConfig, create_control_plane_server


class ControlPlaneSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.stream = RuntimeActivityStream()
        recorder = ControlPlaneActivityRecorder(self.stream)
        recorder.record_request(request_id="req-1", session_id="desktop")
        recorder.record_response(
            request_id="req-1",
            session_id="desktop",
            status=InterfaceResponseStatus.ACCEPTED,
            metadata={"artifact_type": "STATUS"},
        )
        self.builder = ControlPlaneSnapshotBuilder(
            world_supplier=lambda: {"landscape": "SURINAME", "authority_granted": False},
            activity_stream=self.stream,
            task_supplier=lambda: {"state": "IDLE", "progress": 0},
            agents_supplier=lambda: ({"id": "coding", "state": "READY"},),
            approvals_supplier=lambda: (),
            tools_supplier=lambda: (),
            model_supplier=lambda: {"provider": "local", "state": "IDLE"},
            blockers_supplier=lambda: (),
            verification_supplier=lambda: {"state": "NOT_APPLICABLE", "evidence": []},
            clock=lambda: "2026-09-14T00:00:00Z",
        )

    def test_snapshot_is_single_runtime_owned_shape(self):
        snapshot = self.builder.build()
        payload = snapshot.to_dict()
        self.assertEqual(payload["schema"], "control-plane.v1")
        self.assertEqual(payload["runtime"]["world"]["landscape"], "SURINAME")
        self.assertEqual(payload["task"]["state"], "IDLE")
        self.assertEqual(payload["agents"][0]["id"], "coding")
        self.assertEqual(payload["model"]["provider"], "local")
        self.assertEqual(payload["events"][0]["kind"], "REQUEST_RECEIVED")
        self.assertEqual(payload["events"][1]["kind"], "RESPONSE_EMITTED")
        self.assertEqual(payload["cursor"], 2)
        self.assertTrue(payload["runtime"]["read_only"])
        json.loads(snapshot.to_json())

    def test_cursor_filters_already_consumed_events(self):
        snapshot = self.builder.build(after_cursor=1)
        self.assertEqual([event["sequence"] for event in snapshot.events], [2])
        self.assertEqual(snapshot.cursor, 2)

    def test_default_clock_produces_nonempty_timestamp(self):
        builder = ControlPlaneSnapshotBuilder(
            world_supplier=lambda: {"landscape": "TEST"},
            activity_stream=self.stream,
        )
        snapshot = builder.build()
        self.assertTrue(snapshot.generated_at)

    def test_invalid_supplier_shape_is_rejected(self):
        builder = ControlPlaneSnapshotBuilder(
            world_supplier=lambda: [],
            activity_stream=self.stream,
            clock=lambda: "now",
        )
        with self.assertRaisesRegex(Exception, "world supplier"):
            builder.build()

    def test_activity_recorder_is_sequential_and_runtime_owned(self):
        stream = RuntimeActivityStream()
        recorder = ControlPlaneActivityRecorder(stream)
        first = recorder.record_request(request_id="req-a", session_id="desktop")
        second = recorder.record_response(
            request_id="req-a",
            session_id="desktop",
            status=InterfaceResponseStatus.FAILED,
        )
        self.assertEqual(first.sequence, 1)
        self.assertEqual(second.sequence, 2)
        self.assertEqual(second.kind.value, "REQUEST_FAILED")
        self.assertEqual(second.operation, InterfaceOperation.PROPOSE)

    def test_agent_and_tool_records_are_preserved_as_runtime_projections(self):
        stream = RuntimeActivityStream()
        builder = ControlPlaneSnapshotBuilder(
            world_supplier=lambda: {"landscape": "TEST"},
            activity_stream=stream,
            agents_supplier=lambda: (
                {
                    "agent_id": "coding-1",
                    "status": "EXECUTING",
                    "authority_granted": False,
                },
            ),
            tools_supplier=lambda: (
                {
                    "name": "read_file",
                    "risk_level": "low",
                    "requires_confirmation": False,
                },
                {
                    "name": "write_file",
                    "risk_level": "high",
                    "requires_confirmation": True,
                },
            ),
            clock=lambda: "2026-09-14T00:00:00Z",
        )
        payload = builder.build().to_dict()
        self.assertEqual(payload["agents"][0]["agent_id"], "coding-1")
        self.assertFalse(payload["agents"][0]["authority_granted"])
        self.assertEqual([tool["name"] for tool in payload["tools"]], ["read_file", "write_file"])
        self.assertEqual(payload["tools"][1]["risk_level"], "high")
        self.assertTrue(payload["tools"][1]["requires_confirmation"])

    def test_local_model_projection_reports_unavailable_when_server_is_unreachable(self):
        def raising_opener(*_args, **_kwargs):
            raise OSError("server offline")

        projection = local_model_projection(
            base_url="http://127.0.0.1:8080",
            model_id="qwen3-4b-local",
            opener=raising_opener,
        )
        self.assertEqual(projection["state"], "UNAVAILABLE")
        self.assertEqual(projection["evidence"], "local_server_models_unreachable")

    def test_local_model_projection_reports_available_from_observed_models(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return b'{"data":[{"id":"qwen3-4b-local"}]}'

        projection = local_model_projection(
            base_url="http://127.0.0.1:8080",
            model_id="qwen3-4b-local",
            opener=lambda *_args, **_kwargs: FakeResponse(),
        )
        self.assertEqual(projection["state"], "AVAILABLE")
        self.assertEqual(projection["observed_model_ids"], ("qwen3-4b-local",))

    def test_local_model_projection_reports_mismatch_when_one_other_model_is_observed(self):
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return b'{"data":[{"id":"different-model"}]}'

        projection = local_model_projection(
            base_url="http://127.0.0.1:8080",
            model_id="qwen3-4b-local",
            opener=lambda *_args, **_kwargs: FakeResponse(),
        )
        self.assertEqual(projection["state"], "MODEL_MISMATCH")


class ControlPlaneHTTPTests(unittest.TestCase):
    def setUp(self):
        stream = RuntimeActivityStream()
        self.builder = ControlPlaneSnapshotBuilder(
            world_supplier=lambda: {"landscape": "TEST"},
            activity_stream=stream,
            clock=lambda: "2026-09-14T00:00:00Z",
        )
        self.server = create_control_plane_server(
            self.builder,
            config=ControlPlaneHTTPConfig(host="127.0.0.1", port=0, path="/api/control-plane"),
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def test_default_transport_port_does_not_conflict_with_command(self):
        self.assertEqual(ControlPlaneHTTPConfig().port, 8768)

    def test_http_endpoint_exposes_read_only_snapshot(self):
        request = Request(f"http://127.0.0.1:{self.server.server_port}/api/control-plane", headers={"Accept": "application/json"})
        with urlopen(request, timeout=2) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            payload = json.loads(response.read().decode("utf-8"))
        self.assertEqual(payload["schema"], "control-plane.v1")
        self.assertTrue(payload["runtime"]["read_only"])
        self.assertEqual(payload["runtime"]["world"]["landscape"], "TEST")

    def test_cursor_query_is_forwarded_into_snapshot(self):
        stream = RuntimeActivityStream()
        recorder = ControlPlaneActivityRecorder(stream)
        recorder.record_request(request_id="req-1", session_id="desktop")
        builder = ControlPlaneSnapshotBuilder(
            world_supplier=lambda: {"landscape": "TEST"},
            activity_stream=stream,
            clock=lambda: "now",
        )
        server = create_control_plane_server(
            builder,
            config=ControlPlaneHTTPConfig(host="127.0.0.1", port=0, path="/api/control-plane"),
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            request = Request(
                f"http://127.0.0.1:{server.server_port}/api/control-plane?after_cursor=1",
                headers={"Accept": "application/json"},
            )
            with urlopen(request, timeout=2) as response:
                payload = json.loads(response.read().decode("utf-8"))
            self.assertEqual(payload["events"], [])
            self.assertEqual(payload["metadata"]["after_cursor"], 1)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_unknown_route_is_not_a_control_plane_endpoint(self):
        request = Request(f"http://127.0.0.1:{self.server.server_port}/api/control-plane/other", headers={"Accept": "application/json"})
        with self.assertRaises(Exception):
            urlopen(request, timeout=2)


if __name__ == "__main__":
    unittest.main()
