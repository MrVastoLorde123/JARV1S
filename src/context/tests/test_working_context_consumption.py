import unittest

from src.ai.models import AIRequest
from src.context.context_source_selection import (
    ContextSourceDecision,
    ContextSourceSelection,
)
from src.context.models import ContextItem, ContextPackage
from src.context.working_context import WorkingContext
from src.context.working_context_consumption import WorkingContextConsumptionBoundary


class WorkingContextConsumptionBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.boundary = WorkingContextConsumptionBoundary()
        self.selection = ContextSourceSelection(
            request="What do we know about the project?",
            selected=(
                ContextSourceDecision(
                    source_id="memory-1",
                    source_type="MEMORY",
                    selected=True,
                    refresh_required=False,
                    authority_allowed=True,
                    reason="eligible",
                ),
            ),
            excluded=(
                ContextSourceDecision(
                    source_id="memory-2",
                    source_type="MEMORY",
                    selected=False,
                    refresh_required=False,
                    authority_allowed=False,
                    reason="source_not_relevant",
                ),
            ),
            refresh_required=(),
        )
        self.working_context = WorkingContext(
            request="What do we know about the project?",
            context_package=ContextPackage(
                request="What do we know about the project?",
                items=(
                    ContextItem(
                        source_type="MEMORY",
                        content="The project is private and local-first.",
                        relevance_score=0.9,
                        provenance={"source_id": "memory-1"},
                    ),
                    ContextItem(
                        source_type="OBSERVATION",
                        content="The current branch contains the M6.5 context boundary.",
                        relevance_score=1.0,
                        provenance={"source_id": "observation-1"},
                    ),
                ),
                instructions=("Treat stored memories as claims, not automatic truth.",),
                metadata={"resolved_persistent_item_count": 1},
            ),
            source_selection=self.selection,
            metadata={"context_stage": "M6.5"},
        )

    def test_consumes_only_working_context(self):
        request = self.boundary.consume(self.working_context)

        self.assertIsInstance(request, AIRequest)
        self.assertEqual(request.task, self.working_context.request)
        self.assertEqual(request.context, self.working_context.to_context())
        self.assertTrue(request.metadata["working_context_consumed"])

    def test_preserves_generation_and_request_metadata(self):
        request = self.boundary.consume(
            self.working_context,
            model="test-model",
            generation_options={"temperature": 0.2},
            metadata={"request_id": "abc-123"},
        )

        self.assertEqual(request.model, "test-model")
        self.assertEqual(request.generation_options, {"temperature": 0.2})
        self.assertEqual(request.metadata["request_id"], "abc-123")
        self.assertTrue(request.metadata["working_context_consumed"])

    def test_selected_and_excluded_source_state_is_carried_forward(self):
        request = self.boundary.consume(self.working_context)
        source_selection = request.context["source_selection"]

        self.assertEqual(source_selection["selected_source_ids"], ("memory-1",))
        self.assertEqual(source_selection["excluded_source_ids"], ("memory-2",))
        self.assertEqual(source_selection["refresh_required"], ())

    def test_rejects_non_working_context(self):
        with self.assertRaises(TypeError):
            self.boundary.consume("not working context")


if __name__ == "__main__":
    unittest.main(verbosity=2)
