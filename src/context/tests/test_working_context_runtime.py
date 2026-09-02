import unittest
from unittest.mock import Mock

from src.context.context_source_integration import ContextSourceIntegration
from src.context.context_source_provider import ContextSourceProvider
from src.context.context_source_selection import ContextSource
from src.context.models import ContextItem, ContextPackage
from src.context.working_context import WorkingContext
from src.context.working_context_runtime import WorkingContextRuntime
from src.core.conversation_models import StateSnapshot


class FakeSourceProvider(ContextSourceProvider):
    def __init__(self, sources, items):
        self.sources = tuple(sources)
        self.items = items
        self.get_sources_calls = []
        self.get_context_items_calls = []

    def get_sources(self, request):
        self.get_sources_calls.append(request)
        return self.sources

    def get_context_items(self, request, sources):
        self.get_context_items_calls.append((request, tuple(sources)))
        return self.items


class WorkingContextRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.sources = (
            ContextSource(
                source_id="memory-1",
                source_type="MEMORY",
                relevance_score=0.9,
                priority=1,
            ),
            ContextSource(
                source_id="memory-2",
                source_type="MEMORY",
                relevance_score=0.1,
                priority=1,
            ),
        )
        self.items = {
            "memory-1": ContextItem(
                source_type="MEMORY",
                content="Selected memory",
                relevance_score=0.9,
                provenance={"source_id": "memory-1"},
            ),
            "memory-2": ContextItem(
                source_type="MEMORY",
                content="Excluded memory",
                relevance_score=0.1,
                provenance={"source_id": "memory-2"},
            ),
        }
        self.provider = FakeSourceProvider(self.sources, self.items)
        self.runtime = WorkingContextRuntime(self.provider)

    def test_runtime_is_single_context_construction_entry_point(self):
        context = self.runtime.compose("Project context")

        self.assertIsInstance(context, WorkingContext)
        self.assertEqual(context.source_selection.selected_source_ids, ("memory-1",))
        self.assertEqual(context.source_selection.excluded_source_ids, ("memory-2",))
        self.assertEqual(len(context.context_package.items), 1)
        self.assertEqual(context.context_package.items[0].content, "Selected memory")

    def test_runtime_owns_source_acquisition_and_passes_sources_to_integration(self):
        integration = Mock(spec=ContextSourceIntegration)
        expected = WorkingContext(
            request="Project context",
            context_package=ContextPackage(
                request="Project context",
                items=(),
            ),
        )
        integration.compose.return_value = expected
        runtime = WorkingContextRuntime(self.provider, integration=integration)

        result = runtime.compose("Project context", now=123.0)

        self.assertIs(result, expected)
        self.assertEqual(self.provider.get_sources_calls, ["Project context"])
        self.assertEqual(
            self.provider.get_context_items_calls,
            [("Project context", self.sources)],
        )
        integration.compose.assert_called_once()
        call = integration.compose.call_args
        self.assertEqual(call.args[0], "Project context")
        self.assertEqual(call.args[1], self.sources)
        self.assertIs(call.args[2], self.items)
        self.assertEqual(call.kwargs["now"], 123.0)

    def test_runtime_cannot_bypass_selection_pipeline(self):
        class RejectingIntegration(ContextSourceIntegration):
            def compose(self, *args, **kwargs):
                raise AssertionError("runtime bypassed selection/resolution integration")

        runtime = WorkingContextRuntime(
            self.provider,
            integration=RejectingIntegration(),
        )
        with self.assertRaises(AssertionError):
            runtime.compose("Project context")

    def test_runtime_accepts_conversation_and_execution_context_without_owning_them(self):
        conversation = StateSnapshot(
            conversation_id="conversation-1",
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
            active_topic="JARVIS",
            active_task=None,
            turns=(),
        )

        context = self.runtime.compose(
            "Project context",
            conversation_state=conversation,
            metadata={"request_id": "abc"},
        )

        self.assertIs(context.conversation_state, conversation)
        self.assertEqual(context.metadata["request_id"], "abc")
        self.assertEqual(context.metadata["working_context_runtime"], "v1")

    def test_runtime_does_not_expose_ai_or_execution_authority(self):
        self.assertFalse(hasattr(self.runtime, "ai_service"))
        self.assertFalse(hasattr(self.runtime, "plan_executor"))
        self.assertFalse(hasattr(self.runtime, "execution_policy"))

    def test_invalid_provider_is_rejected(self):
        with self.assertRaises(TypeError):
            WorkingContextRuntime(object())

    def test_empty_request_is_rejected_before_source_acquisition(self):
        with self.assertRaises(ValueError):
            self.runtime.compose("   ")
        self.assertEqual(self.provider.get_sources_calls, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
