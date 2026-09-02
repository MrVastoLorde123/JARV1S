import unittest

from src.context.context_source_selection import (
    ContextSource,
    ContextSourceSelector,
)
from src.context.models import ContextItem, ContextPackage
from src.context.working_context_composer import WorkingContextComposer


class ContextSourceSelectorTests(unittest.TestCase):
    def _selector(self):
        return ContextSourceSelector(minimum_relevance=0.20)

    def test_selects_relevant_persistent_sources_deterministically(self):
        selector = self._selector()
        sources = (
            ContextSource("memory-b", "MEMORY", relevance_score=0.7, priority=1),
            ContextSource("memory-a", "MEMORY", relevance_score=0.7, priority=1),
            ContextSource("evidence-a", "EVIDENCE", relevance_score=0.5, priority=2),
        )

        first = selector.select("find config", sources)
        second = selector.select("find config", reversed(sources))

        self.assertEqual(first.selected_source_ids, ("memory-a", "memory-b", "evidence-a"))
        self.assertEqual(first.selected_source_ids, second.selected_source_ids)
        self.assertEqual(first.refresh_required, ())

    def test_excludes_irrelevant_disabled_and_non_persistent_sources(self):
        selector = self._selector()
        result = selector.select(
            "find config",
            (
                ContextSource("relevant", "MEMORY", relevance_score=0.9),
                ContextSource("irrelevant", "MEMORY", relevance_score=0.1),
                ContextSource("disabled", "MEMORY", relevance_score=0.9, enabled=False),
                ContextSource("ephemeral", "STATE", relevance_score=0.9, persistent=False),
            ),
        )

        self.assertEqual(result.selected_source_ids, ("relevant",))
        reasons = {decision.source_id: decision.reason for decision in result.excluded}
        self.assertEqual(reasons["irrelevant"], "below_relevance_threshold")
        self.assertEqual(reasons["disabled"], "source_disabled")
        self.assertEqual(reasons["ephemeral"], "source_not_persistent")

    def test_stale_source_is_selected_but_not_authoritative_and_requires_refresh(self):
        selector = self._selector()
        result = selector.select(
            "find config",
            (
                ContextSource(
                    "memory-1",
                    "MEMORY",
                    relevance_score=0.9,
                    last_refreshed_at=100.0,
                    refresh_interval_seconds=50.0,
                ),
            ),
            now=151.0,
        )

        decision = result.selected[0]
        self.assertTrue(decision.selected)
        self.assertTrue(decision.refresh_required)
        self.assertFalse(decision.authority_allowed)
        self.assertEqual(result.refresh_required, ("memory-1",))
        self.assertEqual(
            decision.reason,
            "refresh_required_before_authoritative_reuse",
        )

    def test_refresh_requires_explicit_clock_when_refresh_interval_exists(self):
        selector = self._selector()
        with self.assertRaises(ValueError):
            selector.select(
                "find config",
                (
                    ContextSource(
                        "memory-1",
                        "MEMORY",
                        relevance_score=0.9,
                        refresh_interval_seconds=50.0,
                    ),
                ),
            )

    def test_explicit_task_and_execution_context_are_outside_source_selection(self):
        selector = self._selector()
        result = selector.select(
            "inspect config",
            (
                ContextSource("memory-1", "MEMORY", relevance_score=0.9),
            ),
        )

        self.assertEqual(result.selected_source_ids, ("memory-1",))
        self.assertNotIn("TASK", [decision.source_type for decision in result.selected])
        self.assertNotIn(
            "EXECUTION",
            [decision.source_type for decision in result.selected],
        )

    def test_selection_does_not_mutate_or_compose_context(self):
        selector = self._selector()
        source = ContextSource("memory-1", "MEMORY", relevance_score=0.9)
        result = selector.select("inspect config", (source,))

        package = ContextPackage(
            request="inspect config",
            items=(ContextItem("MEMORY", "stored config"),),
            instructions=(),
        )
        calls = []
        composer = WorkingContextComposer(
            lambda *args, **kwargs: calls.append((args, kwargs)) or package
        )

        working = composer.compose("inspect config")

        self.assertEqual(source.relevance_score, 0.9)
        self.assertEqual(result.selected_source_ids, ("memory-1",))
        self.assertEqual(len(calls), 1)
        self.assertIs(working.context_package, package)


if __name__ == "__main__":
    unittest.main()
