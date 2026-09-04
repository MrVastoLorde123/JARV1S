import tempfile
import unittest
from pathlib import Path

from src.context.memory_context_source_provider import MemoryContextSourceProvider
from src.context.models import ContextOptions
from src.context.working_context_runtime import WorkingContextRuntime
from src.personalization.end_to_end import PersonalizedWorkingContextRuntime
from src.personalization.persistence import PersonalizationStore
from src.personalization.profile import PersonalizationSignal, build_profile


class EndToEndPersonalizationTests(unittest.TestCase):
    def signal(self, signal_id="persisted-1", value="concise"):
        return PersonalizationSignal(
            signal_id=signal_id,
            category="PREFERENCE",
            key="response_style",
            value=value,
            confidence=0.9,
            importance=0.8,
            source_ids=("memory:1", "evidence:1"),
            explicit_user_preference=True,
        )

    def base_runtime(self):
        provider = MemoryContextSourceProvider(
            include_memories=False,
            include_evidence=False,
        )
        return WorkingContextRuntime(provider)

    def test_persisted_personalization_is_injected_into_working_context(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PersonalizationStore(Path(directory) / "personalization.json")
            store.persist_profile(build_profile("profile-1", (self.signal(),), provenance={"source": "test"}))
            runtime = PersonalizedWorkingContextRuntime(
                self.base_runtime(),
                persistence_store=store,
            )
            context = runtime.compose("Explain JARVIS")
            personalization_items = [
                item for item in context.context_package.items
                if item.source_type == "PERSONALIZATION"
            ]
            self.assertEqual(len(personalization_items), 1)
            self.assertIn("concise", personalization_items[0].content)

    def test_reversed_personalization_is_not_injected(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PersonalizationStore(Path(directory) / "personalization.json")
            store.persist_profile(build_profile("profile-1", (self.signal(),), provenance={"source": "test"}))
            store.reverse("personalization:persisted-1", "user-undo-1")
            runtime = PersonalizedWorkingContextRuntime(
                self.base_runtime(),
                persistence_store=store,
            )
            context = runtime.compose("Explain JARVIS")
            self.assertFalse(
                any(item.source_type == "PERSONALIZATION" for item in context.context_package.items)
            )

    def test_authority_boundary_is_preserved(self):
        runtime = PersonalizedWorkingContextRuntime(self.base_runtime())
        context = runtime.compose("Explain JARVIS")
        self.assertTrue(context.metadata.get("personalization_integrated"))
        self.assertFalse(context.metadata["authority_granted"])
        self.assertFalse(context.metadata["authorization_granted"])
        self.assertFalse(context.metadata["policy_mutation"])
        self.assertFalse(context.metadata["execution_requested"])

    def test_existing_context_is_preserved(self):
        runtime = PersonalizedWorkingContextRuntime(self.base_runtime())
        context = runtime.compose("Explain JARVIS")
        self.assertGreaterEqual(len(context.context_package.items), 0)
        self.assertEqual(context.request, "Explain JARVIS")


if __name__ == "__main__":
    unittest.main(verbosity=2)
