import unittest
from datetime import datetime, timezone

from src.core.canonical_cognitive_runtime import (
    CanonicalCognitiveRuntime,
    CanonicalCognitiveRuntimeError,
)


class CanonicalCognitiveRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = CanonicalCognitiveRuntime(
            clock=lambda: datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
        )

    def test_composes_context_world_reasoning_planning_and_initiative(self) -> None:
        result = self.runtime.run(
            "prepare a safe next step",
            request_id="request-cs1",
            context_ids=("session-cs1",),
        )

        self.assertEqual(
            result.stage_sequence,
            ("context", "world_model", "reasoning", "planning", "initiative"),
        )
        self.assertEqual(result.lineage["request_id"], "request-cs1")
        self.assertEqual(result.lineage["world_snapshot_id"], result.world_snapshot.snapshot_id)
        self.assertEqual(result.lineage["reasoning_result_id"], result.reasoning.context.request_id)
        self.assertEqual(result.lineage["planning_context_id"], result.planning.context.context_id)
        self.assertIsNotNone(result.proposal_id)
        self.assertTrue(result.ready_for_downstream_validation)

    def test_cognitive_result_never_grants_authority_or_execution(self) -> None:
        result = self.runtime.run("review this task", request_id="request-boundary")
        context = result.to_context()

        self.assertFalse(context["authority_granted"])
        self.assertFalse(context["authorization_granted"])
        self.assertFalse(context["execution_requested"])
        self.assertFalse(context["execution_performed"])
        self.assertFalse(context["truth_established"])
        self.assertFalse(context["certainty_established"])
        self.assertFalse(self.runtime.authorizes_execution)
        self.assertFalse(self.runtime.executes_capability)
        self.assertFalse(self.runtime.establishes_truth)
        self.assertFalse(self.runtime.establishes_certainty)

    def test_invalid_request_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            self.runtime.run("")

    def test_invalid_timestamp_fails_closed(self) -> None:
        with self.assertRaises(CanonicalCognitiveRuntimeError):
            self.runtime.run("review", request_id="bad-time", created_at="not-a-timestamp")


if __name__ == "__main__":
    unittest.main()
