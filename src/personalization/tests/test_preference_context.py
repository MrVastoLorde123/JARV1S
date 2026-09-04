import unittest

from src.personalization.preference_context import PreferenceContextResolver


class FakeMemory:
    def __init__(self, memory_id, category, key, content, confidence=0.8, importance=0.6, relevance_score=0.9):
        self.memory_id = memory_id
        self.category = category
        self.memory_key = key
        self.content = content
        self.confidence = confidence
        self.importance = importance
        self.status = "ACTIVE"
        self.relevance_score = relevance_score


class FakeLoadedMemory:
    def __init__(self, evidence=()):
        self.evidence = evidence


class PreferenceContextResolverTests(unittest.TestCase):
    def setUp(self):
        self.memories = [
            FakeMemory(1, "PREFERENCE", "response_style", "Prefer concise answers."),
            FakeMemory(2, "PROJECT", "project", "JARVIS"),
        ]
        self.loaded = {
            1: FakeLoadedMemory(((11, 1, "conversation", "message", "Prefer concise answers.", "DIRECT", 0.9, "t", "t"),)),
        }

    def resolver(self):
        return PreferenceContextResolver(
            searcher=lambda query, limit: self.memories[:limit],
            loader=lambda memory_id: self.loaded.get(memory_id),
        )

    def test_resolves_only_preference_memories(self):
        profile = self.resolver().resolve("how should you answer me?")
        self.assertEqual(len(profile.preferences), 1)
        self.assertEqual(profile.preferences[0].value, "Prefer concise answers.")

    def test_preserves_memory_and_evidence_provenance(self):
        profile = self.resolver().resolve("how should you answer me?")
        signal = profile.preferences[0]
        self.assertEqual(signal.source_ids, ("memory:1", "evidence:11"))
        self.assertEqual(signal.metadata["memory_id"], 1)
        self.assertEqual(signal.metadata["evidence_count"], 1)

    def test_profile_remains_non_authoritative(self):
        profile = self.resolver().resolve("how should you answer me?")
        data = profile.to_dict()
        self.assertFalse(data["truth_guaranteed"])
        self.assertFalse(data["authority_granted"])
        self.assertFalse(data["authorization_granted"])
        self.assertFalse(data["policy_mutation"])
        self.assertFalse(data["execution_requested"])

    def test_empty_query_is_rejected(self):
        with self.assertRaises(ValueError):
            self.resolver().resolve("   ")

    def test_zero_limit_returns_empty_profile(self):
        profile = self.resolver().resolve("preferences", limit=0)
        self.assertEqual(profile.signals, ())


if __name__ == "__main__":
    unittest.main(verbosity=2)
