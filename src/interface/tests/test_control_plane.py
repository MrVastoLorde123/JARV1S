import json
import threading
import unittest
from urllib.request import Request, urlopen

from src.core.interface_backend import InterfaceOperation, InterfaceRequest, InterfaceResponse, InterfaceResponseStatus
from src.core.runtime_activity_stream import InterfaceRuntimeActivityRecorder, RuntimeActivityStream
from src.interface.control_plane import ControlPlaneSnapshotBuilder
from src.interface.http_control_plane import ControlPlaneHTTPConfig, create_control_plane_server


class ControlPlaneSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.stream = RuntimeActivityStream()
        recorder = InterfaceRuntimeActivityRecorder(self.stream)
        request = InterfaceRequest(
            request_id="req-1",
            session_id="desktop",
            actor_id="user",
            operation=InterfaceOperation.STATUS,
            payload={},
            metadata={},
        )
        recorder.record_request(request)
        recorder.record_response(
            request,
            InterfaceResponse(
                request_id="req-1",
                operation=InterfaceOperation.STATUS,
                status=InterfaceResponseStatus.ACCEPTED,
                payload={"ok": True},
                metadata={"artifact_type": "STATUS"},
            ),
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
        json.loads(snapshot.to_json())

    def test_cursor_filters_already_consumed_events(self):
        snapshot = self.builder.build(after_cursor=1)
        self.assertEqual([event["sequence"] for event in snapshot.events], [2])
        self.assertEqual(snapshot.cursor, 2)

    def test_invalid_supplier_shape_is_rejected(self):
        builder = ControlPlaneSnapshotBuilder(
            world_supplier=lambda: [],
            activity_stream=self.stream,
            clock=lambda: "now",
        )
        with self.assertRaisesRegex(Exception, "world supplier"):
            builder.build()


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

    def test_http_endpoint_exposes_read_only_snapshot(self):
        request = Request(f"http://127.0.0.1:{self.server.server_port}/api/control-plane", headers={"Accept": "application/json"})
        with urlopen(request, timeout=2) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            payload = json.loads(response.read().decode("utf-8"))
        self.assertEqual(payload["schema"], "control-plane.v1")
        self.assertTrue(payload["runtime"]["read_only"])
        self.assertEqual(payload["runtime"]["world"]["landscape"], "TEST")

    def test_unknown_route_is_not_a_control_plane_endpoint(self):
        request = Request(f"http://127.0.0.1:{self.server.server_port}/api/control-plane/other", headers={"Accept": "application/json"})
        with self.assertRaises(Exception):
            urlopen(request, timeout=2)


if __name__ == "__main__":
    unittest.main()
