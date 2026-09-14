import tempfile
import unittest
from pathlib import Path

from src.core.interface_backend import InterfaceResponseStatus
from src.core.runtime_activity_stream import RuntimeActivityStream
from src.interface.control_plane import ControlPlaneActivityRecorder
from src.interface.control_plane_store import ControlPlaneActivityStore


class ControlPlanePersistenceTests(unittest.TestCase):
    def test_activity_survives_recorder_restart_with_monotonic_cursor(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "jarvis.db"

            first_stream = RuntimeActivityStream()
            first_store = ControlPlaneActivityStore(database_path)
            first_recorder = ControlPlaneActivityRecorder(
                first_stream,
                durable_store=first_store,
            )
            first_recorder.record_request(request_id="req-1", session_id="desktop")
            first_recorder.record_response(
                request_id="req-1",
                session_id="desktop",
                status=InterfaceResponseStatus.ACCEPTED,
                metadata={
                    "route": "CODING_AGENT",
                    "stage": "CONFIRMATION",
                    "task_id": "task-1",
                    "rationale": "private reasoning must stay absent",
                },
            )

            restarted_stream = RuntimeActivityStream()
            restarted_store = ControlPlaneActivityStore(database_path)
            restarted_recorder = ControlPlaneActivityRecorder(
                restarted_stream,
                durable_store=restarted_store,
            )

            restored = restarted_stream.snapshot()
            self.assertEqual([event.sequence for event in restored], [1, 2])
            self.assertEqual(restored[1].metadata["task_id"], "task-1")
            self.assertNotIn("rationale", restored[1].metadata)

            next_event = restarted_recorder.record_request(
                request_id="req-2",
                session_id="desktop",
            )
            self.assertEqual(next_event.sequence, 3)
            self.assertEqual(next_event.event_id, "control-event-3")

            loaded = restarted_store.load_events()
            self.assertEqual([event.sequence for event in loaded], [1, 2, 3])

    def test_empty_store_does_not_change_existing_in_memory_semantics(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            stream = RuntimeActivityStream()
            store = ControlPlaneActivityStore(Path(temp_dir) / "jarvis.db")
            recorder = ControlPlaneActivityRecorder(stream, durable_store=store)
            event = recorder.record_request(request_id="req-1", session_id="desktop")
            self.assertEqual(event.sequence, 1)
            self.assertEqual(stream.size, 1)
            self.assertEqual(store.load_events()[0].event_id, event.event_id)


if __name__ == "__main__":
    unittest.main()
