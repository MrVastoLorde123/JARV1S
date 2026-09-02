import unittest
from types import SimpleNamespace

from src.context.context_source_integration import ContextSourceIntegration
from src.context.context_source_selection import ContextSource
from src.context.models import ContextItem, ContextPackage
from src.context.working_context_composer import WorkingContextComposer


class ContextSourceIntegrationTests(unittest.TestCase):
    def _composer(self):
        package = ContextPackage(
            request="inspect config",
            items=(),
            instructions=(),
        )
        return WorkingContextComposer(lambda *args, **kwargs: package)

    def test_selection_flows_into_working_context(self):
        integration = ContextSourceIntegration(composer=self._composer())
        result = integration.compose(
            "inspect config",
            (
                ContextSource("memory-1", "MEMORY", relevance_score=0.9),
                ContextSource("memory-2", "MEMORY", relevance_score=0.1),
            ),
            {
                "memory-1": ContextItem(
                    "MEMORY", "selected", provenance={"source_id": "memory-1"}
                ),
                "memory-2": ContextItem(
                    "MEMORY", "excluded", provenance={"source_id": "memory-2"}
                ),
            },
        )

        self.assertEqual(result.source_selection.selected_source_ids, ("memory-1",))
        self.assertEqual(result.source_selection.excluded_source_ids, ("memory-2",))
        self.assertEqual(result.metadata["source_selection_count"], 1)

    def test_stale_selection_remains_visible_but_not_authoritative(self):
        integration = ContextSourceIntegration(composer=self._composer())
        result = integration.compose(
            "inspect config",
            (
                ContextSource(
                    "memory-1",
                    "MEMORY",
                    relevance_score=0.9,
                    last_refreshed_at=100.0,
                    refresh_interval_seconds=50.0,
                ),
            ),
            {
                "memory-1": ContextItem(
                    "MEMORY", "old value", provenance={"source_id": "memory-1"}
                ),
            },
            now=151.0,
        )

        decision = result.source_selection.selected[0]
        self.assertTrue(decision.refresh_required)
        self.assertFalse(decision.authority_allowed)
        self.assertEqual(result.context_package.items, ())

    def test_non_selected_persistent_items_cannot_bypass_selection(self):
        from src.context.context_source_selection import ContextSourceSelector

        selection = ContextSourceSelector(minimum_relevance=0.2).select(
            "inspect config",
            (ContextSource("memory-1", "MEMORY", relevance_score=0.9),),
        )
        composer = self._composer()
        with self.assertRaises(ValueError):
            composer.compose(
                "inspect config",
                source_selection=selection,
            )


if __name__ == "__main__":
    unittest.main()
