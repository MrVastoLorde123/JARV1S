import unittest

from src.context.context_source_resolution import ContextSourceResolver
from src.context.context_source_selection import ContextSource, ContextSourceSelector
from src.context.models import ContextItem


class ContextSourceResolverTests(unittest.TestCase):
    def _selection(self):
        return ContextSourceSelector(minimum_relevance=0.2).select(
            "inspect config",
            (
                ContextSource("memory-1", "MEMORY", relevance_score=0.9),
                ContextSource("memory-2", "MEMORY", relevance_score=0.1),
            ),
        )

    def test_resolves_only_selected_source_ids(self):
        selection = self._selection()
        resolver = ContextSourceResolver()
        result = resolver.resolve(
            selection,
            {
                "memory-1": ContextItem(
                    "MEMORY", "selected memory", provenance={"source_id": "memory-1"}
                ),
                "memory-2": ContextItem(
                    "MEMORY", "excluded memory", provenance={"source_id": "memory-2"}
                ),
            },
        )

        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.items[0].content, "selected memory")
        self.assertEqual(result.missing_source_ids, ())

    def test_reports_missing_selected_sources_without_inventing_items(self):
        selection = self._selection()
        resolver = ContextSourceResolver()
        result = resolver.resolve(
            selection,
            {},
        )

        self.assertEqual(result.items, ())
        self.assertEqual(result.missing_source_ids, ("memory-1",))

    def test_iterable_sources_require_explicit_source_id_provenance(self):
        selection = self._selection()
        resolver = ContextSourceResolver()
        with self.assertRaises(ValueError):
            resolver.resolve(
                selection,
                (ContextItem("MEMORY", "missing identity"),),
            )

    def test_mapping_values_must_be_context_items(self):
        selection = self._selection()
        resolver = ContextSourceResolver()
        with self.assertRaises(TypeError):
            resolver.resolve(selection, {"memory-1": "not a context item"})


if __name__ == "__main__":
    unittest.main()
