import unittest

from src.context.context_source_integration import ContextSourceIntegration
from src.context.context_source_selection import ContextSource, ContextSourceSelector
from src.context.models import ContextItem, ContextPackage
from src.context.working_context_composer import WorkingContextComposer


class ContextSourceIntegrationTests(unittest.TestCase):
    def _composer(self, items=()):
        package = ContextPackage(
            request="inspect config",
            items=tuple(items),
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
        self.assertEqual(result.context_package.items[0].content, "selected")
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
        self.assertEqual(result.context_package.items[0].content, "old value")
        self.assertEqual(result.source_selection.refresh_required, ("memory-1",))

    def test_composer_rejects_persistent_item_without_selected_identity(self):
        selection = ContextSourceSelector(minimum_relevance=0.2).select(
            "inspect config",
            (ContextSource("memory-1", "MEMORY", relevance_score=0.9),),
        )
        composer = self._composer(
            items=(ContextItem("MEMORY", "unidentified"),)
        )
        with self.assertRaises(ValueError):
            composer.compose(
                "inspect config",
                source_selection=selection,
            )

    def test_composer_rejects_resolved_items_without_selection(self):
        composer = self._composer()
        with self.assertRaises(ValueError):
            composer.compose(
                "inspect config",
                resolved_persistent_items=(
                    ContextItem(
                        "MEMORY", "memory", provenance={"source_id": "memory-1"}
                    ),
                ),
            )


if __name__ == "__main__":
    unittest.main()
